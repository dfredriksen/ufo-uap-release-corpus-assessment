from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111688816"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR26"
REPORT_ID = "DoW-UAP-D12"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111688816.mp4")
FALLBACK_VIDEO = Path("research/ufo-derived/video-motion-pass/pr26-d12-image-review/source") / VIDEO_NAME
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr26-d12-image-review") / VIDEO_ID

ROI_X0 = 150
ROI_Y0 = 120
ROI_X1 = 820
ROI_Y1 = 760
LEFT_QUARTER_X1 = 640.0
RETICLE_X = 960.0
RETICLE_Y = 540.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def open_capture(video: Path) -> tuple[Path, cv2.VideoCapture]:
    candidates = [video]
    if video == DEFAULT_VIDEO and FALLBACK_VIDEO not in candidates:
        candidates.append(FALLBACK_VIDEO)
    tried: list[str] = []
    for candidate in candidates:
        tried.append(str(candidate))
        cap = cv2.VideoCapture(str(candidate))
        if cap.isOpened():
            return candidate, cap
        cap.release()
    raise RuntimeError(f"Could not open any PR26 source video: {tried}")


def review_phase(second: float) -> tuple[str, str]:
    anchor = (
        "DVIDS image description: encircled elongated area of contrast in top-left quarter; "
        "D12 described north-to-northeast movement"
    )
    if second < 17.0:
        return "primary visible left-field contrast", anchor
    if second < 30.0:
        return "intermittent left-field contrast", anchor
    return "late low-or-absent contrast", anchor


