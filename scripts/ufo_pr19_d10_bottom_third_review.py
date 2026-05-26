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


VIDEO_ID = "DOD_111688723"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR19"
REPORT_ID = "DoW-UAP-D10"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111688723.mp4"
FALLBACK_VIDEO = Path("research/ufo-derived/video-motion-pass/pr19-d10-bottom-third-review/source") / VIDEO_NAME
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr19-d10-bottom-third-review") / VIDEO_ID

ROI_X0 = 55
ROI_Y0 = 700
ROI_X1 = 800
ROI_Y1 = 850
BOTTOM_THIRD_Y0 = 720.0
BOTTOM_THIRD_Y1 = 1080.0


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
    raise RuntimeError(f"Could not open any PR19 source video: {tried}")


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 2.45:
        return "pre-crossing context", "Before the DVIDS-described bottom-third crossing is visible locally"
    if second <= 2.68:
        return "bottom-third crossing", "DVIDS: near the two-second mark, an area of contrast moves left-to-right across the bottom third"
    return "post-crossing context", "After the short bottom-third crossing interval"


def detect_bottom_third_streak(frame: np.ndarray) -> dict | None:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    background = cv2.medianBlur(gray, 51)
    dark_delta = background.astype(np.int16) - gray.astype(np.int16)
    valid = (gray > 8) & (gray < 240)
    if int(valid.sum()) < 1000:
        return None

    threshold = max(12.0, float(np.percentile(dark_delta[valid], 99.0)))
    raw = ((dark_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((11, 3), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((4, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 8 or area > 3000:
            continue
        if w < 12 or h > 45:
            continue
        aspect = float(w) / max(1.0, float(h))
        if aspect < 2.0:
            continue

        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        values = gray[labels == label]
        deltas = dark_delta[labels == label]
        contrast_delta = float(deltas.max())
        score = (
            contrast_delta * 5.0
            + float(area) * 0.2
            + aspect * 15.0
            - min(abs(full_y - 775.0), 100.0)
            - max(0.0, full_x - 700.0) * 2.0
        )
        candidates.append(
            {
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "aspect_ratio": aspect,
                "center_x": full_x,
                "center_y": full_y,
                "component_min_luma": int(values.min()),
                "component_max_luma": int(values.max()),
                "component_mean_luma": float(values.mean()),
                "local_median_luma": float(np.median(background[labels == label])),
                "dark_contrast_delta_luma": contrast_delta,
                "detection_threshold": threshold,
                "score": score,
                "bottom_third_proxy": BOTTOM_THIRD_Y0 <= full_y <= BOTTOM_THIRD_Y1,
            }
        )

    if not candidates:
        return None
    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    return best if best["score"] >= 400.0 else None


def classify_candidate(candidate: dict | None) -> tuple[str, str]:
    if candidate is None:
        return "none", "no lane-compatible dark elongated candidate recovered"

    score = float(candidate["score"])
    width = int(candidate["bbox_w"])
    area = int(candidate["area"])
    aspect = float(candidate["aspect_ratio"])
    contrast = float(candidate["dark_contrast_delta_luma"])
    center_x = float(candidate["center_x"])
    center_y = float(candidate["center_y"])
    y_ok = 735.0 <= center_y <= 820.0
    x_ok = center_x <= 760.0

    if score >= 640.0 and x_ok and y_ok and width >= 60 and area >= 800 and aspect >= 4.0 and contrast >= 55.0:
        return "high", "strong dark elongated bottom-third candidate aligned with DVIDS left-to-right crossing"
    if score >= 540.0 and x_ok and y_ok and width >= 50 and area >= 600 and aspect >= 3.5 and contrast >= 45.0:
        return "medium", "usable bottom-third candidate, but weaker than high-confidence streak frames"
    return "low", "candidate is weak or outside the narrow PR19 bottom-third streak profile"


def row_for_frame(frame_index: int, fps: float, frame: np.ndarray) -> dict:
    second = frame_index / fps
    phase, phase_note = dvids_phase(second)
    candidate = detect_bottom_third_streak(frame)
    quality, note = classify_candidate(candidate)
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
        "bbox_x": "",
        "bbox_y": "",
        "bbox_w": "",
        "bbox_h": "",
        "component_area": "",
        "aspect_ratio": "",
        "center_x": "",
        "center_y": "",
        "component_min_luma": "",
        "component_max_luma": "",
        "component_mean_luma": "",
        "local_median_luma": "",
        "dark_contrast_delta_luma": "",
        "detection_threshold": "",
        "score": "",
        "bottom_third_proxy": "",
        "notes": note,
    }
    if candidate is not None:
        row.update(
            {
                "bbox_x": ROI_X0 + int(candidate["roi_x"]),
                "bbox_y": ROI_Y0 + int(candidate["roi_y"]),
                "bbox_w": int(candidate["bbox_w"]),
                "bbox_h": int(candidate["bbox_h"]),
                "component_area": int(candidate["area"]),
                "aspect_ratio": round(float(candidate["aspect_ratio"]), 6),
                "center_x": round(float(candidate["center_x"]), 3),
                "center_y": round(float(candidate["center_y"]), 3),
                "component_min_luma": int(candidate["component_min_luma"]),
                "component_max_luma": int(candidate["component_max_luma"]),
                "component_mean_luma": round(float(candidate["component_mean_luma"]), 6),
                "local_median_luma": round(float(candidate["local_median_luma"]), 6),
                "dark_contrast_delta_luma": round(float(candidate["dark_contrast_delta_luma"]), 6),
                "detection_threshold": round(float(candidate["detection_threshold"]), 6),
                "score": round(float(candidate["score"]), 6),
                "bottom_third_proxy": bool(candidate["bottom_third_proxy"]),
            }
        )
    return row


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
    previous_frame = int(supported[0]["frame_index"])
    previous_second = float(supported[0]["second"])
    for row in supported[1:]:
        frame_index = int(row["frame_index"])
        second = float(row["second"])
        if frame_index == previous_frame + 1:
            previous_frame = frame_index
            previous_second = second
            continue
        intervals.append((start, previous_second))
        start = second
        previous_frame = frame_index
        previous_second = second
    intervals.append((start, previous_second))
    return "; ".join(f"{start:.3f}s-{end:.3f}s" for start, end in intervals)


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


def candidate_track_summary(rows: list[dict]) -> dict:
    supported = [row for row in rows if row["review_quality"] in {"high", "medium"}]
    if len(supported) < 2:
        return {
            "metric": "supported_candidate_track",
            "value": len(supported),
            "note": "insufficient supported rows for image-plane track summary",
        }
    points = [(float(row["second"]), float(row["center_x"]), float(row["center_y"])) for row in supported]
    net = math.hypot(points[-1][1] - points[0][1], points[-1][2] - points[0][2])
    path = 0.0
    step_rates: list[float] = []
    for prev, curr in zip(points, points[1:]):
        dt = curr[0] - prev[0]
        step = math.hypot(curr[1] - prev[1], curr[2] - prev[2])
        path += step
        if dt > 0:
            step_rates.append(step / dt)
    span = max(points[-1][0] - points[0][0], 1e-9)
    return {
        "metric": "supported_candidate_track",
        "value": len(supported),
        "note": (
            f"{points[0][0]:.3f}s-{points[-1][0]:.3f}s; "
            f"dx={points[-1][1] - points[0][1]:.3f}px; dy={points[-1][2] - points[0][2]:.3f}px; "
            f"net={net:.3f}px; path={path:.3f}px; path_rate={path / span:.3f}px/s; "
            f"median_step_rate={statistics.median(step_rates):.3f}px/s; image-plane only, not physical speed validation"
        ),
    }


def build_summary_rows(rows: list[dict], source_video: Path, fps: float, total_frames: int, duration: float) -> list[dict]:
    supported = [row for row in rows if row["review_quality"] in {"high", "medium"}]
    counts = Counter(row["review_quality"] for row in rows)
    phase_counts = Counter(row["phase"] for row in supported)
    summary_rows = [
        {"metric": "video", "value": VIDEO_NAME, "note": f"source video used: {source_video}"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "report_id", "value": REPORT_ID, "note": "DVIDS-stated accompanying mission report"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "dense_frame_count", "value": len(rows), "note": "all decoded frames reviewed"},
        {"metric": "supported_high_or_medium_frames", "value": len(supported), "note": "frames with usable bottom-third dark elongated candidate"},
        {"metric": "supported_intervals", "value": supported_intervals(rows), "note": "dense-frame supported interval(s)"},
        candidate_track_summary(rows),
        numeric_summary("component_area", [float(row["component_area"]) for row in supported], "selected bottom-third candidate pixel area"),
        numeric_summary("dark_contrast_delta_luma", [float(row["dark_contrast_delta_luma"]) for row in supported], "local background minus candidate minimum/mean dark contrast proxy"),
        numeric_summary("aspect_ratio", [float(row["aspect_ratio"]) for row in supported], "selected candidate horizontal elongation proxy"),
        numeric_summary("target_center_x", [float(row["center_x"]) for row in supported], "selected candidate x-position"),
        numeric_summary("target_center_y", [float(row["center_y"]) for row in supported], "selected candidate y-position"),
    ]
    if supported:
        first = float(supported[0]["second"])
        last = float(supported[-1]["second"])
        coverage = (int(supported[-1]["frame_index"]) - int(supported[0]["frame_index"]) + 1) / fps
        summary_rows.append(
            {
                "metric": "supported_center_span_seconds",
                "value": round(last - first, 3),
                "note": f"frame-center span; inclusive frame coverage is {coverage:.3f}s",
            }
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
    if row["review_quality"] in {"high", "medium", "low"} and row["bbox_x"] != "":
        x = int(row["bbox_x"])
        y = int(row["bbox_y"])
        w = int(row["bbox_w"])
        h = int(row["bbox_h"])
        color = (0, 255, 0) if row["review_quality"] == "high" else (0, 200, 255)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 3)
        cv2.drawMarker(
            annotated,
            (int(float(row["center_x"])), int(float(row["center_y"]))),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=30,
            thickness=2,
        )
    label = f'{row["second"]:.3f}s {row["review_quality"]}'
    cv2.putText(annotated, label, (70, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 4, cv2.LINE_AA)
    return annotated


def make_visual_assets(video: Path, rows: list[dict]) -> list[dict]:
    ensure_dir(OUT_ROOT)
    supported = [row for row in rows if row["review_quality"] in {"high", "medium"}]
    focus_frames = sorted(
        {
            max(0, int(row["frame_index"]) + offset)
            for row in supported
            for offset in range(-3, 4)
            if 0 <= int(row["frame_index"]) + offset < len(rows)
        }
    )
    if not focus_frames:
        focus_frames = list(range(0, min(len(rows), 12)))

    patch_images: list[np.ndarray] = []
    full_images: list[np.ndarray] = []
    for frame_index in focus_frames:
        frame = read_frame_at(video, frame_index)
        if frame is None:
            continue
        row = rows[frame_index]
        annotated = draw_row(frame, row)
        full_images.append(cv2.resize(annotated, (480, 270), interpolation=cv2.INTER_AREA))
        crop = annotated[650:880, 0:900].copy()
        crop = cv2.resize(crop, (540, 138), interpolation=cv2.INTER_AREA)
        crop_label = f'{row["second"]:.3f}s {row["review_quality"]}'
        cv2.putText(crop, crop_label, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        patch_images.append(crop)

    assets: list[dict] = []
    if patch_images:
        rows_img = []
        for index in range(0, len(patch_images), 2):
            chunk = patch_images[index : index + 2]
            while len(chunk) < 2:
                chunk.append(np.zeros_like(patch_images[0]))
            rows_img.append(np.hstack(chunk))
        patch_sheet = np.vstack(rows_img)
        patch_path = OUT_ROOT / f"{VIDEO_ID}-pr19-d10-bottom-third-patches.jpg"
        cv2.imwrite(str(patch_path), patch_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "patch_sheet", "path": str(patch_path).replace("\\", "/"), "note": "lower-third dense event window with detections"})

    if full_images:
        rows_img = []
        for index in range(0, len(full_images), 3):
            chunk = full_images[index : index + 3]
            while len(chunk) < 3:
                chunk.append(np.zeros_like(full_images[0]))
            rows_img.append(np.hstack(chunk))
        full_sheet = np.vstack(rows_img)
        full_path = OUT_ROOT / f"{VIDEO_ID}-pr19-d10-bottom-third-annotated.jpg"
        cv2.imwrite(str(full_path), full_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "annotated_sheet", "path": str(full_path).replace("\\", "/"), "note": "full-frame ROI and candidate annotations"})

    assets.insert(0, {"artifact_type": "source_video", "path": str(video).replace("\\", "/"), "note": "source video used for PR19/D10 review"})
    return assets


def run(video: Path) -> None:
    source_video, cap = open_capture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if fps else 0.0

    rows: list[dict] = []
    frame_index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        rows.append(row_for_frame(frame_index, fps, frame))
        frame_index += 1
    cap.release()

    if not rows:
        raise RuntimeError(f"No frames decoded from {source_video}")

    review_path = Path("research/ufo-video-pr19-d10-bottom-third-review-dod111688723.csv")
    summary_path = Path("research/ufo-video-pr19-d10-bottom-third-review-summary.csv")
    assets_path = Path("research/ufo-video-pr19-d10-bottom-third-review-assets.csv")

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
    parser = argparse.ArgumentParser(description="PR19/D10 bottom-third dark streak review")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO, help="Path to DOD_111688723.mp4")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.video)

