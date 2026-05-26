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


VIDEO_ID = "DOD_111688954"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR28"
DVIDS_STATED_REPORT_ID = "DoW-UAP-D7"
CONTENT_REPORT_ID = "DoW-UAP-D25"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111688954.mp4"
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr28-d25-review") / VIDEO_ID

ROI_X0 = 245
ROI_Y0 = 95
ROI_X1 = 1665
ROI_Y1 = 960
RETICLE_X = 960.0
RETICLE_Y = 540.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def phase_for(second: float) -> tuple[str, str]:
    if second < 4.0:
        return "split-view startup", "DVIDS 00:00-00:03 split EO/SWIR display before target is called out"
    if second < 10.0:
        return "split-view initial contrast", "DVIDS 00:04 area of contrast becomes distinguishable in the split display"
    if second < 55.0:
        return "full-screen SWIR track", "DVIDS 00:10 full-screen SWIR feed; area of contrast generally remains in center field"
    if second < 56.0:
        return "late SWIR teardrop view", "DVIDS 00:55 area resembles inverted teardrop with vertical trailing mass"
    if second < 57.0:
        return "visible-spectrum loss", "DVIDS 00:56 visible-spectrum switch loses subject against background"
    return "SWIR black-hot non-reacquisition", "DVIDS 00:57-01:05 SWIR black-hot switch does not reacquire area of contrast"


