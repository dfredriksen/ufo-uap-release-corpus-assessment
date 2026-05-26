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


VIDEO_ID = "DOD_111688762"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR21"
REPORT_ID = "DoW-UAP-D14"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111688762.mp4"
FALLBACK_VIDEO = Path("research/ufo-derived/video-motion-pass/pr21-d14-two-area-review/source") / VIDEO_NAME
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr21-d14-two-area-review") / VIDEO_ID

ROI_X0 = 680
ROI_Y0 = 300
ROI_X1 = 1250
ROI_Y1 = 780
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
    raise RuntimeError(f"Could not open any PR21 source video: {tried}")


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 10.0:
        return "central two-area runtime", "DVIDS: two areas of contrast move together near center field throughout runtime"
    return "late terminal frame", "final brightened/noisy end sample; treat as low-confidence context"


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    mask = ((sat > 35) & (val > 35) & (hue >= 35) & (hue <= 115)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def fixed_overlay_mask(shape: tuple[int, int, int]) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)
    boxes = [
        (0, 0, 165, 1080),
        (1760, 0, 1920, 1080),
        (0, 0, 1920, 70),
        (0, 1060, 1920, 1080),
        (840, 0, 1105, 90),
        (1170, 0, 1305, 65),
        (1390, 0, 1505, 65),
        (1700, 0, 1920, 80),
        (935, 520, 1048, 650),
        (890, 470, 1035, 610),
        (610, 420, 735, 560),
        (1680, 760, 1920, 1080),
    ]
    for x0, y0, x1, y1 in boxes:
        cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(width, x1), min(height, y1)), 255, -1)
    return mask


