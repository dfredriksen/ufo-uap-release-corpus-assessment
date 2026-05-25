from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689168"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR49"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689168.mp4")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr49-two-area-review") / VIDEO_ID

ROI_X0 = 180
ROI_Y0 = 80
ROI_X1 = 1780
ROI_Y1 = 990
RETICLE_X = 960.0
RETICLE_Y = 540.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def dvids_phase(second: float) -> tuple[str, str, int]:
    if second < 9.0:
        return "initial area of interest", "DVIDS 00:00-00:08: sensor tracks an initial area of interest", 1
    if second < 17.0:
        return "two-area acquisition and zoom-in", "DVIDS 00:09-00:16: sensor pans right-to-left to track two areas of contrast while narrowing FOV", 2
    if second < 64.0:
        return "zoomed-out two-area tracking", "DVIDS 00:17-01:03: sensor widens FOV and keeps areas generally centered", 2
    if second < 69.0:
        return "rapid zoom cycling", "DVIDS 01:04-01:08: FOV rapidly cycles, making areas appear to change size", 2
    return "late two-area tracking", "DVIDS 01:09-01:48: sensor tracks areas of contrast while intermittently cycling contrast settings", 2


def fixed_overlay_mask(shape: tuple[int, int, int], include_reticle: bool) -> np.ndarray:
    height, width = shape[:2]
    mask = np.zeros((height, width), dtype=np.uint8)

    # Fixed redaction/status blocks and static symbology. The central reticle is
    # optionally excluded because the late target sometimes sits directly on it.
    fixed_boxes = [
        (0, 0, 180, 80),
        (0, 880, 240, 1080),
        (1680, 0, 1920, 210),
        (1660, 760, 1920, 1020),
        (650, 0, 1290, 175),
        (0, 400, 230, 720),
        (1300, 560, 1385, 660),  # N marker
        (450, 245, 520, 325),
        (1400, 245, 1475, 325),
        (450, 780, 520, 850),
        (1400, 780, 1475, 850),
    ]
    if include_reticle:
        fixed_boxes.append((900, 480, 1025, 600))
    for x0, y0, x1, y1 in fixed_boxes:
        cv2.rectangle(mask, (max(0, x0), max(0, y0)), (min(width, x1), min(height, y1)), 255, -1)
    return mask


def remove_line_artifacts(mask: np.ndarray) -> np.ndarray:
    horizontal = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((1, 33), np.uint8))
    vertical = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((33, 1), np.uint8))
    line_mask = cv2.dilate(cv2.bitwise_or(horizontal, vertical), np.ones((5, 5), np.uint8), iterations=1)
    return cv2.bitwise_and(mask, cv2.bitwise_not(line_mask))


def detect_components(frame: np.ndarray, include_reticle_mask: bool) -> list[dict]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay = fixed_overlay_mask(frame.shape, include_reticle_mask)[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    valid = (gray > 3) & (gray < 252) & (overlay == 0)
    if int(valid.sum()) < 1000:
        return []

    background = cv2.medianBlur(gray, 41)
    bright_delta = gray.astype(np.int16) - background.astype(np.int16)
    threshold = max(16.0, float(np.percentile(bright_delta[valid], 99.70)))
    raw = ((bright_delta >= threshold) & valid).astype(np.uint8) * 255
    raw = cv2.medianBlur(raw, 3)
    raw = remove_line_artifacts(raw)
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)
    components: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 2 or area > 600:
            continue
        if w > 90 or h > 70:
            continue
        if w <= 1 or h <= 1:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 9.0:
            continue
        values = gray[labels == label]
        local_patch = gray[max(0, y - 28) : min(gray.shape[0], y + h + 28), max(0, x - 28) : min(gray.shape[1], x + w + 28)]
        local_median = float(np.median(local_patch)) if local_patch.size else float(np.median(gray))
        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        distance_from_reticle = math.hypot(full_x - RETICLE_X, full_y - RETICLE_Y)
        edge_margin = min(full_x - ROI_X0, ROI_X1 - full_x, full_y - ROI_Y0, ROI_Y1 - full_y)
        max_luma = int(values.max())
        contrast_delta = max_luma - local_median
        fill = area / max(1, w * h)
        score = (
            contrast_delta * 5.0
            + min(int(area), 200) * 1.1
            + min(fill, 0.85) * 70.0
            + max_luma * 0.18
            - distance_from_reticle * 0.05
            - max(0.0, aspect - 4.0) * 10.0
            - max(0.0, 30.0 - edge_margin) * 2.0
        )
        components.append(
            {
                "x": ROI_X0 + int(x),
                "y": ROI_Y0 + int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area),
                "center_x": full_x,
                "center_y": full_y,
                "max_luma": max_luma,
                "mean_luma": float(values.mean()),
                "local_median_luma": local_median,
                "contrast_delta": contrast_delta,
                "distance_from_reticle_px": distance_from_reticle,
                "edge_margin_px": edge_margin,
                "threshold": threshold,
                "score": score,
            }
        )
    components.sort(key=lambda item: item["score"], reverse=True)
    return components