def expected_center(second: float) -> tuple[float, float]:
    if second < 4.0:
        return 790.0, 445.0
    if second < 10.0:
        alpha = (second - 4.0) / 6.0
        return 760.0 + 210.0 * alpha, 420.0 + 35.0 * alpha
    if second < 30.0:
        alpha = (second - 10.0) / 20.0
        return 970.0 + 45.0 * alpha, 455.0
    if second < 56.0:
        alpha = (second - 30.0) / 26.0
        return 1015.0 - 80.0 * alpha, 455.0 + 155.0 * alpha
    return RETICLE_X, RETICLE_Y


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    orange_red = (hue <= 25) | (hue >= 168)
    green_cyan = (hue >= 35) & (hue <= 105)
    blue = (hue >= 100) & (hue <= 125)
    mask = ((sat > 45) & (val > 45) & (orange_red | green_cyan | blue)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def nearest_overlay_distance_from_mask(mask: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
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


def remove_line_artifacts(mask: np.ndarray) -> np.ndarray:
    horizontal = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((1, 27), np.uint8))
    vertical = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((27, 1), np.uint8))
    line_mask = cv2.dilate(cv2.bitwise_or(horizontal, vertical), np.ones((3, 3), np.uint8), iterations=1)
    return cv2.bitwise_and(mask, cv2.bitwise_not(line_mask))


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    overlay_clear = colored_overlay_mask(roi) == 0
    valid = overlay_clear & (gray > 28) & (hsv[:, :, 1] < 120)
    if int(valid.sum()) < 200:
        return roi, gray, np.zeros_like(gray, dtype=np.uint8), 0.0

    background = cv2.medianBlur(gray, 47)
    bright_delta = gray.astype(np.int16) - background.astype(np.int16)
    threshold = max(20.0, float(np.percentile(bright_delta[valid], 99.72)))
    raw = ((bright_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = remove_line_artifacts(raw)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return roi, gray, raw, threshold


def detect_candidates(frame: np.ndarray, second: float, limit: int = 20) -> list[dict]:
    _roi, gray, mask, threshold = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    overlay_mask = colored_overlay_mask(frame)
    expected_x, expected_y = expected_center(second)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 3 or area > 900:
            continue
        if w > 70 or h > 95:
            continue
        if w <= 1 or h <= 1:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 8.0 and min(w, h) <= 5:
            continue
        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        values = gray[labels == label]
        local_patch = gray[max(0, y - 26) : min(gray.shape[0], y + h + 26), max(0, x - 26) : min(gray.shape[1], x + w + 26)]
        local_median = float(np.median(local_patch)) if local_patch.size else float(np.median(gray))
        max_luma = int(values.max())
        min_luma = int(values.min())
        mean_luma = float(values.mean())
        contrast_delta = max_luma - local_median
        dist_expected = math.hypot(full_x - expected_x, full_y - expected_y)
        dist_reticle = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        fill = area / max(1, w * h)
        relation, nearest = nearest_overlay_distance_from_mask(overlay_mask, full_x, full_y)
        score = (
            contrast_delta * 4.5
            + min(area, 180) * 1.2
            + min(fill, 0.75) * 85.0
            + max_luma * 0.15
            - dist_expected * 0.36
            - max(0.0, aspect - 3.8) * 18.0
        )
        if relation.startswith("intersects"):
            score -= 80.0
        elif relation.startswith("near"):
            score -= 20.0
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
                "distance_from_expected_px": dist_expected,
                "distance_from_reticle_px": dist_reticle,
                "overlay_relation": relation,
                "nearest_overlay_px": nearest,
                "threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:limit]


def transition_penalty(prev: dict, curr: dict) -> float:
    dist = math.hypot(float(curr["center_x"]) - float(prev["center_x"]), float(curr["center_y"]) - float(prev["center_y"]))
    penalty = dist * 0.28
    if dist > 130:
        penalty += (dist - 130) * 0.75
    return penalty


def choose_contiguous_track(candidate_rows: list[list[dict]]) -> list[dict | None]:
    dp: list[list[float]] = []
    parent: list[list[int | None]] = []
    for row_index, candidates in enumerate(candidate_rows):
        if not candidates:
            dp.append([])
            parent.append([])
            continue
        scores = []
        parents = []
        for candidate in candidates:
            if row_index == 0 or not dp[row_index - 1]:
                scores.append(float(candidate["raw_score"]))
                parents.append(None)
                continue
            best_score = -1e12
            best_parent: int | None = None
            for prev_index, prev_candidate in enumerate(candidate_rows[row_index - 1]):
                score = dp[row_index - 1][prev_index] + float(candidate["raw_score"]) - transition_penalty(prev_candidate, candidate)
                if score > best_score:
                    best_score = score
                    best_parent = prev_index
            scores.append(best_score)
            parents.append(best_parent)
        dp.append(scores)
        parent.append(parents)

    track: list[dict | None] = [None] * len(candidate_rows)
    last_index: int | None = None
    for row_index in range(len(dp) - 1, -1, -1):
        if dp[row_index]:
            last_index = int(max(range(len(dp[row_index])), key=lambda idx: dp[row_index][idx]))
            break
    if last_index is None:
        return track

    for row_index in range(len(candidate_rows) - 1, -1, -1):
        if last_index is None or not candidate_rows[row_index]:
            track[row_index] = None
            continue
        track[row_index] = candidate_rows[row_index][last_index]
        last_index = parent[row_index][last_index]
    return track


def choose_track(candidate_rows: list[list[dict]]) -> list[dict | None]:
    track: list[dict | None] = [None] * len(candidate_rows)
    start: int | None = None
    for index, candidates in enumerate(candidate_rows + [[]]):
        if candidates and start is None:
            start = index
        if (not candidates) and start is not None:
            segment = candidate_rows[start:index]
            segment_track = choose_contiguous_track(segment)
            for offset, candidate in enumerate(segment_track):
                track[start + offset] = candidate
            start = None
    return track


def classify(candidate: dict | None, prev_supported: dict | None, second: float) -> tuple[str, str, float | None]:
    if candidate is None:
        return "none", "no compact bright contrast component survived filtering", None
    step = None
    if prev_supported is not None:
        step = math.hypot(float(candidate["center_x"]) - float(prev_supported["center_x"]), float(candidate["center_y"]) - float(prev_supported["center_y"]))

    contrast = float(candidate["contrast_delta"])
    area = int(candidate["area"])
    width = int(candidate["bbox_w"])
    height = int(candidate["bbox_h"])
    distance = float(candidate["distance_from_expected_px"])
    relation = str(candidate["overlay_relation"])

    if second >= 56.0:
        return "low", "post-modality-switch row; DVIDS says the subject is lost or not reacquired", step
    if second < 4.0:
        return "low", "startup row before DVIDS target callout", step
    if second < 10.0:
        if contrast >= 30 and area >= 4 and distance <= 260 and not relation.startswith("intersects"):
            return "medium", "split-view candidate aligned with DVIDS initial contrast callout", step
        return "low", "weak or background-confounded split-view candidate", step
    if contrast >= 38 and area >= 7 and width >= 2 and height >= 2 and distance <= 190 and not relation.startswith("intersects"):
        return "high", "compact SWIR bright-return candidate aligned with PR28/D25 phase description", step
    if contrast >= 24 and area >= 4 and distance <= 260 and not (relation.startswith("intersects") and area < 18):
        return "medium", "usable but weak, cloud-confounded, or overlay-adjacent SWIR candidate", step
    return "low", "weak, cloud-confounded, distant from expected lane, or overlay-adjacent candidate", step


def add_label(img: np.ndarray, text: str, width: int = 1280) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 38), (0, 0, 0), -1)
    cv2.putText(out, text, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, candidate: dict | None, second: float, quality: str, phase: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (80, 80, 80), 1)
    ex, ey = expected_center(second)
    cv2.drawMarker(out, (int(round(ex)), int(round(ey))), (255, 0, 0), markerType=cv2.MARKER_CROSS, markerSize=28, thickness=1)
    if candidate is not None:
        x0 = int(round(ROI_X0 + candidate["roi_x"]))
        y0 = int(round(ROI_Y0 + candidate["roi_y"]))
        x1 = x0 + int(candidate["bbox_w"])
        y1 = y0 + int(candidate["bbox_h"])
        color = (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255)
        cv2.rectangle(out, (x0, y0), (x1, y1), color, 2)
        center = (int(round(candidate["center_x"])), int(round(candidate["center_y"])))
        cv2.drawMarker(out, center, color, markerType=cv2.MARKER_CROSS, markerSize=32, thickness=2)
        cv2.line(out, (int(round(ex)), int(round(ey))), center, (255, 255, 0), 1)
    return add_label(out, f"{VIDEO_ID} t={second:05.1f}s PR28/D25 {phase}; quality={quality}")


