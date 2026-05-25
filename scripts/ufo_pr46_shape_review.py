from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689133"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR46"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689133.mp4")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr46-shape-review") / VIDEO_ID

ROI_X0 = 730
ROI_Y0 = 350
ROI_X1 = 1160
ROI_Y1 = 740
EXPECTED_CENTER_X = 985.0
EXPECTED_CENTER_Y = 525.0
TARGET_RADIUS_PX = 160.0


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    blue = (hue >= 90) & (hue <= 140)
    red = (hue <= 15) | (hue >= 170)
    cyan_green = (hue >= 35) & (hue <= 115)
    yellow = (hue >= 18) & (hue <= 38)
    mask = ((sat > 32) & (val > 35) & (blue | red | cyan_green | yellow)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def line_artifact_mask(signed_contrast: np.ndarray, valid: np.ndarray) -> np.ndarray:
    dark = ((signed_contrast < -28) & valid).astype(np.uint8) * 255
    horizontal = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((1, 29), np.uint8))
    vertical = cv2.morphologyEx(dark, cv2.MORPH_OPEN, np.ones((29, 1), np.uint8))
    lines = cv2.bitwise_or(horizontal, vertical)
    return cv2.dilate(lines, np.ones((3, 3), np.uint8), iterations=1)


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay_clear = colored_overlay_mask(roi) == 0
    not_blackout = gray > 24
    valid = overlay_clear & not_blackout
    if int(valid.sum()) < 250:
        empty = np.zeros_like(gray, dtype=np.uint8)
        return roi, gray, valid, empty, empty.astype(np.int16), empty, 0.0, 0.0

    background = cv2.medianBlur(gray, 81)
    signed_contrast = gray.astype(np.int16) - background.astype(np.int16)
    abs_contrast = np.abs(signed_contrast).astype(np.uint8)
    line_mask = line_artifact_mask(signed_contrast, valid) > 0
    valid_without_lines = valid & (~line_mask)
    values = abs_contrast[valid_without_lines]
    threshold = max(35.0, float(np.percentile(values, 98.9))) if values.size else 255.0
    raw = ((abs_contrast >= threshold) & valid_without_lines).astype(np.uint8) * 255
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    local_median = float(np.median(gray[valid])) if int(valid.sum()) else 0.0
    return roi, gray, valid_without_lines, abs_contrast, signed_contrast, raw, threshold, local_median


def component_rows(
    labels_count: int,
    labels: np.ndarray,
    stats: np.ndarray,
    centroids: np.ndarray,
    gray: np.ndarray,
    abs_contrast: np.ndarray,
    signed_contrast: np.ndarray,
    threshold: float,
) -> list[dict]:
    components: list[dict] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 16 or area > 2600:
            continue
        if w > 180 or h > 125:
            continue
        if w <= 1 or h <= 1:
            continue
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 9.0 and area < 140:
            continue

        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        distance = math.hypot(full_x - EXPECTED_CENTER_X, full_y - EXPECTED_CENTER_Y)
        if distance > TARGET_RADIUS_PX:
            continue

        mask = labels == label
        abs_values = abs_contrast[mask]
        signed_values = signed_contrast[mask]
        gray_values = gray[mask]
        fill = float(area / max(1, w * h))
        score = (
            float(abs_values.sum())
            + float(abs_values.max()) * 7.0
            + min(float(area), 1500.0) * 1.2
            + min(fill, 0.85) * 80.0
            - distance * 2.4
            - max(0.0, aspect - 4.5) * 25.0
        )
        components.append(
            {
                "label": label,
                "x": ROI_X0 + int(x),
                "y": ROI_Y0 + int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area),
                "fill_ratio": fill,
                "center_x": full_x,
                "center_y": full_y,
                "distance_from_expected_px": distance,
                "max_luma": int(gray_values.max()),
                "min_luma": int(gray_values.min()),
                "mean_luma": float(gray_values.mean()),
                "max_abs_contrast": int(abs_values.max()),
                "mean_abs_contrast": float(abs_values.mean()),
                "mean_signed_contrast": float(signed_values.mean()),
                "threshold": threshold,
                "score": score,
            }
        )
    components.sort(key=lambda item: item["score"], reverse=True)
    return components


