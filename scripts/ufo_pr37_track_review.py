from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689044"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR37"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689044.mp4")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr37-track-review") / VIDEO_ID

SEARCH_X0 = 280
SEARCH_Y0 = 80
SEARCH_X1 = 820
SEARCH_Y1 = 1068

DVIDS_EVENT_START = 6.0
DVIDS_EVENT_END = 8.0
VISIBLE_LANE_START = 6.4
VISIBLE_LANE_END = 7.8


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def phase_for(second: float) -> tuple[str, str]:
    if second < DVIDS_EVENT_START:
        return "pre-described context", "DVIDS gives no target description before 00:06"
    if second <= DVIDS_EVENT_END:
        return (
            "bottom-to-top left-side crossing",
            "DVIDS 00:06-00:08: contrast area enters from bottom-left quarter, moves generally bottom-to-top, exits top-left quarter",
        )
    return "post-described context", "DVIDS gives no target description after 00:08"


def is_event_window(second: float) -> bool:
    return DVIDS_EVENT_START <= second <= DVIDS_EVENT_END


def expected_center(second: float) -> tuple[float, float]:
    alpha = min(max((second - VISIBLE_LANE_START) / (VISIBLE_LANE_END - VISIBLE_LANE_START), 0.0), 1.0)
    # Image-plane lane used only to rank ambiguous bright components in the DVIDS
    # event window. It follows the visible bottom-to-top streak in the local file.
    return 505.0 + (623.0 - 505.0) * alpha, 1028.0 + (140.0 - 1028.0) * alpha


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 35) & (hue <= 115)
    mask = ((sat > 35) & (val > 35) & cyan_green).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    roi = frame[SEARCH_Y0:SEARCH_Y1, SEARCH_X0:SEARCH_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay_clear = colored_overlay_mask(roi) == 0
    not_blackout = gray > 28
    valid = overlay_clear & not_blackout
    if int(valid.sum()) < 50:
        empty = np.zeros_like(gray, dtype=np.uint8)
        return roi, gray, valid, empty, empty, 0.0, 0.0

    background = cv2.medianBlur(gray, 41)
    positive_contrast = np.clip(gray.astype(np.int16) - background.astype(np.int16), 0, 255).astype(np.uint8)
    values = positive_contrast[valid]
    threshold = max(14.0, float(np.percentile(values, 99.75))) if values.size else 255.0
    raw = ((positive_contrast >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    local_median = float(np.median(gray[valid]))
    return roi, gray, valid, positive_contrast, raw, threshold, local_median


def detect_target(frame: np.ndarray, second: float) -> dict:
    roi, gray, _valid, positive_contrast, mask, threshold, local_median = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    expected_x, expected_y = expected_center(second)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 3 or area > 650:
            continue
        if w > 60 or h > 125:
            continue
        if w < 2 or h < 3:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 18.0:
            continue

        cx, cy = centroids[label]
        full_x = SEARCH_X0 + float(cx)
        full_y = SEARCH_Y0 + float(cy)
        contrast_values = positive_contrast[labels == label]
        gray_values = gray[labels == label]
        distance = math.hypot(full_x - expected_x, full_y - expected_y)
        fill = area / max(1, w * h)
        vertical_bonus = min(float(h), 80.0) * 2.0 if h >= w else 0.0
        score = (
            float(contrast_values.sum())
            + float(contrast_values.max()) * 2.0
            + vertical_bonus
            + float(area) * 0.5
            - distance * 3.0
            - max(0.0, aspect - 8.0) * 20.0
        )
        candidates.append(
            {
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "component_area": int(area),
                "fill_ratio": fill,
                "center_x": full_x,
                "center_y": full_y,
                "distance_from_expected_lane": distance,
                "max_luma": int(gray_values.max()),
                "min_luma": int(gray_values.min()),
                "mean_luma": float(gray_values.mean()),
                "max_positive_contrast": int(contrast_values.max()),
                "mean_positive_contrast": float(contrast_values.mean()),
                "positive_contrast_sum": float(contrast_values.sum()),
                "brightness_delta": float(gray_values.max()) - local_median,
                "score": score,
            }
        )

    if not candidates:
        return {
            "detected": False,
            "candidate_count": 0,
            "threshold": round(threshold, 3),
            "local_median_luma": round(local_median, 3),
        }

    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    x0 = SEARCH_X0 + best["roi_x"]
    y0 = SEARCH_Y0 + best["roi_y"]
    return {
        "detected": True,
        "candidate_count": len(candidates),
        "threshold": round(threshold, 3),
        "local_median_luma": round(local_median, 3),
        "center_x": best["center_x"],
        "center_y": best["center_y"],
        "bbox_x0": x0,
        "bbox_y0": y0,
        "bbox_x1": x0 + best["bbox_w"],
        "bbox_y1": y0 + best["bbox_h"],
        **best,
    }


def classify_detection(result: dict, second: float) -> tuple[str, str]:
    if not is_event_window(second):
        return "none", "outside DVIDS-described 00:06-00:08 event window"
    if not result.get("detected"):
        return "none", "no bright compact contrast component survived overlay/blackout suppression"

    distance = float(result["distance_from_expected_lane"])
    area = int(result["component_area"])
    width = int(result["bbox_w"])
    height = int(result["bbox_h"])
    max_contrast = float(result["max_positive_contrast"])
    brightness_delta = float(result["brightness_delta"])

    if (
        VISIBLE_LANE_START <= second <= VISIBLE_LANE_END
        and distance <= 85
        and area >= 80
        and height >= 12
        and max_contrast >= 60
        and brightness_delta >= 55
    ):
        return "high", "bright compact component on the visible DVIDS bottom-to-top event lane"
    if distance <= 150 and area >= 30 and min(width, height) >= 4 and max_contrast >= 35:
        return "medium", "usable partial or lower-contrast component near the DVIDS event lane"
    if distance <= 220 and area >= 5:
        return "low", "weak or poorly separated component near the event lane"
    return "none", "candidate is too far from the DVIDS-described event lane or too weak"


def add_label(img: np.ndarray, text: str, width: int = 1420) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 38), (0, 0, 0), -1)
    cv2.putText(out, text, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, result: dict, second: float, quality: str, phase: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (SEARCH_X0, SEARCH_Y0), (SEARCH_X1, SEARCH_Y1), (80, 80, 80), 1)
    start = expected_center(VISIBLE_LANE_START)
    end = expected_center(VISIBLE_LANE_END)
    expected_x, expected_y = expected_center(second)
    cv2.line(out, (int(start[0]), int(start[1])), (int(end[0]), int(end[1])), (255, 0, 0), 1)
    cv2.drawMarker(
        out,
        (int(round(expected_x)), int(round(expected_y))),
        (255, 0, 0),
        markerType=cv2.MARKER_CROSS,
        markerSize=26,
        thickness=1,
    )
    if result.get("detected"):
        x0 = int(round(result["bbox_x0"]))
        y0 = int(round(result["bbox_y0"]))
        x1 = int(round(result["bbox_x1"]))
        y1 = int(round(result["bbox_y1"]))
        color = (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255)
        cv2.rectangle(out, (x0, y0), (x1, y1), color, 2)
        center = (int(round(result["center_x"])), int(round(result["center_y"])))
        cv2.drawMarker(out, center, color, markerType=cv2.MARKER_CROSS, markerSize=30, thickness=2)
        cv2.line(out, (int(round(expected_x)), int(round(expected_y))), center, (255, 255, 0), 1)
    label = f"{VIDEO_ID} t={second:04.1f}s PR37 {phase}; quality={quality}"
    return add_label(out, label)


def crop_patch(frame: np.ndarray, result: dict, second: float, size: int = 260) -> np.ndarray:
    height, width = frame.shape[:2]
    if result.get("detected"):
        cx = int(round(result["center_x"]))
        cy = int(round(result["center_y"]))
    else:
        cx, cy = expected_center(second)
        cx = int(round(cx))
        cy = int(round(cy))
    half = size // 2
    x0 = max(0, min(width - size, cx - half))
    y0 = max(0, min(height - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(frame: np.ndarray, result: dict, second: float, quality: str) -> np.ndarray:
    patch = crop_patch(frame, result, second)
    if result.get("detected"):
        x_offset = int(round(result["bbox_x0"])) - max(0, min(frame.shape[1] - patch.shape[1], int(round(result["center_x"])) - patch.shape[1] // 2))
        y_offset = int(round(result["bbox_y0"])) - max(0, min(frame.shape[0] - patch.shape[0], int(round(result["center_y"])) - patch.shape[0] // 2))
        x1 = x_offset + int(result["bbox_w"])
        y1 = y_offset + int(result["bbox_h"])
        color = (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255)
        cv2.rectangle(patch, (x_offset, y_offset), (x1, y1), color, 2)
    patch = cv2.resize(patch, (520, 520), interpolation=cv2.INTER_NEAREST)
    return add_label(patch, f"{VIDEO_ID} t={second:04.1f}s quality={quality}", width=520)


def sample_seconds(duration: float, sample_rate: float) -> list[float]:
    count = int(math.floor(duration * sample_rate)) + 1
    seconds = []
    for index in range(count):
        second = round(index / sample_rate, 3)
        if second <= duration:
            seconds.append(second)
    if not seconds or seconds[-1] < duration:
        seconds.append(round(duration, 3))
    return seconds


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_contact_sheets(paths: list[Path], out_dir: Path, stem: str, cols: int, thumb_width: int) -> list[Path]:
    ensure_dir(out_dir)
    sheets: list[Path] = []
    for sheet_index, start in enumerate(range(0, len(paths), cols * 10)):
        chunk = paths[start : start + cols * 10]
        thumbs: list[np.ndarray] = []
        for path in chunk:
            img = cv2.imread(str(path))
            if img is None:
                continue
            scale = thumb_width / img.shape[1]
            thumb_height = max(1, int(round(img.shape[0] * scale)))
            thumbs.append(cv2.resize(img, (thumb_width, thumb_height), interpolation=cv2.INTER_AREA))
        if not thumbs:
            continue
        thumb_height = max(img.shape[0] for img in thumbs)
        rows = int(math.ceil(len(thumbs) / cols))
        sheet = np.zeros((rows * thumb_height, cols * thumb_width, 3), dtype=np.uint8)
        for index, img in enumerate(thumbs):
            y = (index // cols) * thumb_height
            x = (index % cols) * thumb_width
            sheet[y : y + img.shape[0], x : x + img.shape[1]] = img
        out_path = out_dir / f"{stem}_{sheet_index:02d}.jpg"
        cv2.imwrite(str(out_path), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        sheets.append(out_path)
    return sheets


def row_from_detection(
    sample_index: int,
    second: float,
    frame_index: int,
    result: dict,
    quality: str,
    caveat: str,
    annotated_path: Path,
    patch_path: Path,
) -> dict:
    phase, anchor = phase_for(second)
    expected_x, expected_y = expected_center(second)
    return {
        "video": VIDEO_NAME,
        "release_id": RELEASE_ID,
        "sample_index": sample_index,
        "approx_second": f"{second:.1f}",
        "source_frame_index": frame_index,
        "is_dvids_event_window": "yes" if is_event_window(second) else "no",
        "dvids_phase": phase,
        "dvids_anchor": anchor,
        "review_quality": quality,
        "candidate_count": result.get("candidate_count", 0),
        "target_center_x": "" if not result.get("detected") else round(float(result["center_x"]), 1),
        "target_center_y": "" if not result.get("detected") else round(float(result["center_y"]), 1),
        "expected_lane_x": round(expected_x, 1),
        "expected_lane_y": round(expected_y, 1),
        "distance_from_expected_lane_px": "" if not result.get("detected") else round(float(result["distance_from_expected_lane"]), 2),
        "bbox_x0": "" if not result.get("detected") else int(result["bbox_x0"]),
        "bbox_y0": "" if not result.get("detected") else int(result["bbox_y0"]),
        "bbox_x1": "" if not result.get("detected") else int(result["bbox_x1"]),
        "bbox_y1": "" if not result.get("detected") else int(result["bbox_y1"]),
        "bbox_w": "" if not result.get("detected") else int(result["bbox_w"]),
        "bbox_h": "" if not result.get("detected") else int(result["bbox_h"]),
        "component_area": "" if not result.get("detected") else int(result["component_area"]),
        "fill_ratio": "" if not result.get("detected") else round(float(result["fill_ratio"]), 3),
        "max_luma": "" if not result.get("detected") else int(result["max_luma"]),
        "mean_luma": "" if not result.get("detected") else round(float(result["mean_luma"]), 3),
        "local_median_luma": result.get("local_median_luma", ""),
        "brightness_delta": "" if not result.get("detected") else round(float(result["brightness_delta"]), 3),
        "max_positive_contrast": "" if not result.get("detected") else int(result["max_positive_contrast"]),
        "mean_positive_contrast": "" if not result.get("detected") else round(float(result["mean_positive_contrast"]), 3),
        "positive_contrast_sum": "" if not result.get("detected") else round(float(result["positive_contrast_sum"]), 3),
        "positive_contrast_threshold": result.get("threshold", ""),
        "score": "" if not result.get("detected") else round(float(result["score"]), 3),
        "caveat": caveat,
        "annotated_frame_path": str(annotated_path).replace("\\", "/"),
        "zoom_patch_path": str(patch_path).replace("\\", "/"),
    }


def supported_rows(rows: list[dict]) -> list[dict]:
    return [
        row
        for row in rows
        if row["review_quality"] in {"high", "medium"}
        and row["is_dvids_event_window"] == "yes"
        and row["target_center_x"] != ""
    ]


def supported_interval_summary(rows: list[dict]) -> dict:
    supported = supported_rows(rows)
    if not supported:
        return {"metric": "supported_intervals", "value": "", "note": "no high or medium event rows"}
    seconds = sorted({round(float(row["approx_second"]), 1) for row in supported})
    ranges: list[tuple[float, float]] = []
    start = seconds[0]
    prev = seconds[0]
    for second in seconds[1:]:
        if second - prev > 0.16:
            ranges.append((start, prev))
            start = second
        prev = second
    ranges.append((start, prev))
    text = "; ".join(f"{start:.1f}s" if start == end else f"{start:.1f}s-{end:.1f}s" for start, end in ranges)
    return {"metric": "supported_intervals", "value": text, "note": f"{len(ranges)} ten-fps high/medium interval(s)"}


def track_stats(rows: list[dict]) -> list[dict]:
    supported = supported_rows(rows)
    if len(supported) < 2:
        return [{"metric": "event_lane_track", "value": len(supported), "note": "fewer than two supported rows"}]

    total = 0.0
    rates = []
    for prev, curr in zip(supported, supported[1:]):
        dt = float(curr["approx_second"]) - float(prev["approx_second"])
        if dt <= 0:
            continue
        step = math.hypot(
            float(curr["target_center_x"]) - float(prev["target_center_x"]),
            float(curr["target_center_y"]) - float(prev["target_center_y"]),
        )
        total += step
        rates.append(step / dt)
    start = supported[0]
    end = supported[-1]
    dx = float(end["target_center_x"]) - float(start["target_center_x"])
    dy = float(end["target_center_y"]) - float(start["target_center_y"])
    net = math.hypot(dx, dy)
    duration = float(end["approx_second"]) - float(start["approx_second"])
    return [
        {
            "metric": "event_lane_track",
            "value": len(supported),
            "note": (
                f"{start['approx_second']}s-{end['approx_second']}s; net={net:.3f}px; path={total:.3f}px; "
                f"dx={dx:.3f}px; dy={dy:.3f}px; upward_displacement={-dy:.3f}px; "
                f"path_rate={(total / duration):.3f}px/s; median_step_rate={statistics.median(rates):.3f}px/s; "
                f"linearity={(net / total if total else 0.0):.3f}"
            ),
        },
        {"metric": "event_lane_horizontal_delta_px", "value": round(dx, 3), "note": "end center x minus start center x"},
        {"metric": "event_lane_vertical_delta_px", "value": round(dy, 3), "note": "end center y minus start center y; negative is upward"},
        {"metric": "event_lane_net_displacement_px", "value": round(net, 3), "note": "start-to-end image-plane displacement"},
        {"metric": "event_lane_path_length_px", "value": round(total, 3), "note": "sum of supported row-to-row image-plane steps"},
    ]


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


def write_summary(path: Path, rows: list[dict], fps: float, total_frames: int, duration: float, sample_rate: float) -> None:
    supported = supported_rows(rows)
    event_rows = [row for row in rows if row["is_dvids_event_window"] == "yes"]
    quality_counts = Counter(row["review_quality"] for row in rows)
    event_quality_counts = Counter(row["review_quality"] for row in event_rows)

    distances = [float(row["distance_from_expected_lane_px"]) for row in supported]
    areas = [float(row["component_area"]) for row in supported]
    widths = [float(row["bbox_w"]) for row in supported]
    heights = [float(row["bbox_h"]) for row in supported]
    brightness = [float(row["brightness_delta"]) for row in supported]
    contrast = [float(row["max_positive_contrast"]) for row in supported]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{sample_rate} fps full-clip review samples"},
        {"metric": "event_window_sample_count", "value": len(event_rows), "note": "samples in DVIDS 00:06-00:08 description window"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "event-window rows with usable target component"},
        supported_interval_summary(rows),
    ]
    summary_rows.extend(track_stats(rows))
    summary_rows.extend(
        [
            numeric_summary("distance_from_expected_lane_px", distances, "supported component distance from PR37 event lane"),
            numeric_summary("component_area", areas, "supported bright component pixel area after overlay/blackout suppression"),
            numeric_summary("bbox_width_px", widths, "supported component bounding-box width"),
            numeric_summary("bbox_height_px", heights, "supported component bounding-box height"),
            numeric_summary("brightness_delta_luma", brightness, "component max luma minus local median luma"),
            numeric_summary("max_positive_contrast_luma", contrast, "maximum luma over local median-background estimate"),
        ]
    )
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "all full-clip review rows"})
    for key, value in sorted(event_quality_counts.items()):
        summary_rows.append({"metric": f"event_quality_count: {key}", "value": value, "note": "DVIDS 00:06-00:08 event rows"})
    write_csv(path, ["metric", "value", "note"], summary_rows)


def run_pass(cap: cv2.VideoCapture, fps: float, total_frames: int, seconds: list[float]) -> tuple[list[dict], list[Path], list[Path]]:
    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "target-patches"
    for directory in [annotated_dir, patch_dir]:
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
        result = detect_target(frame, second)
        quality, caveat = classify_detection(result, second)
        phase, _anchor = phase_for(second)

        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, result, second, quality, phase), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, result, second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)
        rows.append(row_from_detection(sample_index, second, frame_index, result, quality, caveat, annotated_path, patch_path))
    return rows, annotated_paths, patch_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="PR37 bottom-to-top event-lane review for DOD_111689044.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=10.0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    seconds = sample_seconds(duration, args.sample_rate)

    rows, annotated_paths, patch_paths = run_pass(cap, fps, total_frames, seconds)
    cap.release()

    sheet_dir = OUT_ROOT / "sheets"
    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr37-annotated", cols=4, thumb_width=480)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr37-patches", cols=6, thumb_width=220)

    review_csv = Path("research/ufo-video-pr37-track-review-dod111689044.csv")
    summary_csv = Path("research/ufo-video-pr37-track-review-summary.csv")
    asset_csv = Path("research/ufo-video-pr37-track-review-assets.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)
    write_summary(summary_csv, rows, fps, total_frames, duration, args.sample_rate)

    asset_rows: list[dict] = [
        {"artifact_type": "track_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR37 ten-fps full-clip event-lane review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR37 event-lane review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR37 annotated event-lane sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR37 target patch sheet"})
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    quality_counts = Counter(row["review_quality"] for row in rows)
    event_quality_counts = Counter(row["review_quality"] for row in rows if row["is_dvids_event_window"] == "yes")
    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"event_quality_counts={dict(event_quality_counts)}")
    print(f"supported_high_or_medium={len(supported_rows(rows))}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