def fixed_overlay_mask(shape: tuple[int, int, int]) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    boxes = [
        (0, 0, 165, 1080),
        (0, 0, 770, 75),
        (830, 0, 1110, 115),
        (1165, 0, 1310, 75),
        (1390, 0, 1520, 75),
        (1810, 0, 1920, 100),
        (0, 465, 140, 665),
        (0, 955, 100, 1080),
        (895, 475, 1045, 635),
        (1690, 795, 1920, 1080),
    ]
    for x0, y0, x1, y1 in boxes:
        cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(width, x1), min(height, y1)), 255, -1)
    return mask


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 35) & (hue <= 115)
    mask = ((sat > 35) & (val > 35) & cyan_green).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=1)


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay = cv2.bitwise_or(fixed_overlay_mask(frame.shape), colored_overlay_mask(frame))
    overlay = cv2.dilate(overlay, np.ones((11, 11), np.uint8), iterations=1)[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    valid = (gray > 12) & (gray < 252) & (overlay == 0)
    if int(valid.sum()) < 1000:
        empty = np.zeros_like(gray, dtype=np.uint8)
        return gray, empty, empty.astype(np.int16), overlay, 0.0

    background = cv2.medianBlur(gray, 45)
    bright_delta = gray.astype(np.int16) - background.astype(np.int16)
    threshold = max(15.0, float(np.percentile(bright_delta[valid], 99.83)))
    raw = ((bright_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return gray, raw, bright_delta, overlay, threshold


def detect_candidates(frame: np.ndarray, limit: int = 16) -> list[dict]:
    gray, mask, bright_delta, _overlay, threshold = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 2 or area > 260:
            continue
        if w < 2 or h < 2 or w > 46 or h > 36:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 10.0:
            continue
        local_patch = gray[max(0, y - 24) : min(gray.shape[0], y + h + 24), max(0, x - 24) : min(gray.shape[1], x + w + 24)]
        if local_patch.size:
            if float(np.mean(local_patch < 12)) > 0.05 or float(np.mean(local_patch > 245)) > 0.08:
                continue
        values = gray[labels == label]
        delta_values = bright_delta[labels == label]
        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        local_median = float(np.median(local_patch)) if local_patch.size else float(np.median(gray))
        contrast_delta = float(values.max()) - local_median
        edge_margin = min(full_x - ROI_X0, ROI_X1 - full_x, full_y - ROI_Y0, ROI_Y1 - full_y)
        distance_from_reticle = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        left_quarter_proxy = full_x <= LEFT_QUARTER_X1 and 220.0 <= full_y <= 690.0
        fill = int(area) / max(1, int(w) * int(h))
        elongation_proxy = aspect >= 1.12 or int(area) >= 80
        score = (
            contrast_delta * 6.0
            + min(int(area), 110) * 1.6
            + min(fill, 0.85) * 45.0
            + (110.0 if left_quarter_proxy else 0.0)
            + (45.0 if elongation_proxy else 0.0)
            + max(0.0, LEFT_QUARTER_X1 - full_x) * 0.10
            - max(0.0, 35.0 - edge_margin) * 2.0
            - max(0.0, aspect - 4.0) * 10.0
            - distance_from_reticle * 0.025
        )
        candidates.append(
            {
                "label": int(label),
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "fill_ratio": fill,
                "center_x": full_x,
                "center_y": full_y,
                "left_quarter_proxy": left_quarter_proxy,
                "elongation_proxy": elongation_proxy,
                "component_max_luma": int(values.max()),
                "component_min_luma": int(values.min()),
                "component_mean_luma": float(values.mean()),
                "mean_bright_delta": float(np.mean(delta_values)),
                "local_median_luma": local_median,
                "contrast_delta": contrast_delta,
                "aspect_ratio": aspect,
                "distance_from_reticle_px": distance_from_reticle,
                "edge_margin_px": edge_margin,
                "detection_threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:limit]


def select_candidate(candidates: list[dict], second: float) -> dict | None:
    if not candidates:
        return None
    if second >= 30.0:
        return candidates[0]
    lane_candidates = [item for item in candidates if item["left_quarter_proxy"]]
    if lane_candidates:
        return lane_candidates[0]
    return candidates[0]


def classify(candidate: dict | None, second: float) -> tuple[str, str]:
    if candidate is None:
        return "none", "no compact bright left-field candidate survived filtering"
    contrast = float(candidate["contrast_delta"])
    area = int(candidate["area"])
    edge = float(candidate["edge_margin_px"])
    left = bool(candidate["left_quarter_proxy"])
    elongated = bool(candidate["elongation_proxy"])
    if second >= 30.0:
        return "low", "late-frame residual or background speck; DVIDS-described area is not robustly visible"
    if left and elongated and contrast >= 80.0 and area >= 80 and edge >= 25.0:
        return "high", "strong compact/elongated bright contrast in the DVIDS-described left/top-left lane"
    if left and contrast >= 55.0 and area >= 35 and edge >= 20.0:
        return "medium", "usable left-field bright contrast candidate; sensor motion and contrast changes limit motion inference"
    if contrast >= 25.0 and area >= 2:
        return "low", "weak, edge-near, or lane-confounded bright contrast candidate"
    return "none", "candidate too weak for PR26/D12 visual-support claim"


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
    cv2.line(out, (int(LEFT_QUARTER_X1), ROI_Y0), (int(LEFT_QUARTER_X1), ROI_Y1), (90, 90, 90), 1)
    if candidate is not None:
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        x0 = ROI_X0 + int(candidate["roi_x"])
        y0 = ROI_Y0 + int(candidate["roi_y"])
        x1 = x0 + int(candidate["bbox_w"])
        y1 = y0 + int(candidate["bbox_h"])
        cv2.rectangle(out, (x0, y0), (x1, y1), color, 1)
        cv2.drawMarker(
            out,
            (int(round(float(candidate["center_x"]))), int(round(float(candidate["center_y"])))),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=18,
            thickness=1,
        )
    cv2.rectangle(out, (0, 0), (1000, 38), (0, 0, 0), -1)
    cv2.putText(
        out,
        f"{VIDEO_ID} {second:.1f}s {quality} {phase}",
        (12, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return out


def annotate_patch(frame: np.ndarray, candidate: dict | None, second: float, quality: str) -> np.ndarray:
    if candidate is None:
        center_x, center_y = 430, 500
    else:
        center_x = int(round(float(candidate["center_x"])))
        center_y = int(round(float(candidate["center_y"])))
    radius = 86
    x0 = max(0, center_x - radius)
    y0 = max(0, center_y - radius)
    x1 = min(frame.shape[1], center_x + radius)
    y1 = min(frame.shape[0], center_y + radius)
    crop = frame[y0:y1, x0:x1].copy()
    if crop.size == 0:
        crop = np.zeros((172, 172, 3), dtype=np.uint8)
    if candidate is not None:
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        bx0 = ROI_X0 + int(candidate["roi_x"]) - x0
        by0 = ROI_Y0 + int(candidate["roi_y"]) - y0
        bx1 = bx0 + int(candidate["bbox_w"])
        by1 = by0 + int(candidate["bbox_h"])
        cv2.rectangle(crop, (bx0, by0), (bx1, by1), color, 1)
        cv2.drawMarker(
            crop,
            (center_x - x0, center_y - y0),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=18,
            thickness=1,
        )
    patch = cv2.resize(crop, (340, 340), interpolation=cv2.INTER_NEAREST)
    cv2.rectangle(patch, (0, 0), (340, 34), (0, 0, 0), -1)
    cv2.putText(patch, f"{second:.1f}s {quality}", (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
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
    seconds = [float(row["approx_second"]) for row in supported_rows(rows)]
    if not seconds:
        return {"metric": "supported_intervals", "value": "", "note": "no supported rows"}
    ranges: list[tuple[float, float]] = []
    start = seconds[0]
    prev = seconds[0]
    for second in seconds[1:]:
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
        return {"metric": "supported_candidate_track", "value": len(supported), "note": "fewer than two supported rows"}
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
        "metric": "supported_candidate_track",
        "value": len(supported),
        "note": (
            f"{supported[0]['approx_second']}s-{supported[-1]['approx_second']}s; "
            f"net={net:.3f}px; path={total:.3f}px; "
            f"path_rate={(total / duration):.3f}px/s; median_step_rate={statistics.median(rates):.3f}px/s; "
            "image-plane candidate path only, not a physical north-to-northeast validation"
        ),
    }


def numeric_summary(metric: str, values: list[float], note: str) -> dict:
    if not values:
        return {"metric": metric, "value": "", "note": note}
    mean = statistics.mean(values)
    stdev = statistics.stdev(values) if len(values) > 1 else 0.0
    median = statistics.median(values)
    cv = stdev / mean if mean else 0.0
    return {"metric": metric, "value": round(median, 3), "note": f"median; mean={mean:.3f}; stdev={stdev:.3f}; cv={cv:.3f}; {note}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="PR26/D12 one-fps compact elongated-contrast review for DOD_111688816.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=1.0)
    args = parser.parse_args()

    source_video, cap = open_capture(args.video)
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
        phase, anchor = review_phase(actual_second)
        candidates = detect_candidates(frame)
        candidate = select_candidate(candidates, actual_second)
        quality, caveat = classify(candidate, actual_second)
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
                "report_id": REPORT_ID,
                "sample_index": sample_index,
                "approx_second": f"{actual_second:.1f}",
                "source_frame_index": frame_index,
                "review_phase": phase,
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
                "left_quarter_proxy": "no" if candidate is None or not candidate["left_quarter_proxy"] else "yes",
                "elongation_proxy": "no" if candidate is None or not candidate["elongation_proxy"] else "yes",
                "component_max_luma": "" if candidate is None else int(candidate["component_max_luma"]),
                "component_min_luma": "" if candidate is None else int(candidate["component_min_luma"]),
                "component_mean_luma": "" if candidate is None else round(float(candidate["component_mean_luma"]), 2),
                "local_median_luma": "" if candidate is None else round(float(candidate["local_median_luma"]), 2),
                "contrast_delta": "" if candidate is None else round(float(candidate["contrast_delta"]), 2),
                "aspect_ratio": "" if candidate is None else round(float(candidate["aspect_ratio"]), 3),
                "distance_from_reticle_px": "" if candidate is None else round(float(candidate["distance_from_reticle_px"]), 2),
                "edge_margin_px": "" if candidate is None else round(float(candidate["edge_margin_px"]), 2),
                "detection_threshold": "" if candidate is None else round(float(candidate["detection_threshold"]), 3),
                "raw_score": "" if candidate is None else round(float(candidate["raw_score"]), 3),
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr26-d12-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr26-d12-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr26-d12-image-review-dod111688816.csv")
    summary_csv = Path("research/ufo-video-pr26-d12-image-review-summary.csv")
    asset_csv = Path("research/ufo-video-pr26-d12-image-review-assets.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    supported = supported_rows(rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    phase_supported_counts = Counter(row["review_phase"] for row in supported)
    areas = [float(row["component_area"]) for row in supported if row["component_area"] != ""]
    contrasts = [float(row["contrast_delta"]) for row in supported if row["contrast_delta"] != ""]
    aspects = [float(row["aspect_ratio"]) for row in supported if row["aspect_ratio"] != ""]
    reticle_offsets = [float(row["distance_from_reticle_px"]) for row in supported if row["distance_from_reticle_px"] != ""]
    xs = [float(row["target_center_x"]) for row in supported if row["target_center_x"] != ""]
    ys = [float(row["target_center_y"]) for row in supported if row["target_center_y"] != ""]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": f"source video used: {source_video}"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "report_id", "value": REPORT_ID, "note": "DVIDS-stated accompanying mission report"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable left-field compact bright candidate"},
        supported_interval_summary(rows),
        track_stats(rows),
        numeric_summary("component_area", areas, "selected compact/elongated bright candidate pixel area"),
        numeric_summary("contrast_delta_luma", contrasts, "selected candidate max luma minus local median"),
        numeric_summary("aspect_ratio", aspects, "selected candidate bounding-box elongation proxy"),
        numeric_summary("distance_from_reticle_px", reticle_offsets, "selected candidate distance from central reticle"),
        numeric_summary("target_center_x", xs, "selected candidate x-position"),
        numeric_summary("target_center_y", ys, "selected candidate y-position"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "review quality"})
    for key, value in sorted(phase_supported_counts.items()):
        summary_rows.append({"metric": f"supported_phase_count: {key}", "value": value, "note": "supported rows by local review phase"})
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "image_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR26/D12 one-fps compact elongated-contrast review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR26/D12 image-plane review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR26/D12 annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR26/D12 target patch sheet"})
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={source_video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"supported={len(supported)}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

