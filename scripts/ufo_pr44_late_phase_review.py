from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689115"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR44"
DEFAULT_VIDEO = Path(r"source-files-not-included/DOD_111689115.mp4")
DEFAULT_SEED_TRACK = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689115.csv")
OUT_ROOT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr44-late-phase-review") / VIDEO_ID

CROP_WIDTH = 960
CROP_HEIGHT = 540
CROP_X0 = 480
CROP_Y0 = 270


@dataclass
class Seed:
    second: int
    x: float | None
    y: float | None
    confidence: str
    note: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def center_crop(frame: np.ndarray) -> np.ndarray:
    return frame[CROP_Y0 : CROP_Y0 + CROP_HEIGHT, CROP_X0 : CROP_X0 + CROP_WIDTH].copy()


def load_seeds(path: Path, start: int, end: int) -> dict[int, Seed]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    seeds: dict[int, Seed] = {}
    for row in rows:
        second = int(float(row["second_index"]))
        if not (start <= second <= end):
            continue
        if row["best_x"] and row["best_y"]:
            x = float(row["best_x"])
            y = float(row["best_y"])
        else:
            x = None
            y = None
        seeds[second] = Seed(second=second, x=x, y=y, confidence=row["confidence"], note=row["note"])
    return seeds


def phase_for(second: int) -> tuple[str, str]:
    if 244 <= second <= 263:
        return (
            "reticle-cycling tail",
            "After dense track; still inside DVIDS 03:25-04:23 changing reticle/field-of-view interval",
        )
    if 264 <= second <= 290:
        return (
            "zoom-out continued-track interval",
            "Within DVIDS 04:24-04:50 sensor zooms out and continues tracking interval",
        )
    if 291 <= second <= 294:
        return (
            "loss-exit interval",
            "Within DVIDS 04:50-04:54 sensor stops tracking as object exits field of view interval",
        )
    return ("outside late review interval", "Outside selected late PR44 review interval")


def colored_overlay_mask(crop: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 45) & (hue <= 115)
    red_or_orange = (hue <= 25) | (hue >= 170)
    mask = ((sat > 65) & (val > 65) & (cyan_green | red_or_orange)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)


