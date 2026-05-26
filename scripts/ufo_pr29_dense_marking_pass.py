from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source-files-not-included"


VIDEO_ID = "DOD_111688964"
DEFAULT_SOURCE = SOURCE_ROOT / "DOD_111688964.mp4"
DEFAULT_MANUAL_TRACK = Path("research/ufo-video-manual-track-dod111688964.csv")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/dense-marking") / VIDEO_ID


@dataclass
class ManualSeed:
    second: float
    x: float
    y: float
    confidence: str
    relation: str
    note: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def center_crop(frame: np.ndarray, width: int = 960, height: int = 540) -> tuple[np.ndarray, int, int]:
    h, w = frame.shape[:2]
    x0 = max(0, (w - width) // 2)
    y0 = max(0, (h - height) // 2)
    return frame[y0 : y0 + height, x0 : x0 + width], x0, y0


def load_manual_seeds(path: Path) -> list[ManualSeed]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    seeds: list[ManualSeed] = []
    for row in rows:
        seeds.append(
            ManualSeed(
                second=float(row["approx_second"]),
                x=float(row["object_x"]),
                y=float(row["object_y"]),
                confidence=row["confidence"],
                relation=row["track_symbology_relation"],
                note=row["note"],
            )
        )
    seeds.sort(key=lambda seed: seed.second)
    return seeds


def interpolate_seed(seeds: list[ManualSeed], second: float) -> tuple[float, float, str, str]:
    seconds = np.array([seed.second for seed in seeds], dtype=np.float32)
    xs = np.array([seed.x for seed in seeds], dtype=np.float32)
    ys = np.array([seed.y for seed in seeds], dtype=np.float32)
    x = float(np.interp(second, seconds, xs))
    y = float(np.interp(second, seconds, ys))

    nearest = min(seeds, key=lambda seed: abs(seed.second - second))
    return x, y, nearest.confidence, nearest.relation


def local_bright_refine(crop: np.ndarray, predicted_x: float, predicted_y: float, radius: int = 58) -> dict:
    h, w = crop.shape[:2]
    px = int(round(predicted_x))
    py = int(round(predicted_y))
    x0 = max(0, px - radius)
    x1 = min(w, px + radius + 1)
    y0 = max(0, py - radius)
    y1 = min(h, py + radius + 1)
    window = crop[y0:y1, x0:x1]

    hsv = cv2.cvtColor(window, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
    low_sat = hsv[:, :, 1] < 72
    valid = low_sat & (gray > 50)
    if int(valid.sum()) < 10:
        return {}

    threshold = int(np.percentile(gray[valid], 98.2))
    threshold = max(145, min(threshold, 235))
    mask = ((gray >= threshold) & low_sat).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 3)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        bx, by, bw, bh, area = stats[label]
        if area < 3 or area > 900:
            continue
        if bw > 70 or bh > 90:
            continue
        cx, cy = centroids[label]
        full_x = x0 + float(cx)
        full_y = y0 + float(cy)
        component_values = gray[labels == label]
        max_luma = int(component_values.max())
        mean_luma = float(component_values.mean())
        distance = math.hypot(full_x - predicted_x, full_y - predicted_y)
        compact_bonus = min(area, 160) / 160.0
        score = (2.1 * max_luma / 255.0) + (mean_luma / 255.0) + compact_bonus - (1.35 * distance / radius)
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


def overlay_mask(crop: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    cyan_green = (hue >= 70) & (hue <= 105)
    orange_red = ((hue <= 25) | (hue >= 170))
    mask = ((sat > 65) & (val > 75) & (cyan_green | orange_red)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return mask


def classify_overlay_relation(crop: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = overlay_mask(crop)
    overlay_points = cv2.findNonZero(mask)
    nearest_distance: float | None = None
    if overlay_points is not None:
        pts = overlay_points.reshape(-1, 2)
        if len(pts):
            distances = np.sqrt((pts[:, 0] - x) ** 2 + (pts[:, 1] - y) ** 2)
            nearest_distance = float(distances.min())

    inside_box = False
    labels_count, _, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    for label in range(1, labels_count):
        bx, by, bw, bh, area = stats[label]
        if area < 25:
            continue
        if bw < 18 or bh < 18:
            continue
        if (bx - 6) <= x <= (bx + bw + 6) and (by - 6) <= y <= (by + bh + 6):
            inside_box = True
            break

    if nearest_distance is None:
        return "no colored track symbology detected", None
    if nearest_distance <= 5:
        return "intersects colored track symbology", nearest_distance
    if inside_box:
        return "inside colored track box", nearest_distance
    if nearest_distance <= 38:
        return "near colored track symbology", nearest_distance
    return "separate from colored track symbology", nearest_distance


def classify_vertical_feature(crop: np.ndarray, x: float, y: float) -> tuple[str, int | None, int | None]:
    h, w = crop.shape[:2]
    cx = int(round(x))
    cy = int(round(y))
    half_w = 34
    half_h = 48
    x0 = max(0, cx - half_w)
    x1 = min(w, cx + half_w + 1)
    y0 = max(0, cy - half_h)
    y1 = min(h, cy + half_h + 1)
    patch = crop[y0:y1, x0:x1]
    if patch.size == 0:
        return "not assessed", None, None

    hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY)
    low_sat = hsv[:, :, 1] < 75
    valid = low_sat & (gray > 65)
    if int(valid.sum()) < 6:
        return "no", None, None

    threshold = int(np.percentile(gray[valid], 95.0))
    threshold = max(145, min(threshold, 225))
    mask = ((gray >= threshold) & low_sat).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 3)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    if labels_count <= 1:
        return "no", None, None

    patch_cx = cx - x0
    patch_cy = cy - y0
    best_label = None
    best_distance = 1e9
    for label in range(1, labels_count):
        bx, by, bw, bh, area = stats[label]
        if area < 3:
            continue
        lx, ly = centroids[label]
        distance = math.hypot(float(lx) - patch_cx, float(ly) - patch_cy)
        if distance < best_distance:
            best_label = label
            best_distance = distance

    if best_label is None:
        return "no", None, None

    bx, by, bw, bh, area = stats[best_label]
    tail_below_center = (by + bh) - patch_cy
    if bh >= 16 and tail_below_center >= 10 and bh >= bw * 1.25:
        return "yes", int(bw), int(bh)
    if bh >= 12 and tail_below_center >= 8:
        return "possible", int(bw), int(bh)
    return "no", int(bw), int(bh)


def confidence_for_mark(refined: dict, nearest_seed_confidence: str, second: float) -> str:
    if not refined:
        return "low"
    distance = float(refined["distance_from_prediction"])
    max_luma = int(refined["max_luma"])
    if nearest_seed_confidence == "high" and distance <= 26 and max_luma >= 178 and 1.0 <= second <= 17.4:
        return "high"
    if distance <= 42 and max_luma >= 160:
        return "medium"
    return "low"


def add_label(img: np.ndarray, text: str) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (520, 30), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 21), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_crop(crop: np.ndarray, x: float, y: float, predicted_x: float, predicted_y: float, label: str) -> np.ndarray:
    out = crop.copy()
    cv2.circle(out, (int(round(predicted_x)), int(round(predicted_y))), 12, (255, 0, 0), 1)
    cv2.drawMarker(out, (int(round(x)), int(round(y))), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
    cv2.circle(out, (int(round(x)), int(round(y))), 16, (0, 0, 255), 1)
    cv2.line(out, (480, 270), (int(round(x)), int(round(y))), (255, 255, 0), 1)
    return add_label(out, label)


def zoom_patch(crop: np.ndarray, x: float, y: float, label: str, size: int = 120) -> np.ndarray:
    h, w = crop.shape[:2]
    half = size // 2
    cx = int(round(x))
    cy = int(round(y))
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    patch = crop[y0 : y0 + size, x0 : x0 + size].copy()
    patch = cv2.resize(patch, (360, 360), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(patch, (180, 180), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    cv2.circle(patch, (180, 180), 38, (0, 0, 255), 2)
    return add_label(patch, label)


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
    parser = argparse.ArgumentParser(description="Generate dense PR29/D27 marking artifacts for DOD_111688964.")
    parser.add_argument("--video", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--manual-track", type=Path, default=DEFAULT_MANUAL_TRACK)
    parser.add_argument("--start", type=float, default=1.0)
    parser.add_argument("--end", type=float, default=21.0)
    parser.add_argument("--sample-rate", type=float, default=5.0)
    args = parser.parse_args()

    seeds = load_manual_seeds(args.manual_track)
    if args.start < seeds[0].second or args.end > seeds[-1].second:
        raise ValueError(f"Requested range {args.start}-{args.end}s is outside manual seed range {seeds[0].second}-{seeds[-1].second}s")

    raw_dir = OUT_ROOT / "raw-crops"
    annotated_dir = OUT_ROOT / "annotated-crops"
    patch_dir = OUT_ROOT / "object-zoom-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for path in [raw_dir, annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(path)

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    sample_count = int(round((args.end - args.start) * args.sample_rate)) + 1
    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    control_deltas: list[float] = []

    for sample_index in range(sample_count):
        second = round(args.start + sample_index / args.sample_rate, 1)
        source_frame_index = min(int(round(second * fps)), max(0, total_frames - 1))
        fivefps_index = int(round(second * args.sample_rate)) + 1
        predicted_x, predicted_y, nearest_seed_confidence, nearest_seed_relation = interpolate_seed(seeds, second)

        cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame_index)
        ok, frame = cap.read()
        if not ok:
            continue

        crop, _, _ = center_crop(frame)
        raw_path = raw_dir / f"frame_{fivefps_index:04d}.jpg"
        cv2.imwrite(str(raw_path), crop, [int(cv2.IMWRITE_JPEG_QUALITY), 94])

        refined = local_bright_refine(crop, predicted_x, predicted_y)
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

        relation, nearest_overlay = classify_overlay_relation(crop, object_x, object_y)
        vertical_flag, vertical_w, vertical_h = classify_vertical_feature(crop, object_x, object_y)
        review_confidence = confidence_for_mark(refined, nearest_seed_confidence, second)

        label = f"t={second:04.1f}s f5={fivefps_index:03d} conf={review_confidence} vert={vertical_flag}"
        annotated = annotate_crop(crop, object_x, object_y, predicted_x, predicted_y, label)
        patch = zoom_patch(crop, object_x, object_y, label)

        annotated_path = annotated_dir / f"frame_{fivefps_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{fivefps_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), patch, [int(cv2.IMWRITE_JPEG_QUALITY), 94])
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
                "fivefps_frame_index": fivefps_index,
                "approx_second": f"{second:.1f}",
                "source_frame_index": source_frame_index,
                "object_x": round(object_x, 1),
                "object_y": round(object_y, 1),
                "dx_from_reticle_center": round(object_x - 480, 1),
                "dy_from_reticle_center": round(object_y - 270, 1),
                "predicted_x_from_manual_seed": round(predicted_x, 1),
                "predicted_y_from_manual_seed": round(predicted_y, 1),
                "refinement_delta_px": round(refinement_delta, 2),
                "object_bbox_w": bbox_w,
                "object_bbox_h": bbox_h,
                "object_component_area": area,
                "object_max_luma": max_luma,
                "object_mean_luma": mean_luma,
                "nearest_colored_overlay_px": "" if nearest_overlay is None else round(nearest_overlay, 2),
                "track_symbology_relation": relation,
                "vertical_feature_flag": vertical_flag,
                "vertical_component_w": "" if vertical_w is None else vertical_w,
                "vertical_component_h": "" if vertical_h is None else vertical_h,
                "review_confidence": review_confidence,
                "nearest_seed_confidence": nearest_seed_confidence,
                "nearest_seed_relation": nearest_seed_relation,
                "manual_seed_match": manual_seed_match,
                "manual_control_delta_px": manual_control_delta,
                "marking_basis": marking_basis,
                "raw_crop_path": str(raw_path).replace("\\", "/"),
                "annotated_crop_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )

    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-dense-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-dense-patches", cols=8, thumb_width=180)

    fieldnames = [
        "video",
        "fivefps_frame_index",
        "approx_second",
        "source_frame_index",
        "object_x",
        "object_y",
        "dx_from_reticle_center",
        "dy_from_reticle_center",
        "predicted_x_from_manual_seed",
        "predicted_y_from_manual_seed",
        "refinement_delta_px",
        "object_bbox_w",
        "object_bbox_h",
        "object_component_area",
        "object_max_luma",
        "object_mean_luma",
        "nearest_colored_overlay_px",
        "track_symbology_relation",
        "vertical_feature_flag",
        "vertical_component_w",
        "vertical_component_h",
        "review_confidence",
        "nearest_seed_confidence",
        "nearest_seed_relation",
        "manual_seed_match",
        "manual_control_delta_px",
        "marking_basis",
        "raw_crop_path",
        "annotated_crop_path",
        "zoom_patch_path",
    ]
    dense_csv = Path("research/ufo-video-dense-track-dod111688964.csv")
    write_csv(dense_csv, fieldnames, rows)

    confidence_counts = Counter(row["review_confidence"] for row in rows)
    relation_counts = Counter(row["track_symbology_relation"] for row in rows)
    vertical_counts = Counter(row["vertical_feature_flag"] for row in rows)
    summary_rows = [
        {"metric": "sample_count", "value": len(rows), "note": f"{args.start:.1f}s-{args.end:.1f}s at {args.sample_rate:.1f} fps"},
        {"metric": "high_confidence_samples", "value": confidence_counts.get("high", 0), "note": "dense review confidence"},
        {"metric": "medium_confidence_samples", "value": confidence_counts.get("medium", 0), "note": "dense review confidence"},
        {"metric": "low_confidence_samples", "value": confidence_counts.get("low", 0), "note": "dense review confidence"},
        {"metric": "vertical_feature_yes", "value": vertical_counts.get("yes", 0), "note": "algorithmic visual flag; requires human interpretation"},
        {"metric": "vertical_feature_possible", "value": vertical_counts.get("possible", 0), "note": "algorithmic visual flag; requires human interpretation"},
        {"metric": "vertical_feature_no", "value": vertical_counts.get("no", 0), "note": "algorithmic visual flag; requires human interpretation"},
        {
            "metric": "manual_control_mean_delta_px",
            "value": round(sum(control_deltas) / len(control_deltas), 2) if control_deltas else "",
            "note": "delta between dense refined mark and existing one-second manual seed on seed seconds",
        },
        {
            "metric": "manual_control_max_delta_px",
            "value": round(max(control_deltas), 2) if control_deltas else "",
            "note": "largest delta on one-second manual seed control frames",
        },
    ]
    for relation, count in sorted(relation_counts.items()):
        summary_rows.append({"metric": f"relation_count: {relation}", "value": count, "note": "colored overlay relation"})

    summary_csv = Path("research/ufo-video-dense-track-dod111688964-summary.csv")
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    index_csv = Path("research/ufo-video-dense-marking-assets-dod111688964.csv")
    index_rows: list[dict] = []
    for path in annotated_sheets:
        index_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "dense 5 fps annotated center-crop sheet"})
    for path in patch_sheets:
        index_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "object-centered zoom-patch sheet"})
    index_rows.append({"artifact_type": "dense_track_csv", "path": str(dense_csv).replace("\\", "/"), "note": "0.2-second dense object/overlay mark table"})
    index_rows.append({"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "dense mark counts and control deltas"})
    write_csv(index_csv, ["artifact_type", "path", "note"], index_rows)

    print(f"video={args.video}")
    print(f"fps={fps}")
    print(f"source_frames={total_frames}")
    print(f"samples={len(rows)}")
    print(f"confidence_counts={dict(confidence_counts)}")
    print(f"vertical_counts={dict(vertical_counts)}")
    print(f"dense_csv={dense_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"index_csv={index_csv}")


if __name__ == "__main__":
    main()