def compact_contrast_candidates(frame: np.ndarray) -> list[dict]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay = cv2.bitwise_or(colored_overlay_mask(frame), fixed_overlay_mask(frame.shape))
    overlay = cv2.dilate(overlay, np.ones((7, 7), np.uint8), iterations=1)[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    valid = (gray > 20) & (gray < 245) & (overlay == 0)
    if int(valid.sum()) < 1000:
        return []

    background = cv2.medianBlur(gray, 45)
    signed_delta = gray.astype(np.int16) - background.astype(np.int16)
    abs_delta = np.abs(signed_delta)
    threshold = max(14.0, float(np.percentile(abs_delta[valid], 99.8)))
    raw = ((abs_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 2 or area > 160:
            continue
        if w > 26 or h > 26:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 4.5:
            continue

        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        values = gray[labels == label]
        signed_values = signed_delta[labels == label]
        abs_values = abs_delta[labels == label]
        mean_signed_delta = float(np.mean(signed_values))
        polarity = "bright" if mean_signed_delta >= 0 else "dark"
        contrast = float(np.max(abs_values))
        distance_from_reticle = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        in_central_lane = 760.0 <= full_x <= 1160.0 and 360.0 <= full_y <= 720.0
        score = (
            contrast * 5.0
            + int(area) * 2.0
            - min(distance_from_reticle, 350.0) * 0.35
            + (40.0 if in_central_lane else 0.0)
        )
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
                "polarity": polarity,
                "component_min_luma": int(values.min()),
                "component_max_luma": int(values.max()),
                "component_mean_luma": float(values.mean()),
                "mean_signed_delta_luma": mean_signed_delta,
                "contrast_delta_luma": contrast,
                "distance_from_reticle_px": distance_from_reticle,
                "detection_threshold": threshold,
                "raw_score": score,
            }
        )
    candidates.sort(key=lambda item: item["raw_score"], reverse=True)
    return candidates[:20]


def select_two_area_pair(candidates: list[dict]) -> dict | None:
    best: dict | None = None
    for left_index, first in enumerate(candidates):
        for second in candidates[left_index + 1 :]:
            separation = math.hypot(first["center_x"] - second["center_x"], first["center_y"] - second["center_y"])
            if separation < 12.0 or separation > 180.0:
                continue
            center_x = (first["center_x"] + second["center_x"]) / 2.0
            center_y = (first["center_y"] + second["center_y"]) / 2.0
            center_distance = math.hypot(center_x - RETICLE_X, center_y - RETICLE_Y)
            if center_distance > 260.0:
                continue
            x_spread = abs(first["center_x"] - second["center_x"])
            y_spread = abs(first["center_y"] - second["center_y"])
            pair_score = (
                first["raw_score"]
                + second["raw_score"]
                - center_distance * 0.7
                - separation * 0.25
                - max(0.0, y_spread - 100.0) * 0.5
                + min(x_spread, 90.0) * 0.2
            )
            pair = {
                "first": first,
                "second": second,
                "pair_score": pair_score,
                "pair_center_x": center_x,
                "pair_center_y": center_y,
                "pair_separation_px": separation,
                "pair_x_spread_px": x_spread,
                "pair_y_spread_px": y_spread,
                "pair_center_distance_from_reticle_px": center_distance,
            }
            if best is None or pair_score > best["pair_score"]:
                best = pair
    return best


def classify_pair(pair: dict | None, second: float) -> tuple[str, str]:
    if pair is None:
        return "none", "no central two-area proxy recovered"
    if second >= 10.0:
        return "low", "late brightened/noisy terminal row; not reliable for two-area support"

    score = float(pair["pair_score"])
    center_distance = float(pair["pair_center_distance_from_reticle_px"])
    separation = float(pair["pair_separation_px"])
    if score >= 550.0 and center_distance <= 190.0 and 35.0 <= separation <= 175.0:
        return "high", "strong central two-area contrast proxy aligned with DVIDS description"
    if score >= 340.0 and center_distance <= 230.0 and 25.0 <= separation <= 180.0:
        return "medium", "usable central two-area contrast proxy, but terrain/texture confounds remain"
    return "low", "weak or poorly centered two-area proxy; retained as context only"


def row_for_sample(frame_index: int, second: float, frame: np.ndarray) -> dict:
    phase, phase_note = dvids_phase(second)
    candidates = compact_contrast_candidates(frame)
    pair = select_two_area_pair(candidates)
    quality, note = classify_pair(pair, second)
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
        "pair_score": "",
        "pair_center_x": "",
        "pair_center_y": "",
        "pair_separation_px": "",
        "pair_x_spread_px": "",
        "pair_y_spread_px": "",
        "pair_center_distance_from_reticle_px": "",
        "first_center_x": "",
        "first_center_y": "",
        "first_area": "",
        "first_bbox_w": "",
        "first_bbox_h": "",
        "first_polarity": "",
        "first_contrast_delta_luma": "",
        "second_center_x": "",
        "second_center_y": "",
        "second_area": "",
        "second_bbox_w": "",
        "second_bbox_h": "",
        "second_polarity": "",
        "second_contrast_delta_luma": "",
        "notes": note,
    }
    if pair is not None:
        first = pair["first"]
        second_candidate = pair["second"]
        row.update(
            {
                "pair_score": round(float(pair["pair_score"]), 6),
                "pair_center_x": round(float(pair["pair_center_x"]), 3),
                "pair_center_y": round(float(pair["pair_center_y"]), 3),
                "pair_separation_px": round(float(pair["pair_separation_px"]), 3),
                "pair_x_spread_px": round(float(pair["pair_x_spread_px"]), 3),
                "pair_y_spread_px": round(float(pair["pair_y_spread_px"]), 3),
                "pair_center_distance_from_reticle_px": round(float(pair["pair_center_distance_from_reticle_px"]), 3),
                "first_center_x": round(float(first["center_x"]), 3),
                "first_center_y": round(float(first["center_y"]), 3),
                "first_area": int(first["area"]),
                "first_bbox_w": int(first["bbox_w"]),
                "first_bbox_h": int(first["bbox_h"]),
                "first_polarity": first["polarity"],
                "first_contrast_delta_luma": round(float(first["contrast_delta_luma"]), 6),
                "second_center_x": round(float(second_candidate["center_x"]), 3),
                "second_center_y": round(float(second_candidate["center_y"]), 3),
                "second_area": int(second_candidate["area"]),
                "second_bbox_w": int(second_candidate["bbox_w"]),
                "second_bbox_h": int(second_candidate["bbox_h"]),
                "second_polarity": second_candidate["polarity"],
                "second_contrast_delta_luma": round(float(second_candidate["contrast_delta_luma"]), 6),
            }
        )
    return row


def sample_rows(video: Path) -> tuple[Path, list[dict], float, int, float]:
    source_video, cap = open_capture(video)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if fps else 0.0
    rows: list[dict] = []
    sample_seconds = list(range(0, int(math.floor(duration)) + 1))
    if not sample_seconds or sample_seconds[-1] < duration - 0.5:
        sample_seconds.append(duration - 1.0 / fps)
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


