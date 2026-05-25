from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111688809"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR23"
REPORT_ID = "DoW-UAP-D18"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111688809.mp4")
FALLBACK_VIDEO = Path("research/ufo-derived/video-motion-pass/pr23-d18-diagonal-review/source") / VIDEO_NAME
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr23-d18-diagonal-review") / VIDEO_ID

# DVIDS describes an area/object of contrast moving from lower-left toward the
# upper-right and exiting near the upper-right around six seconds. The public
# clip is an urban ISR scene, so this script treats the line as a visual proxy,
# not as a validated object track.
LINE_START = np.array([330.0, 760.0])
LINE_END = np.array([1530.0, 120.0])
LINE_VECTOR = LINE_END - LINE_START
LINE_LENGTH = float(np.linalg.norm(LINE_VECTOR))
LINE_UNIT = LINE_VECTOR / LINE_LENGTH

ROI_X0 = 180
ROI_Y0 = 90
ROI_X1 = 1710
ROI_Y1 = 900


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
    raise RuntimeError(f"Could not open any PR23 source video: {tried}")


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 3.5:
        return "early diagonal-lane context", "DVIDS: lower-left to upper-right movement; early/lower-half support is not cleanly recoverable in this public MP4"
    if second <= 6.5:
        return "upper-right exit interval", "DVIDS: area of contrast exits near the upper-right around six seconds"
    return "post-exit context", "after the described exit interval; retained as context only"


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((sat > 38) & (val > 35) & (hue >= 35) & (hue <= 115)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def fixed_overlay_mask(shape: tuple[int, int, int]) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    boxes = [
        (0, 0, 1920, 70),
        (0, 0, 150, 1080),
        (1760, 0, 1920, 1080),
        (0, 1030, 1920, 1080),
        (0, 0, 320, 190),
        (480, 0, 835, 145),
        (875, 0, 1165, 130),
        (1215, 0, 1465, 125),
        (1530, 0, 1920, 165),
        (1680, 720, 1920, 1080),
        (0, 820, 260, 1080),
        (845, 520, 1045, 640),
    ]
    for x0, y0, x1, y1 in boxes:
        cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(width, x1), min(height, y1)), 255, -1)
    return mask


def point_line_metrics(x: float, y: float, second: float) -> tuple[float, float, float, float, float]:
    point = np.array([x, y])
    rel = point - LINE_START
    projection_px = float(np.dot(rel, LINE_UNIT))
    projection_fraction = max(0.0, min(1.0, projection_px / LINE_LENGTH))
    nearest = LINE_START + LINE_UNIT * max(0.0, min(LINE_LENGTH, projection_px))
    line_distance = float(np.linalg.norm(point - nearest))

    expected_fraction = max(0.0, min(1.0, second / 6.0))
    expected = LINE_START + LINE_VECTOR * expected_fraction
    expected_distance = float(np.linalg.norm(point - expected))
    return line_distance, expected_distance, projection_fraction, float(expected[0]), float(expected[1])


def build_background(video: Path, fps: float, total_frames: int) -> np.ndarray:
    cap = cv2.VideoCapture(str(video))
    frames: list[np.ndarray] = []
    for second in np.arange(0.0, min(7.0, total_frames / fps), 0.25):
        frame_index = min(total_frames - 1, max(0, int(round(float(second) * fps))))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    cap.release()
    if not frames:
        raise RuntimeError("Could not build PR23 median background")
    stack = np.stack(frames, axis=0)
    return np.median(stack, axis=0).astype(np.uint8)


