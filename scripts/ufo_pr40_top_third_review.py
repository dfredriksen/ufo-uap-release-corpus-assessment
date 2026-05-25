from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689082"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR40"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689082.mp4")
FALLBACK_VIDEO = Path("research/ufo-derived/video-motion-pass/pr40-top-third-review/source") / VIDEO_NAME
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr40-top-third-review") / VIDEO_ID

ROI_X0 = 360
ROI_Y0 = 90
ROI_X1 = 1505
ROI_Y1 = 610
TOP_THIRD_Y1 = 500.0
RETICLE_X = 960.0
RETICLE_Y = 540.0
ANNOTATION_BOX = (845, 390, 892, 422)
ANNOTATION_FOCUS_X = 870.0
ANNOTATION_FOCUS_Y = 405.0


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
    raise RuntimeError(f"Could not open any PR40 source video: {tried}")


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 10.0:
        return "initial brightening", "DVIDS 00:00-00:09: area of contrast brightens and becomes distinct"
    if second < 15.0:
        return "reporter annotation pause", "DVIDS 00:10-00:14: playback pauses on reporter annotation for small thermal signature"
    return "post-annotation top-third tracking", "DVIDS 00:15-01:03: sensor pans while contrast/zoom settings cycle"


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 35) & (hue <= 115)
    mask = ((sat > 35) & (val > 35) & cyan_green).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=1)


def fixed_overlay_mask(shape: tuple[int, int, int]) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    boxes = [
        (0, 0, 165, 1080),
        (1765, 0, 1920, 1080),
        (0, 0, 1920, 70),
        (0, 1060, 1920, 1080),
        (690, 0, 1270, 230),
        (0, 165, 275, 325),
        (0, 345, 340, 770),
        (0, 875, 235, 1010),
        (1570, 115, 1785, 315),
        (1535, 675, 1790, 1060),
        (900, 480, 1030, 615),
    ]
    for x0, y0, x1, y1 in boxes:
        cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(width, x1), min(height, y1)), 255, -1)
    return mask


