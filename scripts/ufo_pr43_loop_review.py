from __future__ import annotations

import argparse
import bisect
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source-files-not-included"


VIDEO_ID = "DOD_111689759"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR43"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111689759.mp4"
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr43-loop-review") / VIDEO_ID


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 35) & (hue <= 115)
    mask = ((sat > 35) & (val > 35) & cyan_green).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def valid_scene_mask(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = (gray >= 24) & (colored_overlay_mask(frame) == 0)
    mask[:80, :] = False
    mask[-45:, :] = False
    mask[:, :40] = False
    mask[:, -40:] = False
    return mask.astype(np.uint8) * 255


def read_video_frames(video: Path) -> tuple[list[np.ndarray], float, int, float]:
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps
    frames: list[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    cap.release()
    return frames, fps, total_frames, duration


def frame_diff_score(prev: np.ndarray, curr: np.ndarray) -> float:
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
    mask = (valid_scene_mask(prev) > 0) & (valid_scene_mask(curr) > 0)
    if int(mask.sum()) < 1000:
        return 0.0
    diff = cv2.absdiff(prev_gray, curr_gray)
    return float(diff[mask].mean())


def detect_loop_boundaries(frames: list[np.ndarray], fps: float) -> tuple[list[int], list[dict]]:
    if len(frames) < 3:
        return [0, len(frames)], []
    diffs = [0.0]
    for index in range(1, len(frames)):
        diffs.append(frame_diff_score(frames[index - 1], frames[index]))

    min_gap = max(1, int(round(fps * 2.45)))
    peak_order = sorted(range(1, len(diffs)), key=lambda i: diffs[i], reverse=True)
    reset_frames: list[int] = []
    for frame_index in peak_order:
        if len(reset_frames) >= 4:
            break
        if diffs[frame_index] < 1.0:
            break
        if all(abs(frame_index - existing) >= min_gap for existing in reset_frames):
            reset_frames.append(frame_index)
    reset_frames.sort()

    boundaries = [0] + reset_frames
    if boundaries[-1] != len(frames):
        boundaries.append(len(frames))

    rows = []
    for loop_index, start_frame in enumerate(boundaries[:-1]):
        end_frame = boundaries[loop_index + 1]
        reset_score = diffs[start_frame] if start_frame < len(diffs) else ""
        rows.append(
            {
                "loop_index": loop_index,
                "start_frame": start_frame,
                "start_second": round(start_frame / fps, 3),
                "end_frame_exclusive": end_frame,
                "end_second": round(end_frame / fps, 3),
                "loop_duration_seconds": round((end_frame - start_frame) / fps, 3),
                "start_reset_mean_absdiff": "" if loop_index == 0 else round(float(reset_score), 6),
            }
        )
    return boundaries, rows


def dvids_phase(cycle_second: float) -> tuple[str, str]:
    if cycle_second <= 2.0:
        return (
            "stated two-second observation",
            "DVIDS 00:00-00:02: small, barely distinguishable area of contrast moves left-to-right and exits from bottom-right quarter",
        )
    return "loop tail/reset padding", "DVIDS says the clip is looped for viewing; local cycle contains post-observation/reset padding"


def expected_lane(cycle_second: float) -> tuple[float, float] | None:
    if cycle_second < 0.0 or cycle_second > 2.35:
        return None
    alpha = min(max(cycle_second / 2.25, 0.0), 1.0)
    # Approximate DVIDS-described image-plane lane, anchored by the left-edge
    # residual and the lower-right residuals visible in the first loop.
    return 115.0 + (1180.0 - 115.0) * alpha, 425.0 + (930.0 - 425.0) * alpha


def compensated_residual_candidates(prev: np.ndarray, curr: np.ndarray, cycle_second: float, limit: int = 18) -> list[dict]:
    prev_gray = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
    prev_mask = valid_scene_mask(prev)
    curr_mask = valid_scene_mask(curr)
    valid = (prev_mask > 0) & (curr_mask > 0)
    if int(valid.sum()) < 1000:
        return []

    shift, response = cv2.phaseCorrelate(
        (prev_gray * (prev_mask > 0)).astype(np.float32),
        (curr_gray * (curr_mask > 0)).astype(np.float32),
    )
    dx, dy = shift
    if abs(dx) > 15 or abs(dy) > 15 or response < 0.02:
        dx = 0.0
        dy = 0.0

    transform = np.float32([[1, 0, dx], [0, 1, dy]])
    prev_warped = cv2.warpAffine(
        prev_gray,
        transform,
        (prev_gray.shape[1], prev_gray.shape[0]),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    signed_diff = curr_gray.astype(np.int16) - prev_warped.astype(np.int16)
    abs_diff = np.abs(signed_diff).astype(np.float32)
    local = cv2.GaussianBlur(abs_diff, (0, 0), 2.0)
    residual = np.maximum(abs_diff - local, 0)
    residual_values = residual[valid]
    if residual_values.size == 0:
        return []

    threshold = max(5.0, float(np.percentile(residual_values, 99.985)))
    raw = ((residual >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)

    lane = expected_lane(cycle_second)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 2 or area > 100:
            continue
        if w > 26 or h > 26:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 7.0:
            continue
        values = residual[labels == label]
        signed_values = signed_diff[labels == label]
        cx, cy = centroids[label]
        lane_distance = math.inf
        if lane is not None:
            lane_distance = math.hypot(float(cx) - lane[0], float(cy) - lane[1])
        raw_score = float(values.sum()) + float(values.max()) * 0.5 - max(0.0, aspect - 2.5) * 15.0
        lane_score = raw_score - min(lane_distance, 500.0) * 2.0
        candidates.append(
            {
                "bbox_x0": int(x),
                "bbox_y0": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "center_x": float(cx),
                "center_y": float(cy),
                "mean_signed_luma_delta": float(signed_values.mean()),
                "max_residual_luma": float(values.max()),
                "mean_residual_luma": float(values.mean()),
                "residual_threshold": threshold,
                "background_shift_x": float(dx),
                "background_shift_y": float(dy),
                "phase_corr_response": float(response),
                "distance_from_expected_lane_px": lane_distance,
                "raw_score": raw_score,
                "lane_score": lane_score,
            }
        )
    candidates.sort(key=lambda item: item["lane_score"], reverse=True)
    return candidates[:limit]


def classify(candidate: dict | None, cycle_second: float) -> tuple[str, str]:
    if cycle_second > 2.35:
        return "none", "post-observation loop/reset padding"
    if candidate is None:
        return "none", "no compact residual component survived filtering near the expected lane"
    distance = float(candidate["distance_from_expected_lane_px"])
    raw_score = float(candidate["raw_score"])
    max_residual = float(candidate["max_residual_luma"])
    if cycle_second > 2.0:
        if distance <= 90 and raw_score >= 40:
            return "low", "post-DVIDS tail residual near expected exit lane; not counted as primary two-second support"
        return "none", "post-DVIDS tail/reset padding"
    if distance <= 55 and raw_score >= 65 and max_residual >= 7:
        return "medium", "lane-compatible compact residual; target remains barely distinguishable and terrain-confounded"
    if distance <= 115 and raw_score >= 35:
        return "low", "weak lane-compatible residual below medium-support threshold"
    return "none", "residual component is too weak or too far from the DVIDS-described lane"


def sample_seconds(duration: float, sample_rate: float) -> list[float]:
    count = int(math.floor(duration * sample_rate)) + 1
    seconds = []
    for index in range(count):
        second = round(index / sample_rate, 3)
        if second <= duration:
            seconds.append(second)
    return seconds


def loop_for_frame(frame_index: int, boundaries: list[int]) -> int:
    return max(0, min(bisect.bisect_right(boundaries, frame_index) - 1, len(boundaries) - 2))


def annotate_frame(frame: np.ndarray, candidate: dict | None, second: float, cycle_second: float, quality: str) -> np.ndarray:
    out = frame.copy()
    lane = expected_lane(cycle_second)
    if lane is not None:
        x, y = int(round(lane[0])), int(round(lane[1]))
        cv2.circle(out, (x, y), 20, (255, 255, 0), 1)
        cv2.drawMarker(out, (x, y), (255, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=16, thickness=1)
    if candidate is not None:
        x0 = int(candidate["bbox_x0"])
        y0 = int(candidate["bbox_y0"])
        x1 = x0 + int(candidate["bbox_w"])
        y1 = y0 + int(candidate["bbox_h"])
        color = (0, 255, 0) if quality == "medium" else (0, 255, 255) if quality == "low" else (0, 0, 255)
        cv2.rectangle(out, (x0 - 5, y0 - 5), (x1 + 5, y1 + 5), color, 2)
        cv2.drawMarker(
            out,
            (int(round(candidate["center_x"])), int(round(candidate["center_y"]))),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=16,
            thickness=1,
        )
    cv2.rectangle(out, (0, 0), (940, 38), (0, 0, 0), -1)
    cv2.putText(
        out,
        f"PR43 t={second:.2f}s cycle={cycle_second:.2f}s quality={quality}",
        (10, 26),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return out


def annotate_patch(frame: np.ndarray, candidate: dict | None, second: float, cycle_second: float, quality: str) -> np.ndarray:
    lane = expected_lane(cycle_second)
    if candidate is not None:
        cx = float(candidate["center_x"])
        cy = float(candidate["center_y"])
    elif lane is not None:
        cx, cy = lane
    else:
        cx, cy = frame.shape[1] / 2, frame.shape[0] / 2
    half = 80
    x0 = max(0, int(round(cx - half)))
    y0 = max(0, int(round(cy - half)))
    x1 = min(frame.shape[1], int(round(cx + half)))
    y1 = min(frame.shape[0], int(round(cy + half)))
    crop = frame[y0:y1, x0:x1].copy()
    if crop.size == 0:
        crop = np.zeros((160, 160, 3), dtype=np.uint8)
    center = (int(round(cx - x0)), int(round(cy - y0)))
    cv2.drawMarker(crop, center, (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=16, thickness=1)
    patch = cv2.resize(crop, (320, 320), interpolation=cv2.INTER_NEAREST)
    cv2.rectangle(patch, (0, 0), (320, 34), (0, 0, 0), -1)
    cv2.putText(
        patch,
        f"{second:.2f}s cyc {cycle_second:.2f}s {quality}",
        (6, 23),
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
    return [
        row
        for row in rows
        if row["review_quality"] == "medium" and row["target_center_x"] != "" and row["is_primary_observation"] == "yes"
    ]


def supported_interval_summary(rows: list[dict]) -> dict:
    supported = supported_rows(rows)
    if not supported:
        return {"metric": "cycle_supported_intervals", "value": "", "note": "no primary medium rows"}
    seconds = sorted({round(float(row["cycle_second"]), 1) for row in supported})
    ranges: list[tuple[float, float]] = []
    start = seconds[0]
    prev = seconds[0]
    for second in seconds[1:]:
        if second - prev > 0.11:
            ranges.append((start, prev))
            start = second
        prev = second
    ranges.append((start, prev))
    text = "; ".join(f"{s:.1f}s" if s == e else f"{s:.1f}s-{e:.1f}s" for s, e in ranges)
    return {"metric": "cycle_supported_intervals", "value": text, "note": f"{len(ranges)} cycle-normalized ten-fps supported interval(s)"}


def track_stats(rows: list[dict]) -> dict:
    supported = supported_rows(rows)
    by_cycle: dict[float, list[dict]] = {}
    for row in supported:
        by_cycle.setdefault(round(float(row["cycle_second"]), 1), []).append(row)
    normalized = []
    for cycle_second, grouped_rows in sorted(by_cycle.items()):
        normalized.append(
            {
                "cycle_second": cycle_second,
                "target_center_x": statistics.median(float(row["target_center_x"]) for row in grouped_rows),
                "target_center_y": statistics.median(float(row["target_center_y"]) for row in grouped_rows),
                "repeat_count": len(grouped_rows),
            }
        )
    if len(normalized) < 2:
        return {
            "metric": "cycle_lane_residual_track",
            "value": len(normalized),
            "note": "fewer than two cycle-normalized primary medium bins",
        }
    total = 0.0
    rates = []
    for prev, curr in zip(normalized, normalized[1:]):
        dt = float(curr["cycle_second"]) - float(prev["cycle_second"])
        if dt <= 0:
            continue
        step = math.hypot(
            float(curr["target_center_x"]) - float(prev["target_center_x"]),
            float(curr["target_center_y"]) - float(prev["target_center_y"]),
        )
        total += step
        rates.append(step / dt)
    net = math.hypot(
        float(normalized[-1]["target_center_x"]) - float(normalized[0]["target_center_x"]),
        float(normalized[-1]["target_center_y"]) - float(normalized[0]["target_center_y"]),
    )
    duration = float(normalized[-1]["cycle_second"]) - float(normalized[0]["cycle_second"])
    return {
        "metric": "cycle_lane_residual_track",
        "value": len(normalized),
        "note": (
            f"cycle {normalized[0]['cycle_second']:.1f}s-{normalized[-1]['cycle_second']:.1f}s; "
            f"repeat_counts={[row['repeat_count'] for row in normalized]}; "
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
    parser = argparse.ArgumentParser(description="PR43 loop-aware review for DOD_111689759.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=10.0)
    args = parser.parse_args()

    frames, fps, total_frames, duration = read_video_frames(args.video)
    boundaries, loop_rows = detect_loop_boundaries(frames, fps)

    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "target-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    seconds = sample_seconds(duration, args.sample_rate)
    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    for sample_index, second in enumerate(seconds):
        frame_index = min(int(round(second * fps)), total_frames - 1)
        loop_index = loop_for_frame(frame_index, boundaries)
        loop_start_frame = boundaries[loop_index]
        cycle_second = (frame_index - loop_start_frame) / fps
        frame = frames[frame_index]
        candidate = None
        candidates: list[dict] = []
        if frame_index > loop_start_frame:
            candidates = compensated_residual_candidates(frames[frame_index - 1], frame, cycle_second)
            candidate = candidates[0] if candidates else None
        quality, caveat = classify(candidate, cycle_second)
        phase, anchor = dvids_phase(cycle_second)
        lane = expected_lane(cycle_second)
        distance = "" if candidate is None else round(float(candidate["distance_from_expected_lane_px"]), 2)
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, candidate, second, cycle_second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, candidate, second, cycle_second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)
        rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "sample_index": sample_index,
                "approx_second": f"{second:.1f}",
                "source_frame_index": frame_index,
                "loop_index": loop_index,
                "cycle_second": f"{cycle_second:.3f}",
                "is_primary_observation": "yes" if cycle_second <= 2.0 else "no",
                "dvids_phase": phase,
                "dvids_anchor": anchor,
                "review_quality": quality,
                "candidate_count": len(candidates),
                "target_center_x": "" if candidate is None else round(float(candidate["center_x"]), 1),
                "target_center_y": "" if candidate is None else round(float(candidate["center_y"]), 1),
                "expected_lane_x": "" if lane is None else round(lane[0], 1),
                "expected_lane_y": "" if lane is None else round(lane[1], 1),
                "distance_from_expected_lane_px": distance,
                "bbox_x0": "" if candidate is None else int(candidate["bbox_x0"]),
                "bbox_y0": "" if candidate is None else int(candidate["bbox_y0"]),
                "bbox_w": "" if candidate is None else int(candidate["bbox_w"]),
                "bbox_h": "" if candidate is None else int(candidate["bbox_h"]),
                "component_area": "" if candidate is None else int(candidate["area"]),
                "mean_signed_luma_delta": "" if candidate is None else round(float(candidate["mean_signed_luma_delta"]), 3),
                "max_residual_luma": "" if candidate is None else round(float(candidate["max_residual_luma"]), 3),
                "mean_residual_luma": "" if candidate is None else round(float(candidate["mean_residual_luma"]), 3),
                "residual_threshold": "" if candidate is None else round(float(candidate["residual_threshold"]), 3),
                "background_shift_x": "" if candidate is None else round(float(candidate["background_shift_x"]), 4),
                "background_shift_y": "" if candidate is None else round(float(candidate["background_shift_y"]), 4),
                "phase_corr_response": "" if candidate is None else round(float(candidate["phase_corr_response"]), 4),
                "raw_score": "" if candidate is None else round(float(candidate["raw_score"]), 3),
                "lane_score": "" if candidate is None else round(float(candidate["lane_score"]), 3),
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr43-loop-annotated", cols=4, thumb_width=480)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr43-loop-patches", cols=6, thumb_width=220)

    review_csv = Path("research/ufo-video-pr43-loop-review-dod111689759.csv")
    loop_csv = Path("research/ufo-video-pr43-loop-review-loop-summary.csv")
    summary_csv = Path("research/ufo-video-pr43-loop-review-summary.csv")
    asset_csv = Path("research/ufo-video-pr43-loop-review-assets.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)
    write_csv(loop_csv, list(loop_rows[0].keys()), loop_rows)

    primary_rows = [row for row in rows if row["is_primary_observation"] == "yes"]
    supported = supported_rows(rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    primary_quality_counts = Counter(row["review_quality"] for row in primary_rows)
    loop_durations = [float(row["loop_duration_seconds"]) for row in loop_rows if int(row["loop_index"]) < len(loop_rows) - 1]
    distances = [float(row["distance_from_expected_lane_px"]) for row in supported if row["distance_from_expected_lane_px"] != ""]
    residuals = [float(row["max_residual_luma"]) for row in supported if row["max_residual_luma"] != ""]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps loop-aware review samples"},
        {"metric": "loop_count", "value": len(loop_rows), "note": "detected loop/reset-delimited segments in local file"},
        numeric_summary("detected_loop_duration_seconds", loop_durations, "reset-to-reset duration; final partial tail excluded"),
        {"metric": "primary_observation_rows", "value": len(primary_rows), "note": "cycle_second <= 2.0 rows across all local loops"},
        {"metric": "primary_medium_rows", "value": len(supported), "note": "conservative lane-compatible residual rows; no high-confidence rows assigned"},
        supported_interval_summary(rows),
        track_stats(rows),
        numeric_summary("distance_from_expected_lane_px", distances, "supported residual distance from DVIDS-shaped lane"),
        numeric_summary("max_residual_luma", residuals, "supported compact residual max luma after frame compensation"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "all local looped-file review rows"})
    for key, value in sorted(primary_quality_counts.items()):
        summary_rows.append({"metric": f"primary_quality_count: {key}", "value": value, "note": "cycle_second <= 2.0 rows"})
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "loop_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR43 ten-fps loop-aware residual review table"},
        {"artifact_type": "loop_summary_csv", "path": str(loop_csv).replace("\\", "/"), "note": "Detected loop/reset boundaries"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR43 loop-aware review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR43 annotated lane/residual sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR43 lane/residual patch sheet"})
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"loops={len(loop_rows)} boundaries={boundaries}")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"primary_rows={len(primary_rows)} primary_quality_counts={dict(primary_quality_counts)}")
    print(f"primary_medium={len(supported)}")
    print(f"review_csv={review_csv}")
    print(f"loop_csv={loop_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

