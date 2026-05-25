from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689051"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR38"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689051.mp4")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr38-startrail-review") / VIDEO_ID

ROI_X0 = 110
ROI_Y0 = 100
ROI_X1 = 1725
ROI_Y1 = 970
RETICLE_X = 960.0
RETICLE_Y = 540.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def dvids_phase(second: float) -> tuple[str, str]:
    if second < 10.0:
        return "initial star-like contrast", "DVIDS 00:00-00:09: initial area of contrast before zoom"
    if second < 11.0:
        return "zoom-in event", "DVIDS 00:10: sensor field of view narrows to zoom in on the area of contrast"
    if second < 30.0:
        return "star-like movement with trail", "DVIDS 00:11-00:29: area of contrast moves in field of view, followed by a visible trail"
    if second < 35.0:
        return "bottom-right exit and cut gap", "DVIDS 00:30-00:34: area leaves the field of view at the bottom right, before an apparent cut"
    if second < 104.0:
        return "post-cut in-field star-like contrast", "DVIDS 00:35-01:43: following apparent cut, area generally remains within field of view"
    return "top-left exit", "DVIDS 01:44-end: area exits frame from the top-left quarter"


def fixed_overlay_mask(shape: tuple[int, int, int]) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)

    # Fixed redaction blocks and persistent sensor symbology. These are broad
    # enough to suppress the repeated black bars without masking the PR38 target.
    fixed_boxes = [
        (0, 0, 135, 1080),
        (1760, 0, 1920, 1080),
        (0, 0, 1920, 90),
        (0, 990, 1920, 1080),
        (705, 0, 1135, 130),
        (1280, 0, 1810, 205),
        (1450, 220, 1730, 370),
        (840, 820, 1265, 940),
        (1280, 800, 1665, 925),
        (1480, 425, 1665, 725),
        (890, 475, 1030, 615),
        (570, 250, 690, 360),
        (1235, 250, 1365, 365),
        (560, 760, 705, 880),
        (1225, 760, 1375, 880),
        (620, 600, 735, 705),
        (390, 520, 530, 625),
        (360, 670, 540, 760),
        (1420, 640, 1600, 705),
    ]
    for x0, y0, x1, y1 in fixed_boxes:
        cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(width, x1), min(height, y1)), 255, -1)
    return mask