def remove_line_artifacts(mask: np.ndarray) -> np.ndarray:
    horizontal = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((1, 31), np.uint8))
    vertical = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((31, 1), np.uint8))
    line_mask = cv2.dilate(cv2.bitwise_or(horizontal, vertical), np.ones((5, 5), np.uint8), iterations=1)
    return cv2.bitwise_and(mask, cv2.bitwise_not(line_mask))


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay = cv2.bitwise_or(fixed_overlay_mask(frame.shape), colored_overlay_mask(frame))
    overlay = cv2.dilate(overlay, np.ones((19, 19), np.uint8), iterations=1)[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    valid = (gray > 10) & (gray < 248) & (overlay == 0)
    if int(valid.sum()) < 1000:
        empty = np.zeros_like(gray, dtype=np.uint8)
        return roi, gray, empty, empty.astype(np.int16), empty.astype(np.int16), 0.0

    background = cv2.medianBlur(gray, 45)
    signed_delta = gray.astype(np.int16) - background.astype(np.int16)
    abs_delta = np.abs(signed_delta)
    threshold = max(14.0, float(np.percentile(abs_delta[valid], 99.82)))
    raw = ((abs_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = remove_line_artifacts(raw)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return roi, gray, raw, signed_delta, abs_delta, threshold


def detect_compact_candidates(frame: np.ndarray, second: float, limit: int = 18) -> list[dict]:
    _roi, gray, mask, signed_delta, abs_delta, threshold = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 2 or area > 160:
            continue
        if w > 30 or h > 30 or w <= 1 or h <= 1:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 5.5:
            continue

        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        values = gray[labels == label]
        signed_values = signed_delta[labels == label]
        abs_values = abs_delta[labels == label]
        local_patch = gray[max(0, y - 24) : min(gray.shape[0], y + h + 24), max(0, x - 24) : min(gray.shape[1], x + w + 24)]
        if local_patch.size:
            black_fraction = float(np.mean(local_patch < 12))
            white_fraction = float(np.mean(local_patch > 245))
            if black_fraction > 0.05 or white_fraction > 0.08:
                continue
        local_median = float(np.median(local_patch)) if local_patch.size else float(np.median(gray))
        mean_signed_delta = float(np.mean(signed_values))
        polarity = "bright" if mean_signed_delta >= 0 else "dark"
        contrast_delta = float(np.max(abs_values))
        distance_from_reticle = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        annotation_distance = math.hypot(full_x - ANNOTATION_FOCUS_X, full_y - ANNOTATION_FOCUS_Y)
        edge_margin = min(full_x - ROI_X0, ROI_X1 - full_x, full_y - ROI_Y0, ROI_Y1 - full_y)
        fill = int(area) / max(1, int(w) * int(h))
        top_third_excess = max(0.0, full_y - TOP_THIRD_Y1)

        score = (
            contrast_delta * 5.6
            + min(int(area), 90) * 1.6
            + min(fill, 0.85) * 55.0
            - distance_from_reticle * 0.035
            - top_third_excess * 1.4
            - max(0.0, 35.0 - edge_margin) * 2.5
            - max(0.0, aspect - 2.8) * 14.0
        )
        if full_y <= TOP_THIRD_Y1:
            score += 95.0
        if second < 16.0:
            score += max(0.0, 180.0 - annotation_distance) * 1.2
        elif second >= 15.0 and full_y <= TOP_THIRD_Y1:
            score += 45.0

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
                "top_third_proxy": full_y <= TOP_THIRD_Y1,
                "polarity": polarity,
                "component_max_luma": int(values.max()),
                "component_min_luma": int(values.min()),
                "component_mean_luma": float(values.mean()),
                "local_median_luma": local_median,
                "contrast_delta": contrast_delta,
                "distance_from_reticle_px": distance_from_reticle,
                "distance_from_annotation_focus_px": annotation_distance,
                "edge_margin_px": edge_margin,
                "detection_threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:limit]


def annotation_guided_candidate(frame: np.ndarray) -> tuple[dict | None, int]:
    x0, y0, x1, y1 = ANNOTATION_BOX
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray[y0:y1, x0:x1]
    valid = (roi > 35) & (roi < 220)
    if int(valid.sum()) < 50:
        return None, 0
    local_median = float(np.median(roi[valid]))
    valid_values = roi[valid]
    peak = int(valid_values.max())
    if peak <= local_median + 6:
        return None, 0
    threshold = max(local_median + 12.0, peak - max(8.0, (peak - local_median) * 0.32))
    raw = ((roi >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)

    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 1 or area > 80 or w > 22 or h > 22:
            continue
        cx, cy = centroids[label]
        full_x = x0 + float(cx)
        full_y = y0 + float(cy)
        values = roi[labels == label]
        contrast_delta = float(values.max()) - local_median
        annotation_distance = math.hypot(full_x - ANNOTATION_FOCUS_X, full_y - ANNOTATION_FOCUS_Y)
        distance_from_reticle = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        fill = int(area) / max(1, int(w) * int(h))
        score = contrast_delta * 5.0 + int(area) * 1.6 + fill * 55.0 - annotation_distance * 2.5
        candidates.append(
            {
                "label": int(label),
                "roi_x": int(full_x - ROI_X0 - (w / 2)),
                "roi_y": int(full_y - ROI_Y0 - (h / 2)),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "fill_ratio": fill,
                "center_x": full_x,
                "center_y": full_y,
                "top_third_proxy": full_y <= TOP_THIRD_Y1,
                "polarity": "bright",
                "component_max_luma": int(values.max()),
                "component_min_luma": int(values.min()),
                "component_mean_luma": float(values.mean()),
                "local_median_luma": local_median,
                "contrast_delta": contrast_delta,
                "distance_from_reticle_px": distance_from_reticle,
                "distance_from_annotation_focus_px": annotation_distance,
                "edge_margin_px": min(full_x - ROI_X0, ROI_X1 - full_x, full_y - ROI_Y0, ROI_Y1 - full_y),
                "detection_threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return (candidates[0] if candidates else None), len(candidates)


def select_candidate(frame: np.ndarray, second: float) -> tuple[dict | None, str, int]:
    if 10.0 <= second < 15.0:
        candidate, count = annotation_guided_candidate(frame)
        if candidate is not None:
            return candidate, "annotation-guided", count
    candidates = detect_compact_candidates(frame, second)
    return (candidates[0] if candidates else None), "compact-contrast", len(candidates)


def classify(candidate: dict | None, second: float, detection_mode: str) -> tuple[str, str]:
    if candidate is None:
        return "none", "no compact contrast candidate survived overlay and redaction filtering"
    contrast = float(candidate["contrast_delta"])
    area = int(candidate["area"])
    top_third = bool(candidate["top_third_proxy"])
    edge = float(candidate["edge_margin_px"])
    focus_distance = float(candidate["distance_from_annotation_focus_px"])

    if detection_mode == "annotation-guided":
        return "medium", "reporter annotation identifies the area; support is capped because playback is paused and overlaid"
    if second < 10.0:
        if contrast >= 28.0 and area >= 4 and focus_distance <= 240.0:
            return "high", "compact brightening candidate near the later reporter-annotated area"
        if contrast >= 18.0 and focus_distance <= 320.0:
            return "medium", "initial compact contrast candidate near the later annotation area"
        return "low", "initial candidate is weak or not close to the later annotation area"
    if second >= 15.0:
        if top_third and contrast >= 55.0 and area >= 5 and edge >= 35.0:
            return "high", "strong compact top-third contrast candidate after playback resumes"
        if top_third and contrast >= 26.0 and area >= 2 and edge >= 20.0:
            return "medium", "usable top-third contrast candidate, but cloud texture and contrast cycling limit object continuity"
        if contrast >= 18.0:
            return "low", "weak, off-lane, or texture-confounded post-annotation contrast candidate"
    return "none", "candidate is too weak for this phase"


def sample_seconds(duration: float, sample_rate: float) -> list[float]:
    count = int(math.floor(duration * sample_rate)) + 1
    seconds = []
    for index in range(count):
        second = round(index / sample_rate, 3)
        if second <= duration:
            seconds.append(second)
    return seconds


def annotate_frame(frame: np.ndarray, candidate: dict | None, second: float, quality: str, phase: str, detection_mode: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (90, 90, 90), 1)
    cv2.line(out, (ROI_X0, int(TOP_THIRD_Y1)), (ROI_X1, int(TOP_THIRD_Y1)), (90, 90, 90), 1)
    cv2.rectangle(out, (ANNOTATION_BOX[0], ANNOTATION_BOX[1]), (ANNOTATION_BOX[2], ANNOTATION_BOX[3]), (120, 120, 120), 1)
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
    cv2.rectangle(out, (0, 0), (930, 38), (0, 0, 0), -1)
    cv2.putText(
        out,
        f"{VIDEO_ID} {second:.1f}s {quality} {phase} {detection_mode}",
        (12, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return out


def annotate_patch(frame: np.ndarray, candidate: dict | None, second: float, quality: str, detection_mode: str) -> np.ndarray:
    if candidate is None:
        center_x = int(ANNOTATION_FOCUS_X)
        center_y = int(ANNOTATION_FOCUS_Y)
    else:
        center_x = int(round(float(candidate["center_x"])))
        center_y = int(round(float(candidate["center_y"])))
    radius = 76
    x0 = max(0, center_x - radius)
    y0 = max(0, center_y - radius)
    x1 = min(frame.shape[1], center_x + radius)
    y1 = min(frame.shape[0], center_y + radius)
    crop = frame[y0:y1, x0:x1].copy()
    if crop.size == 0:
        crop = np.zeros((152, 152, 3), dtype=np.uint8)
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
    cv2.putText(
        patch,
        f"{second:.1f}s {quality} {detection_mode}",
        (8, 23),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
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


def post_resume_supported_rows(rows: list[dict]) -> list[dict]:
    return [
        row
        for row in supported_rows(rows)
        if float(row["approx_second"]) >= 15.0 and row["detection_mode"] == "compact-contrast" and row["top_third_proxy"] == "yes"
    ]


def annotation_rows(rows: list[dict]) -> list[dict]:
    return [row for row in supported_rows(rows) if row["detection_mode"] == "annotation-guided"]


def supported_interval_summary(rows: list[dict], metric: str, source_rows: list[dict]) -> dict:
    seconds = [float(row["approx_second"]) for row in source_rows]
    if not seconds:
        return {"metric": metric, "value": "", "note": "no supported rows"}
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
    return {"metric": metric, "value": text, "note": f"{len(ranges)} one-fps supported interval(s)"}


def track_stats(rows: list[dict]) -> dict:
    supported = post_resume_supported_rows(rows)
    if len(supported) < 2:
        return {"metric": "post_resume_compact_candidate_track", "value": len(supported), "note": "fewer than two supported post-resume rows"}
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
        "metric": "post_resume_compact_candidate_track",
        "value": len(supported),
        "note": (
            f"{supported[0]['approx_second']}s-{supported[-1]['approx_second']}s; "
            f"net={net:.3f}px; path={total:.3f}px; "
            f"path_rate={(total / duration):.3f}px/s; median_step_rate={statistics.median(rates):.3f}px/s; "
            "candidate path only, object identity continuity not asserted"
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
    parser = argparse.ArgumentParser(description="PR40 one-fps top-third compact contrast review for DOD_111689082.")
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
        phase, anchor = dvids_phase(actual_second)
        candidate, detection_mode, candidate_count = select_candidate(frame, actual_second)
        quality, caveat = classify(candidate, actual_second, detection_mode)
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, candidate, actual_second, quality, phase, detection_mode), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, candidate, actual_second, quality, detection_mode), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
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
                "detection_mode": detection_mode,
                "candidate_count": candidate_count,
                "target_center_x": "" if candidate is None else round(float(candidate["center_x"]), 1),
                "target_center_y": "" if candidate is None else round(float(candidate["center_y"]), 1),
                "bbox_x0": "" if candidate is None else ROI_X0 + int(candidate["roi_x"]),
                "bbox_y0": "" if candidate is None else ROI_Y0 + int(candidate["roi_y"]),
                "bbox_w": "" if candidate is None else int(candidate["bbox_w"]),
                "bbox_h": "" if candidate is None else int(candidate["bbox_h"]),
                "component_area": "" if candidate is None else int(candidate["area"]),
                "fill_ratio": "" if candidate is None else round(float(candidate["fill_ratio"]), 3),
                "polarity": "" if candidate is None else str(candidate["polarity"]),
                "top_third_proxy": "no" if candidate is None or not candidate["top_third_proxy"] else "yes",
                "component_max_luma": "" if candidate is None else int(candidate["component_max_luma"]),
                "component_min_luma": "" if candidate is None else int(candidate["component_min_luma"]),
                "component_mean_luma": "" if candidate is None else round(float(candidate["component_mean_luma"]), 2),
                "local_median_luma": "" if candidate is None else round(float(candidate["local_median_luma"]), 2),
                "contrast_delta": "" if candidate is None else round(float(candidate["contrast_delta"]), 2),
                "distance_from_reticle_px": "" if candidate is None else round(float(candidate["distance_from_reticle_px"]), 2),
                "distance_from_annotation_focus_px": "" if candidate is None else round(float(candidate["distance_from_annotation_focus_px"]), 2),
                "edge_margin_px": "" if candidate is None else round(float(candidate["edge_margin_px"]), 2),
                "detection_threshold": "" if candidate is None else round(float(candidate["detection_threshold"]), 3),
                "raw_score": "" if candidate is None else round(float(candidate["raw_score"]), 3),
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr40-top-third-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr40-top-third-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr40-top-third-review-dod111689082.csv")
    summary_csv = Path("research/ufo-video-pr40-top-third-review-summary.csv")
    asset_csv = Path("research/ufo-video-pr40-top-third-review-assets.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    supported = supported_rows(rows)
    annotation_supported = annotation_rows(rows)
    post_supported = post_resume_supported_rows(rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    phase_supported_counts = Counter(row["dvids_phase"] for row in supported)
    mode_counts = Counter(row["detection_mode"] for row in supported)
    polarity_counts = Counter(row["polarity"] for row in supported if row["polarity"])
    areas = [float(row["component_area"]) for row in supported if row["component_area"] != ""]
    contrasts = [float(row["contrast_delta"]) for row in supported if row["contrast_delta"] != ""]
    reticle_offsets = [float(row["distance_from_reticle_px"]) for row in supported if row["distance_from_reticle_px"] != ""]
    annotation_offsets = [float(row["distance_from_annotation_focus_px"]) for row in supported if row["distance_from_annotation_focus_px"] != ""]
    post_y = [float(row["target_center_y"]) for row in post_supported if row["target_center_y"] != ""]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": f"source video used: {source_video}"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "annotation-guided or compact contrast rows"},
        {"metric": "annotation_guided_supported_rows", "value": len(annotation_supported), "note": "paused reporter annotation interval"},
        {"metric": "post_resume_top_third_supported_rows", "value": len(post_supported), "note": "post-annotation compact contrast candidates in top-third lane"},
        supported_interval_summary(rows, "supported_intervals", supported),
        supported_interval_summary(rows, "annotation_guided_intervals", annotation_supported),
        supported_interval_summary(rows, "post_resume_top_third_intervals", post_supported),
        track_stats(rows),
        numeric_summary("component_area", areas, "selected compact contrast candidate pixel area"),
        numeric_summary("contrast_delta_luma", contrasts, "absolute local contrast against median background"),
        numeric_summary("distance_from_reticle_px", reticle_offsets, "selected candidate distance from central reticle"),
        numeric_summary("distance_from_annotation_focus_px", annotation_offsets, "selected candidate distance from PR40 annotation focus"),
        numeric_summary("post_resume_target_center_y", post_y, f"post-resume selected candidate y; top-third proxy threshold={TOP_THIRD_Y1}px"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "review quality"})
    for key, value in sorted(phase_supported_counts.items()):
        summary_rows.append({"metric": f"supported_phase_count: {key}", "value": value, "note": "supported rows by DVIDS phase"})
    for key, value in sorted(mode_counts.items()):
        summary_rows.append({"metric": f"detection_mode_count: {key}", "value": value, "note": "supported rows by detection mode"})
    for key, value in sorted(polarity_counts.items()):
        summary_rows.append({"metric": f"polarity_count: {key}", "value": value, "note": "supported selected candidate polarity"})
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "top_third_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR40 one-fps top-third compact contrast review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR40 top-third compact contrast review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR40 annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR40 target/candidate patch sheet"})
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={source_video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"supported={len(supported)} annotation_guided={len(annotation_supported)} post_resume_top_third={len(post_supported)}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