def crop_patch(frame: np.ndarray, candidate: dict | None, second: float, size: int = 260) -> np.ndarray:
    h, w = frame.shape[:2]
    if candidate is not None:
        cx = int(round(candidate["center_x"]))
        cy = int(round(candidate["center_y"]))
    else:
        cx, cy = expected_center(second)
        cx = int(round(cx))
        cy = int(round(cy))
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(frame: np.ndarray, candidate: dict | None, second: float, quality: str) -> np.ndarray:
    patch = crop_patch(frame, candidate, second)
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


def run_pass(cap: cv2.VideoCapture, fps: float, total_frames: int, seconds: list[float], out_label: str) -> tuple[list[dict], list[Path], list[Path]]:
    frames: list[np.ndarray] = []
    frame_indices: list[int] = []
    candidate_rows: list[list[dict]] = []
    for second in seconds:
        frame_index = min(int(round(second * fps)), max(0, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        frames.append(frame)
        frame_indices.append(frame_index)
        candidate_rows.append(detect_candidates(frame, second))

    track = choose_track(candidate_rows)
    annotated_dir = OUT_ROOT / out_label / "annotated-frames"
    patch_dir = OUT_ROOT / out_label / "target-patches"
    for directory in [annotated_dir, patch_dir]:
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    previous_supported: dict | None = None
    for sample_index, (second, frame_index, frame, candidates, candidate) in enumerate(zip(seconds, frame_indices, frames, candidate_rows, track)):
        quality, caveat, step = classify(candidate, previous_supported, second)
        if quality in {"high", "medium"} and candidate is not None:
            previous_supported = candidate
        phase, anchor = phase_for(second)
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, candidate, second, quality, phase), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, candidate, second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)
        rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "dvids_stated_report_id": DVIDS_STATED_REPORT_ID,
                "content_report_id": CONTENT_REPORT_ID,
                "pass_label": out_label,
                "sample_index": sample_index,
                "approx_second": f"{second:.1f}",
                "source_frame_index": frame_index,
                "dvids_phase": phase,
                "dvids_anchor": anchor,
                "review_quality": quality,
                "candidate_count": len(candidates),
                "track_candidate_rank": "" if candidate is None else candidates.index(candidate) + 1,
                "target_center_x": "" if candidate is None else round(float(candidate["center_x"]), 1),
                "target_center_y": "" if candidate is None else round(float(candidate["center_y"]), 1),
                "bbox_x0": "" if candidate is None else round(float(ROI_X0 + candidate["roi_x"]), 1),
                "bbox_y0": "" if candidate is None else round(float(ROI_Y0 + candidate["roi_y"]), 1),
                "bbox_w": "" if candidate is None else int(candidate["bbox_w"]),
                "bbox_h": "" if candidate is None else int(candidate["bbox_h"]),
                "component_area": "" if candidate is None else int(candidate["area"]),
                "fill_ratio": "" if candidate is None else round(float(candidate["fill_ratio"]), 3),
                "component_max_luma": "" if candidate is None else int(candidate["max_luma"]),
                "component_min_luma": "" if candidate is None else int(candidate["min_luma"]),
                "component_mean_luma": "" if candidate is None else round(float(candidate["mean_luma"]), 2),
                "local_median_luma": "" if candidate is None else round(float(candidate["local_median_luma"]), 2),
                "contrast_delta": "" if candidate is None else round(float(candidate["contrast_delta"]), 2),
                "step_from_previous_supported_px": "" if step is None else round(float(step), 3),
                "distance_from_expected_px": "" if candidate is None else round(float(candidate["distance_from_expected_px"]), 2),
                "distance_from_reticle_px": "" if candidate is None else round(float(candidate["distance_from_reticle_px"]), 2),
                "overlay_relation": "" if candidate is None else candidate["overlay_relation"],
                "nearest_colored_overlay_px": "" if candidate is None or candidate.get("nearest_overlay_px") is None else round(float(candidate["nearest_overlay_px"]), 2),
                "detection_threshold": "" if candidate is None else round(float(candidate["threshold"]), 3),
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )
    return rows, annotated_paths, patch_paths