def detect_components(frame: np.ndarray) -> list[dict]:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    roi = gray[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    overlay = fixed_overlay_mask(frame.shape)[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    valid = (roi > 8) & (roi < 248) & (overlay == 0)
    if int(valid.sum()) < 1000:
        return []

    background = cv2.medianBlur(roi, 71)
    dark_delta = background.astype(np.int16) - roi.astype(np.int16)
    threshold = max(18.0, float(np.percentile(dark_delta[valid], 99.10)))
    raw = ((dark_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)
    components: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 8 or area > 10000:
            continue
        if w < 3 or h < 3 or w > 320 or h > 320:
            continue
        values = roi[labels == label]
        if values.size == 0:
            continue
        center_x = ROI_X0 + float(centroids[label][0])
        center_y = ROI_Y0 + float(centroids[label][1])
        contrast = float(dark_delta[labels == label].max())
        fill = area / max(1, w * h)
        aspect = max(w / max(1, h), h / max(1, w))
        edge_margin = min(center_x - ROI_X0, ROI_X1 - center_x, center_y - ROI_Y0, ROI_Y1 - center_y)

        if fill > 0.75 and area < 180:
            continue
        if aspect > 9.0 and area < 1200:
            continue

        score = (
            contrast * 7.0
            + min(int(area), 2500) * 0.8
            + min(int(w * h), 12000) * 0.04
            + max(w, h) * 1.2
            - min(math.hypot(center_x - RETICLE_X, center_y - RETICLE_Y), 900.0) * 0.03
            - max(0.0, 35.0 - edge_margin) * 4.0
        )
        components.append(
            {
                "x": ROI_X0 + int(x),
                "y": ROI_Y0 + int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area),
                "center_x": center_x,
                "center_y": center_y,
                "min_luma": int(values.min()),
                "mean_luma": float(values.mean()),
                "dark_contrast_delta": contrast,
                "fill_ratio": fill,
                "aspect_ratio": aspect,
                "edge_margin_px": edge_margin,
                "threshold": threshold,
                "score": score,
            }
        )
    components.sort(key=lambda item: item["score"], reverse=True)
    return components


def group_components(components: list[dict]) -> list[dict]:
    used = [False] * len(components)
    groups: list[dict] = []
    for index, component in enumerate(components):
        if used[index]:
            continue
        group = [component]
        used[index] = True
        changed = True
        while changed:
            changed = False
            for candidate_index, candidate in enumerate(components):
                if used[candidate_index]:
                    continue
                if any(math.hypot(candidate["center_x"] - item["center_x"], candidate["center_y"] - item["center_y"]) <= 85.0 for item in group):
                    group.append(candidate)
                    used[candidate_index] = True
                    changed = True

        total_area = sum(int(item["area"]) for item in group)
        if total_area <= 0:
            continue
        x0 = min(int(item["x"]) for item in group)
        y0 = min(int(item["y"]) for item in group)
        x1 = max(int(item["x"]) + int(item["w"]) for item in group)
        y1 = max(int(item["y"]) + int(item["h"]) for item in group)
        center_x = sum(float(item["center_x"]) * int(item["area"]) for item in group) / total_area
        center_y = sum(float(item["center_y"]) * int(item["area"]) for item in group) / total_area
        bbox_w = x1 - x0
        bbox_h = y1 - y0
        fill = total_area / max(1, bbox_w * bbox_h)
        aspect = max(bbox_w / max(1, bbox_h), bbox_h / max(1, bbox_w))
        contrast = max(float(item["dark_contrast_delta"]) for item in group)
        edge_margin = min(center_x - ROI_X0, ROI_X1 - center_x, center_y - ROI_Y0, ROI_Y1 - center_y)
        distance_from_reticle = math.hypot(center_x - RETICLE_X, center_y - RETICLE_Y)
        star_like_proxy = bbox_w >= 22 and bbox_h >= 22 and fill <= 0.65 and contrast >= 35.0
        score = (
            sum(float(item["score"]) for item in group)
            + (280.0 if star_like_proxy else 0.0)
            + min(bbox_w, bbox_h) * 2.0
            - max(0.0, aspect - 4.0) * 100.0
        )
        groups.append(
            {
                "components": group,
                "component_count": len(group),
                "star_like_proxy": star_like_proxy,
                "x": x0,
                "y": y0,
                "w": bbox_w,
                "h": bbox_h,
                "area": total_area,
                "center_x": center_x,
                "center_y": center_y,
                "min_luma": min(int(item["min_luma"]) for item in group),
                "mean_luma": sum(float(item["mean_luma"]) * int(item["area"]) for item in group) / total_area,
                "dark_contrast_delta": contrast,
                "fill_ratio": fill,
                "aspect_ratio": aspect,
                "edge_margin_px": edge_margin,
                "distance_from_reticle_px": distance_from_reticle,
                "score": score,
            }
        )
    groups.sort(key=lambda item: item["score"], reverse=True)
    return groups


def phase_adjusted_score(group: dict, second: float) -> float:
    score = float(group["score"])
    x = float(group["center_x"])
    y = float(group["center_y"])
    edge = float(group["edge_margin_px"])
    star_like = bool(group["star_like_proxy"])

    if second < 10.0:
        score -= min(math.hypot(x - RETICLE_X, y - RETICLE_Y), 1000.0) * 0.30
        if edge < 45.0:
            score -= 500.0
    elif second < 30.0:
        if star_like and x >= 850.0 and y >= 560.0:
            score += 300.0
        if edge < 20.0 and second < 29.0:
            score -= 250.0
    elif second < 35.0:
        if x >= 1300.0 and y >= 700.0:
            score += 100.0
        if edge < 25.0:
            score -= 100.0
    elif second < 104.0:
        if star_like and 350.0 <= x <= 1650.0 and 250.0 <= y <= 910.0:
            score += 250.0
        if edge < 25.0:
            score -= 250.0
    else:
        if star_like and x <= 1150.0 and y <= 620.0:
            score += 450.0
        if x > 1300.0 or y > 800.0:
            score -= 500.0
    return score


def detect_target(frame: np.ndarray, second: float) -> tuple[dict | None, int]:
    groups = group_components(detect_components(frame))
    if not groups:
        return None, 0
    groups.sort(key=lambda item: phase_adjusted_score(item, second), reverse=True)
    return groups[0], len(groups)


def classify(group: dict | None, second: float) -> tuple[str, str]:
    phase, _ = dvids_phase(second)
    if group is None:
        return "none", "no dark star-like contrast group survived overlay filtering"

    contrast = float(group["dark_contrast_delta"])
    area = int(group["area"])
    edge = float(group["edge_margin_px"])
    star_like = bool(group["star_like_proxy"])
    x = float(group["center_x"])
    y = float(group["center_y"])

    if phase == "initial star-like contrast":
        initial_lane = 600.0 <= x <= 1250.0 and 500.0 <= y <= 870.0 and math.hypot(x - RETICLE_X, y - RETICLE_Y) <= 430.0
        if star_like and contrast >= 45.0 and area >= 35 and edge >= 80.0 and initial_lane:
            return "medium", "initial area recovered; support capped because target is small before zoom"
        if contrast >= 30.0 and area >= 18 and edge >= 70.0 and initial_lane:
            return "low", "weak pre-zoom area of contrast near the central field"
        return "none", "pre-zoom mark is too weak, edge-confounded, or inconsistent with the central area"

    if phase == "bottom-right exit and cut gap":
        if star_like and contrast >= 50.0 and area >= 40 and x >= 1250.0 and y >= 650.0:
            return "medium", "edge/exit-phase star-like group recovered near the bottom-right lane"
        if contrast >= 35.0 and x >= 1200.0 and y >= 620.0:
            return "low", "weak bottom-right exit residual"
        return "none", "cut-gap/exit phase does not contain a usable in-frame target group"

    if phase == "top-left exit":
        if star_like and contrast >= 45.0 and area >= 35 and x <= 1200.0 and y <= 650.0:
            return "medium", "top-left exit-phase group recovered; support capped near the end of frame sequence"
        if contrast >= 30.0 and x <= 1250.0 and y <= 700.0:
            return "low", "weak top-left exit residual"
        return "none", "late mark is inconsistent with the top-left exit lane"

    if star_like and contrast >= 65.0 and area >= 80 and edge >= 25.0:
        if phase == "star-like movement with trail":
            return "high", "dark star-like contrast group recovered during DVIDS trail/movement interval"
        return "high", "dark star-like contrast group recovered in the sensor field"
    if star_like and contrast >= 45.0 and area >= 35 and edge >= 18.0:
        return "medium", "usable star-like group, but contrast, size, or overlay separation is weaker"
    if contrast >= 30.0 and area >= 18:
        return "low", "weak or partially overlay-confounded dark contrast group"
    return "none", "candidate is too weak for the PR38 star-like target"


def sample_seconds(duration: float, sample_rate: float) -> list[float]:
    seconds = []
    count = int(math.floor(duration * sample_rate)) + 1
    for index in range(count):
        second = round(index / sample_rate, 3)
        if second <= duration:
            seconds.append(second)
    return seconds


def annotate_frame(frame: np.ndarray, group: dict | None, second: float, quality: str, phase: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (75, 75, 75), 1)
    if group is not None:
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        x0 = int(group["x"])
        y0 = int(group["y"])
        x1 = x0 + int(group["w"])
        y1 = y0 + int(group["h"])
        cv2.rectangle(out, (x0 - 7, y0 - 7), (x1 + 7, y1 + 7), color, 2)
        cv2.drawMarker(
            out,
            (int(round(group["center_x"])), int(round(group["center_y"]))),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=22,
            thickness=1,
        )
    cv2.rectangle(out, (0, 0), (1280, 42), (0, 0, 0), -1)
    cv2.putText(
        out,
        f"PR38 t={second:.1f}s quality={quality} phase={phase}",
        (10, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.62,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return out


def annotate_patch(frame: np.ndarray, group: dict | None, second: float, quality: str) -> np.ndarray:
    if group is None:
        cx, cy = RETICLE_X, RETICLE_Y
    else:
        cx = float(group["center_x"])
        cy = float(group["center_y"])
    half = 135
    x0 = max(0, int(round(cx - half)))
    y0 = max(0, int(round(cy - half)))
    x1 = min(frame.shape[1], int(round(cx + half)))
    y1 = min(frame.shape[0], int(round(cy + half)))
    crop = frame[y0:y1, x0:x1].copy()
    if crop.size == 0:
        crop = np.zeros((270, 270, 3), dtype=np.uint8)
    if group is not None:
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        cv2.rectangle(
            crop,
            (int(group["x"] - x0), int(group["y"] - y0)),
            (int(group["x"] + group["w"] - x0), int(group["y"] + group["h"] - y0)),
            color,
            1,
        )
    patch = cv2.resize(crop, (360, 360), interpolation=cv2.INTER_NEAREST)
    cv2.rectangle(patch, (0, 0), (360, 34), (0, 0, 0), -1)
    cv2.putText(patch, f"{second:.1f}s {quality}", (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
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


def star_supported_rows(rows: list[dict]) -> list[dict]:
    return [row for row in supported_rows(rows) if row["star_like_proxy"] == "yes"]


def supported_interval_summary(rows: list[dict], metric: str, star_only: bool = False) -> dict:
    source_rows = star_supported_rows(rows) if star_only else supported_rows(rows)
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
    supported = star_supported_rows(rows)
    if len(supported) < 2:
        return {"metric": "star_like_group_track", "value": len(supported), "note": "fewer than two supported star-like rows"}
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
        "metric": "star_like_group_track",
        "value": len(supported),
        "note": (
            f"{supported[0]['approx_second']}s-{supported[-1]['approx_second']}s; "
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
    return {"metric": metric, "value": round(median, 3), "note": f"median; mean={mean:.3f}; stdev={stdev:.3f}; cv={cv:.3f}; {note}"}


def main() -> None:
    parser = argparse.ArgumentParser(description="PR38 one-fps dark star-like contrast review for DOD_111689051.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=1.0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
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
        group, candidate_count = detect_target(frame, actual_second)
        quality, caveat = classify(group, actual_second)
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, group, actual_second, quality, phase), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, group, actual_second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
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
                "candidate_group_count": candidate_count,
                "target_center_x": "" if group is None else round(float(group["center_x"]), 1),
                "target_center_y": "" if group is None else round(float(group["center_y"]), 1),
                "bbox_x0": "" if group is None else int(group["x"]),
                "bbox_y0": "" if group is None else int(group["y"]),
                "bbox_w": "" if group is None else int(group["w"]),
                "bbox_h": "" if group is None else int(group["h"]),
                "component_count": "" if group is None else int(group["component_count"]),
                "star_like_proxy": "no" if group is None or not group["star_like_proxy"] else "yes",
                "component_area": "" if group is None else int(group["area"]),
                "component_min_luma": "" if group is None else int(group["min_luma"]),
                "dark_contrast_delta": "" if group is None else round(float(group["dark_contrast_delta"]), 2),
                "fill_ratio": "" if group is None else round(float(group["fill_ratio"]), 4),
                "aspect_ratio": "" if group is None else round(float(group["aspect_ratio"]), 3),
                "distance_from_reticle_px": "" if group is None else round(float(group["distance_from_reticle_px"]), 2),
                "edge_margin_px": "" if group is None else round(float(group["edge_margin_px"]), 2),
                "raw_score": "" if group is None else round(float(group["score"]), 3),
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr38-startrail-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr38-startrail-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr38-startrail-review-dod111689051.csv")
    summary_csv = Path("research/ufo-video-pr38-startrail-review-summary.csv")
    asset_csv = Path("research/ufo-video-pr38-startrail-review-assets.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    supported = supported_rows(rows)
    star_supported = star_supported_rows(rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    phase_supported_counts = Counter(row["dvids_phase"] for row in supported)
    phase_star_counts = Counter(row["dvids_phase"] for row in star_supported)
    areas = [float(row["component_area"]) for row in supported if row["component_area"] != ""]
    contrasts = [float(row["dark_contrast_delta"]) for row in supported if row["dark_contrast_delta"] != ""]
    reticle_offsets = [float(row["distance_from_reticle_px"]) for row in supported if row["distance_from_reticle_px"] != ""]
    edge_margins = [float(row["edge_margin_px"]) for row in supported if row["edge_margin_px"] != ""]
    bbox_widths = [float(row["bbox_w"]) for row in supported if row["bbox_w"] != ""]
    bbox_heights = [float(row["bbox_h"]) for row in supported if row["bbox_h"] != ""]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable dark contrast group"},
        {"metric": "star_like_proxy_supported_rows", "value": len(star_supported), "note": "supported rows with star-like bbox/fill proxy"},
        supported_interval_summary(rows, "supported_intervals"),
        supported_interval_summary(rows, "star_like_proxy_supported_intervals", star_only=True),
        track_stats(rows),
        numeric_summary("component_area", areas, "selected dark star-like group pixel area"),
        numeric_summary("dark_contrast_delta", contrasts, "local median luma minus selected group min/dark luma proxy"),
        numeric_summary("distance_from_reticle_px", reticle_offsets, "selected group distance from central reticle"),
        numeric_summary("edge_margin_px", edge_margins, "selected group distance from central ROI edge"),
        numeric_summary("bbox_width_px", bbox_widths, "selected group bounding-box width"),
        numeric_summary("bbox_height_px", bbox_heights, "selected group bounding-box height"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "review quality"})
    for key, value in sorted(phase_supported_counts.items()):
        summary_rows.append({"metric": f"supported_phase_count: {key}", "value": value, "note": "supported rows by DVIDS phase"})
    for key, value in sorted(phase_star_counts.items()):
        summary_rows.append({"metric": f"star_like_phase_count: {key}", "value": value, "note": "star-like proxy rows by DVIDS phase"})
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "startrail_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR38 one-fps star-like contrast review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR38 star-like contrast review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR38 annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR38 target patch sheet"})
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"supported={len(supported)} star_like_proxy_supported={len(star_supported)}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

