from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689142"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR47"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689142.mp4")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr47-formation-review") / VIDEO_ID

ROI_X0 = 340
ROI_Y0 = 120
ROI_X1 = 1540
ROI_Y1 = 930


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def colored_overlay_mask(img: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 45) & (hue <= 115)
    red_or_orange = (hue <= 25) | (hue >= 170)
    mask = ((sat > 60) & (val > 55) & (cyan_green | red_or_orange)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def nearest_overlay_distance(img: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(img)
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


def candidate_mask(frame: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, int]:
    roi = frame[ROI_Y0:ROI_Y1, ROI_X0:ROI_X1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    overlay_clear = colored_overlay_mask(roi) == 0
    low_sat = hsv[:, :, 1] < 90
    midtone_or_brighter = gray > 50
    valid = overlay_clear & low_sat & midtone_or_brighter
    values = gray[valid]
    if values.size == 0:
        return roi, gray, valid, np.zeros_like(gray, dtype=np.uint8), 255
    threshold = max(135, int(np.percentile(values, 99.55)))
    threshold = min(threshold, 245)
    mask = ((gray >= threshold) & valid).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 3)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    return roi, gray, valid, mask, threshold


def detect_formation(frame: np.ndarray) -> dict:
    roi, gray, valid, mask, threshold = candidate_mask(frame)
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    frame_center_x = frame.shape[1] / 2
    frame_center_y = frame.shape[0] / 2
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if x <= 1 or y <= 1 or (x + w) >= mask.shape[1] - 2 or (y + h) >= mask.shape[0] - 2:
            continue
        if area < 4 or area > 6000:
            continue
        if w > 180 or h > 120:
            continue
        component_values = gray[labels == label]
        max_luma = int(component_values.max())
        mean_luma = float(component_values.mean())
        cx, cy = centroids[label]
        full_x = ROI_X0 + float(cx)
        full_y = ROI_Y0 + float(cy)
        dist = math.hypot(full_x - frame_center_x, full_y - frame_center_y)
        aspect = max(w / max(1, h), h / max(1, w))
        if aspect > 8.0 and area < 80:
            continue
        score = area * 0.55 + max_luma * 2.0 + mean_luma * 0.7 - dist * 0.08 - max(0.0, aspect - 3.5) * 25.0
        candidates.append(
            {
                "label": label,
                "roi_x": int(x),
                "roi_y": int(y),
                "bbox_w": int(w),
                "bbox_h": int(h),
                "area": int(area),
                "max_luma": max_luma,
                "mean_luma": mean_luma,
                "center_x": full_x,
                "center_y": full_y,
                "score": score,
                "threshold": int(threshold),
            }
        )
    if not candidates:
        return {"detected": False, "threshold": int(threshold), "candidate_count": 0}

    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    component_mask = (labels == best["label"]).astype(np.uint8) * 255
    component_points = np.column_stack(np.where(component_mask > 0))
    # component_points are y,x in ROI coordinates.
    centers = []
    if len(component_points) >= 12:
        cv2.setRNGSeed(47)
        coords = component_points[:, ::-1].astype(np.float32)
        _compactness, cluster_labels, cluster_centers = cv2.kmeans(
            coords,
            3,
            None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 80, 0.2),
            10,
            cv2.KMEANS_PP_CENTERS,
        )
        for cluster_id, center in enumerate(cluster_centers):
            count = int((cluster_labels.flatten() == cluster_id).sum())
            centers.append(
                {
                    "x": ROI_X0 + float(center[0]),
                    "y": ROI_Y0 + float(center[1]),
                    "count": count,
                }
            )
        centers.sort(key=lambda item: item["x"])

    x0 = ROI_X0 + best["roi_x"]
    y0 = ROI_Y0 + best["roi_y"]
    x1 = x0 + best["bbox_w"]
    y1 = y0 + best["bbox_h"]
    relation, nearest = nearest_overlay_distance(frame, best["center_x"], best["center_y"])

    out = {
        "detected": True,
        "candidate_count": len(candidates),
        "threshold": int(threshold),
        "center_x": best["center_x"],
        "center_y": best["center_y"],
        "bbox_x0": x0,
        "bbox_y0": y0,
        "bbox_x1": x1,
        "bbox_y1": y1,
        "bbox_w": best["bbox_w"],
        "bbox_h": best["bbox_h"],
        "area": best["area"],
        "max_luma": best["max_luma"],
        "mean_luma": best["mean_luma"],
        "overlay_relation": relation,
        "nearest_overlay_px": nearest,
        "subclusters": centers,
    }
    if len(centers) == 3:
        left, middle, right = centers
        d_lm = math.hypot(middle["x"] - left["x"], middle["y"] - left["y"])
        d_mr = math.hypot(right["x"] - middle["x"], right["y"] - middle["y"])
        d_lr = math.hypot(right["x"] - left["x"], right["y"] - left["y"])
        angle = math.degrees(math.atan2(right["y"] - left["y"], right["x"] - left["x"]))
        midline_offset = abs(
            (right["x"] - left["x"]) * (left["y"] - middle["y"])
            - (left["x"] - middle["x"]) * (right["y"] - left["y"])
        ) / max(d_lr, 1e-6)
        out.update(
            {
                "left_x": left["x"],
                "left_y": left["y"],
                "middle_x": middle["x"],
                "middle_y": middle["y"],
                "right_x": right["x"],
                "right_y": right["y"],
                "left_middle_px": d_lm,
                "middle_right_px": d_mr,
                "left_right_px": d_lr,
                "left_middle_to_middle_right_ratio": d_lm / d_mr if d_mr else "",
                "formation_angle_deg": angle,
                "middle_offset_from_left_right_line_px": midline_offset,
            }
        )
    return out


def classify_detection(result: dict) -> tuple[str, str]:
    if not result.get("detected"):
        return "none", "no compact bright formation candidate found"
    area = int(result["area"])
    width = int(result["bbox_w"])
    height = int(result["bbox_h"])
    subclusters = result.get("subclusters", [])
    relation = str(result.get("overlay_relation", ""))
    if area >= 160 and len(subclusters) == 3 and width >= 24 and height >= 12 and not relation.startswith("intersects"):
        return "high", "compact bright cluster with three modeled subclusters"
    if area >= 80 and len(subclusters) == 3 and width >= 20 and height >= 8:
        return "medium", "compact bright cluster with usable three-subcluster model"
    return "low", "weak, small, overlay-adjacent, or poorly separated bright cluster"


def add_label(img: np.ndarray, text: str, width: int = 1240) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 38), (0, 0, 0), -1)
    cv2.putText(out, text, (10, 26), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, result: dict, second: float, quality: str) -> np.ndarray:
    out = frame.copy()
    cv2.rectangle(out, (ROI_X0, ROI_Y0), (ROI_X1, ROI_Y1), (80, 80, 80), 1)
    if result.get("detected"):
        x0 = int(round(result["bbox_x0"]))
        y0 = int(round(result["bbox_y0"]))
        x1 = int(round(result["bbox_x1"]))
        y1 = int(round(result["bbox_y1"]))
        color = (0, 0, 255) if quality in {"high", "medium"} else (0, 165, 255)
        cv2.rectangle(out, (x0, y0), (x1, y1), color, 2)
        center = (int(round(result["center_x"])), int(round(result["center_y"])))
        cv2.drawMarker(out, center, color, markerType=cv2.MARKER_CROSS, markerSize=30, thickness=2)
        centers = result.get("subclusters", [])
        if len(centers) == 3:
            points = [(int(round(item["x"])), int(round(item["y"]))) for item in centers]
            cv2.polylines(out, [np.array(points, dtype=np.int32)], False, (255, 255, 0), 2)
            for idx, point in enumerate(points, start=1):
                cv2.circle(out, point, 12, (0, 255, 255), 2)
                cv2.putText(out, str(idx), (point[0] + 8, point[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (0, 255, 255), 1, cv2.LINE_AA)
    label = f"{VIDEO_ID} t={second:05.1f}s PR47 formation review quality={quality}"
    return add_label(out, label)


def crop_patch(frame: np.ndarray, result: dict, size: int = 240) -> np.ndarray:
    h, w = frame.shape[:2]
    if result.get("detected"):
        cx = int(round(result["center_x"]))
        cy = int(round(result["center_y"]))
    else:
        cx = w // 2
        cy = h // 2
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(frame: np.ndarray, result: dict, second: float, quality: str) -> np.ndarray:
    patch = crop_patch(frame, result)
    out = cv2.resize(patch, (480, 480), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (240, 240), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=36, thickness=2)
    cv2.circle(out, (240, 240), 50, (0, 0, 255), 2)
    return add_label(out, f"{VIDEO_ID} t={second:05.1f}s quality={quality}", width=480)


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


def distance(a: dict, b: dict) -> float:
    return math.hypot(float(b["cluster_center_x"]) - float(a["cluster_center_x"]), float(b["cluster_center_y"]) - float(a["cluster_center_y"]))


def track_stats(rows: list[dict]) -> dict:
    detected = [row for row in rows if row["review_quality"] in {"high", "medium"} and row["cluster_center_x"] != ""]
    if len(detected) < 2:
        return {"metric": "formation_center_track", "value": len(detected), "note": "fewer than two supported rows"}
    duration = float(detected[-1]["approx_second"]) - float(detected[0]["approx_second"])
    net = distance(detected[0], detected[-1])
    total = 0.0
    rates = []
    for prev, curr in zip(detected, detected[1:]):
        dt = float(curr["approx_second"]) - float(prev["approx_second"])
        if dt <= 0:
            continue
        step = distance(prev, curr)
        total += step
        rates.append(step / dt)
    return {
        "metric": "formation_center_track",
        "value": len(detected),
        "note": (
            f"{detected[0]['approx_second']}s-{detected[-1]['approx_second']}s; "
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


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="PR47 formation review for DOD_111689142.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=1.0)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps

    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "formation-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    sample_count = int(math.floor(duration * args.sample_rate)) + 1
    for sample_index in range(sample_count):
        second = round(sample_index / args.sample_rate, 3)
        if second > duration:
            continue
        frame_index = min(int(round(second * fps)), max(0, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        result = detect_formation(frame)
        quality, caveat = classify_detection(result)

        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, result, second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, result, second, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)

        row = {
            "video": VIDEO_NAME,
            "release_id": RELEASE_ID,
            "sample_index": sample_index,
            "approx_second": f"{second:.1f}",
            "source_frame_index": frame_index,
            "dvids_anchor": "Within DVIDS 00:00-01:59 three-contrast-area tracking interval",
            "review_quality": quality,
            "candidate_count": result.get("candidate_count", 0),
            "threshold": result.get("threshold", ""),
            "cluster_center_x": "" if not result.get("detected") else round(float(result["center_x"]), 1),
            "cluster_center_y": "" if not result.get("detected") else round(float(result["center_y"]), 1),
            "bbox_x0": "" if not result.get("detected") else round(float(result["bbox_x0"]), 1),
            "bbox_y0": "" if not result.get("detected") else round(float(result["bbox_y0"]), 1),
            "bbox_w": "" if not result.get("detected") else int(result["bbox_w"]),
            "bbox_h": "" if not result.get("detected") else int(result["bbox_h"]),
            "component_area": "" if not result.get("detected") else int(result["area"]),
            "component_max_luma": "" if not result.get("detected") else int(result["max_luma"]),
            "component_mean_luma": "" if not result.get("detected") else round(float(result["mean_luma"]), 2),
            "subcluster_count": len(result.get("subclusters", [])),
            "left_x": "" if "left_x" not in result else round(float(result["left_x"]), 1),
            "left_y": "" if "left_y" not in result else round(float(result["left_y"]), 1),
            "middle_x": "" if "middle_x" not in result else round(float(result["middle_x"]), 1),
            "middle_y": "" if "middle_y" not in result else round(float(result["middle_y"]), 1),
            "right_x": "" if "right_x" not in result else round(float(result["right_x"]), 1),
            "right_y": "" if "right_y" not in result else round(float(result["right_y"]), 1),
            "left_middle_px": "" if "left_middle_px" not in result else round(float(result["left_middle_px"]), 3),
            "middle_right_px": "" if "middle_right_px" not in result else round(float(result["middle_right_px"]), 3),
            "left_right_px": "" if "left_right_px" not in result else round(float(result["left_right_px"]), 3),
            "left_middle_to_middle_right_ratio": "" if "left_middle_to_middle_right_ratio" not in result else round(float(result["left_middle_to_middle_right_ratio"]), 3),
            "formation_angle_deg": "" if "formation_angle_deg" not in result else round(float(result["formation_angle_deg"]), 3),
            "middle_offset_from_left_right_line_px": "" if "middle_offset_from_left_right_line_px" not in result else round(float(result["middle_offset_from_left_right_line_px"]), 3),
            "overlay_relation": result.get("overlay_relation", ""),
            "nearest_colored_overlay_px": "" if result.get("nearest_overlay_px") is None else round(float(result["nearest_overlay_px"]), 2),
            "caveat": caveat,
            "annotated_frame_path": str(annotated_path).replace("\\", "/"),
            "zoom_patch_path": str(patch_path).replace("\\", "/"),
        }
        rows.append(row)
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr47-formation-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr47-formation-patches", cols=8, thumb_width=180)

    review_csv = Path("research/ufo-video-pr47-formation-review-dod111689142.csv")
    write_csv(review_csv, list(rows[0].keys()), rows)

    supported = [row for row in rows if row["review_quality"] in {"high", "medium"}]
    triple_supported = [row for row in supported if row["subcluster_count"] == 3]
    ratios = [float(row["left_middle_to_middle_right_ratio"]) for row in triple_supported if row["left_middle_to_middle_right_ratio"] != ""]
    angles = [float(row["formation_angle_deg"]) for row in triple_supported if row["formation_angle_deg"] != ""]
    widths = [float(row["left_right_px"]) for row in triple_supported if row["left_right_px"] != ""]
    offsets = [float(row["middle_offset_from_left_right_line_px"]) for row in triple_supported if row["middle_offset_from_left_right_line_px"] != ""]
    quality_counts = Counter(row["review_quality"] for row in rows)
    overlay_counts = Counter(row["overlay_relation"] for row in rows if row["overlay_relation"])
    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_id", "value": RELEASE_ID, "note": "DVIDS public release identity"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": f"fps={fps}; frames={total_frames}"},
        {"metric": "sample_count", "value": len(rows), "note": f"{args.sample_rate} fps review samples"},
        {"metric": "supported_high_or_medium_rows", "value": len(supported), "note": "rows with usable compact bright formation candidate"},
        {"metric": "triple_subcluster_supported_rows", "value": len(triple_supported), "note": "supported rows modeled as three visual subclusters"},
        track_stats(rows),
        numeric_summary("left_right_spacing_px", widths, "scale-dependent image-plane formation width"),
        numeric_summary("left_middle_to_middle_right_ratio", ratios, "scale-normalized subcluster spacing ratio"),
        numeric_summary("formation_angle_deg", angles, "image-plane orientation of left-to-right subcluster axis"),
        numeric_summary("middle_offset_from_axis_px", offsets, "middle subcluster offset from left-right line"),
    ]
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"quality_count: {key}", "value": value, "note": "review quality"})
    for key, value in sorted(overlay_counts.items()):
        summary_rows.append({"metric": f"overlay_count: {key}", "value": value, "note": "cluster relation to colored overlay"})

    summary_csv = Path("research/ufo-video-pr47-formation-review-summary.csv")
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "formation_review_csv", "path": str(review_csv).replace("\\", "/"), "note": "PR47 one-fps formation review table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR47 formation review summary"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR47 formation annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "PR47 formation patch sheet"})
    asset_csv = Path("research/ufo-video-pr47-formation-review-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} frames={total_frames} duration={duration:.3f}s")
    print(f"samples={len(rows)} quality_counts={dict(quality_counts)}")
    print(f"triple_supported={len(triple_supported)}")
    print(f"review_csv={review_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

