from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689123"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR45"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689123.mp4")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr45-size-exit-review") / VIDEO_ID

SEARCH_X0 = 680
SEARCH_Y0 = 280
SEARCH_X1 = 1330
SEARCH_Y1 = 825


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def phase_for(second: float) -> tuple[str, str]:
    if second < 4.0:
        return "reticle-lock acquisition", "DVIDS 00:00-00:03 tracks area of contrast while acquiring reticle lock"
    if second < 31.0:
        return "increasing distinctiveness pre-zoom", "DVIDS 00:04-00:30 area of contrast gradually increases in distinctiveness"
    if second < 32.0:
        return "field-of-view narrows", "DVIDS 00:31 sensor narrows field of view to zoom"
    if second < 57.0:
        return "post-zoom apparent size increase", "DVIDS 00:32-00:56 area increases in apparent size and distinctiveness"
    return "exit from field of view", "DVIDS 00:57-00:58 target leaves center and exits bottom-right"


def expected_center(second: float) -> tuple[float, float]:
    # The public description and source video show a centered track through 56s, then a
    # rapid lower-right exit. This prediction is only used to rank ambiguous image blobs.
    if second < 55.5:
        return 960.0, 548.0
    alpha = min(1.0, max(0.0, (second - 55.5) / 3.0))
    return 960.0 + 190.0 * alpha, 548.0 + 210.0 * alpha


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    green = (hue >= 40) & (hue <= 90)
    magenta = (hue >= 125) & (hue <= 165)
    red_or_orange = (hue <= 20) | (hue >= 170)
    mask = ((sat > 55) & (val > 45) & (green | magenta | red_or_orange)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def remove_line_artifacts(mask: np.ndarray) -> np.ndarray:
    horizontal = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((1, 31), np.uint8))
    vertical = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((31, 1), np.uint8))
    line_mask = cv2.dilate(cv2.bitwise_or(horizontal, vertical), np.ones((3, 3), np.uint8), iterations=1)
    return cv2.bitwise_and(mask, cv2.bitwise_not(line_mask))