def pca_metrics(points_xy: np.ndarray) -> dict:
    if len(points_xy) < 3:
        return {
            "major_axis_angle_deg": 0.0,
            "oriented_major_px": 0.0,
            "oriented_minor_px": 0.0,
            "oriented_aspect": 0.0,
        }
    center = points_xy.mean(axis=0)
    centered = points_xy - center
    covariance = np.cov(centered.T)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1]
    vectors = vectors[:, order]
    major = vectors[:, 0]
    minor = vectors[:, 1]
    major_projection = centered @ major
    minor_projection = centered @ minor
    major_extent = float(major_projection.max() - major_projection.min() + 1.0)
    minor_extent = float(minor_projection.max() - minor_projection.min() + 1.0)
    angle = math.degrees(math.atan2(float(major[1]), float(major[0])))
    if angle <= -90.0:
        angle += 180.0
    if angle > 90.0:
        angle -= 180.0
    return {
        "major_axis_angle_deg": angle,
        "oriented_major_px": major_extent,
        "oriented_minor_px": minor_extent,
        "oriented_aspect": major_extent / max(1.0, minor_extent),
    }


def aggregate_group(components: list[dict], labels: np.ndarray, gray: np.ndarray, abs_contrast: np.ndarray, signed_contrast: np.ndarray) -> dict | None:
    if not components:
        return None
    anchor = components[0]
    group = [
        component
        for component in components
        if math.hypot(component["center_x"] - anchor["center_x"], component["center_y"] - anchor["center_y"]) <= 140.0
        or component["distance_from_expected_px"] <= 125.0
    ]
    if not group:
        return None

    selected_labels = {int(component["label"]) for component in group}
    aggregate_mask = np.isin(labels, list(selected_labels))
    ys, xs = np.where(aggregate_mask)
    if len(xs) == 0:
        return None

    full_xs = xs.astype(np.float64) + ROI_X0
    full_ys = ys.astype(np.float64) + ROI_Y0
    points_xy = np.column_stack([full_xs, full_ys])
    x0 = int(full_xs.min())
    y0 = int(full_ys.min())
    x1 = int(full_xs.max()) + 1
    y1 = int(full_ys.max()) + 1
    area = int(len(xs))
    center_x = float(full_xs.mean())
    center_y = float(full_ys.mean())
    bbox_w = x1 - x0
    bbox_h = y1 - y0
    bbox_aspect = max(bbox_w / max(1, bbox_h), bbox_h / max(1, bbox_w))
    pca = pca_metrics(points_xy)
    abs_values = abs_contrast[aggregate_mask]
    signed_values = signed_contrast[aggregate_mask]
    gray_values = gray[aggregate_mask]
    projection_proxy_count = min(3, max(0, len(group) - 1))
    if projection_proxy_count == 0 and bbox_h >= 32 and pca["oriented_aspect"] >= 1.35:
        projection_proxy_count = 1
    return {
        "components": group,
        "component_count": len(group),
        "projection_proxy_count": projection_proxy_count,
        "center_x": center_x,
        "center_y": center_y,
        "distance_from_expected_px": math.hypot(center_x - EXPECTED_CENTER_X, center_y - EXPECTED_CENTER_Y),
        "bbox_x0": x0,
        "bbox_y0": y0,
        "bbox_x1": x1,
        "bbox_y1": y1,
        "bbox_w": bbox_w,
        "bbox_h": bbox_h,
        "bbox_aspect": bbox_aspect,
        "aggregate_area": area,
        "fill_ratio": float(area / max(1, bbox_w * bbox_h)),
        "max_luma": int(gray_values.max()),
        "min_luma": int(gray_values.min()),
        "mean_luma": float(gray_values.mean()),
        "max_abs_contrast": int(abs_values.max()),
        "mean_abs_contrast": float(abs_values.mean()),
        "mean_signed_contrast": float(signed_values.mean()),
        "score": sum(float(item["score"]) for item in group),
        **pca,
    }


def detect_shape(frame: np.ndarray) -> tuple[dict | None, dict]:
    _roi, gray, _valid, abs_contrast, signed_contrast, mask, threshold, local_median = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    components = component_rows(labels_count, labels, stats, centroids, gray, abs_contrast, signed_contrast, threshold)
    group = aggregate_group(components, labels, gray, abs_contrast, signed_contrast)
    meta = {
        "candidate_count": len(components),
        "threshold": threshold,
        "local_median_luma": local_median,
    }
    return group, meta


