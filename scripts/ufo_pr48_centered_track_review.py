from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source-files-not-included"


VIDEO_ID = "DOD_111689167"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR48"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111689167.mp4"
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr48-track-review") / VIDEO_ID

ROI_X0 = 500
ROI_Y0 = 120
ROI_X1 = 1500
ROI_Y1 = 880
RETICLE_X = 960.0
RETICLE_Y = 540.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 18.0:
        return "initial centered track", "DVIDS 00:00-01:39: sensor tracks an area of contrast generally near center"
    if second < 42.0:
        return "open-water centered track", "DVIDS 00:00-01:39: center-frame tracking continues over low-texture water"
    if second < 76.0:
        return "wind-farm crossing", "DVIDS 00:00-01:39: center-frame tracking continues while wind turbines pass through scene"
    return "late centered track", "DVIDS 00:00-01:39: area of contrast remains generally within center field"


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    magenta = (hue >= 125) & (hue <= 170)
    cyan_green = (hue >= 35) & (hue <= 115)
    mask = ((sat > 35) & (val > 35) & (magenta | cyan_green)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def remove_line_artifacts(mask: np.ndarray) -> np.ndarray:
    horizontal = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((1, 31), np.uint8))
    vertical = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((31, 1), np.uint8))
    line_mask = cv2.dilate(cv2.bitwise_or(horizontal, vertical), np.ones((3, 3), np.uint8), iterations=1)
    return cv2.bitwise_and(mask, cv2.bitwise_not(line_mask))


def dark_structure_mask(frame: np.ndarray) -> np.ndarray:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay_clear = colored_overlay_mask(roi) == 0
    mask = ((gray < 72) & overlay_clear).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return mask


