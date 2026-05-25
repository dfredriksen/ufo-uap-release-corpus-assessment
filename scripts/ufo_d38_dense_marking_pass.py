from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689030"
DEFAULT_SOURCE = Path(r"I:\My Drive\UFO\DOD_111689030.mp4")
DEFAULT_MANUAL_TRACK = Path("research/ufo-video-manual-track-dod111689030.csv")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/dense-marking") / VIDEO_ID


@dataclass
class ManualSeed:
    second: float
    x: float
    y: float
    quality: str
    phase: str
    caveat: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_manual_seeds(path: Path) -> list[ManualSeed]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    seeds: list[ManualSeed] = []
    for row in rows:
        seeds.append(
            ManualSeed(
                second=float(row["sample_second"]),
                x=float(row["manual_x_full_frame"]),
                y=float(row["manual_y_full_frame"]),
                quality=row["manual_quality"],
                phase=row["phase"],
                caveat=row["caveat"],
            )
        )
    seeds.sort(key=lambda seed: seed.second)
    return seeds


def phase_for_second(second: float) -> str:
    if 50.0 <= second <= 75.0:
        return "primary sustained DVIDS in-FOV interval"
    if 75.0 < second < 76.0:
        return "zoom-transition lead-in"
    if 76.0 <= second <= 87.0:
        return "post-zoom sustained interval"
    return "outside validated dense interval"


def interpolate_seed(seeds: list[ManualSeed], second: float) -> tuple[float, float, str, str]:
    seconds = np.array([seed.second for seed in seeds], dtype=np.float32)
    xs = np.array([seed.x for seed in seeds], dtype=np.float32)
    ys = np.array([seed.y for seed in seeds], dtype=np.float32)
    x = float(np.interp(second, seconds, xs))
    y = float(np.interp(second, seconds, ys))

    nearest = min(seeds, key=lambda seed: abs(seed.second - second))
    return x, y, nearest.quality, nearest.caveat


def local_bright_refine(frame: np.ndarray, predicted_x: float, predicted_y: float, radius: int = 72) -> dict:
    h, w = frame.shape[:2]
    px = int(round(predicted_x))
    py = int(round(predicted_y))
    x0 = max(0, px - radius)
    x1 = min(w, px + radius + 1)
    y0 = max(0, py - radius)
    y1 = min(h, py + radius + 1)
    window = frame[y0:y1, x0:x1]

    hsv = cv2.cvtColor(window, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
    low_sat = hsv[:, :, 1] < 58
    valid = low_sat & (gray > 55)
    if int(valid.sum()) < 12:
        return {}

    threshold = int(np.percentile(gray[valid], 98.9))
    threshold = max(155, min(threshold, 238))
    mask = ((gray >= threshold) & low_sat).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 3)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        bx, by, bw, bh, area = stats[label]
        if area < 3 or area > 1600:
            continue
        if bw > 90 or bh > 90:
            continue
        cx, cy = centroids[label]
        full_x = x0 + float(cx)
        full_y = y0 + float(cy)
        component_values = gray[labels == label]
        max_luma = int(component_values.max())
        mean_luma = float(component_values.mean())
        distance = math.hypot(full_x - predicted_x, full_y - predicted_y)
        compact_bonus = min(area, 240) / 240.0
        score = (2.0 * max_luma / 255.0) + (mean_luma / 255.0) + compact_bonus - (1.25 * distance / radius)
        candidates.append(
            {
                "x": full_x,
                "y": full_y,
                "bbox_x": x0 + int(bx),
                "bbox_y": y0 + int(by),
                "bbox_w": int(bw),
                "bbox_h": int(bh),
                "area": int(area),
                "max_luma": max_luma,
                "mean_luma": mean_luma,
                "distance_from_prediction": distance,
                "score": score,
            }
        )

    if not candidates:
        return {}
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[0]


