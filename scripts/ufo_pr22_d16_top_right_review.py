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


VIDEO_ID = "DOD_111688775"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR22"
REPORT_ID = "DoW-UAP-D16"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111688775.mp4"
FALLBACK_VIDEO = Path("research/ufo-derived/video-motion-pass/pr22-d16-top-right-review/source") / VIDEO_NAME
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr22-d16-top-right-review") / VIDEO_ID

# The public video is a split IR/EO display. The strongest visible candidate is in
# the upper field of the left/IR pane near the DVIDS-described five-second event.
ROI_X0 = 120
ROI_Y0 = 130
ROI_X1 = 540
ROI_Y1 = 430
EXPECTED_X = 395.0
EXPECTED_Y = 340.0


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
    raise RuntimeError(f"Could not open any PR22 source video: {tried}")


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 1.0:
        return "startup/black interval", "startup frame; no reliable PR22 target context"
    if second <= 8.5:
        return "upper-field dark-contrast interval", "DVIDS: at about five seconds, object moves right-to-left across top-right field"
    return "post-event transition context", "later scene/contrast transition; retained as context only"


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((sat > 40) & (val > 35) & (hue >= 35) & (hue <= 115)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def fixed_overlay_mask(shape: tuple[int, int, int]) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    boxes = [
        (0, 0, 295, 180),
        (500, 0, 1320, 210),
        (477, 210, 700, 1070),
        (0, 495, 140, 630),
        (318, 870, 475, 1000),
        (0, 980, 90, 1080),
        (1375, 20, 1605, 185),
        (1238, 214, 1600, 990),
        (1685, 755, 1915, 1065),
        (1730, 0, 1908, 50),
        (1850, 36, 1908, 80),
    ]
    for x0, y0, x1, y1 in boxes:
        cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(width, x1), min(height, y1)), 255, -1)
    return mask