def classify(group: dict | None) -> tuple[str, str]:
    if group is None:
        return "none", "no target-region contrast group survived overlay and line-artifact filtering"
    area = int(group["aggregate_area"])
    aspect = float(group["oriented_aspect"])
    bbox_aspect = float(group["bbox_aspect"])
    contrast = float(group["max_abs_contrast"])
    distance = float(group["distance_from_expected_px"])
    component_count = int(group["component_count"])
    projection_proxy_count = int(group["projection_proxy_count"])
    if area >= 520 and aspect >= 1.35 and contrast >= 80 and distance <= 125 and (component_count >= 2 or projection_proxy_count >= 1):
        return "high", "target-region elongated contrast group with projection-like detached or merged lobes"
    if area >= 360 and (aspect >= 1.20 or bbox_aspect >= 1.35) and contrast >= 65 and distance <= 145:
        return "medium", "target-region football/elongated contrast is visible, but projection support is weaker"
    if area >= 120 and contrast >= 45 and distance <= 160:
        return "low", "weak target-region contrast group; morphology is only partially recovered"
    return "none", "candidate is too weak, compact, or far from the persistent target region"


def sample_seconds(duration: float, sample_rate: float) -> list[float]:
    count = int(math.floor(duration * sample_rate)) + 1
    seconds = []
    for index in range(count):
        second = round(index / sample_rate, 3)
        if second <= duration:
            seconds.append(second)
    return seconds


def add_label(img: np.ndarray, text: str, width: int) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 36), (0, 0, 0), -1)
    cv2.putText(out, text, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, group: dict | None, second: float, quality: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (70, 70, 70), 1)
    cv2.circle(out, (int(round(EXPECTED_CENTER_X)), int(round(EXPECTED_CENTER_Y))), int(round(TARGET_RADIUS_PX)), (90, 90, 90), 1)
    if group is not None:
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        cv2.rectangle(
            out,
            (int(group["bbox_x0"]) - 6, int(group["bbox_y0"]) - 6),
            (int(group["bbox_x1"]) + 6, int(group["bbox_y1"]) + 6),
            color,
            2,
        )
        cv2.drawMarker(
            out,
            (int(round(group["center_x"])), int(round(group["center_y"]))),
            color,
            markerType=cv2.MARKER_CROSS,
            markerSize=22,
            thickness=1,
        )
        for component in group["components"]:
            cv2.circle(out, (int(round(component["center_x"])), int(round(component["center_y"]))), 10, color, 1)
    return add_label(out, f"PR46 t={second:04.1f}s quality={quality} shape-review", width=980)


def annotate_patch(frame: np.ndarray, group: dict | None, second: float, quality: str) -> np.ndarray:
    if group is None:
        cx, cy = EXPECTED_CENTER_X, EXPECTED_CENTER_Y
    else:
        cx = float(group["center_x"])
        cy = float(group["center_y"])
    size = 240
    half = size // 2
    x0 = max(0, min(frame.shape[1] - size, int(round(cx)) - half))
    y0 = max(0, min(frame.shape[0] - size, int(round(cy)) - half))
    patch = frame[y0 : y0 + size, x0 : x0 + size].copy()
    if group is not None:
        color = (0, 255, 0) if quality == "high" else (0, 255, 255) if quality == "medium" else (0, 0, 255)
        cv2.rectangle(
            patch,
            (int(group["bbox_x0"]) - x0 - 5, int(group["bbox_y0"]) - y0 - 5),
            (int(group["bbox_x1"]) - x0 + 5, int(group["bbox_y1"]) - y0 + 5),
            color,
            2,
        )
        for component in group["components"]:
            cv2.circle(
                patch,
                (int(round(component["center_x"])) - x0, int(round(component["center_y"])) - y0),
                8,
                color,
                1,
            )
    patch = cv2.resize(patch, (480, 480), interpolation=cv2.INTER_NEAREST)
    return add_label(patch, f"PR46 t={second:04.1f}s quality={quality}", width=480)