def supported_rows(rows: list[dict]) -> list[dict]:
    return [row for row in rows if row["review_quality"] in {"high", "medium"} and row["target_center_x"] != ""]


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


def supported_interval_summary(rows: list[dict], metric_name: str) -> dict:
    seconds = [float(row["approx_second"]) for row in supported_rows(rows)]
    if not seconds:
        return {"metric": metric_name, "value": "", "note": "no supported rows"}
    ranges: list[tuple[float, float, int]] = []
    start = seconds[0]
    prev = seconds[0]
    count = 1
    max_gap = 0.21 if rows and rows[0]["pass_label"] == "dense-swir-track" else 1.01
    for second in seconds[1:]:
        if second - prev > max_gap:
            ranges.append((start, prev, count))
            start = second
            count = 1
        else:
            count += 1
        prev = second
    ranges.append((start, prev, count))
    parts = [f"{s:.1f}s" if s == e else f"{s:.1f}s-{e:.1f}s" for s, e, _count in ranges]
    return {"metric": metric_name, "value": "; ".join(parts), "note": f"{len(ranges)} contiguous supported interval(s)"}


def track_stats(rows: list[dict], metric_name: str) -> dict:
    supported = supported_rows(rows)
    if len(supported) < 2:
        return {"metric": metric_name, "value": len(supported), "note": "fewer than two supported rows"}
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
        "metric": metric_name,
        "value": len(supported),
        "note": (
            f"{supported[0]['approx_second']}s-{supported[-1]['approx_second']}s; "
            f"net={net:.3f}px; path={total:.3f}px; "
            f"path_rate={(total / duration):.3f}px/s; median_step_rate={statistics.median(rates):.3f}px/s"
        ),
    }