def dark_elongated_candidates(frame: np.ndarray) -> list[dict]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay = cv2.bitwise_or(colored_overlay_mask(frame), fixed_overlay_mask(frame.shape))
    overlay = cv2.dilate(overlay, np.ones((5, 5), np.uint8), iterations=1)[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    valid = (gray > 30) & (gray < 235) & (overlay == 0)
    if int(valid.sum()) < 1000:
        return []

    background = cv2.medianBlur(gray, 45)
    signed_delta = gray.astype(np.int16) - background.astype(np.int16)
    abs_delta = np.abs(signed_delta)
    threshold = max(18.0, float(np.percentile(abs_delta[valid], 99.3)))
    raw = ((signed_delta <= -threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 8 or area > 900:
            continue
        if w < 4 or h < 2 or w > 80 or h > 45:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect < 1.3 or aspect > 10.0:
            continue

        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        values = gray[labels == label]
        abs_values = abs_delta[labels == label]
        mean_signed_delta = float(np.mean(signed_delta[labels == label]))
        contrast = float(np.max(abs_values))
        distance_from_expected = math.hypot(full_x - EXPECTED_X, full_y - EXPECTED_Y)
        score = contrast * 5.0 + int(area) * 1.5 + aspect * 25.0 - distance_from_expected * 0.25
        candidates.append(
            {
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "aspect_ratio": float(aspect),
                "center_x": full_x,
                "center_y": full_y,
                "component_min_luma": int(values.min()),
                "component_max_luma": int(values.max()),
                "component_mean_luma": float(values.mean()),
                "mean_signed_delta_luma": mean_signed_delta,
                "contrast_delta_luma": contrast,
                "distance_from_expected_px": distance_from_expected,
                "detection_threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:12]


def classify_candidate(candidate: dict | None, second: float) -> tuple[str, str]:
    if candidate is None:
        return "none", "no usable dark elongated upper-field candidate recovered"
    if second < 1.0:
        return "low", "startup frame; retained as context only"
    if second > 8.5:
        return "low", "post-event scene transition or false candidate; retained as context only"

    score = float(candidate["raw_score"])
    area = float(candidate["area"])
    contrast = float(candidate["contrast_delta_luma"])
    distance = float(candidate["distance_from_expected_px"])
    aspect = float(candidate["aspect_ratio"])
    if score >= 900.0 and area >= 120.0 and contrast >= 120.0 and distance <= 110.0 and aspect >= 1.45:
        return "high", "strong dark elongated upper-field contrast candidate near DVIDS-described interval"
    if score >= 650.0 and area >= 70.0 and contrast >= 90.0 and distance <= 145.0:
        return "medium", "usable dark elongated upper-field candidate, but terrain/overlay confounds remain"
    return "low", "weak or poorly located upper-field candidate; retained as context only"


def row_for_sample(frame_index: int, second: float, frame: np.ndarray) -> dict:
    phase, phase_note = dvids_phase(second)
    candidates = dark_elongated_candidates(frame)
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
        "candidate_distance_from_expected_px": "",
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
                "candidate_distance_from_expected_px": round(float(candidate["distance_from_expected_px"]), 3),
            }
        )
    return row


def sample_rows(video: Path) -> tuple[Path, list[dict], float, int, float]:
    source_video, cap = open_capture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if fps else 0.0
    sample_seconds = list(range(0, int(math.floor(duration)) + 1))
    if not sample_seconds or sample_seconds[-1] < duration - 0.5:
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
        rows.append(row_for_sample(frame_index, actual_second, frame))
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
        if second <= previous + 1.05:
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
        return [{"metric": "supported_candidate_path", "value": len(supported), "note": "insufficient rows for candidate path"}]
    points = [(float(row["second"]), float(row["candidate_center_x"]), float(row["candidate_center_y"])) for row in supported]
    net = math.hypot(points[-1][1] - points[0][1], points[-1][2] - points[0][2])
    path = 0.0
    for prev, curr in zip(points, points[1:]):
        path += math.hypot(curr[1] - prev[1], curr[2] - prev[2])
    span = max(points[-1][0] - points[0][0], 1e-9)
    x_shift = points[-1][1] - points[0][1]
    y_shift = points[-1][2] - points[0][2]
    direction_note = (
        "positive x-shift in image coordinates; does not independently validate DVIDS right-to-left wording"
        if x_shift > 0
        else "negative x-shift in image coordinates; compatible with right-to-left wording only at image-plane level"
    )
    return [
        {
            "metric": "supported_candidate_path",
            "value": len(supported),
            "note": (
                f"{points[0][0]:.1f}s-{points[-1][0]:.1f}s; net={net:.3f}px; path={path:.3f}px; "
                f"path_rate={path / span:.3f}px/s; image-plane candidate only"
            ),
        },
        {"metric": "candidate_x_shift_px", "value": round(x_shift, 3), "note": direction_note},
        {"metric": "candidate_y_shift_px", "value": round(y_shift, 3), "note": "image-plane y-shift; not a physical north-south validation"},
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
        {"metric": "sample_count", "value": len(rows), "note": "one-fps full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable upper-field dark elongated candidate"},
        {"metric": "supported_intervals", "value": supported_intervals(rows), "note": "one-fps supported interval(s)"},
    ]
    summary_rows.extend(candidate_path_summary(rows))
    summary_rows.extend(
        [
            numeric_summary("candidate_score", [float(row["candidate_score"]) for row in supported], "selected dark elongated candidate score"),
            numeric_summary("candidate_area", [float(row["candidate_area"]) for row in supported], "selected candidate component area"),
            numeric_summary("candidate_contrast_delta_luma", [float(row["candidate_contrast_delta_luma"]) for row in supported], "selected candidate dark contrast delta"),
            numeric_summary("candidate_aspect_ratio", [float(row["candidate_aspect_ratio"]) for row in supported], "selected candidate aspect ratio"),
            numeric_summary("candidate_center_x", [float(row["candidate_center_x"]) for row in supported], "selected candidate x-position"),
            numeric_summary("candidate_center_y", [float(row["candidate_center_y"]) for row in supported], "selected candidate y-position"),
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
    if row["candidate_center_x"] != "":
        color = (0, 255, 0) if row["review_quality"] == "high" else (0, 200, 255) if row["review_quality"] == "medium" else (0, 128, 255)
        center = (int(float(row["candidate_center_x"])), int(float(row["candidate_center_y"])))
        half_w = max(8, int(float(row["candidate_bbox_w"])) // 2 + 8)
        half_h = max(8, int(float(row["candidate_bbox_h"])) // 2 + 8)
        cv2.rectangle(annotated, (center[0] - half_w, center[1] - half_h), (center[0] + half_w, center[1] + half_h), color, 2)
        cv2.drawMarker(annotated, center, color, markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    label = f'{row["second"]:.1f}s {row["review_quality"]}'
    cv2.putText(annotated, label, (60, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 4, cv2.LINE_AA)
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
        crop = annotated[220:420, 250:540].copy()
        crop = cv2.resize(crop, (580, 400), interpolation=cv2.INTER_NEAREST)
        crop_label = f'{row["second"]:.1f}s {row["review_quality"]}'
        cv2.putText(crop, crop_label, (8, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2, cv2.LINE_AA)
        patch_images.append(crop)

    assets: list[dict] = [{"artifact_type": "source_video", "path": str(video).replace("\\", "/"), "note": "source video used for PR22/D16 review"}]
    if patch_images:
        patch_rows = []
        for index in range(0, len(patch_images), 3):
            chunk = patch_images[index : index + 3]
            while len(chunk) < 3:
                chunk.append(np.zeros_like(patch_images[0]))
            patch_rows.append(np.hstack(chunk))
        patch_sheet = np.vstack(patch_rows)
        patch_path = OUT_ROOT / f"{VIDEO_ID}-pr22-d16-upper-field-patches.jpg"
        cv2.imwrite(str(patch_path), patch_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "patch_sheet", "path": str(patch_path).replace("\\", "/"), "note": "upper-field dark elongated candidate patches"})

    if full_images:
        full_rows = []
        for index in range(0, len(full_images), 3):
            chunk = full_images[index : index + 3]
            while len(chunk) < 3:
                chunk.append(np.zeros_like(full_images[0]))
            full_rows.append(np.hstack(chunk))
        full_sheet = np.vstack(full_rows)
        full_path = OUT_ROOT / f"{VIDEO_ID}-pr22-d16-upper-field-annotated.jpg"
        cv2.imwrite(str(full_path), full_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "annotated_sheet", "path": str(full_path).replace("\\", "/"), "note": "full-frame ROI and candidate annotations"})
    return assets


def run(video: Path) -> None:
    source_video, rows, fps, total_frames, duration = sample_rows(video)
    if not rows:
        raise RuntimeError(f"No PR22 rows generated from {source_video}")

    review_path = Path("research/ufo-video-pr22-d16-top-right-review-dod111688775.csv")
    summary_path = Path("research/ufo-video-pr22-d16-top-right-review-summary.csv")
    assets_path = Path("research/ufo-video-pr22-d16-top-right-review-assets.csv")

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
    parser = argparse.ArgumentParser(description="PR22/D16 upper-field dark elongated contrast review")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO, help="Path to DOD_111688775.mp4")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.video)