def component_groups(components: list[dict]) -> list[dict]:
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
                if any(math.hypot(candidate["center_x"] - item["center_x"], candidate["center_y"] - item["center_y"]) <= 90.0 for item in group):
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
        max_component_separation = 0.0
        if len(group) >= 2:
            max_component_separation = max(
                math.hypot(a["center_x"] - b["center_x"], a["center_y"] - b["center_y"]) for a in group for b in group
            )
        bbox_w = x1 - x0
        bbox_h = y1 - y0
        max_luma = max(int(item["max_luma"]) for item in group)
        contrast_delta = max(float(item["contrast_delta"]) for item in group)
        merged_two_area_proxy = bbox_w >= 24 and bbox_h >= 7 and total_area >= 55 and contrast_delta >= 70
        two_area_proxy = len(group) >= 2 or merged_two_area_proxy
        distance_from_reticle = math.hypot(center_x - RETICLE_X, center_y - RETICLE_Y)
        score = sum(float(item["score"]) for item in group) - distance_from_reticle * 0.08
        groups.append(
            {
                "components": group,
                "component_count": len(group),
                "two_area_proxy": two_area_proxy,
                "center_x": center_x,
                "center_y": center_y,
                "bbox_x0": x0,
                "bbox_y0": y0,
                "bbox_w": bbox_w,
                "bbox_h": bbox_h,
                "area": total_area,
                "max_luma": max_luma,
                "contrast_delta": contrast_delta,
                "distance_from_reticle_px": distance_from_reticle,
                "edge_margin_px": min(center_x - ROI_X0, ROI_X1 - center_x, center_y - ROI_Y0, ROI_Y1 - center_y),
                "max_component_separation_px": max_component_separation,
                "score": score,
            }
        )
    groups.sort(key=lambda item: item["score"], reverse=True)
    return groups


def detect_groups(frame: np.ndarray, allow_reticle_fallback: bool) -> tuple[list[dict], str]:
    groups = component_groups(detect_components(frame, include_reticle_mask=True))
    if groups or not allow_reticle_fallback:
        return groups, "overlay-suppressed"
    fallback = component_groups(detect_components(frame, include_reticle_mask=False))
    return fallback, "reticle-adjacent-fallback"


def select_group(groups: list[dict], required_areas: int) -> dict | None:
    if not groups:
        return None
    if required_areas == 1:
        return groups[0]
    two_area_groups = [group for group in groups if group["two_area_proxy"]]
    if two_area_groups:
        return two_area_groups[0]
    return groups[0]


