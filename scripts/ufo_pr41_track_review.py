from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689083"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR41"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689083.mp4")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr41-track-review") / VIDEO_ID

ROI_X0 = 230
ROI_Y0 = 90
ROI_X1 = 1680
ROI_Y1 = 965
RETICLE_X = 960.0
RETICLE_Y = 548.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 1.0:
        return "pre-entry/startup", "Before DVIDS 00:01 entry description"
    if second < 2.0:
        return "left-side entry", "DVIDS 00:01 area of contrast enters from bottom third of left side"
    return "sensor pan/tracking", "DVIDS 00:02-01:34 sensor pans left-to-right while keeping area generally centered"


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 40) & (hue <= 115)
    mask = ((sat > 45) & (val > 45) & cyan_green).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def nearest_overlay_distance(frame: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(frame)
    return nearest_overlay_distance_from_mask(mask, x, y)


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
    horizontal = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((1, 25), np.uint8))
    vertical = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((25, 1), np.uint8))
    line_mask = cv2.dilate(cv2.bitwise_or(horizontal, vertical), np.ones((3, 3), np.uint8), iterations=1)
    return cv2.bitwise_and(mask, cv2.bitwise_not(line_mask))


def candidate_masks(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    overlay_clear = colored_overlay_mask(roi) == 0
    valid = overlay_clear & (gray > 28) & (gray < 242) & (hsv[:, :, 1] < 95)
    if int(valid.sum()) < 100:
        return roi, gray, np.zeros_like(gray, dtype=np.uint8), 0.0, 0.0

    bright_threshold = max(120.0, float(np.percentile(gray[valid], 99.82)))
    dark_threshold = float(np.percentile(gray[valid], 0.12))
    background = cv2.medianBlur(gray, 41)
    bright = ((gray >= bright_threshold) & valid & ((gray.astype(np.int16) - background.astype(np.int16)) >= 12)).astype(np.uint8) * 255
    dark = ((gray <= dark_threshold) & valid & ((background.astype(np.int16) - gray.astype(np.int16)) >= 16)).astype(np.uint8) * 255
    mask = cv2.bitwise_or(bright, dark)
    mask = cv2.medianBlur(mask, 3)
    mask = remove_line_artifacts(mask)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    return roi, gray, mask, bright_threshold, dark_threshold


def detect_candidates(frame: np.ndarray, second: float, limit: int = 18) -> list[dict]:
    _roi, gray, mask, bright_threshold, dark_threshold = candidate_masks(frame)
    overlay_mask = colored_overlay_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 2 or area > 160:
            continue
        if w > 28 or h > 28:
            continue
        if w <= 1 or h <= 1:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 5.5:
            continue
        values = gray[labels == label]
        max_luma = int(values.max())
        min_luma = int(values.min())
        mean_luma = float(values.mean())
        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        local_patch = gray[max(0, y - 18) : min(gray.shape[0], y + h + 18), max(0, x - 18) : min(gray.shape[1], x + w + 18)]
        local_median = float(np.median(local_patch)) if local_patch.size else float(np.median(gray))
        bright_delta = max_luma - local_median
        dark_delta = local_median - min_luma
        polarity = "bright" if bright_delta >= dark_delta else "dark"
        contrast_delta = max(bright_delta, dark_delta)
        frame_center_dist = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        # Favor compact high-contrast marks near the sensor's central tracking area,
        # but do not force the target onto the reticle.
        score = (
            contrast_delta * 4.0
            + min(area, 60) * 2.2
            + (max_luma if polarity == "bright" else 255 - min_luma) * 0.35
            - frame_center_dist * 0.055
            - max(0.0, aspect - 2.2) * 15.0
        )
        relation, nearest = nearest_overlay_distance_from_mask(overlay_mask, full_x, full_y)
        candidates.append(
            {
                "second": second,
                "label": label,
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "center_x": full_x,
                "center_y": full_y,
                "max_luma": max_luma,
                "min_luma": min_luma,
                "mean_luma": mean_luma,
                "local_median_luma": local_median,
                "bright_delta": bright_delta,
                "dark_delta": dark_delta,
                "contrast_delta": contrast_delta,
                "polarity": polarity,
                "distance_from_reticle_px": frame_center_dist,
                "overlay_relation": relation,
                "nearest_overlay_px": nearest,
                "bright_threshold": bright_threshold,
                "dark_threshold": dark_threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:limit]


def transition_penalty(prev: dict, curr: dict) -> float:
    dist = math.hypot(float(curr["center_x"]) - float(prev["center_x"]), float(curr["center_y"]) - float(prev["center_y"]))
    penalty = dist * 0.32
    if dist > 140:
        penalty += (dist - 140) * 0.9
    return penalty


def choose_track(candidate_rows: list[list[dict]]) -> list[dict | None]:
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
                prev_score = dp[row_index - 1][prev_index]
                score = prev_score + float(candidate["raw_score"]) - transition_penalty(prev_candidate, candidate)
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


def classify(candidate: dict | None, prev: dict | None, second: float) -> tuple[str, str, float | None]:
    if candidate is None:
        return "none", "no compact contrast candidate survived filtering", None
    contrast = float(candidate["contrast_delta"])
    area = int(candidate["area"])
    width = int(candidate["bbox_w"])
    height = int(candidate["bbox_h"])
    relation = str(candidate["overlay_relation"])
    step = None
    if prev is not None:
        step = math.hypot(float(candidate["center_x"]) - float(prev["center_x"]), float(candidate["center_y"]) - float(prev["center_y"]))

    if second < 2.0:
        if contrast >= 28 and area >= 4:
            return "medium", "entry/startup contrast candidate; target is not yet cleanly separated", step
        return "low", "pre-entry or weak startup row", step
    if contrast >= 45 and area >= 8 and width >= 2 and height >= 2 and (step is None or step <= 115) and not relation.startswith("intersects"):
        return "high", "compact contrast candidate on smooth sensor-tracked lane", step
    if contrast >= 26 and area >= 3 and (step is None or step <= 165):
        return "medium", "usable but weak, background-confounded, or less smooth contrast candidate", step
    return "low", "weak, background-confounded, overlay-adjacent, or discontinuous contrast candidate", step


def add_label(img: np.ndarray, text: str, width: int = 1260) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 38), (0, 0, 0), -1)
    cv2.putText(out, text, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, candidate: dict | None, second: float, quality: str, phase: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (80, 80, 80), 1)
    if candidate is not None:
        x0 = int(round(ROI_X0 + candidate["roi_x"]))
        y0 = int(round(ROI_Y0 + candidate["roi_y"]))
        x1 = x0 + int(candidate["bbox_w"])
        y1 = y0 + int(candidate["bbox_h"])
        color = (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255)
        cv2.rectangle(out, (x0, y0), (x1, y1), color, 2)
        center = (int(round(candidate["center_x"])), int(round(candidate["center_y"])))
        cv2.drawMarker(out, center, color, markerType=cv2.MARKER_CROSS, markerSize=30, thickness=2)
        cv2.line(out, (int(round(RETICLE_X)), int(round(RETICLE_Y))), center, (255, 255, 0), 1)
    label = f"{VIDEO_ID} t={second:05.1f}s PR41 {phase}; quality={quality}"
    return add_label(out, label)