def make_sheet(images: list[np.ndarray], cols: int, bg: tuple[int, int, int] = (18, 18, 18)) -> np.ndarray:
    if not images:
        return np.zeros((10, 10, 3), dtype=np.uint8)
    height = max(img.shape[0] for img in images)
    width = max(img.shape[1] for img in images)
    rows = math.ceil(len(images) / cols)
    sheet = np.full((rows * height, cols * width, 3), bg, dtype=np.uint8)
    for index, img in enumerate(images):
        row = index // cols
        col = index % cols
        y0 = row * height
        x0 = col * width
        sheet[y0 : y0 + img.shape[0], x0 : x0 + img.shape[1]] = img
    return sheet


def frame_at_second(cap: cv2.VideoCapture, fps: float, second: float) -> tuple[bool, np.ndarray | None, int]:
    frame_index = int(round(second * fps))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    return ok, frame, frame_index


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run(video_path: Path, sample_rate: float) -> None:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise SystemExit(f"Unable to open video: {video_path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = frame_count / fps if fps else 0.0

    out_dir = OUT_ROOT
    ensure_dir(out_dir)
    detail_csv = Path("research/ufo-video-pr46-shape-review-dod111689133.csv")
    summary_csv = Path("research/ufo-video-pr46-shape-review-summary.csv")
    assets_csv = Path("research/ufo-video-pr46-shape-review-assets.csv")
    annotated_sheet = out_dir / "DOD_111689133_pr46_shape_annotated_sheet.jpg"
    patch_sheet = out_dir / "DOD_111689133_pr46_shape_patch_sheet.jpg"

    rows: list[dict] = []
    annotated_images: list[np.ndarray] = []
    patch_images: list[np.ndarray] = []

    for second in sample_seconds(duration, sample_rate):
        ok, frame, frame_index = frame_at_second(cap, fps, second)
        if not ok or frame is None:
            continue
        group, meta = detect_shape(frame)
        quality, rationale = classify(group)
        base_row = {
            "video": VIDEO_NAME,
            "release_id": RELEASE_ID,
            "frame_index": frame_index,
            "second": f"{second:.3f}",
            "review_quality": quality,
            "rationale": rationale,
            "candidate_count": int(meta["candidate_count"]),
            "threshold": f"{float(meta['threshold']):.3f}",
            "local_median_luma": f"{float(meta['local_median_luma']):.3f}",
        }
        if group is None:
            row = {
                **base_row,
                "component_count": 0,
                "projection_proxy_count": 0,
                "center_x": "",
                "center_y": "",
                "distance_from_expected_px": "",
                "bbox_x0": "",
                "bbox_y0": "",
                "bbox_x1": "",
                "bbox_y1": "",
                "bbox_w": "",
                "bbox_h": "",
                "bbox_aspect": "",
                "aggregate_area": "",
                "fill_ratio": "",
                "oriented_major_px": "",
                "oriented_minor_px": "",
                "oriented_aspect": "",
                "major_axis_angle_deg": "",
                "max_abs_contrast": "",
                "mean_abs_contrast": "",
                "mean_signed_contrast": "",
            }
        else:
            row = {
                **base_row,
                "component_count": int(group["component_count"]),
                "projection_proxy_count": int(group["projection_proxy_count"]),
                "center_x": f"{float(group['center_x']):.3f}",
                "center_y": f"{float(group['center_y']):.3f}",
                "distance_from_expected_px": f"{float(group['distance_from_expected_px']):.3f}",
                "bbox_x0": int(group["bbox_x0"]),
                "bbox_y0": int(group["bbox_y0"]),
                "bbox_x1": int(group["bbox_x1"]),
                "bbox_y1": int(group["bbox_y1"]),
                "bbox_w": int(group["bbox_w"]),
                "bbox_h": int(group["bbox_h"]),
                "bbox_aspect": f"{float(group['bbox_aspect']):.3f}",
                "aggregate_area": int(group["aggregate_area"]),
                "fill_ratio": f"{float(group['fill_ratio']):.3f}",
                "oriented_major_px": f"{float(group['oriented_major_px']):.3f}",
                "oriented_minor_px": f"{float(group['oriented_minor_px']):.3f}",
                "oriented_aspect": f"{float(group['oriented_aspect']):.3f}",
                "major_axis_angle_deg": f"{float(group['major_axis_angle_deg']):.3f}",
                "max_abs_contrast": int(group["max_abs_contrast"]),
                "mean_abs_contrast": f"{float(group['mean_abs_contrast']):.3f}",
                "mean_signed_contrast": f"{float(group['mean_signed_contrast']):.3f}",
            }
        rows.append(row)
        annotated = annotate_frame(frame, group, second, quality)
        annotated_images.append(cv2.resize(annotated, (480, 270), interpolation=cv2.INTER_AREA))
        patch_images.append(annotate_patch(frame, group, second, quality))

    cap.release()

    fieldnames = [
        "video",
        "release_id",
        "frame_index",
        "second",
        "review_quality",
        "rationale",
        "candidate_count",
        "threshold",
        "local_median_luma",
        "component_count",
        "projection_proxy_count",
        "center_x",
        "center_y",
        "distance_from_expected_px",
        "bbox_x0",
        "bbox_y0",
        "bbox_x1",
        "bbox_y1",
        "bbox_w",
        "bbox_h",
        "bbox_aspect",
        "aggregate_area",
        "fill_ratio",
        "oriented_major_px",
        "oriented_minor_px",
        "oriented_aspect",
        "major_axis_angle_deg",
        "max_abs_contrast",
        "mean_abs_contrast",
        "mean_signed_contrast",
    ]
    write_csv(detail_csv, rows, fieldnames)

    high_or_medium = [row for row in rows if row["review_quality"] in {"high", "medium"}]
    numeric_rows = [row for row in rows if row["aggregate_area"] != ""]
    counts = Counter(row["review_quality"] for row in rows)
    summary_row = {
        "video": VIDEO_NAME,
        "release_id": RELEASE_ID,
        "fps": f"{fps:.3f}",
        "frames": frame_count,
        "width": width,
        "height": height,
        "duration_s": f"{duration:.3f}",
        "sample_rate_fps": f"{sample_rate:.3f}",
        "rows": len(rows),
        "high": counts.get("high", 0),
        "medium": counts.get("medium", 0),
        "low": counts.get("low", 0),
        "none": counts.get("none", 0),
        "high_or_medium": len(high_or_medium),
        "supported_start_s": min((row["second"] for row in high_or_medium), default=""),
        "supported_end_s": max((row["second"] for row in high_or_medium), default=""),
        "median_aggregate_area": f"{statistics.median(float(row['aggregate_area']) for row in numeric_rows):.3f}" if numeric_rows else "",
        "median_oriented_aspect": f"{statistics.median(float(row['oriented_aspect']) for row in numeric_rows):.3f}" if numeric_rows else "",
        "median_component_count": f"{statistics.median(float(row['component_count']) for row in numeric_rows):.3f}" if numeric_rows else "",
        "median_projection_proxy_count": f"{statistics.median(float(row['projection_proxy_count']) for row in numeric_rows):.3f}" if numeric_rows else "",
        "median_max_abs_contrast": f"{statistics.median(float(row['max_abs_contrast']) for row in numeric_rows):.3f}" if numeric_rows else "",
        "median_center_x": f"{statistics.median(float(row['center_x']) for row in numeric_rows):.3f}" if numeric_rows else "",
        "median_center_y": f"{statistics.median(float(row['center_y']) for row in numeric_rows):.3f}" if numeric_rows else "",
        "analysis_note": "Full-clip morphology audit for the DVIDS football-shaped PR46 visual description; image-plane only, no telemetry-derived physical inference.",
    }
    write_csv(summary_csv, [summary_row], list(summary_row.keys()))

    cv2.imwrite(str(annotated_sheet), make_sheet(annotated_images, cols=4))
    cv2.imwrite(str(patch_sheet), make_sheet(patch_images, cols=5))
    asset_rows = [
        {
            "video": VIDEO_NAME,
            "artifact": "annotated_contact_sheet",
            "path": str(annotated_sheet),
            "description": "Two-fps annotated full-frame samples with target-region box and selected morphology group.",
        },
        {
            "video": VIDEO_NAME,
            "artifact": "patch_contact_sheet",
            "path": str(patch_sheet),
            "description": "Two-fps target-region patch samples for reviewing football-like body and projection-like lobes.",
        },
    ]
    write_csv(assets_csv, asset_rows, list(asset_rows[0].keys()))

    print(f"Wrote {detail_csv}")
    print(f"Wrote {summary_csv}")
    print(f"Wrote {assets_csv}")
    print(f"Wrote {annotated_sheet}")
    print(f"Wrote {patch_sheet}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Review PR46/DOD_111689133 morphology in the public MP4.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=2.0)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.video, args.sample_rate)