def nearest_dark_structure_distance(frame: np.ndarray, full_x: float, full_y: float) -> tuple[str, float | None]:
    mask = dark_structure_mask(frame)
    pts = cv2.findNonZero(mask)
    if pts is None:
        return "no dark structure detected", None
    arr = pts.reshape(-1, 2).astype(np.float32)
    local_x = full_x - ROI_X0
    local_y = full_y - ROI_Y0
    distances = np.sqrt((arr[:, 0] - local_x) ** 2 + (arr[:, 1] - local_y) ** 2)
    nearest = float(distances.min()) if len(distances) else None
    if nearest is None:
        return "no dark structure detected", None
    if nearest <= 12:
        return "adjacent to dark structure", nearest
    if nearest <= 35:
        return "near dark structure", nearest
    return "separate from dark structure", nearest


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    overlay_clear = colored_overlay_mask(roi) == 0
    valid = overlay_clear & (gray > 24) & (gray < 252) & (hsv[:, :, 1] < 115)
    if int(valid.sum()) < 1000:
        return roi, gray, np.zeros_like(gray, dtype=np.uint8), 0.0

    background = cv2.medianBlur(gray, 45)
    bright_delta = gray.astype(np.int16) - background.astype(np.int16)
    threshold = max(18.0, float(np.percentile(bright_delta[valid], 99.84)))
    raw = ((bright_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = remove_line_artifacts(raw)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return roi, gray, raw, threshold


def detect_candidates(frame: np.ndarray, second: float, limit: int = 18) -> list[dict]:
    _roi, gray, mask, threshold = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 3 or area > 220:
            continue
        if w > 38 or h > 38:
            continue
        if w <= 1 or h <= 1:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 5.5:
            continue
        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        values = gray[labels == label]
        local_patch = gray[max(0, y - 24) : min(gray.shape[0], y + h + 24), max(0, x - 24) : min(gray.shape[1], x + w + 24)]
        local_median = float(np.median(local_patch)) if local_patch.size else float(np.median(gray))
        max_luma = int(values.max())
        min_luma = int(values.min())
        mean_luma = float(values.mean())
        contrast_delta = max_luma - local_median
        fill = area / max(1, w * h)
        distance_from_reticle = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        edge_margin = min(full_x - ROI_X0, ROI_X1 - full_x, full_y - ROI_Y0, ROI_Y1 - full_y)
        structure_relation, nearest_structure = nearest_dark_structure_distance(frame, full_x, full_y)
        score = (
            contrast_delta * 5.0
            + min(area, 90) * 1.8
            + min(fill, 0.85) * 65.0
            + max_luma * 0.12
            - distance_from_reticle * 0.22
            - max(0.0, 60.0 - edge_margin) * 3.0
            - max(0.0, aspect - 2.5) * 12.0
        )
        if structure_relation == "adjacent to dark structure":
            score -= 55.0
        elif structure_relation == "near dark structure":
            score -= 18.0
        candidates.append(
            {
                "label": label,
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "fill_ratio": fill,
                "center_x": full_x,
                "center_y": full_y,
                "max_luma": max_luma,
                "min_luma": min_luma,
                "mean_luma": mean_luma,
                "local_median_luma": local_median,
                "contrast_delta": contrast_delta,
                "distance_from_reticle_px": distance_from_reticle,
                "edge_margin_px": edge_margin,
                "dark_structure_relation": structure_relation,
                "nearest_dark_structure_px": nearest_structure,
                "threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:limit]


def classify(candidate: dict | None) -> tuple[str, str]:
    if candidate is None:
        return "none", "no compact bright central-field candidate survived filtering"
    contrast = float(candidate["contrast_delta"])
    area = int(candidate["area"])
    width = int(candidate["bbox_w"])
    height = int(candidate["bbox_h"])
    distance = float(candidate["distance_from_reticle_px"])
    edge_margin = float(candidate["edge_margin_px"])
    relation = str(candidate["dark_structure_relation"])

    if contrast >= 90 and area >= 18 and width >= 3 and height >= 3 and distance <= 520 and edge_margin >= 45 and relation != "adjacent to dark structure":
        return "high", "compact bright contrast candidate in central field"
    if contrast >= 50 and area >= 8 and distance <= 650 and edge_margin >= 25:
        if relation == "adjacent to dark structure":
            return "medium", "central bright candidate, but adjacent to wind-turbine/dark-structure mask"
        return "medium", "usable central bright contrast candidate"
    if contrast >= 35 and distance <= 780:
        return "low", "weak, far from reticle, or structure-confounded central candidate"
    return "none", "candidate is too weak or too far from center field"


def sample_seconds(duration: float, sample_rate: float) -> list[float]:
    count = int(math.floor(duration * sample_rate)) + 1
    seconds = []
    for index in range(count):
        second = round(index / sample_rate, 3)
        if second <= duration:
            seconds.append(second)
    return seconds


def annotate_frame(frame: np.ndarray, candidate: dict | None, second: float, quality: str, phase: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (90, 90, 90), 1)
    cv2.circle(out, (int(RETICLE_X), int(RETICLE_Y)), 520, (90, 90, 90), 1)
    if candidate is not None:
        x0 = ROI_X0 + int(candidate["roi_x"])
        y0 = ROI_Y0 + int(candidate["roi_y"])
        x1 = x0 + int(candidate["bbox_w"])
        y1 = y0 + int(candidate["bbox_h"])
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        cv2.rectangle(out, (x0 - 5, y0 - 5), (x1 + 5, y1 + 5), color, 2)
        cv2.drawMarker(
            out,
            (int(round(candidate["center_x"])), int(round(candidate["center_y"]))),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=18,
            thickness=1,
        )
    cv2.rectangle(out, (0, 0), (980, 40), (0, 0, 0), -1)
    cv2.putText(
        out,
        f"PR48 t={second:.1f}s quality={quality} phase={phase}",
        (10, 27),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return out


def annotate_patch(frame: np.ndarray, candidate: dict | None, second: float, quality: str) -> np.ndarray:
    if candidate is None:
        cx, cy = RETICLE_X, RETICLE_Y
    else:
        cx = float(candidate["center_x"])
        cy = float(candidate["center_y"])
    half = 90
    x0 = max(0, int(round(cx - half)))
    y0 = max(0, int(round(cy - half)))
    x1 = min(frame.shape[1], int(round(cx + half)))
    y1 = min(frame.shape[0], int(round(cy + half)))
    crop = frame[y0:y1, x0:x1].copy()
    if crop.size == 0:
        crop = np.zeros((180, 180, 3), dtype=np.uint8)
    cv2.drawMarker(
        crop,
        (int(round(cx - x0)), int(round(cy - y0))),
        (0, 0, 255),
        markerType=cv2.MARKER_CROSS,
        markerSize=18,
        thickness=1,
    )
    patch = cv2.resize(crop, (340, 340), interpolation=cv2.INTER_NEAREST)
    cv2.rectangle(patch, (0, 0), (340, 34), (0, 0, 0), -1)
    cv2.putText(
        patch,
        f"{second:.1f}s {quality}",
        (8, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.52,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return patch


def write_contact_sheets(paths: list[Path], out_dir: Path, prefix: str, cols: int, thumb_width: int) -> list[Path]:
    ensure_dir(out_dir)
    written: list[Path] = []
    page_size = cols * 5
    for page, start in enumerate(range(0, len(paths), page_size), 1):
        thumbs = []
        for path in paths[start : start + page_size]:
            img = cv2.imread(str(path))
            if img is None:
                continue
            h, w = img.shape[:2]
            thumb_height = max(1, int(round(h * (thumb_width / w))))
            thumbs.append(cv2.resize(img, (thumb_width, thumb_height), interpolation=cv2.INTER_AREA))
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


def supported_rows(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["review_quality"] in {"high", "medium"} and row["target_center_x"] != ""]


def supported_interval_summary(rows: list[dict]) -> dict:
    supported_seconds = [float(row["approx_second"]) for row in supported_rows(rows)]
    if not supported_seconds:
        return {"metric": "supported_intervals", "value": "", "note": "no supported rows"}
    ranges: list[tuple[float, float]] = []
    start = supported_seconds[0]
    prev = supported_seconds[0]
    for second in supported_seconds[1:]:
        if second - prev > 1.01:
            ranges.append((start, prev))
            start = second
        prev = second
    ranges.append((start, prev))
    text = "; ".join(f"{s:.1f}s" if s == e else f"{s:.1f}s-{e:.1f}s" for s, e in ranges)
    return {"metric": "supported_intervals", "value": text, "note": f"{len(ranges)} one-fps supported interval(s)"}


def track_stats(rows: list[dict]) -> dict:
    supported = supported_rows(rows)
    if len(supported) < 2:
        return {"metric": "target_center_track", "value": len(supported), "note": "fewer than two supported rows"}
    total = 0.0
    rates = []
    for prev, curr in zip(supported, supported[1:]):
        dt = float(curr["approx_second"]) - float(prev["approx_second"])
        if dt <= 0:
            continue
        step = math.hypot(float(curr["target_center_x"]) - float(prev["target_center_x"]), float(curr["target_center_y"]) - float(prev["target_center_y"]))
        total += step
        rates.append(step / dt)
    net = math.hypot(
        float(supported[-1]["target_center_x"]) - float(supported[0]["target_center_x"]),
        float(supported[-1]["target_center_y"]) - float(supported[0]["target_center_y"]),
    )
    duration = float(supported[-1]["approx_second"]) - float(supported[0]["approx_second"])
    return {
        "metric": "target_center_track",
        "value": len(supported),
        "note": (
            f"{supported[0]['approx_second']}s-{supported[-1]['approx_second']}s; "
            f"net={net:.3f}px; path={total:.3f}px; "
            f"path_rate={(total / duration):.3f}px/s; median_step_rate={statistics.median(rates):.3f}px/s"
        ),
    }


def numeric_summary(metric: str, values: list[float], note: str) -> dict:
    if not values:
        return {"metric": metric, "value": "", "note": note}
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    median = statistics.median(values)
    cv = stdev / mean if mean else 0.0
    return {
        "metric": metric,
        "value": round(median, 3),
        "note": f"median; mean={mean:.3f}; stdev={stdev:.3f}; cv={cv:.3f}; {note}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="PR48 centered compact-bright-track review for DOD_111689167.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=1.0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    seconds = sample_seconds(duration, args.sample_rate)

    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "target-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    for sample_index, second in enumerate(seconds):
        frame_index = min(int(round(second * fps)), max(0, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        actual_second = frame_index / fps
        candidates = detect_candidates(frame, actual_second)
        candidate = candidates[0] if candidates else None
        quality, caveat = classify(candidate)
        phase, anchor = dvids_phase(actual_second)
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, candidate, actual_second, quality, phase), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, candidate, actual_second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)
        rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "sample_index": sample_index,
                "approx_second": f"{actual_second:.1f}",
                "source_frame_index": frame_index,
                "dvids_phase": phase,
                "dvids_anchor": anchor,
                "review_quality": quality,
                "candidate_count": len(candidates),
                "target_center_x": "" if candidate is None else round(float(candidate["center_x"]), 1),
                "target_center_y": "" if candidate is None else round(float(candidate["center_y"]), 1),
                "bbox_x0": "" if candidate is None else ROI_X0 + int(candidate["roi_x"]),
                "bbox_y0": "" if candidate is None else ROI_Y0 + int(candidate["roi_y"]),
                "bbox_w": "" if candidate is None else int(candidate["bbox_w"]),
                "bbox_h": "" if candidate is None else int(candidate["bbox_h"]),
                "component_area": "" if candidate is None else int(candidate["area"]),
                "fill_ratio": "" if candidate is None else round(float(candidate["fill_ratio"]), 3),
                "component_max_luma": "" if candidate is None else int(candidate["max_luma"]),
                "component_min_luma": "" if candidate is None else int(candidate["min_luma"]),
                "component_mean_luma": "" if candidate is None else round(float(candidate["mean_luma"]), 2),
                "local_median_luma": "" if candidate is None else round(float(candidate["local_median_luma"]), 2),
                "contrast_delta": "" if candidate is None else round(float(candidate["contrast_delta"]), 2),
                "distance_from_reticle_px": "" if candidate is None else round(float(candidate["distance_from_reticle_px"]), 2),
                "edge_margin_px": "" if candidate is None else round(float(candidate["edge_margin_px"]), 2),
                "dark_structure_relation": "" if candidate is None else candidate["dark_structure_relation"],
                "nearest_dark_structure_px": "" if candidate is None or candidate["nearest_dark_structure_px"] is None else round(float(candidate["nearest_dark_structure_px"]), 2),
                "detection_threshold": "" if candidate is None else round(float(candidate["threshold"]), 3),
                "raw_score": "" if candidate is None else round(float(candidate["raw_score"]), 3),
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr48-track-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr48-track-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr48-centered-track-review-dod111689167.csv")
    summary_csv = Path("research/ufo-video-pr48-centered-track-review-summary.csv")
    asset_csv = Path("research/ufo-video-pr48-centered-track-review-assets.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    supported = supported_rows(rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    phase_supported_counts = Counter(row["dvids_phase"] for row in supported)
    structure_counts = Counter(row["dark_structure_relation"] for row in supported if row["dark_structure_relation"])
    areas = [float(row["component_area"]) for row in supported]
    contrasts = [float(row["contrast_delta"]) for row in supported]
    reticle_offsets = [float(row["distance_from_reticle_px"]) for row in supported]
    edge_margins = [float(row["edge_margin_px"]) for row in supported]
    structure_distances = [float(row["nearest_dark_structure_px"]) for row in supported if row["nearest_dark_structure_px"] != ""]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable compact bright central-field candidate"},
        supported_interval_summary(rows),
        track_stats(rows),
        numeric_summary("component_area", areas, "tracked compact bright component pixel area"),
        numeric_summary("contrast_delta_luma", contrasts, "component max luma minus local median"),
        numeric_summary("distance_from_reticle_px", reticle_offsets, "distance from central reticle to candidate"),
        numeric_summary("edge_margin_px", edge_margins, "minimum distance from candidate center to central ROI boundary"),
        numeric_summary("nearest_dark_structure_px", structure_distances, "distance from candidate to dark wind-turbine/structure mask"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "review quality"})
    for key, value in sorted(phase_supported_counts.items()):
        summary_rows.append({"metric": f"supported_phase_count: {key}", "value": value, "note": "supported rows by local scene phase"})
    for key, value in sorted(structure_counts.items()):
        summary_rows.append({"metric": f"dark_structure_relation_count: {key}", "value": value, "note": "supported candidate relation to dark structure mask"})
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "track_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR48 one-fps centered compact-bright track table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR48 centered track review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR48 annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR48 target patch sheet"})
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"supported={len(supported)}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