def crop_patch(frame: np.ndarray, candidate: dict | None, size: int = 220) -> np.ndarray:
    h, w = frame.shape[:2]
    if candidate is not None:
        cx = int(round(candidate["center_x"]))
        cy = int(round(candidate["center_y"]))
    else:
        cx = int(round(RETICLE_X))
        cy = int(round(RETICLE_Y))
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(frame: np.ndarray, candidate: dict | None, second: float, quality: str) -> np.ndarray:
    patch = crop_patch(frame, candidate)
    out = cv2.resize(patch, (440, 440), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (220, 220), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=36, thickness=2)
    cv2.circle(out, (220, 220), 48, (0, 0, 255), 2)
    return add_label(out, f"{VIDEO_ID} t={second:05.1f}s quality={quality}", width=440)


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
    return [row for row in rows if row["review_quality"] in {"high", "medium"} and row["target_center_x"] != ""]


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
        step = math.hypot(
            float(curr["target_center_x"]) - float(prev["target_center_x"]),
            float(curr["target_center_y"]) - float(prev["target_center_y"]),
        )
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


def supported_interval_summary(rows: list[dict]) -> dict:
    supported_seconds = [float(row["approx_second"]) for row in supported_rows(rows)]
    if not supported_seconds:
        return {"metric": "supported_intervals", "value": "", "note": "no supported rows"}
    ranges: list[tuple[float, float, int]] = []
    start = supported_seconds[0]
    prev = supported_seconds[0]
    count = 1
    for second in supported_seconds[1:]:
        if second - prev > 1.01:
            ranges.append((start, prev, count))
            start = second
            count = 1
        else:
            count += 1
        prev = second
    ranges.append((start, prev, count))
    text_parts = []
    for start, end, _count in ranges:
        if start == end:
            text_parts.append(f"{start:.1f}s")
        else:
            text_parts.append(f"{start:.1f}s-{end:.1f}s")
    return {
        "metric": "supported_intervals",
        "value": "; ".join(text_parts),
        "note": f"{len(ranges)} one-fps contiguous supported interval(s)",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="PR41 single tracked contrast review for DOD_111689083.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=1.0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    seconds = []
    sample_count = int(math.floor(duration * args.sample_rate)) + 1
    for sample_index in range(sample_count):
        second = round(sample_index / args.sample_rate, 3)
        if second <= duration:
            seconds.append(second)

    frames: list[np.ndarray] = []
    candidate_rows: list[list[dict]] = []
    frame_indices: list[int] = []
    for second in seconds:
        frame_index = min(int(round(second * fps)), max(0, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        frames.append(frame)
        frame_indices.append(frame_index)
        candidate_rows.append(detect_candidates(frame, second))
    cap.release()

    track = choose_track(candidate_rows)
    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "target-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    previous_supported: dict | None = None
    for sample_index, (second, frame_index, frame, candidates, candidate) in enumerate(zip(seconds, frame_indices, frames, candidate_rows, track)):
        quality, caveat, step = classify(candidate, previous_supported, second)
        if quality in {"high", "medium"} and candidate is not None:
            previous_supported = candidate
        phase, anchor = dvids_phase(second)
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, candidate, second, quality, phase), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, candidate, second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)
        row = {
            "video": VIDEO_NAME,
            "release_id": RELEASE_ID,
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
            "polarity": "" if candidate is None else candidate["polarity"],
            "component_max_luma": "" if candidate is None else int(candidate["max_luma"]),
            "component_min_luma": "" if candidate is None else int(candidate["min_luma"]),
            "component_mean_luma": "" if candidate is None else round(float(candidate["mean_luma"]), 2),
            "local_median_luma": "" if candidate is None else round(float(candidate["local_median_luma"]), 2),
            "bright_delta": "" if candidate is None else round(float(candidate["bright_delta"]), 2),
            "dark_delta": "" if candidate is None else round(float(candidate["dark_delta"]), 2),
            "contrast_delta": "" if candidate is None else round(float(candidate["contrast_delta"]), 2),
            "step_from_previous_supported_px": "" if step is None else round(float(step), 3),
            "distance_from_reticle_px": "" if candidate is None else round(float(candidate["distance_from_reticle_px"]), 2),
            "overlay_relation": "" if candidate is None else candidate["overlay_relation"],
            "nearest_colored_overlay_px": "" if candidate is None or candidate.get("nearest_overlay_px") is None else round(float(candidate["nearest_overlay_px"]), 2),
            "caveat": caveat,
            "annotated_frame_path": str(annotated_path).replace("\\", "/"),
            "zoom_patch_path": str(patch_path).replace("\\", "/"),
        }
        rows.append(row)

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr41-track-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr41-track-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr41-track-review-dod111689083.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    supported = supported_rows(rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    phase_supported_counts = Counter(row["dvids_phase"] for row in supported)
    polarity_counts = Counter(row["polarity"] for row in supported if row["polarity"])
    overlay_counts = Counter(row["overlay_relation"] for row in rows if row["overlay_relation"])
    areas = [float(row["component_area"]) for row in supported]
    contrasts = [float(row["contrast_delta"]) for row in supported]
    reticle_offsets = [float(row["distance_from_reticle_px"]) for row in supported]
    steps = [float(row["step_from_previous_supported_px"]) for row in supported if row["step_from_previous_supported_px"] != ""]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps review samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable compact contrast candidate"},
        supported_interval_summary(rows),
        track_stats(rows),
        numeric_summary("component_area", areas, "tracked compact contrast-component pixel area"),
        numeric_summary("contrast_delta_luma", contrasts, "max bright/dark local contrast delta"),
        numeric_summary("distance_from_reticle_px", reticle_offsets, "distance from central reticle to tracked candidate"),
        numeric_summary("step_from_previous_supported_px", steps, "one-second image-plane step between supported rows"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "review quality"})
    for key, value in sorted(phase_supported_counts.items()):
        summary_rows.append({"metric": f"supported_phase_count: {key}", "value": value, "note": "supported rows by DVIDS phase"})
    for key, value in sorted(polarity_counts.items()):
        summary_rows.append({"metric": f"polarity_count: {key}", "value": value, "note": "tracked candidate polarity"})
    for key, value in sorted(overlay_counts.items()):
        summary_rows.append({"metric": f"overlay_count: {key}", "value": value, "note": "candidate relation to colored overlay"})

    summary_csv = Path("research/ufo-video-pr41-track-review-summary.csv")
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "track_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR41 one-fps dynamic compact-contrast track table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR41 track review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR41 annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR41 target patch sheet"})
    asset_csv = Path("research/ufo-video-pr41-track-review-assets.csv")
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

