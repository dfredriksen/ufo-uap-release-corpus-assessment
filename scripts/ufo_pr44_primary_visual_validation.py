from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689115"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR44"
DEFAULT_VIDEO = Path(r"source-files-not-included/DOD_111689115.mp4")
DEFAULT_DENSE_TRACK = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-dense-track-dod111689115.csv")
OUT_ROOT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr44-primary-validation") / VIDEO_ID

CROP_WIDTH = 960
CROP_HEIGHT = 540
CROP_X0 = 480
CROP_Y0 = 270


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def center_crop(frame: np.ndarray) -> np.ndarray:
    return frame[CROP_Y0 : CROP_Y0 + CROP_HEIGHT, CROP_X0 : CROP_X0 + CROP_WIDTH].copy()


def colored_overlay_mask(crop: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 45) & (hue <= 115)
    red_or_orange = (hue <= 25) | (hue >= 170)
    mask = ((sat > 65) & (val > 65) & (cyan_green | red_or_orange)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


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


def load_dense_rows(path: Path, start: float, end: float) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    selected = []
    for row in rows:
        second = float(row["approx_second"])
        if start <= second <= end and row["phase"].startswith("primary"):
            selected.append(row)
    selected.sort(key=lambda item: float(item["approx_second"]))
    return selected


def find_visual_candidate(crop: np.ndarray, center_x: float, center_y: float, radius: int = 96) -> dict:
    h, w = crop.shape[:2]
    px = int(round(center_x))
    py = int(round(center_y))
    x0 = max(0, px - radius)
    x1 = min(w, px + radius + 1)
    y0 = max(0, py - radius)
    y1 = min(h, py + radius + 1)
    window = crop[y0:y1, x0:x1]
    if window.size == 0:
        return {}

    hsv = cv2.cvtColor(window, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
    overlay_clear = colored_overlay_mask(window) == 0
    low_sat = hsv[:, :, 1] < 95
    valid = overlay_clear & low_sat & (gray > 25)
    if int(valid.sum()) < 16:
        return {}

    values = gray[valid]
    thresholds = [
        max(145, int(np.percentile(values, 99.65))),
        max(135, int(np.percentile(values, 99.35))),
        max(125, int(np.percentile(values, 99.00))),
    ]

    candidates: list[dict] = []
    for threshold in thresholds:
        mask = ((gray >= threshold) & valid).astype(np.uint8) * 255
        mask = cv2.medianBlur(mask, 3)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
        labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
        for label in range(1, labels_count):
            bx, by, bw, bh, area = stats[label]
            if area < 2 or area > 360:
                continue
            if bw > 48 or bh > 48:
                continue
            aspect = max(bw / max(1, bh), bh / max(1, bw))
            if aspect > 8.0:
                continue
            cx, cy = centroids[label]
            full_x = x0 + float(cx)
            full_y = y0 + float(cy)
            component_values = gray[labels == label]
            max_luma = int(component_values.max())
            mean_luma = float(component_values.mean())
            dist = math.hypot(full_x - center_x, full_y - center_y)
            if dist > radius * 0.95:
                continue
            score = (
                (max_luma / 255.0) * 2.2
                + (mean_luma / 255.0)
                + min(area, 90) / 90.0
                - 0.75 * (dist / radius)
                - 0.04 * max(0.0, aspect - 2.5)
            )
            candidates.append(
                {
                    "x": full_x,
                    "y": full_y,
                    "bbox_w": int(bw),
                    "bbox_h": int(bh),
                    "area": int(area),
                    "max_luma": max_luma,
                    "mean_luma": mean_luma,
                    "distance_from_search_center": dist,
                    "threshold": int(threshold),
                    "score": score,
                }
            )
        if candidates:
            break

    if not candidates:
        return {}
    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    best["candidate_count"] = len(candidates)
    return best


def classify_visual(row: dict, candidate: dict, overlay_relation: str, shift_from_dense: float) -> tuple[str, str, str]:
    dense_confidence = row["review_confidence"]
    if not candidate:
        return (
            "unconfirmed_seed_or_dense_mark",
            "low",
            "no compact low-saturation bright candidate found inside expanded validation window",
        )

    max_luma = int(candidate["max_luma"])
    area = int(candidate["area"])
    distance = float(candidate["distance_from_search_center"])
    if shift_from_dense <= 10 and max_luma >= 205 and area >= 3 and not overlay_relation.startswith("intersects"):
        quality = "high" if dense_confidence in {"high", "medium"} else "medium"
        return (
            "confirmed_dense_mark",
            quality,
            "expanded-window validation found a compact bright candidate at the dense mark",
        )
    if shift_from_dense <= 35 and max_luma >= 190 and area >= 3:
        quality = "medium" if not overlay_relation.startswith("intersects") else "low"
        return (
            "confirmed_near_dense_mark",
            quality,
            "expanded-window validation found a compact bright candidate near the dense mark",
        )
    if max_luma >= 205 and area >= 3 and distance <= 90:
        quality = "medium" if not overlay_relation.startswith("intersects") else "low"
        return (
            "recentered_visual_candidate",
            quality,
            "expanded-window validation found a compact bright candidate offset from the seeded dense mark",
        )
    return (
        "weak_visual_candidate",
        "low",
        "candidate exists but is weak, overlay-adjacent, or too far from the dense mark for strong validation",
    )


def draw_marker(img: np.ndarray, x: float, y: float, color: tuple[int, int, int], radius: int, thickness: int = 2) -> None:
    point = (int(round(x)), int(round(y)))
    cv2.drawMarker(img, point, color, markerType=cv2.MARKER_CROSS, markerSize=26, thickness=thickness)
    cv2.circle(img, point, radius, color, thickness)


def add_label(img: np.ndarray, text: str, width: int = 820) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 34), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def crop_patch(crop: np.ndarray, x: float, y: float, size: int = 140) -> tuple[np.ndarray, int, int]:
    h, w = crop.shape[:2]
    half = size // 2
    cx = int(round(x))
    cy = int(round(y))
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return crop[y0 : y0 + size, x0 : x0 + size].copy(), x0, y0


def annotate_crop(crop: np.ndarray, row: dict, visual_x: float, visual_y: float, status: str, quality: str) -> np.ndarray:
    out = crop.copy()
    dense_x = float(row["object_x_center_crop"])
    dense_y = float(row["object_y_center_crop"])
    pred_x = float(row["predicted_x_center_crop"])
    pred_y = float(row["predicted_y_center_crop"])
    draw_marker(out, pred_x, pred_y, (255, 0, 0), 13, 1)
    draw_marker(out, dense_x, dense_y, (255, 255, 0), 18, 1)
    color = (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255)
    draw_marker(out, visual_x, visual_y, color, 24, 2)
    if math.hypot(visual_x - dense_x, visual_y - dense_y) > 3:
        cv2.line(out, (int(round(dense_x)), int(round(dense_y))), (int(round(visual_x)), int(round(visual_y))), (255, 255, 255), 1)
    label = f"{VIDEO_ID} t={float(row['approx_second']):05.1f}s {quality} {status.replace('_', '-')}"
    return add_label(out, label)


def annotate_patch(crop: np.ndarray, row: dict, visual_x: float, visual_y: float, quality: str) -> np.ndarray:
    patch, x0, y0 = crop_patch(crop, visual_x, visual_y)
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    scale = 420 / patch.shape[1]
    draw_marker(out, 210, 210, (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255), 46, 2)
    dense_x = float(row["object_x_center_crop"])
    dense_y = float(row["object_y_center_crop"])
    rel_x = (dense_x - x0) * scale
    rel_y = (dense_y - y0) * scale
    if 0 <= rel_x < 420 and 0 <= rel_y < 420:
        draw_marker(out, rel_x, rel_y, (255, 255, 0), 30, 1)
    label = f"{VIDEO_ID} t={float(row['approx_second']):05.1f}s val={quality} dense={row['review_confidence']}"
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


def distance(a: dict, b: dict) -> float:
    return math.hypot(float(b["visual_x_center_crop"]) - float(a["visual_x_center_crop"]), float(b["visual_y_center_crop"]) - float(a["visual_y_center_crop"]))


def stats_for(name: str, rows: list[dict]) -> dict:
    if len(rows) < 2:
        return {"track": name, "sample_count": len(rows)}
    rows = sorted(rows, key=lambda item: float(item["approx_second"]))
    duration = float(rows[-1]["approx_second"]) - float(rows[0]["approx_second"])
    net = distance(rows[0], rows[-1])
    total_path = 0.0
    step_rates = []
    for prev, curr in zip(rows, rows[1:]):
        dt = float(curr["approx_second"]) - float(prev["approx_second"])
        if dt <= 0:
            continue
        step = distance(prev, curr)
        total_path += step
        step_rates.append(step / dt)
    return {
        "track": name,
        "sample_count": len(rows),
        "start_second": rows[0]["approx_second"],
        "end_second": rows[-1]["approx_second"],
        "duration_second": round(duration, 3),
        "net_displacement_px": round(net, 3),
        "net_rate_px_s": round(net / duration, 3) if duration else "",
        "total_path_px": round(total_path, 3),
        "path_average_rate_px_s": round(total_path / duration, 3) if duration else "",
        "step_rate_mean_px_s": round(statistics.mean(step_rates), 3) if step_rates else "",
        "step_rate_median_px_s": round(statistics.median(step_rates), 3) if step_rates else "",
        "step_rate_p95_px_s": round(sorted(step_rates)[int(round(0.95 * (len(step_rates) - 1)))], 3) if step_rates else "",
    }


def draw_trajectory(rows: list[dict], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    canvas = np.full((CROP_HEIGHT, CROP_WIDTH, 3), 34, dtype=np.uint8)
    cv2.line(canvas, (CROP_WIDTH // 2, 0), (CROP_WIDTH // 2, CROP_HEIGHT), (70, 70, 70), 1)
    cv2.line(canvas, (0, CROP_HEIGHT // 2), (CROP_WIDTH, CROP_HEIGHT // 2), (70, 70, 70), 1)
    dense_points = [
        (int(round(float(row["dense_x_center_crop"]))), int(round(float(row["dense_y_center_crop"]))))
        for row in rows
    ]
    visual_points = [
        (int(round(float(row["visual_x_center_crop"]))), int(round(float(row["visual_y_center_crop"]))))
        for row in rows
    ]
    cv2.polylines(canvas, [np.array(dense_points, dtype=np.int32)], False, (255, 255, 0), 1)
    cv2.polylines(canvas, [np.array(visual_points, dtype=np.int32)], False, (0, 0, 255), 2)
    for row, point in zip(rows, visual_points):
        color = (0, 0, 255) if row["visual_quality"] in {"high", "medium"} else (0, 165, 255)
        cv2.circle(canvas, point, 2, color, -1)
    cv2.rectangle(canvas, (0, 0), (930, 38), (0, 0, 0), -1)
    cv2.putText(
        canvas,
        "PR44 primary validation 154.0s-204.8s; yellow=dense seed track, red/orange=visual validation",
        (8, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.imwrite(str(out_path), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="PR44 primary interval visual validation for DOD_111689115.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--dense-track", type=Path, default=DEFAULT_DENSE_TRACK)
    parser.add_argument("--start", type=float, default=154.0)
    parser.add_argument("--end", type=float, default=204.8)
    args = parser.parse_args()

    dense_rows = load_dense_rows(args.dense_track, args.start, args.end)
    if not dense_rows:
        raise RuntimeError(f"No dense primary rows found in {args.dense_track}")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")

    annotated_dir = OUT_ROOT / "annotated-center-crops"
    patch_dir = OUT_ROOT / "visual-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []

    for index, row in enumerate(dense_rows):
        frame_index = int(row["source_frame_index"])
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        crop = center_crop(frame)
        dense_x = float(row["object_x_center_crop"])
        dense_y = float(row["object_y_center_crop"])
        predicted_x = float(row["predicted_x_center_crop"])
        predicted_y = float(row["predicted_y_center_crop"])
        search_x = dense_x if row["marking_basis"].endswith("refinement") else predicted_x
        search_y = dense_y if row["marking_basis"].endswith("refinement") else predicted_y
        candidate = find_visual_candidate(crop, search_x, search_y)
        if candidate:
            visual_x = float(candidate["x"])
            visual_y = float(candidate["y"])
            bbox_w = int(candidate["bbox_w"])
            bbox_h = int(candidate["bbox_h"])
            area = int(candidate["area"])
            max_luma = int(candidate["max_luma"])
            mean_luma = round(float(candidate["mean_luma"]), 2)
            candidate_count = int(candidate["candidate_count"])
            threshold = int(candidate["threshold"])
        else:
            visual_x = dense_x
            visual_y = dense_y
            bbox_w = ""
            bbox_h = ""
            area = ""
            max_luma = ""
            mean_luma = ""
            candidate_count = ""
            threshold = ""
        overlay_relation, overlay_distance = nearest_overlay_distance(crop, visual_x, visual_y)
        shift_from_dense = math.hypot(visual_x - dense_x, visual_y - dense_y)
        shift_from_prediction = math.hypot(visual_x - predicted_x, visual_y - predicted_y)
        validation_status, visual_quality, caveat = classify_visual(row, candidate, overlay_relation, shift_from_dense)

        annotated_path = annotated_dir / f"frame_{index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{index:04d}_patch.jpg"
        cv2.imwrite(
            str(annotated_path),
            annotate_crop(crop, row, visual_x, visual_y, validation_status, visual_quality),
            [int(cv2.IMWRITE_JPEG_QUALITY), 92],
        )
        cv2.imwrite(
            str(patch_path),
            annotate_patch(crop, row, visual_x, visual_y, visual_quality),
            [int(cv2.IMWRITE_JPEG_QUALITY), 94],
        )
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)

        rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "sample_index": row["sample_index"],
                "validation_index": index,
                "approx_second": row["approx_second"],
                "source_frame_index": frame_index,
                "phase": row["phase"],
                "dense_review_confidence": row["review_confidence"],
                "dense_marking_basis": row["marking_basis"],
                "dense_x_center_crop": round(dense_x, 1),
                "dense_y_center_crop": round(dense_y, 1),
                "predicted_x_center_crop": round(predicted_x, 1),
                "predicted_y_center_crop": round(predicted_y, 1),
                "visual_x_center_crop": round(visual_x, 1),
                "visual_y_center_crop": round(visual_y, 1),
                "visual_x_full_frame": round(visual_x + CROP_X0, 1),
                "visual_y_full_frame": round(visual_y + CROP_Y0, 1),
                "shift_from_dense_px": round(shift_from_dense, 2),
                "shift_from_prediction_px": round(shift_from_prediction, 2),
                "validation_status": validation_status,
                "visual_quality": visual_quality,
                "visual_bbox_w": bbox_w,
                "visual_bbox_h": bbox_h,
                "visual_component_area": area,
                "visual_max_luma": max_luma,
                "visual_mean_luma": mean_luma,
                "candidate_count": candidate_count,
                "visual_threshold": threshold,
                "nearest_colored_overlay_px": "" if overlay_distance is None else round(overlay_distance, 2),
                "overlay_relation": overlay_relation,
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )

    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr44-primary-validation-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr44-primary-validation-patches", cols=8, thumb_width=180)
    trajectory_path = sheet_dir / f"{VIDEO_ID}-pr44-primary-validation-trajectory.jpg"
    draw_trajectory(rows, trajectory_path)

    validation_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-primary-visual-validation-dod111689115.csv")
    write_csv(validation_csv, list(rows[0].keys()), rows)

    high_medium = [row for row in rows if row["visual_quality"] in {"high", "medium"}]
    low_rows = [row for row in rows if row["visual_quality"] == "low"]
    recentered = [row for row in rows if row["validation_status"] == "recentered_visual_candidate"]
    unconfirmed = [row for row in rows if row["validation_status"] == "unconfirmed_seed_or_dense_mark"]
    summary_rows = [
        stats_for("pr44_primary_visual_validation_all_154_2048", rows),
        stats_for("pr44_primary_visual_validation_high_medium_only", high_medium),
    ]
    for key, value in sorted(Counter(row["visual_quality"] for row in rows).items()):
        summary_rows.append({"track": f"visual_quality_count: {key}", "sample_count": value})
    for key, value in sorted(Counter(row["validation_status"] for row in rows).items()):
        summary_rows.append({"track": f"validation_status_count: {key}", "sample_count": value})
    for key, value in sorted(Counter(row["overlay_relation"] for row in rows).items()):
        summary_rows.append({"track": f"overlay_count: {key}", "sample_count": value})
    for key, value in sorted(Counter(row["dense_review_confidence"] for row in rows).items()):
        summary_rows.append({"track": f"source_dense_confidence_count: {key}", "sample_count": value})

    summary_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-primary-visual-validation-summary.csv")
    write_csv(
        summary_csv,
        [
            "track",
            "sample_count",
            "start_second",
            "end_second",
            "duration_second",
            "net_displacement_px",
            "net_rate_px_s",
            "total_path_px",
            "path_average_rate_px_s",
            "step_rate_mean_px_s",
            "step_rate_median_px_s",
            "step_rate_p95_px_s",
        ],
        summary_rows,
    )

    asset_rows: list[dict] = [
        {"artifact_type": "visual_validation_csv", "path": str(validation_csv).replace("\\", "/"), "note": "PR44 primary visual-validation table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR44 primary visual-validation summary"},
        {"artifact_type": "trajectory_plot", "path": str(trajectory_path).replace("\\", "/"), "note": "dense-vs-validated trajectory overview"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "primary validation annotated center-crop sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "primary validation zoom-patch sheet"})
    asset_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-primary-visual-validation-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"interval={args.start:.1f}-{args.end:.1f}s rows={len(rows)}")
    print(f"visual_quality_counts={dict(Counter(row['visual_quality'] for row in rows))}")
    print(f"validation_status_counts={dict(Counter(row['validation_status'] for row in rows))}")
    print(f"high_medium={len(high_medium)} low={len(low_rows)} recentered={len(recentered)} unconfirmed={len(unconfirmed)}")
    print(f"validation_csv={validation_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()
