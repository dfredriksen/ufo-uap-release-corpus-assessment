from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = ROOT / "source-files-not-included" / "DOD_111689115.mp4"
DEFAULT_OUT_DIR = ROOT / "research" / "ufo-derived" / "overlay-measurement-audit" / "DOD_111689115-motion-compare"
DEFAULT_OUTPUT = ROOT / "research" / "ufo-overlay-measurement-pr44-motion-compare.csv"
DEFAULT_CONTACT_SHEET = DEFAULT_OUT_DIR / "pr44_overlay_motion_compare_contact_sheet.jpg"


def cyan_mask(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((hue >= 45) & (hue <= 115) & (sat > 45) & (val > 60)).astype(np.uint8) * 255
    return cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))


def bright_white_mask(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((sat < 70) & (val > 185)).astype(np.uint8) * 255
    return cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))


def components(mask: np.ndarray) -> list[dict[str, float]]:
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    rows: list[dict[str, float]] = []
    for label in range(1, count):
        x, y, w, h, area = stats[label]
        if area <= 0:
            continue
        cx, cy = centroids[label]
        rows.append(
            {
                "x": float(x),
                "y": float(y),
                "w": float(w),
                "h": float(h),
                "area": float(area),
                "cx": float(cx),
                "cy": float(cy),
            }
        )
    return rows


def pick_reticle_box(cyan_components: list[dict[str, float]]) -> dict[str, float] | None:
    candidates = [
        comp
        for comp in cyan_components
        if comp["w"] >= 80 and comp["h"] >= 80 and 0.65 <= comp["w"] / max(comp["h"], 1) <= 1.35
    ]
    return max(candidates, key=lambda comp: comp["area"], default=None)


def pick_label(cyan_components: list[dict[str, float]], box: dict[str, float]) -> dict[str, float] | None:
    box_right = box["x"] + box["w"]
    box_mid_y = box["y"] + box["h"] / 2
    candidates = []
    for comp in cyan_components:
        if comp is box:
            continue
        if comp["x"] <= box_right:
            continue
        if abs(comp["cy"] - box_mid_y) > 45:
            continue
        if not (12 <= comp["w"] <= 80 and 8 <= comp["h"] <= 40):
            continue
        candidates.append(comp)
    return min(candidates, key=lambda comp: comp["x"], default=None)


def pick_object(white_components: list[dict[str, float]], box: dict[str, float]) -> dict[str, float] | None:
    candidates = []
    for comp in white_components:
        if comp["x"] >= box["x"]:
            continue
        if comp["area"] < 8 or comp["area"] > 250:
            continue
        if comp["w"] > 25 or comp["h"] > 25:
            continue
        candidates.append(comp)
    if not candidates:
        return None
    return max(candidates, key=lambda comp: comp["area"])


def crop_analysis_region(frame: np.ndarray) -> tuple[np.ndarray, int, int]:
    x0, y0 = 840, 440
    x1, y1 = 1140, 670
    return frame[y0:y1, x0:x1].copy(), x0, y0