def nearest_overlay_distance(frame: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(frame)
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


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    roi = frame[SEARCH_Y0:SEARCH_Y1, SEARCH_X0:SEARCH_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    overlay_clear = colored_overlay_mask(roi) == 0
    not_blackout = gray > 22
    low_sat = hsv[:, :, 1] < 95
    valid = overlay_clear & not_blackout & low_sat
    if int(valid.sum()) < 50:
        return roi, gray, valid, np.zeros_like(gray, dtype=np.uint8), 0.0, 0.0

    background = cv2.medianBlur(gray, 35)
    contrast = cv2.absdiff(gray, background)
    values = contrast[valid]
    local_median = float(np.median(gray[valid]))
    threshold = max(15.0, float(np.percentile(values, 98.8)))
    raw = ((contrast >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = remove_line_artifacts(raw)
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return roi, gray, valid, raw, threshold, local_median


def detect_target(frame: np.ndarray, second: float) -> dict:
    roi, gray, valid, mask, threshold, local_median = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    expected_x, expected_y = expected_center(second)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 3 or area > 8500:
            continue
        if w > 210 or h > 180:
            continue
        if w <= 2 or h <= 2:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 7.0 and min(w, h) <= 6:
            continue
        cx, cy = centroids[label]
        full_x = SEARCH_X0 + float(cx)
        full_y = SEARCH_Y0 + float(cy)
        values = gray[labels == label]
        max_luma = int(values.max())
        min_luma = int(values.min())
        mean_luma = float(values.mean())
        brightness_delta = max_luma - local_median
        darkness_delta = local_median - min_luma
        dist = math.hypot(full_x - expected_x, full_y - expected_y)
        fill = area / max(1, w * h)
        score = (
            area * 0.75
            + max(brightness_delta, darkness_delta) * 3.0
            + max_luma * 0.35
            + min(fill, 0.7) * 90.0
            - dist * 0.65
            - max(0.0, aspect - 3.2) * 18.0
        )
        candidates.append(
            {
                "label": label,
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "fill_ratio": fill,
                "max_luma": max_luma,
                "min_luma": min_luma,
                "mean_luma": mean_luma,
                "brightness_delta": brightness_delta,
                "darkness_delta": darkness_delta,
                "center_x": full_x,
                "center_y": full_y,
                "distance_from_prediction": dist,
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
    x1 = x0 + best["bbox_w"]
    y1 = y0 + best["bbox_h"]
    relation, nearest = nearest_overlay_distance(frame, best["center_x"], best["center_y"])
    return {
        "detected": True,
        "candidate_count": len(candidates),
        "threshold": round(threshold, 3),
        "local_median_luma": round(local_median, 3),
        "center_x": best["center_x"],
        "center_y": best["center_y"],
        "bbox_x0": x0,
        "bbox_y0": y0,
        "bbox_x1": x1,
        "bbox_y1": y1,
        "bbox_w": best["bbox_w"],
        "bbox_h": best["bbox_h"],
        "component_area": best["area"],
        "fill_ratio": best["fill_ratio"],
        "max_luma": best["max_luma"],
        "min_luma": best["min_luma"],
        "mean_luma": best["mean_luma"],
        "brightness_delta": best["brightness_delta"],
        "darkness_delta": best["darkness_delta"],
        "distance_from_prediction": best["distance_from_prediction"],
        "overlay_relation": relation,
        "nearest_overlay_px": nearest,
    }


def classify_detection(result: dict, second: float) -> tuple[str, str]:
    if not result.get("detected"):
        return "none", "no contrast component survived overlay/line suppression"
    area = int(result["component_area"])
    width = int(result["bbox_w"])
    height = int(result["bbox_h"])
    contrast = max(float(result["brightness_delta"]), float(result["darkness_delta"]))
    distance = float(result["distance_from_prediction"])
    relation = str(result["overlay_relation"])
    if second >= 58.4 and width <= 8:
        return "low", "post-exit lock-box edge or mostly out-of-frame residual"
    if second >= 58.2 and area < 65:
        return "low", "post-exit or mostly out-of-frame weak residual"
    if area >= 55 and width >= 8 and height >= 7 and contrast >= 35 and distance <= 110 and not relation.startswith("intersects"):
        return "high", "compact contrast component near expected PR45 track"
    if area >= 20 and width >= 5 and height >= 5 and contrast >= 24 and distance <= 170:
        return "medium", "usable but small, reticle-adjacent, or partly occluded contrast component"
    return "low", "weak, line-adjacent, far from expected track, or poorly separated contrast component"


def add_label(img: np.ndarray, text: str, width: int = 1260) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 38), (0, 0, 0), -1)
    cv2.putText(out, text, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, result: dict, second: float, quality: str, phase: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (SEARCH_X0, SEARCH_Y0), (SEARCH_X1, SEARCH_Y1), (80, 80, 80), 1)
    expected_x, expected_y = expected_center(second)
    cv2.drawMarker(out, (int(round(expected_x)), int(round(expected_y))), (255, 0, 0), markerType=cv2.MARKER_CROSS, markerSize=26, thickness=1)
    if result.get("detected"):
        x0 = int(round(result["bbox_x0"]))
        y0 = int(round(result["bbox_y0"]))
        x1 = int(round(result["bbox_x1"]))
        y1 = int(round(result["bbox_y1"]))
        color = (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255)
        cv2.rectangle(out, (x0, y0), (x1, y1), color, 2)
        center = (int(round(result["center_x"])), int(round(result["center_y"])))
        cv2.drawMarker(out, center, color, markerType=cv2.MARKER_CROSS, markerSize=32, thickness=2)
        cv2.line(out, (int(round(expected_x)), int(round(expected_y))), center, (255, 255, 0), 1)
    label = f"{VIDEO_ID} t={second:05.1f}s PR45 {phase}; quality={quality}"
    return add_label(out, label)


def crop_patch(frame: np.ndarray, result: dict, second: float, size: int = 260) -> np.ndarray:
    h, w = frame.shape[:2]
    if result.get("detected"):
        cx = int(round(result["center_x"]))
        cy = int(round(result["center_y"]))
    else:
        cx, cy = expected_center(second)
        cx = int(round(cx))
        cy = int(round(cy))
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(frame: np.ndarray, result: dict, second: float, quality: str) -> np.ndarray:
    patch = crop_patch(frame, result, second)
    out = cv2.resize(patch, (520, 520), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (260, 260), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=40, thickness=2)
    cv2.circle(out, (260, 260), 58, (0, 0, 255), 2)
    return add_label(out, f"{VIDEO_ID} t={second:05.1f}s quality={quality}", width=520)


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


def sample_seconds(duration: float, rate: float, start: float, end: float) -> list[float]:
    last = min(duration, end)
    seconds: list[float] = []
    index = 0
    while True:
        second = round(start + index / rate, 3)
        if second > last + 1e-6:
            break
        seconds.append(second)
        index += 1
    return seconds


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
    return {
        "video": VIDEO_NAME,
        "release_id": RELEASE_ID,
        "sample_index": sample_index,
        "approx_second": f"{second:.1f}",
        "source_frame_index": frame_index,
        "dvids_phase": phase,
        "dvids_anchor": anchor,
        "review_quality": quality,
        "candidate_count": result.get("candidate_count", 0),
        "contrast_threshold": result.get("threshold", ""),
        "local_median_luma": result.get("local_median_luma", ""),
        "target_center_x": "" if not result.get("detected") else round(float(result["center_x"]), 1),
        "target_center_y": "" if not result.get("detected") else round(float(result["center_y"]), 1),
        "bbox_x0": "" if not result.get("detected") else round(float(result["bbox_x0"]), 1),
        "bbox_y0": "" if not result.get("detected") else round(float(result["bbox_y0"]), 1),
        "bbox_w": "" if not result.get("detected") else int(result["bbox_w"]),
        "bbox_h": "" if not result.get("detected") else int(result["bbox_h"]),
        "component_area": "" if not result.get("detected") else int(result["component_area"]),
        "fill_ratio": "" if not result.get("detected") else round(float(result["fill_ratio"]), 3),
        "component_max_luma": "" if not result.get("detected") else int(result["max_luma"]),
        "component_min_luma": "" if not result.get("detected") else int(result["min_luma"]),
        "component_mean_luma": "" if not result.get("detected") else round(float(result["mean_luma"]), 2),
        "brightness_delta": "" if not result.get("detected") else round(float(result["brightness_delta"]), 2),
        "darkness_delta": "" if not result.get("detected") else round(float(result["darkness_delta"]), 2),
        "distance_from_prediction_px": "" if not result.get("detected") else round(float(result["distance_from_prediction"]), 2),
        "overlay_relation": result.get("overlay_relation", ""),
        "nearest_colored_overlay_px": "" if result.get("nearest_overlay_px") is None else round(float(result["nearest_overlay_px"]), 2),
        "caveat": caveat,
        "annotated_frame_path": str(annotated_path).replace("\\", "/"),
        "zoom_patch_path": str(patch_path).replace("\\", "/"),
    }


def run_pass(cap: cv2.VideoCapture, fps: float, total_frames: int, seconds: list[float], out_label: str) -> tuple[list[dict], list[Path], list[Path]]:
    annotated_dir = OUT_ROOT / out_label / "annotated-frames"
    patch_dir = OUT_ROOT / out_label / "target-patches"
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


def supported_rows(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["review_quality"] in {"high", "medium"} and row["component_area"] != ""]


def phase_counts(rows: list[dict]) -> Counter:
    return Counter(row["dvids_phase"] for row in supported_rows(rows))


def scale_change_row(rows: list[dict], start_second: float, end_second: float, metric: str) -> dict:
    supported = supported_rows(rows)
    start = [row for row in supported if abs(float(row["approx_second"]) - start_second) <= 1.0]
    end = [row for row in supported if abs(float(row["approx_second"]) - end_second) <= 1.0]
    if not start or not end:
        return {"metric": f"{metric}_change", "value": "", "note": "missing start or end supported rows"}
    start_value = statistics.median(float(row[metric]) for row in start)
    end_value = statistics.median(float(row[metric]) for row in end)
    ratio = end_value / start_value if start_value else 0.0
    return {
        "metric": f"{metric}_change",
        "value": round(ratio, 3),
        "note": f"median near {start_second:.0f}s={start_value:.3f}; median near {end_second:.0f}s={end_value:.3f}; ratio=end/start",
    }


def track_stats(rows: list[dict]) -> dict:
    detected = supported_rows(rows)
    if len(detected) < 2:
        return {"metric": "target_center_track", "value": len(detected), "note": "fewer than two supported rows"}
    total = 0.0
    rates = []
    for prev, curr in zip(detected, detected[1:]):
        dt = float(curr["approx_second"]) - float(prev["approx_second"])
        if dt <= 0:
            continue
        step = math.hypot(
            float(curr["target_center_x"]) - float(prev["target_center_x"]),
            float(curr["target_center_y"]) - float(prev["target_center_y"]),
        )
        total += step
        rates.append(step / dt)
    net = math.hypot(
        float(detected[-1]["target_center_x"]) - float(detected[0]["target_center_x"]),
        float(detected[-1]["target_center_y"]) - float(detected[0]["target_center_y"]),
    )
    duration = float(detected[-1]["approx_second"]) - float(detected[0]["approx_second"])
    return {
        "metric": "target_center_track",
        "value": len(detected),
        "note": (
            f"{detected[0]['approx_second']}s-{detected[-1]['approx_second']}s; "
            f"net={net:.3f}px; path={total:.3f}px; "
            f"path_rate={(total / duration):.3f}px/s; median_step_rate={statistics.median(rates):.3f}px/s"
        ),
    }


def write_summary(
    path: Path,
    rows: list[dict],
    exit_rows: list[dict],
    fps: float,
    total_frames: int,
    duration: float,
    full_rate: float,
    exit_rate: float,
) -> None:
    supported = supported_rows(rows)
    supported_exit = supported_rows(exit_rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    exit_quality_counts = Counter(row["review_quality"] for row in exit_rows)
    overlay_counts = Counter(row["overlay_relation"] for row in rows if row["overlay_relation"])

    areas = [float(row["component_area"]) for row in supported]
    widths = [float(row["bbox_w"]) for row in supported]
    heights = [float(row["bbox_h"]) for row in supported]
    brightness = [float(row["brightness_delta"]) for row in supported]
    distances = [float(row["distance_from_prediction_px"]) for row in supported]
    exit_seconds = [float(row["approx_second"]) for row in supported_exit]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{full_rate} fps full-clip review samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable contrast component"},
        {"metric": "exit_window_sample_count", "value": len(exit_rows), "note": f"{exit_rate} fps review samples from 54s to video end"},
        {"metric": "exit_window_supported_rows", "value": len(supported_exit), "note": "usable contrast component during exit-window pass"},
        {
            "metric": "exit_window_supported_interval",
            "value": "" if not exit_seconds else f"{min(exit_seconds):.1f}s-{max(exit_seconds):.1f}s",
            "note": "last dense supported target interval before disappearance or occlusion",
        },
        track_stats(rows),
        scale_change_row(rows, 4.0, 30.0, "component_area"),
        scale_change_row(rows, 32.0, 56.0, "component_area"),
        scale_change_row(rows, 4.0, 56.0, "component_area"),
        numeric_summary("component_area", areas, "detected contrast-component pixel area after overlay/line suppression"),
        numeric_summary("bbox_width_px", widths, "detected component bounding-box width"),
        numeric_summary("bbox_height_px", heights, "detected component bounding-box height"),
        numeric_summary("brightness_delta_luma", brightness, "component max luma minus local median"),
        numeric_summary("distance_from_prediction_px", distances, "distance from the phase-specific expected target lane"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "full-clip review quality"})
    for key, value in sorted(exit_quality_counts.items()):
        summary_rows.append({"metric": f"exit_quality_count: {key}", "value": value, "note": "exit-window review quality"})
    for key, value in sorted(overlay_counts.items()):
        summary_rows.append({"metric": f"overlay_count: {key}", "value": value, "note": "full-clip target relation to colored overlay"})
    for key, value in sorted(phase_counts(rows).items()):
        summary_rows.append({"metric": f"supported_phase_count: {key}", "value": value, "note": "full-clip supported rows by DVIDS phase"})
    write_csv(path, ["metric", "value", "note"], summary_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="PR45 apparent-size and exit review for DOD_111689123.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--full-sample-rate", type=float, default=1.0)
    parser.add_argument("--exit-sample-rate", type=float, default=5.0)
    parser.add_argument("--exit-start", type=float, default=54.0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    full_seconds = sample_seconds(duration, args.full_sample_rate, 0.0, duration)
    exit_seconds = sample_seconds(duration, args.exit_sample_rate, args.exit_start, duration)

    full_rows, full_annotated, full_patches = run_pass(cap, fps, total_frames, full_seconds, "full-clip")
    exit_rows, exit_annotated, exit_patches = run_pass(cap, fps, total_frames, exit_seconds, "exit-window")
    cap.release()

    sheet_dir = OUT_ROOT / "sheets"
    full_sheets = write_contact_sheets(full_annotated, sheet_dir, f"{VIDEO_ID}-pr45-full-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(full_patches, sheet_dir, f"{VIDEO_ID}-pr45-full-patches", cols=8, thumb_width=180)
    exit_sheets = write_contact_sheets(exit_annotated, sheet_dir, f"{VIDEO_ID}-pr45-exit-annotated", cols=5, thumb_width=384)
    exit_patch_sheets = write_contact_sheets(exit_patches, sheet_dir, f"{VIDEO_ID}-pr45-exit-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr45-size-exit-review-dod111689123.csv")
    exit_csv = Path("research/ufo-video-pr45-size-exit-review-exit-window.csv")
    summary_csv = Path("research/ufo-video-pr45-size-exit-review-summary.csv")
    write_csv(review_csv, list(full_rows[0].keys()), full_rows)
    write_csv(exit_csv, list(exit_rows[0].keys()), exit_rows)
    write_summary(summary_csv, full_rows, exit_rows, fps, total_frames, duration, args.full_sample_rate, args.exit_sample_rate)

    asset_rows: list[dict] = [
        {"artifact_type": "size_exit_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR45 one-fps full-clip size/exit review table"},
        {"artifact_type": "exit_window_csv", "path": str(exit_csv).replace("\\", "/"), "note": "PR45 five-fps exit-window review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR45 size/exit review summary"},
    ]
    for path in full_sheets:
        asset_rows.append({"artifact_type": "full_annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR45 full-clip annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "full_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR45 full-clip target patch sheet"})
    for path in exit_sheets:
        asset_rows.append({"artifact_type": "exit_annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR45 dense exit-window annotated sheet"})
    for path in exit_patch_sheets:
        asset_rows.append({"artifact_type": "exit_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR45 dense exit-window patch sheet"})
    asset_csv = Path("research/ufo-video-pr45-size-exit-review-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"full_samples={len(full_rows)} quality_counts={dict(Counter(row['review_quality'] for row in full_rows))}")
    print(f"exit_samples={len(exit_rows)} quality_counts={dict(Counter(row['review_quality'] for row in exit_rows))}")
    print(f"review_csv={review_csv}")
    print(f"exit_csv={exit_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