def compact_residual_candidates(frame: np.ndarray, background: np.ndarray, second: float) -> list[dict]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    overlay = cv2.bitwise_or(colored_overlay_mask(frame), fixed_overlay_mask(frame.shape))
    overlay = cv2.dilate(overlay, np.ones((5, 5), np.uint8), iterations=1)

    yy, xx = np.indices(gray.shape)
    rel_x = xx.astype(np.float32) - float(LINE_START[0])
    rel_y = yy.astype(np.float32) - float(LINE_START[1])
    projection_px = rel_x * float(LINE_UNIT[0]) + rel_y * float(LINE_UNIT[1])
    nearest_x = float(LINE_START[0]) + np.clip(projection_px, 0.0, LINE_LENGTH) * float(LINE_UNIT[0])
    nearest_y = float(LINE_START[1]) + np.clip(projection_px, 0.0, LINE_LENGTH) * float(LINE_UNIT[1])
    line_distance = np.sqrt((xx.astype(np.float32) - nearest_x) ** 2 + (yy.astype(np.float32) - nearest_y) ** 2)
    projection_fraction = np.clip(projection_px / LINE_LENGTH, 0.0, 1.0)

    abs_delta = cv2.absdiff(gray, background)
    signed_delta = gray.astype(np.int16) - background.astype(np.int16)
    valid = (
        (xx >= ROI_X0)
        & (xx <= ROI_X1)
        & (yy >= ROI_Y0)
        & (yy <= ROI_Y1)
        & (gray > 20)
        & (gray < 245)
        & (overlay == 0)
        & (line_distance <= 115.0)
    )
    if int(valid.sum()) < 1000:
        return []

    threshold = max(20.0, float(np.percentile(abs_delta[valid], 99.65)))
    raw = ((abs_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 8 or area > 600:
            continue
        if w < 3 or h < 3 or w > 55 or h > 55:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 7.5:
            continue

        cx, cy = centroids[label]
        values = gray[labels == label]
        abs_values = abs_delta[labels == label]
        signed_values = signed_delta[labels == label]
        line_dist, expected_dist, projection_frac, expected_x, expected_y = point_line_metrics(float(cx), float(cy), second)
        exit_window_bonus = 120.0 if 4.0 <= second <= 6.5 and projection_frac >= 0.58 else 0.0
        score = (
            float(np.max(abs_values)) * 4.2
            + int(area) * 1.4
            + min(aspect, 4.0) * 18.0
            + exit_window_bonus
            - line_dist * 1.9
            - expected_dist * 0.5
        )
        candidates.append(
            {
                "bbox_x": int(x),
                "bbox_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "aspect_ratio": float(aspect),
                "center_x": float(cx),
                "center_y": float(cy),
                "component_min_luma": int(values.min()),
                "component_max_luma": int(values.max()),
                "component_mean_luma": float(values.mean()),
                "mean_signed_delta_luma": float(np.mean(signed_values)),
                "contrast_delta_luma": float(np.max(abs_values)),
                "line_distance_px": line_dist,
                "expected_distance_px": expected_dist,
                "line_projection_fraction": projection_frac,
                "expected_center_x": expected_x,
                "expected_center_y": expected_y,
                "detection_threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:15]


def classify_candidate(candidate: dict | None, second: float) -> tuple[str, str]:
    if candidate is None:
        return "none", "no compact diagonal-lane residual candidate recovered"
    if second < 3.5:
        return "low", "early diagonal-lane residual retained as context; lower-left-to-mid movement is not cleanly recovered"
    if second > 6.5:
        return "low", "post-exit residual retained as context only"

    score = float(candidate["raw_score"])
    contrast = float(candidate["contrast_delta_luma"])
    area = float(candidate["area"])
    line_dist = float(candidate["line_distance_px"])
    expected_dist = float(candidate["expected_distance_px"])
    projection = float(candidate["line_projection_fraction"])
    if (
        score >= 520.0
        and contrast >= 85.0
        and area >= 25.0
        and line_dist <= 75.0
        and expected_dist <= 145.0
        and projection >= 0.58
    ):
        return "medium", "best recovered upper-right diagonal/exit residual candidate near DVIDS-described interval; not a clean moving track"
    if (
        score >= 350.0
        and contrast >= 60.0
        and area >= 14.0
        and line_dist <= 95.0
        and expected_dist <= 190.0
        and projection >= 0.52
    ):
        return "medium", "usable upper-right diagonal/exit residual candidate, but urban terrain and compression confounds remain"
    return "low", "weak, poorly phased, or poorly located diagonal-lane residual; retained as context only"


def row_for_sample(frame_index: int, second: float, frame: np.ndarray, background: np.ndarray) -> dict:
    phase, phase_note = dvids_phase(second)
    candidates = compact_residual_candidates(frame, background, second)
    candidate = candidates[0] if candidates else None
    quality, note = classify_candidate(candidate, second)
    row = {
        "video": VIDEO_NAME,
        "release_id": RELEASE_ID,
        "report_id": REPORT_ID,
        "frame_index": frame_index,
        "second": round(second, 3),
        "phase": phase,
        "phase_note": phase_note,
        "target_candidate": quality in {"high", "medium"},
        "review_quality": quality,
        "candidate_count": len(candidates),
        "candidate_score": "",
        "candidate_center_x": "",
        "candidate_center_y": "",
        "candidate_area": "",
        "candidate_bbox_w": "",
        "candidate_bbox_h": "",
        "candidate_aspect_ratio": "",
        "candidate_min_luma": "",
        "candidate_max_luma": "",
        "candidate_mean_luma": "",
        "candidate_mean_signed_delta_luma": "",
        "candidate_contrast_delta_luma": "",
        "candidate_line_distance_px": "",
        "candidate_expected_distance_px": "",
        "candidate_line_projection_fraction": "",
        "expected_center_x": "",
        "expected_center_y": "",
        "notes": note,
    }
    if candidate is not None:
        row.update(
            {
                "candidate_score": round(float(candidate["raw_score"]), 6),
                "candidate_center_x": round(float(candidate["center_x"]), 3),
                "candidate_center_y": round(float(candidate["center_y"]), 3),
                "candidate_area": int(candidate["area"]),
                "candidate_bbox_w": int(candidate["bbox_w"]),
                "candidate_bbox_h": int(candidate["bbox_h"]),
                "candidate_aspect_ratio": round(float(candidate["aspect_ratio"]), 6),
                "candidate_min_luma": int(candidate["component_min_luma"]),
                "candidate_max_luma": int(candidate["component_max_luma"]),
                "candidate_mean_luma": round(float(candidate["component_mean_luma"]), 6),
                "candidate_mean_signed_delta_luma": round(float(candidate["mean_signed_delta_luma"]), 6),
                "candidate_contrast_delta_luma": round(float(candidate["contrast_delta_luma"]), 6),
                "candidate_line_distance_px": round(float(candidate["line_distance_px"]), 3),
                "candidate_expected_distance_px": round(float(candidate["expected_distance_px"]), 3),
                "candidate_line_projection_fraction": round(float(candidate["line_projection_fraction"]), 6),
                "expected_center_x": round(float(candidate["expected_center_x"]), 3),
                "expected_center_y": round(float(candidate["expected_center_y"]), 3),
            }
        )
    return row


def sample_rows(video: Path) -> tuple[Path, list[dict], float, int, float]:
    source_video, cap = open_capture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if fps else 0.0
    cap.release()

    background = build_background(source_video, fps, total_frames)
    cap = cv2.VideoCapture(str(source_video))
    sample_seconds = list(np.arange(0.0, max(0.0, duration - 1.0 / fps) + 0.001, 0.5))
    if not sample_seconds or sample_seconds[-1] < duration - 0.35:
        sample_seconds.append(duration - 1.0 / fps)

    rows: list[dict] = []
    for nominal_second in sample_seconds:
        second = min(float(nominal_second), max(0.0, duration - 1.0 / fps))
        frame_index = min(total_frames - 1, max(0, int(round(second * fps))))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        actual_second = frame_index / fps
        rows.append(row_for_sample(frame_index, actual_second, frame, background))
    cap.release()
    return source_video, rows, fps, total_frames, duration


def write_csv(path: Path, rows: list[dict]) -> None:
    ensure_dir(path.parent)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def supported_intervals(rows: list[dict]) -> str:
    supported = [row for row in rows if row["review_quality"] in {"high", "medium"}]
    if not supported:
        return ""
    intervals: list[tuple[float, float]] = []
    start = float(supported[0]["second"])
    previous = float(supported[0]["second"])
    for row in supported[1:]:
        second = float(row["second"])
        if second <= previous + 0.55:
            previous = second
            continue
        intervals.append((start, previous))
        start = second
        previous = second
    intervals.append((start, previous))
    return "; ".join(f"{start:.1f}s-{end:.1f}s" for start, end in intervals)


def numeric_summary(name: str, values: list[float], note: str) -> dict:
    if not values:
        return {"metric": name, "value": "", "note": note}
    if len(values) == 1:
        return {"metric": name, "value": round(values[0], 3), "note": f"{note}; single supported value"}
    mean = statistics.fmean(values)
    stdev = statistics.pstdev(values)
    cv = stdev / mean if mean else 0.0
    return {
        "metric": name,
        "value": round(statistics.median(values), 3),
        "note": f"median; mean={mean:.3f}; stdev={stdev:.3f}; cv={cv:.3f}; {note}",
    }


def candidate_path_summary(rows: list[dict]) -> list[dict]:
    supported = [row for row in rows if row["review_quality"] in {"high", "medium"} and row["candidate_center_x"] != ""]
    if len(supported) < 2:
        return [{"metric": "supported_candidate_path", "value": len(supported), "note": "insufficient rows for image-plane path summary"}]
    points = [(float(row["second"]), float(row["candidate_center_x"]), float(row["candidate_center_y"])) for row in supported]
    net = math.hypot(points[-1][1] - points[0][1], points[-1][2] - points[0][2])
    path = 0.0
    step_rates: list[float] = []
    for prev, curr in zip(points, points[1:]):
        step = math.hypot(curr[1] - prev[1], curr[2] - prev[2])
        path += step
        dt = curr[0] - prev[0]
        if dt > 0:
            step_rates.append(step / dt)
    span = max(points[-1][0] - points[0][0], 1e-9)
    return [
        {
            "metric": "supported_candidate_path",
            "value": len(supported),
            "note": (
                f"{points[0][0]:.1f}s-{points[-1][0]:.1f}s; net={net:.3f}px; path={path:.3f}px; "
                f"path_rate={path / span:.3f}px/s; median_step_rate={statistics.median(step_rates):.3f}px/s; "
                "image-plane residual proxy only"
            ),
        },
        {"metric": "candidate_x_shift_px", "value": round(points[-1][1] - points[0][1], 3), "note": "image-plane x-shift across supported residual rows"},
        {"metric": "candidate_y_shift_px", "value": round(points[-1][2] - points[0][2], 3), "note": "image-plane y-shift across supported residual rows"},
    ]


def build_summary_rows(rows: list[dict], source_video: Path, fps: float, total_frames: int, duration: float) -> list[dict]:
    supported = [row for row in rows if row["review_quality"] in {"high", "medium"}]
    counts = Counter(row["review_quality"] for row in rows)
    phase_counts = Counter(row["phase"] for row in supported)
    summary_rows = [
        {"metric": "video", "value": VIDEO_NAME, "note": f"source video used: {source_video}"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "report_id", "value": REPORT_ID, "note": "DVIDS-stated accompanying mission report"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": "half-second full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable upper-right diagonal/exit residual candidate"},
        {"metric": "supported_intervals", "value": supported_intervals(rows), "note": "half-second supported interval(s)"},
    ]
    summary_rows.extend(candidate_path_summary(rows))
    summary_rows.extend(
        [
            numeric_summary("candidate_score", [float(row["candidate_score"]) for row in supported], "selected compact residual score"),
            numeric_summary("candidate_area", [float(row["candidate_area"]) for row in supported], "selected compact residual area"),
            numeric_summary("candidate_contrast_delta_luma", [float(row["candidate_contrast_delta_luma"]) for row in supported], "selected residual contrast delta"),
            numeric_summary("candidate_line_distance_px", [float(row["candidate_line_distance_px"]) for row in supported], "distance from DVIDS diagonal proxy line"),
            numeric_summary("candidate_expected_distance_px", [float(row["candidate_expected_distance_px"]) for row in supported], "distance from six-second linearized diagonal proxy point"),
            numeric_summary("candidate_line_projection_fraction", [float(row["candidate_line_projection_fraction"]) for row in supported], "fractional position along lower-left to upper-right proxy line"),
            numeric_summary("candidate_center_x", [float(row["candidate_center_x"]) for row in supported], "selected residual x-position"),
            numeric_summary("candidate_center_y", [float(row["candidate_center_y"]) for row in supported], "selected residual y-position"),
        ]
    )
    for quality in sorted(counts):
        summary_rows.append({"metric": f"quality_count: {quality}", "value": counts[quality], "note": "review quality"})
    for phase, count in sorted(phase_counts.items()):
        summary_rows.append({"metric": f"supported_phase_count: {phase}", "value": count, "note": "supported rows by DVIDS phase"})
    return summary_rows


def read_frame_at(video: Path, frame_index: int) -> np.ndarray | None:
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    cap.release()
    return frame if ok else None


def draw_row(frame: np.ndarray, row: dict) -> np.ndarray:
    annotated = frame.copy()
    cv2.rectangle(annotated, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (0, 255, 255), 2)
    cv2.line(
        annotated,
        (int(LINE_START[0]), int(LINE_START[1])),
        (int(LINE_END[0]), int(LINE_END[1])),
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )
    if row["expected_center_x"] != "":
        expected = (int(float(row["expected_center_x"])), int(float(row["expected_center_y"])))
        cv2.drawMarker(annotated, expected, (255, 200, 0), markerType=cv2.MARKER_TILTED_CROSS, markerSize=24, thickness=2)
    if row["candidate_center_x"] != "":
        color = (0, 255, 0) if row["review_quality"] == "high" else (0, 200, 255) if row["review_quality"] == "medium" else (0, 128, 255)
        center = (int(float(row["candidate_center_x"])), int(float(row["candidate_center_y"])))
        half_w = max(8, int(float(row["candidate_bbox_w"])) // 2 + 8)
        half_h = max(8, int(float(row["candidate_bbox_h"])) // 2 + 8)
        cv2.rectangle(annotated, (center[0] - half_w, center[1] - half_h), (center[0] + half_w, center[1] + half_h), color, 2)
        cv2.drawMarker(annotated, center, color, markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    label = f'{row["second"]:.1f}s {row["review_quality"]}'
    cv2.putText(annotated, label, (60, 82), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 4, cv2.LINE_AA)
    return annotated


def make_visual_assets(video: Path, rows: list[dict]) -> list[dict]:
    ensure_dir(OUT_ROOT)
    patch_images: list[np.ndarray] = []
    full_images: list[np.ndarray] = []
    for row in rows:
        frame = read_frame_at(video, int(row["frame_index"]))
        if frame is None:
            continue
        annotated = draw_row(frame, row)
        full_images.append(cv2.resize(annotated, (480, 270), interpolation=cv2.INTER_AREA))
        crop = annotated[70:390, 1060:1685].copy()
        crop = cv2.resize(crop, (625, 320), interpolation=cv2.INTER_AREA)
        crop_label = f'{row["second"]:.1f}s {row["review_quality"]}'
        cv2.putText(crop, crop_label, (10, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 255), 2, cv2.LINE_AA)
        patch_images.append(crop)

    assets: list[dict] = [{"artifact_type": "source_video", "path": str(video).replace("\\", "/"), "note": "source video used for PR23/D18 review"}]
    if patch_images:
        patch_rows = []
        for index in range(0, len(patch_images), 3):
            chunk = patch_images[index : index + 3]
            while len(chunk) < 3:
                chunk.append(np.zeros_like(patch_images[0]))
            patch_rows.append(np.hstack(chunk))
        patch_sheet = np.vstack(patch_rows)
        patch_path = OUT_ROOT / f"{VIDEO_ID}-pr23-d18-upper-right-exit-patches.jpg"
        cv2.imwrite(str(patch_path), patch_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "patch_sheet", "path": str(patch_path).replace("\\", "/"), "note": "upper-right diagonal/exit candidate patches"})

    if full_images:
        full_rows = []
        for index in range(0, len(full_images), 4):
            chunk = full_images[index : index + 4]
            while len(chunk) < 4:
                chunk.append(np.zeros_like(full_images[0]))
            full_rows.append(np.hstack(chunk))
        full_sheet = np.vstack(full_rows)
        full_path = OUT_ROOT / f"{VIDEO_ID}-pr23-d18-diagonal-annotated.jpg"
        cv2.imwrite(str(full_path), full_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "annotated_sheet", "path": str(full_path).replace("\\", "/"), "note": "full-frame diagonal line, expected points, and residual candidates"})
    return assets


def run(video: Path) -> None:
    source_video, rows, fps, total_frames, duration = sample_rows(video)
    if not rows:
        raise RuntimeError(f"No PR23 rows generated from {source_video}")

    review_path = Path("research/ufo-video-pr23-d18-diagonal-review-dod111688809.csv")
    summary_path = Path("research/ufo-video-pr23-d18-diagonal-review-summary.csv")
    assets_path = Path("research/ufo-video-pr23-d18-diagonal-review-assets.csv")

    write_csv(review_path, rows)
    write_csv(summary_path, build_summary_rows(rows, source_video, fps, total_frames, duration))
    write_csv(assets_path, make_visual_assets(source_video, rows))

    print(f"source video: {source_video}")
    print(f"fps={fps:.3f} frames={total_frames} duration={duration:.3f}s")
    print(f"wrote {review_path}")
    print(f"wrote {summary_path}")
    print(f"wrote {assets_path}")
    print(f"quality counts: {dict(Counter(row['review_quality'] for row in rows))}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PR23/D18 diagonal upper-right exit residual review")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO, help="Path to DOD_111688809.mp4")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.video)