def write_summary(path: Path, full_rows: list[dict], dense_rows: list[dict], fps: float, total_frames: int, duration: float, full_rate: float, dense_rate: float) -> None:
    full_supported = supported_rows(full_rows)
    dense_supported = supported_rows(dense_rows)
    all_supported = full_supported + dense_supported
    areas = [float(row["component_area"]) for row in all_supported]
    contrasts = [float(row["contrast_delta"]) for row in all_supported]
    expected_offsets = [float(row["distance_from_expected_px"]) for row in all_supported]
    reticle_offsets = [float(row["distance_from_reticle_px"]) for row in all_supported]
    dense_steps = [float(row["step_from_previous_supported_px"]) for row in dense_supported if row["step_from_previous_supported_px"] != ""]
    full_quality = Counter(row["review_quality"] for row in full_rows)
    dense_quality = Counter(row["review_quality"] for row in dense_rows)
    full_phase_supported = Counter(row["dvids_phase"] for row in full_supported)
    dense_phase_supported = Counter(row["dvids_phase"] for row in dense_supported)

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "dvids_stated_report_id", "value": DVIDS_STATED_REPORT_ID, "note": "DVIDS page label; retained as source-label discrepancy"},
        {"metric": "content_report_id", "value": CONTENT_REPORT_ID, "note": "matching War.gov/local written-report content lane"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "full_sample_count", "value": len(full_rows), "note": f"{full_rate} fps full-clip samples"},
        {"metric": "full_supported_high_or_medium_rows", "value": len(full_supported), "note": "full pass rows with usable compact contrast candidate before modality-loss cutoff"},
        supported_interval_summary(full_rows, "full_supported_intervals"),
        {"metric": "dense_sample_count", "value": len(dense_rows), "note": f"{dense_rate} fps samples from 10s to 56s"},
        {"metric": "dense_supported_high_or_medium_rows", "value": len(dense_supported), "note": "dense SWIR rows with usable compact contrast candidate"},
        supported_interval_summary(dense_rows, "dense_supported_intervals"),
        track_stats(full_rows, "full_target_center_track"),
        track_stats(dense_rows, "dense_target_center_track"),
        numeric_summary("component_area", areas, "tracked compact bright component pixel area"),
        numeric_summary("contrast_delta_luma", contrasts, "component max luma minus local median"),
        numeric_summary("distance_from_expected_px", expected_offsets, "distance from phase-specific expected target lane"),
        numeric_summary("distance_from_reticle_px", reticle_offsets, "distance from central reticle"),
        numeric_summary("dense_step_from_previous_supported_px", dense_steps, "0.2-second image-plane step between dense supported rows"),
    ]
    for key, value in sorted(full_quality.items()):
        summary_rows.append({"metric": f"full_quality_count: {key}", "value": value, "note": "full pass review quality"})
    for key, value in sorted(dense_quality.items()):
        summary_rows.append({"metric": f"dense_quality_count: {key}", "value": value, "note": "dense pass review quality"})
    for key, value in sorted(full_phase_supported.items()):
        summary_rows.append({"metric": f"full_supported_phase_count: {key}", "value": value, "note": "full pass supported rows by DVIDS phase"})
    for key, value in sorted(dense_phase_supported.items()):
        summary_rows.append({"metric": f"dense_supported_phase_count: {key}", "value": value, "note": "dense pass supported rows by DVIDS phase"})
    write_csv(path, ["metric", "value", "note"], summary_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="PR28/D25 visual review for DOD_111688954.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--full-sample-rate", type=float, default=1.0)
    parser.add_argument("--dense-sample-rate", type=float, default=5.0)
    parser.add_argument("--dense-start", type=float, default=10.0)
    parser.add_argument("--dense-end", type=float, default=56.0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    full_seconds = sample_seconds(duration, args.full_sample_rate, 0.0, duration)
    dense_seconds = sample_seconds(duration, args.dense_sample_rate, args.dense_start, args.dense_end)

    full_rows, full_annotated, full_patches = run_pass(cap, fps, total_frames, full_seconds, "full-clip")
    dense_rows, dense_annotated, dense_patches = run_pass(cap, fps, total_frames, dense_seconds, "dense-swir-track")
    cap.release()

    sheet_dir = OUT_ROOT / "sheets"
    full_sheets = write_contact_sheets(full_annotated, sheet_dir, f"{VIDEO_ID}-pr28-full-annotated", cols=5, thumb_width=384)
    full_patch_sheets = write_contact_sheets(full_patches, sheet_dir, f"{VIDEO_ID}-pr28-full-patches", cols=8, thumb_width=180)
    dense_sheets = write_contact_sheets(dense_annotated, sheet_dir, f"{VIDEO_ID}-pr28-dense-annotated", cols=5, thumb_width=384)
    dense_patch_sheets = write_contact_sheets(dense_patches, sheet_dir, f"{VIDEO_ID}-pr28-dense-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr28-d25-review-dod111688954.csv")
    dense_csv = Path("research/ufo-video-pr28-d25-review-dense.csv")
    summary_csv = Path("research/ufo-video-pr28-d25-review-summary.csv")
    write_csv(review_csv, list(full_rows[0].keys()), full_rows)
    write_csv(dense_csv, list(dense_rows[0].keys()), dense_rows)
    write_summary(summary_csv, full_rows, dense_rows, fps, total_frames, duration, args.full_sample_rate, args.dense_sample_rate)

    asset_rows: list[dict] = [
        {"artifact_type": "full_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR28/D25 one-fps full-clip review table"},
        {"artifact_type": "dense_review_csv", "path": str(dense_csv).replace("\\", "/"), "note": "PR28/D25 five-fps SWIR-track review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR28/D25 visual review summary"},
    ]
    for path in full_sheets:
        asset_rows.append({"artifact_type": "full_annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR28/D25 full-pass annotated sheet"})
    for path in full_patch_sheets:
        asset_rows.append({"artifact_type": "full_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR28/D25 full-pass target patch sheet"})
    for path in dense_sheets:
        asset_rows.append({"artifact_type": "dense_annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR28/D25 dense-pass annotated sheet"})
    for path in dense_patch_sheets:
        asset_rows.append({"artifact_type": "dense_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR28/D25 dense-pass target patch sheet"})
    asset_csv = Path("research/ufo-video-pr28-d25-review-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"full_samples={len(full_rows)} quality_counts={dict(Counter(row['review_quality'] for row in full_rows))}")
    print(f"dense_samples={len(dense_rows)} quality_counts={dict(Counter(row['review_quality'] for row in dense_rows))}")
    print(f"full_supported={len(supported_rows(full_rows))}")
    print(f"dense_supported={len(supported_rows(dense_rows))}")
    print(f"review_csv={review_csv}")
    print(f"dense_csv={dense_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