def pair_center_summary(rows: list[dict]) -> dict:
    supported = [row for row in rows if row["review_quality"] in {"high", "medium"} and row["pair_center_x"] != ""]
    if len(supported) < 2:
        return {"metric": "supported_pair_center_path", "value": len(supported), "note": "insufficient rows for pair-center path"}
    points = [(float(row["second"]), float(row["pair_center_x"]), float(row["pair_center_y"])) for row in supported]
    net = math.hypot(points[-1][1] - points[0][1], points[-1][2] - points[0][2])
    path = 0.0
    for prev, curr in zip(points, points[1:]):
        path += math.hypot(curr[1] - prev[1], curr[2] - prev[2])
    span = max(points[-1][0] - points[0][0], 1e-9)
    return {
        "metric": "supported_pair_center_path",
        "value": len(supported),
        "note": (
            f"{points[0][0]:.1f}s-{points[-1][0]:.1f}s; net={net:.3f}px; path={path:.3f}px; "
            f"path_rate={path / span:.3f}px/s; two-area proxy only, terrain/texture confounded"
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
        {"metric": "sample_count", "value": len(rows), "note": "one-fps full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable central two-area proxy"},
        {"metric": "supported_intervals", "value": supported_intervals(rows), "note": "one-fps supported interval(s)"},
        pair_center_summary(rows),
        numeric_summary("pair_score", [float(row["pair_score"]) for row in supported], "selected two-area pair score"),
        numeric_summary("pair_separation_px", [float(row["pair_separation_px"]) for row in supported], "distance between selected two areas"),
        numeric_summary(
            "pair_center_distance_from_reticle_px",
            [float(row["pair_center_distance_from_reticle_px"]) for row in supported],
            "selected pair-center distance from central reticle",
        ),
        numeric_summary("pair_center_x", [float(row["pair_center_x"]) for row in supported], "selected pair-center x-position"),
        numeric_summary("pair_center_y", [float(row["pair_center_y"]) for row in supported], "selected pair-center y-position"),
    ]
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
    if row["pair_center_x"] != "":
        color = (0, 255, 0) if row["review_quality"] == "high" else (0, 200, 255) if row["review_quality"] == "medium" else (0, 128, 255)
        first = (int(float(row["first_center_x"])), int(float(row["first_center_y"])))
        second = (int(float(row["second_center_x"])), int(float(row["second_center_y"])))
        cv2.circle(annotated, first, 18, color, 2)
        cv2.circle(annotated, second, 18, color, 2)
        cv2.line(annotated, first, second, color, 2)
        cv2.drawMarker(annotated, first, color, markerType=cv2.MARKER_CROSS, markerSize=24, thickness=2)
        cv2.drawMarker(annotated, second, color, markerType=cv2.MARKER_CROSS, markerSize=24, thickness=2)
    label = f'{row["second"]:.1f}s {row["review_quality"]}'
    cv2.putText(annotated, label, (70, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.6, (0, 255, 255), 4, cv2.LINE_AA)
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
        crop = annotated[280:780, 650:1280].copy()
        crop = cv2.resize(crop, (630, 500), interpolation=cv2.INTER_AREA)
        crop_label = f'{row["second"]:.1f}s {row["review_quality"]}'
        cv2.putText(crop, crop_label, (8, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2, cv2.LINE_AA)
        patch_images.append(crop)

    assets: list[dict] = [{"artifact_type": "source_video", "path": str(video).replace("\\", "/"), "note": "source video used for PR21/D14 review"}]
    if patch_images:
        patch_rows = []
        for index in range(0, len(patch_images), 2):
            chunk = patch_images[index : index + 2]
            while len(chunk) < 2:
                chunk.append(np.zeros_like(patch_images[0]))
            patch_rows.append(np.hstack(chunk))
        patch_sheet = np.vstack(patch_rows)
        patch_path = OUT_ROOT / f"{VIDEO_ID}-pr21-d14-two-area-patches.jpg"
        cv2.imwrite(str(patch_path), patch_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "patch_sheet", "path": str(patch_path).replace("\\", "/"), "note": "central two-area proxy patches"})

    if full_images:
        full_rows = []
        for index in range(0, len(full_images), 3):
            chunk = full_images[index : index + 3]
            while len(chunk) < 3:
                chunk.append(np.zeros_like(full_images[0]))
            full_rows.append(np.hstack(chunk))
        full_sheet = np.vstack(full_rows)
        full_path = OUT_ROOT / f"{VIDEO_ID}-pr21-d14-two-area-annotated.jpg"
        cv2.imwrite(str(full_path), full_sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        assets.append({"artifact_type": "annotated_sheet", "path": str(full_path).replace("\\", "/"), "note": "full-frame central ROI and pair annotations"})
    return assets


def run(video: Path) -> None:
    source_video, rows, fps, total_frames, duration = sample_rows(video)
    if not rows:
        raise RuntimeError(f"No PR21 rows generated from {source_video}")

    review_path = Path("research/ufo-video-pr21-d14-two-area-review-dod111688762.csv")
    summary_path = Path("research/ufo-video-pr21-d14-two-area-review-summary.csv")
    assets_path = Path("research/ufo-video-pr21-d14-two-area-review-assets.csv")

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
    parser = argparse.ArgumentParser(description="PR21/D14 central two-area proxy review")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO, help="Path to DOD_111688762.mp4")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.video)