def colored_overlay_mask(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    green_cyan = (hue >= 45) & (hue <= 105)
    yellow_orange_red = ((hue <= 30) | (hue >= 170))
    mask = ((sat > 70) & (val > 75) & (green_cyan | yellow_orange_red)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return mask


def classify_overlay_relation(frame: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(frame)
    overlay_points = cv2.findNonZero(mask)
    nearest_distance: float | None = None
    if overlay_points is not None:
        pts = overlay_points.reshape(-1, 2)
        if len(pts):
            distances = np.sqrt((pts[:, 0] - x) ** 2 + (pts[:, 1] - y) ** 2)
            nearest_distance = float(distances.min())

    if nearest_distance is None:
        return "no colored overlay detected", None
    if nearest_distance <= 5:
        return "intersects colored overlay", nearest_distance
    if nearest_distance <= 30:
        return "near colored overlay", nearest_distance
    return "separate from colored overlay", nearest_distance


def classify_confidence(refined: dict, nearest_seed_quality: str, second: float) -> str:
    if not refined:
        return "low"
    distance = float(refined["distance_from_prediction"])
    max_luma = int(refined["max_luma"])
    if nearest_seed_quality == "high" and distance <= 28 and max_luma >= 178:
        return "high"
    if distance <= 46 and max_luma >= 160:
        return "medium"
    if 76.0 <= second <= 87.0 and distance <= 58 and max_luma >= 150:
        return "medium"
    return "low"


def crop_patch(frame: np.ndarray, x: float, y: float, size: int = 140) -> np.ndarray:
    h, w = frame.shape[:2]
    half = size // 2
    cx = int(round(x))
    cy = int(round(y))
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def add_label(img: np.ndarray, text: str, width: int = 620) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 32), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, x: float, y: float, px: float, py: float, label: str) -> np.ndarray:
    out = frame.copy()
    cv2.circle(out, (int(round(px)), int(round(py))), 18, (255, 0, 0), 2)
    cv2.drawMarker(out, (int(round(x)), int(round(y))), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    cv2.circle(out, (int(round(x)), int(round(y))), 24, (0, 0, 255), 2)
    cv2.line(out, (960, 540), (int(round(x)), int(round(y))), (255, 255, 0), 2)
    return add_label(out, label)


def annotate_patch(patch: np.ndarray, label: str) -> np.ndarray:
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (210, 210), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=34, thickness=2)
    cv2.circle(out, (210, 210), 46, (0, 0, 255), 2)
    return add_label(out, label, width=420)


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
        thumb_h = max(t.shape[0] for t in thumbs)
        rows = math.ceil(len(thumbs) / cols)
        sheet = np.zeros((rows * thumb_h, cols * thumb_width, 3), dtype=np.uint8)
        for idx, thumb in enumerate(thumbs):
            row = idx // cols
            col = idx % cols
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
    parser = argparse.ArgumentParser(description="Generate dense D38 marking artifacts for DOD_111689030.")
    parser.add_argument("--video", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--manual-track", type=Path, default=DEFAULT_MANUAL_TRACK)
    parser.add_argument("--start", type=float, default=50.0)
    parser.add_argument("--end", type=float, default=87.0)
    parser.add_argument("--sample-rate", type=float, default=5.0)
    args = parser.parse_args()

    seeds = load_manual_seeds(args.manual_track)
    if args.start < seeds[0].second or args.end > seeds[-1].second:
        raise ValueError(f"Requested range {args.start}-{args.end}s outside manual seed range {seeds[0].second}-{seeds[-1].second}s")

    raw_dir = OUT_ROOT / "raw-frames"
    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "object-zoom-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for path in [raw_dir, annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(path)

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    control_deltas: list[float] = []
    sample_count = int(round((args.end - args.start) * args.sample_rate)) + 1

    for sample_index in range(sample_count):
        second = round(args.start + sample_index / args.sample_rate, 1)
        source_frame_index = min(int(round(second * fps)), max(0, total_frames - 1))
        dense_index = int(round(second * args.sample_rate))
        predicted_x, predicted_y, nearest_seed_quality, nearest_seed_caveat = interpolate_seed(seeds, second)

        cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame_index)
        ok, frame = cap.read()
        if not ok:
            continue

        raw_path = raw_dir / f"frame_{dense_index:04d}.jpg"
        cv2.imwrite(str(raw_path), frame, [int(cv2.IMWRITE_JPEG_QUALITY), 94])

        refined = local_bright_refine(frame, predicted_x, predicted_y)
        if refined:
            object_x = float(refined["x"])
            object_y = float(refined["y"])
            refinement_delta = float(refined["distance_from_prediction"])
            bbox_w = int(refined["bbox_w"])
            bbox_h = int(refined["bbox_h"])
            area = int(refined["area"])
            max_luma = int(refined["max_luma"])
            mean_luma = round(float(refined["mean_luma"]), 2)
            marking_basis = "manual-seed interpolation plus local bright-feature refinement"
        else:
            object_x = predicted_x
            object_y = predicted_y
            refinement_delta = 0.0
            bbox_w = ""
            bbox_h = ""
            area = ""
            max_luma = ""
            mean_luma = ""
            marking_basis = "manual-seed interpolation only; local bright feature not isolated"

        phase = phase_for_second(second)
        relation, nearest_overlay = classify_overlay_relation(frame, object_x, object_y)
        review_confidence = classify_confidence(refined, nearest_seed_quality, second)
        label = f"t={second:04.1f}s f={source_frame_index:04d} conf={review_confidence}"

        annotated_path = annotated_dir / f"frame_{dense_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{dense_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, object_x, object_y, predicted_x, predicted_y, label), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(crop_patch(frame, object_x, object_y), label), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)

        manual_seed_match = ""
        manual_control_delta = ""
        for seed in seeds:
            if abs(seed.second - second) < 0.001:
                manual_seed_match = "yes"
                manual_control_delta = round(math.hypot(object_x - seed.x, object_y - seed.y), 2)
                control_deltas.append(float(manual_control_delta))
                break

        rows.append(
            {
                "video": f"{VIDEO_ID}.mp4",
                "dense_frame_index": dense_index,
                "approx_second": f"{second:.1f}",
                "source_frame_index": source_frame_index,
                "object_x_full_frame": round(object_x, 1),
                "object_y_full_frame": round(object_y, 1),
                "dx_from_frame_center": round(object_x - 960, 1),
                "dy_from_frame_center": round(object_y - 540, 1),
                "predicted_x_from_manual_seed": round(predicted_x, 1),
                "predicted_y_from_manual_seed": round(predicted_y, 1),
                "refinement_delta_px": round(refinement_delta, 2),
                "object_bbox_w": bbox_w,
                "object_bbox_h": bbox_h,
                "object_component_area": area,
                "object_max_luma": max_luma,
                "object_mean_luma": mean_luma,
                "nearest_colored_overlay_px": "" if nearest_overlay is None else round(nearest_overlay, 2),
                "overlay_relation": relation,
                "review_confidence": review_confidence,
                "nearest_seed_quality": nearest_seed_quality,
                "manual_seed_match": manual_seed_match,
                "manual_control_delta_px": manual_control_delta,
                "phase": phase,
                "nearest_seed_caveat": nearest_seed_caveat,
                "marking_basis": marking_basis,
                "raw_frame_path": str(raw_path).replace("\\", "/"),
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )

    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-dense-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-dense-patches", cols=8, thumb_width=180)

    fieldnames = [
        "video",
        "dense_frame_index",
        "approx_second",
        "source_frame_index",
        "object_x_full_frame",
        "object_y_full_frame",
        "dx_from_frame_center",
        "dy_from_frame_center",
        "predicted_x_from_manual_seed",
        "predicted_y_from_manual_seed",
        "refinement_delta_px",
        "object_bbox_w",
        "object_bbox_h",
        "object_component_area",
        "object_max_luma",
        "object_mean_luma",
        "nearest_colored_overlay_px",
        "overlay_relation",
        "review_confidence",
        "nearest_seed_quality",
        "manual_seed_match",
        "manual_control_delta_px",
        "phase",
        "nearest_seed_caveat",
        "marking_basis",
        "raw_frame_path",
        "annotated_frame_path",
        "zoom_patch_path",
    ]
    dense_csv = Path("research/ufo-video-d38-dense-track-dod111689030.csv")
    write_csv(dense_csv, fieldnames, rows)

    confidence_counts = Counter(row["review_confidence"] for row in rows)
    phase_counts = Counter(row["phase"] for row in rows)
    overlay_counts = Counter(row["overlay_relation"] for row in rows)
    summary_rows = [
        {"metric": "sample_count", "value": len(rows), "note": f"{args.start:.1f}s-{args.end:.1f}s at {args.sample_rate:.1f} fps"},
        {"metric": "high_confidence_samples", "value": confidence_counts.get("high", 0), "note": "dense review confidence"},
        {"metric": "medium_confidence_samples", "value": confidence_counts.get("medium", 0), "note": "dense review confidence"},
        {"metric": "low_confidence_samples", "value": confidence_counts.get("low", 0), "note": "dense review confidence"},
        {
            "metric": "manual_control_mean_delta_px",
            "value": round(sum(control_deltas) / len(control_deltas), 2) if control_deltas else "",
            "note": "delta between dense refined mark and existing one-second accepted mark on seed seconds",
        },
        {
            "metric": "manual_control_max_delta_px",
            "value": round(max(control_deltas), 2) if control_deltas else "",
            "note": "largest delta on one-second manual seed control frames",
        },
    ]
    for phase, count in sorted(phase_counts.items()):
        summary_rows.append({"metric": f"phase_count: {phase}", "value": count, "note": "DVIDS/local phase"})
    for relation, count in sorted(overlay_counts.items()):
        summary_rows.append({"metric": f"overlay_count: {relation}", "value": count, "note": "colored overlay relation"})

    summary_csv = Path("research/ufo-video-d38-dense-track-dod111689030-summary.csv")
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    index_rows: list[dict] = []
    for path in annotated_sheets:
        index_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "dense 5 fps annotated full-frame sheet"})
    for path in patch_sheets:
        index_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "object-centered zoom-patch sheet"})
    index_rows.append({"artifact_type": "dense_track_csv", "path": str(dense_csv).replace("\\", "/"), "note": "0.2-second dense D38 track table"})
    index_rows.append({"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "dense mark counts and control deltas"})
    index_csv = Path("research/ufo-video-d38-dense-marking-assets-dod111689030.csv")
    write_csv(index_csv, ["artifact_type", "path", "note"], index_rows)

    print(f"video={args.video}")
    print(f"fps={fps}")
    print(f"source_frames={total_frames}")
    print(f"samples={len(rows)}")
    print(f"confidence_counts={dict(confidence_counts)}")
    print(f"phase_counts={dict(phase_counts)}")
    print(f"dense_csv={dense_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"index_csv={index_csv}")


if __name__ == "__main__":
    main()