def nearest_overlay_distance(crop: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(crop)
    pts = cv2.findNonZero(mask)
    if pts is None:
        return "no colored overlay detected", None
    arr = pts.reshape(-1, 2)
    distances = np.sqrt((arr[:, 0] - x) ** 2 + (arr[:, 1] - y) ** 2)
    nearest = float(distances.min()) if len(distances) else None
    if nearest is None:
        return "no colored overlay detected", None
    if nearest <= 5:
        return "intersects colored overlay", nearest
    if nearest <= 35:
        return "near colored overlay", nearest
    return "separate from colored overlay", nearest


def add_label(img: np.ndarray, text: str, width: int = 900) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 34), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def draw_seed(out: np.ndarray, x: float, y: float, color: tuple[int, int, int] = (0, 0, 255)) -> None:
    point = (int(round(x)), int(round(y)))
    cv2.drawMarker(out, point, color, markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    cv2.circle(out, point, 22, color, 2)
    cv2.line(out, (CROP_WIDTH // 2, CROP_HEIGHT // 2), point, (255, 255, 0), 1)


def crop_patch(crop: np.ndarray, x: float, y: float, size: int = 140) -> np.ndarray:
    h, w = crop.shape[:2]
    half = size // 2
    cx = int(round(x))
    cy = int(round(y))
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return crop[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_crop(crop: np.ndarray, second: int, phase: str, seed: Seed) -> np.ndarray:
    out = crop.copy()
    if seed.x is not None and seed.y is not None:
        draw_seed(out, seed.x, seed.y)
        status = f"seed={seed.confidence}"
    else:
        status = "no conservative seed"
    label = f"{VIDEO_ID} t={second:03d}s {phase}; {status}"
    return add_label(out, label)


def annotate_patch(patch: np.ndarray, second: int, confidence: str) -> np.ndarray:
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (210, 210), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=34, thickness=2)
    cv2.circle(out, (210, 210), 46, (0, 0, 255), 2)
    return add_label(out, f"{VIDEO_ID} t={second:03d}s seed={confidence}", width=420)


def write_contact_sheets(paths: list[Path], out_dir: Path, prefix: str, cols: int, thumb_width: int) -> list[Path]:
    ensure_dir(out_dir)
    written: list[Path] = []
    page_size = cols * 5
    for page, start in enumerate(range(0, len(paths), page_size)):
        chunk = paths[start : start + page_size]
        thumbs = []
        for path in chunk:
            img = cv2.imread(str(path))
            if img is None:
                continue
            scale = thumb_width / img.shape[1]
            thumbs.append(cv2.resize(img, (thumb_width, int(img.shape[0] * scale)), interpolation=cv2.INTER_AREA))
        if not thumbs:
            continue
        thumb_h = max(thumb.shape[0] for thumb in thumbs)
        rows = math.ceil(len(thumbs) / cols)
        sheet = np.zeros((rows * thumb_h, cols * thumb_width, 3), dtype=np.uint8)
        for index, thumb in enumerate(thumbs):
            row = index // cols
            col = index % cols
            y = row * thumb_h
            x = col * thumb_width
            sheet[y : y + thumb.shape[0], x : x + thumb.shape[1]] = thumb
        out = out_dir / f"{prefix}-{page:02d}.jpg"
        cv2.imwrite(str(out), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        written.append(out)
    return written


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="PR44 late-phase qualitative review for DOD_111689115.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--seed-track", type=Path, default=DEFAULT_SEED_TRACK)
    parser.add_argument("--start", type=int, default=244)
    parser.add_argument("--end", type=int, default=294)
    args = parser.parse_args()

    seeds = load_seeds(args.seed_track, args.start, args.end)
    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0

    annotated_dir = OUT_ROOT / "annotated-center-crops"
    patch_dir = OUT_ROOT / "seed-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    for index, second in enumerate(range(args.start, args.end + 1)):
        frame_index = int(round(second * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        crop = center_crop(frame)
        seed = seeds.get(second, Seed(second=second, x=None, y=None, confidence="none", note="no row in seed table"))
        phase, dvids_anchor = phase_for(second)
        phase_observation = "conservative compact return detected" if seed.x is not None and seed.y is not None else "no conservative compact return detected"
        relation = ""
        nearest_overlay = ""
        annotated_path = annotated_dir / f"frame_{index:04d}_annotated.jpg"
        cv2.imwrite(str(annotated_path), annotate_crop(crop, second, phase, seed), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        annotated_paths.append(annotated_path)

        patch_path = ""
        if seed.x is not None and seed.y is not None:
            relation, nearest = nearest_overlay_distance(crop, seed.x, seed.y)
            nearest_overlay = "" if nearest is None else round(nearest, 2)
            path = patch_dir / f"frame_{index:04d}_patch.jpg"
            cv2.imwrite(str(path), annotate_patch(crop_patch(crop, seed.x, seed.y), second, seed.confidence), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
            patch_paths.append(path)
            patch_path = str(path).replace("\\", "/")

        rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "review_index": index,
                "approx_second": second,
                "source_frame_index": frame_index,
                "phase": phase,
                "dvids_anchor": dvids_anchor,
                "phase_observation": phase_observation,
                "seed_x_center_crop": "" if seed.x is None else round(seed.x, 1),
                "seed_y_center_crop": "" if seed.y is None else round(seed.y, 1),
                "seed_x_full_frame": "" if seed.x is None else round(seed.x + CROP_X0, 1),
                "seed_y_full_frame": "" if seed.y is None else round(seed.y + CROP_Y0, 1),
                "seed_confidence": seed.confidence,
                "seed_note": seed.note,
                "overlay_relation": relation,
                "nearest_colored_overlay_px": nearest_overlay,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": patch_path,
            }
        )
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr44-late-phase-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr44-late-phase-patches", cols=8, thumb_width=180)

    review_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-late-phase-review-dod111689115.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "interval", "value": f"{args.start}s-{args.end}s", "note": "late PR44 phase review interval"},
        {"metric": "sample_count", "value": len(rows), "note": "one-fps qualitative samples"},
        {"metric": "detected_seed_rows", "value": sum(1 for row in rows if row["seed_x_center_crop"] != ""), "note": "conservative one-fps compact-return detections"},
        {"metric": "no_seed_rows", "value": sum(1 for row in rows if row["seed_x_center_crop"] == ""), "note": "no conservative compact target found"},
    ]
    for key, value in sorted(Counter(row["phase"] for row in rows).items()):
        phase_rows = [row for row in rows if row["phase"] == key]
        detections = sum(1 for row in phase_rows if row["seed_x_center_crop"] != "")
        summary_rows.append({"metric": f"phase_count: {key}", "value": value, "note": f"{detections} compact-return detections in this phase"})
    for key, value in sorted(Counter(row["seed_confidence"] for row in rows).items()):
        summary_rows.append({"metric": f"seed_confidence_count: {key}", "value": value, "note": "one-fps seed confidence"})
    for key, value in sorted(Counter(row["overlay_relation"] for row in rows if row["overlay_relation"]).items()):
        summary_rows.append({"metric": f"overlay_count: {key}", "value": value, "note": "seed relation to colored overlay"})

    summary_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-late-phase-review-summary.csv")
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "late_phase_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR44 one-fps late phase review"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR44 late phase summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "late phase annotated center-crop sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "late phase seed zoom-patch sheet"})
    asset_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-late-phase-review-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"interval={args.start}-{args.end}s rows={len(rows)}")
    print(f"phase_counts={dict(Counter(row['phase'] for row in rows))}")
    print(f"seed_confidence_counts={dict(Counter(row['seed_confidence'] for row in rows))}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()