def draw_box(img: np.ndarray, comp: dict[str, float] | None, color: tuple[int, int, int], label: str) -> None:
    if comp is None:
        return
    x, y, w, h = int(comp["x"]), int(comp["y"]), int(comp["w"]), int(comp["h"])
    cv2.rectangle(img, (x, y), (x + w, y + h), color, 1)
    cv2.putText(img, label, (x, max(14, y - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1, cv2.LINE_AA)


def make_contact_sheet(images: list[np.ndarray], labels: list[str], output: Path, columns: int = 4) -> None:
    if not images:
        return
    tile_w, tile_h = 300, 230
    rows = (len(images) + columns - 1) // columns
    canvas = np.zeros((rows * tile_h, columns * tile_w, 3), dtype=np.uint8)
    for index, img in enumerate(images):
        tile = cv2.resize(img, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
        cv2.putText(tile, labels[index], (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 0, 255), 2, cv2.LINE_AA)
        y = (index // columns) * tile_h
        x = (index % columns) * tile_w
        canvas[y : y + tile_h, x : x + tile_w] = tile
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare PR44 label, reticle, and object motion across transition frames.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--start-frame", type=int, default=6996)
    parser.add_argument("--end-frame", type=int, default=7002)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--contact-sheet", type=Path, default=DEFAULT_CONTACT_SHEET)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.video.exists():
        raise SystemExit(f"Missing source video: {args.video}")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    annotated: list[np.ndarray] = []
    labels: list[str] = []

    for frame_index in range(args.start_frame, args.end_frame + 1):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        crop, x0, y0 = crop_analysis_region(frame)
        cyan_components = components(cyan_mask(crop))
        white_components = components(bright_white_mask(crop))
        box = pick_reticle_box(cyan_components)
        label = pick_label(cyan_components, box) if box else None
        obj = pick_object(white_components, box) if box else None

        out = crop.copy()
        draw_box(out, box, (0, 255, 255), "reticle")
        draw_box(out, label, (255, 255, 0), "label")
        draw_box(out, obj, (255, 255, 255), "object")

        second = frame_index / fps
        crop_path = args.out_dir / f"DOD_111689115_f{frame_index:06d}_motion_compare.jpg"
        cv2.imwrite(str(crop_path), out, [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated.append(out)
        labels.append(f"{second:.3f}s f{frame_index}")

        def full(comp: dict[str, float] | None, key: str) -> str:
            if comp is None:
                return ""
            if key in {"x", "cx"}:
                return f"{comp[key] + x0:.2f}"
            if key in {"y", "cy"}:
                return f"{comp[key] + y0:.2f}"
            return f"{comp[key]:.2f}"

        box_cx = box["cx"] + x0 if box else None
        box_cy = box["cy"] + y0 if box else None
        label_cx = label["cx"] + x0 if label else None
        label_cy = label["cy"] + y0 if label else None
        obj_cx = obj["cx"] + x0 if obj else None
        obj_cy = obj["cy"] + y0 if obj else None

        rows.append(
            {
                "case": "PR44",
                "video": args.video.name,
                "record_id": "DOW-UAP-PR44",
                "frame_index": str(frame_index),
                "second": f"{second:.3f}",
                "manual_label_text": "11M" if frame_index <= 6996 else "10M",
                "reticle_box_cx": "" if box_cx is None else f"{box_cx:.2f}",
                "reticle_box_cy": "" if box_cy is None else f"{box_cy:.2f}",
                "reticle_box_w": full(box, "w"),
                "reticle_box_h": full(box, "h"),
                "label_cx": "" if label_cx is None else f"{label_cx:.2f}",
                "label_cy": "" if label_cy is None else f"{label_cy:.2f}",
                "label_w": full(label, "w"),
                "label_h": full(label, "h"),
                "object_cx": "" if obj_cx is None else f"{obj_cx:.2f}",
                "object_cy": "" if obj_cy is None else f"{obj_cy:.2f}",
                "object_w": full(obj, "w"),
                "object_h": full(obj, "h"),
                "label_dx_from_reticle": "" if box_cx is None or label_cx is None else f"{label_cx - box_cx:.2f}",
                "label_dy_from_reticle": "" if box_cy is None or label_cy is None else f"{label_cy - box_cy:.2f}",
                "object_dx_from_reticle": "" if box_cx is None or obj_cx is None else f"{obj_cx - box_cx:.2f}",
                "object_dy_from_reticle": "" if box_cy is None or obj_cy is None else f"{obj_cy - box_cy:.2f}",
                "crop_artifact": str(crop_path.relative_to(ROOT)),
                "notes": "Computer-vision component positions for reticle, label, and bright object candidate; semantics unresolved.",
            }
        )

    cap.release()

    fieldnames = list(rows[0].keys()) if rows else []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    make_contact_sheet(annotated, labels, args.contact_sheet)
    print(f"Wrote {len(rows)} motion-comparison rows to {args.output}")
    print(f"Wrote contact sheet to {args.contact_sheet}")


if __name__ == "__main__":
    main()