def classify(group: dict | None, required_areas: int, detection_mode: str, second: float) -> tuple[str, str]:
    if group is None:
        return "none", "no compact bright area group survived filtering"
    contrast = float(group["contrast_delta"])
    area = int(group["area"])
    distance = float(group["distance_from_reticle_px"])
    two_area = bool(group["two_area_proxy"])
    component_count = int(group["component_count"])
    if detection_mode == "reticle-adjacent-fallback":
        return "medium", "target group is reticle-adjacent; support capped because overlay and target overlap"
    if required_areas == 1:
        if contrast >= 70 and area >= 15 and distance <= 650:
            return "medium", "initial area of interest recovered, but phase precedes DVIDS two-area tracking"
        return "low", "weak or partially obscured initial area of interest"
    if two_area and contrast >= 80 and area >= 40 and distance <= 700:
        if second >= 64.0 and second < 69.0:
            return "high", "two-area group recovered during rapid zoom-cycling interval"
        return "high", "two-area contrast group recovered in central field"
    if contrast >= 55 and area >= 18 and distance <= 760:
        return "medium", f"usable bright group, but two-area evidence is weaker (components={component_count})"
    if contrast >= 35 and distance <= 820:
        return "low", "weak, distant, or partially overlay-confounded bright group"
    return "none", "group is too weak or too far from the tracked center field"


def sample_seconds(duration: float, sample_rate: float) -> list[float]:
    count = int(math.floor(duration * sample_rate)) + 1
    seconds = []
    for index in range(count):
        second = round(index / sample_rate, 3)
        if second <= duration:
            seconds.append(second)
    return seconds


def annotate_frame(frame: np.ndarray, group: dict | None, second: float, quality: str, phase: str, detection_mode: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (70, 70, 70), 1)
    if group is not None:
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        x0 = int(group["bbox_x0"])
        y0 = int(group["bbox_y0"])
        x1 = x0 + int(group["bbox_w"])
        y1 = y0 + int(group["bbox_h"])
        cv2.rectangle(out, (x0 - 6, y0 - 6), (x1 + 6, y1 + 6), color, 2)
        cv2.drawMarker(
            out,
            (int(round(group["center_x"])), int(round(group["center_y"]))),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=18,
            thickness=1,
        )
        for component in group["components"]:
            cx = int(round(component["center_x"]))
            cy = int(round(component["center_y"]))
            cv2.circle(out, (cx, cy), 10, color, 1)
    cv2.rectangle(out, (0, 0), (1180, 40), (0, 0, 0), -1)
    cv2.putText(
        out,
        f"PR49 t={second:.1f}s quality={quality} phase={phase} mode={detection_mode}",
        (10, 27),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.58,
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
    half = 105
    x0 = max(0, int(round(cx - half)))
    y0 = max(0, int(round(cy - half)))
    x1 = min(frame.shape[1], int(round(cx + half)))
    y1 = min(frame.shape[0], int(round(cy + half)))
    crop = frame[y0:y1, x0:x1].copy()
    if crop.size == 0:
        crop = np.zeros((210, 210, 3), dtype=np.uint8)
    if group is not None:
        cv2.rectangle(
            crop,
            (int(group["bbox_x0"] - x0), int(group["bbox_y0"] - y0)),
            (int(group["bbox_x0"] + group["bbox_w"] - x0), int(group["bbox_y0"] + group["bbox_h"] - y0)),
            (0, 255, 0) if quality == "high" else (0, 255, 255),
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


def two_area_supported_rows(rows: list[dict]) -> list[dict]:
    return [row for row in supported_rows(rows) if row["required_area_count"] == 2 and row["two_area_proxy"] == "yes"]


def supported_interval_summary(rows: list[dict], metric: str, only_two_area: bool = False) -> dict:
    source_rows = two_area_supported_rows(rows) if only_two_area else supported_rows(rows)
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


def track_stats(rows: list[dict], metric: str) -> dict:
    supported = two_area_supported_rows(rows)
    if len(supported) < 2:
        return {"metric": metric, "value": len(supported), "note": "fewer than two supported two-area rows"}
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
        "metric": metric,
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
    parser = argparse.ArgumentParser(description="PR49 one-fps two-area contrast review for DOD_111689168.")
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
        phase, anchor, required_areas = dvids_phase(actual_second)
        groups, detection_mode = detect_groups(frame, allow_reticle_fallback=True)
        group = select_group(groups, required_areas)
        quality, caveat = classify(group, required_areas, detection_mode, actual_second)
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, group, actual_second, quality, phase, detection_mode), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
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
                "required_area_count": required_areas,
                "review_quality": quality,
                "detection_mode": detection_mode,
                "candidate_group_count": len(groups),
                "target_center_x": "" if group is None else round(float(group["center_x"]), 1),
                "target_center_y": "" if group is None else round(float(group["center_y"]), 1),
                "bbox_x0": "" if group is None else int(group["bbox_x0"]),
                "bbox_y0": "" if group is None else int(group["bbox_y0"]),
                "bbox_w": "" if group is None else int(group["bbox_w"]),
                "bbox_h": "" if group is None else int(group["bbox_h"]),
                "component_count": "" if group is None else int(group["component_count"]),
                "two_area_proxy": "no" if group is None or not group["two_area_proxy"] else "yes",
                "component_area": "" if group is None else int(group["area"]),
                "component_max_luma": "" if group is None else int(group["max_luma"]),
                "contrast_delta": "" if group is None else round(float(group["contrast_delta"]), 2),
                "distance_from_reticle_px": "" if group is None else round(float(group["distance_from_reticle_px"]), 2),
                "edge_margin_px": "" if group is None else round(float(group["edge_margin_px"]), 2),
                "max_component_separation_px": "" if group is None else round(float(group["max_component_separation_px"]), 2),
                "raw_score": "" if group is None else round(float(group["score"]), 3),
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr49-two-area-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr49-two-area-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr49-two-area-review-dod111689168.csv")
    summary_csv = Path("research/ufo-video-pr49-two-area-review-summary.csv")
    asset_csv = Path("research/ufo-video-pr49-two-area-review-assets.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    supported = supported_rows(rows)
    two_supported = two_area_supported_rows(rows)
    quality_counts = Counter(row["review_quality"] for row in rows)
    phase_supported_counts = Counter(row["dvids_phase"] for row in supported)
    phase_two_counts = Counter(row["dvids_phase"] for row in two_supported)
    mode_counts = Counter(row["detection_mode"] for row in supported)
    areas = [float(row["component_area"]) for row in supported if row["component_area"] != ""]
    contrasts = [float(row["contrast_delta"]) for row in supported if row["contrast_delta"] != ""]
    reticle_offsets = [float(row["distance_from_reticle_px"]) for row in supported if row["distance_from_reticle_px"] != ""]
    separations = [float(row["max_component_separation_px"]) for row in two_supported if row["max_component_separation_px"] != ""]

    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps full-clip samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable compact bright group"},
        {"metric": "two_area_proxy_supported_rows", "value": len(two_supported), "note": "supported rows with explicit or merged two-area proxy"},
        supported_interval_summary(rows, "supported_intervals"),
        supported_interval_summary(rows, "two_area_proxy_supported_intervals", only_two_area=True),
        track_stats(rows, "two_area_group_track"),
        numeric_summary("component_area", areas, "selected bright group pixel area"),
        numeric_summary("contrast_delta_luma", contrasts, "selected group max luma minus local median"),
        numeric_summary("distance_from_reticle_px", reticle_offsets, "selected group distance from central reticle"),
        numeric_summary("max_component_separation_px", separations, "two-area proxy component/group separation"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "review quality"})
    for key, value in sorted(phase_supported_counts.items()):
        summary_rows.append({"metric": f"supported_phase_count: {key}", "value": value, "note": "supported rows by DVIDS phase"})
    for key, value in sorted(phase_two_counts.items()):
        summary_rows.append({"metric": f"two_area_phase_count: {key}", "value": value, "note": "two-area proxy rows by DVIDS phase"})
    for key, value in sorted(mode_counts.items()):
        summary_rows.append({"metric": f"detection_mode_count: {key}", "value": value, "note": "supported rows by detection mode"})
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "two_area_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR49 one-fps two-area review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR49 two-area review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR49 annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR49 target patch sheet"})
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"supported={len(supported)} two_area_proxy_supported={len(two_supported)}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

