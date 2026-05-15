from __future__ import annotations

import argparse
import csv
import itertools
import math
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689142"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR47"
DEFAULT_VIDEO = Path(r"source-files-not-included/DOD_111689142.mp4")
OUT_ROOT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr47-standalone") / VIDEO_ID

CROP_WIDTH = 960
CROP_HEIGHT = 540
CROP_X0 = 480
CROP_Y0 = 270
CROP_CENTER_X = CROP_WIDTH // 2
CROP_CENTER_Y = CROP_HEIGHT // 2


@dataclass(frozen=True)
class Phase:
    name: str
    start: float
    end: float
    note: str


PHASES = (
    Phase(
        "upper-field formation track",
        0.0,
        42.9,
        "Three-area contrast cluster rides high in the crop, partly near the vertical reticle line.",
    ),
    Phase(
        "upper-to-mid descent",
        43.0,
        82.9,
        "Contrast cluster remains visible while drifting lower in the sensor field.",
    ),
    Phase(
        "reticle-near pass",
        83.0,
        108.9,
        "Cluster approaches the reticle center; overlay/reticle confounds increase.",
    ),
    Phase(
        "late lower-field interval",
        109.0,
        119.5,
        "Late interval after the formation-like cluster has moved lower in the field.",
    ),
)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def center_crop(frame: np.ndarray) -> np.ndarray:
    return frame[CROP_Y0 : CROP_Y0 + CROP_HEIGHT, CROP_X0 : CROP_X0 + CROP_WIDTH].copy()


def phase_for(second: float) -> Phase:
    for phase in PHASES:
        if phase.start <= second <= phase.end:
            return phase
    return PHASES[-1]


def colored_overlay_mask(crop: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    red = (hue <= 25) | (hue >= 165)
    green_cyan = (hue >= 42) & (hue <= 118)
    mask = ((sat > 50) & (val > 45) & (red | green_cyan)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=1)


def nearest_overlay_distance(crop: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(crop)
    pts = cv2.findNonZero(mask)
    if pts is None:
        return "no colored overlay detected", None
    arr = pts.reshape(-1, 2)
    if len(arr) == 0:
        return "no colored overlay detected", None
    distances = np.sqrt((arr[:, 0] - x) ** 2 + (arr[:, 1] - y) ** 2)
    nearest = float(distances.min())
    if nearest <= 5:
        return "intersects colored overlay", nearest
    if nearest <= 35:
        return "near colored overlay", nearest
    return "separate from colored overlay", nearest


def extract_candidates(crop: np.ndarray) -> list[dict]:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    overlay = colored_overlay_mask(crop)

    # Avoid black redaction bars while keeping the high-field cluster.
    low_sat = hsv[:, :, 1] < 105
    not_overlay = overlay == 0
    not_black = gray > 42
    not_right_border = np.ones_like(gray, dtype=bool)
    not_right_border[:, CROP_WIDTH - 34 :] = False
    not_left_border = np.ones_like(gray, dtype=bool)
    not_left_border[:, :28] = False
    valid = low_sat & not_overlay & not_black & not_right_border & not_left_border
    if int(valid.sum()) < 1000:
        return []

    values = gray[valid]
    thresholds = [
        max(142, int(np.percentile(values, 99.74))),
        max(132, int(np.percentile(values, 99.45))),
        max(120, int(np.percentile(values, 99.10))),
    ]

    candidates: list[dict] = []
    for threshold in thresholds:
        mask = ((gray >= threshold) & valid).astype(np.uint8) * 255
        mask = cv2.medianBlur(mask, 3)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
        labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

        for label in range(1, labels_count):
            x, y, bw, bh, area = stats[label]
            if area < 3 or area > 1800:
                continue
            if bw > 90 or bh > 70:
                continue
            aspect = max(bw / max(1, bh), bh / max(1, bw))
            if aspect > 7.0:
                continue
            cx, cy = centroids[label]
            component_values = gray[labels == label]
            max_luma = int(component_values.max())
            mean_luma = float(component_values.mean())
            if max_luma < 138:
                continue
            distance_from_center = math.hypot(float(cx) - CROP_CENTER_X, float(cy) - CROP_CENTER_Y)
            score = (
                (max_luma / 255.0) * 2.0
                + (mean_luma / 255.0)
                + min(int(area), 260) / 260.0
                + max(0.0, 1.0 - distance_from_center / 520.0)
            )
            candidates.append(
                {
                    "x": float(cx),
                    "y": float(cy),
                    "bbox_x": int(x),
                    "bbox_y": int(y),
                    "bbox_w": int(bw),
                    "bbox_h": int(bh),
                    "area": int(area),
                    "max_luma": max_luma,
                    "mean_luma": mean_luma,
                    "threshold": int(threshold),
                    "score": score,
                }
            )
        if len(candidates) >= 2:
            break

    candidates.sort(key=lambda item: item["score"], reverse=True)
    return candidates[:18]


def group_score(group: list[dict]) -> float:
    if not group:
        return -999.0
    distances = pairwise_distances(group)
    if not distances:
        compactness = 0.0
    else:
        max_dist = max(distances)
        compactness = max(0.0, 1.0 - max_dist / 170.0)
    mean_x = statistics.mean(item["x"] for item in group)
    mean_y = statistics.mean(item["y"] for item in group)
    high_field_bonus = max(0.0, 1.0 - mean_y / CROP_HEIGHT)
    centerline_bonus = max(0.0, 1.0 - abs(mean_x - CROP_CENTER_X) / 260.0)
    brightness = sum(item["score"] for item in group)
    cardinality_bonus = 1.2 if len(group) >= 3 else 0.45 if len(group) == 2 else 0.0
    return brightness + compactness + high_field_bonus + centerline_bonus + cardinality_bonus


def select_group(candidates: list[dict]) -> list[dict]:
    if not candidates:
        return []

    groups: list[list[dict]] = []
    for size in (3, 2):
        for combo in itertools.combinations(candidates[:12], size):
            mean_x = statistics.mean(item["x"] for item in combo)
            if mean_x < 250 or mean_x > 720:
                continue
            distances = pairwise_distances(list(combo))
            if not distances:
                continue
            max_dist = max(distances)
            min_dist = min(distances)
            if max_dist > 145:
                continue
            if min_dist < 3:
                continue
            groups.append(list(combo))
        if groups:
            break

    if not groups:
        return [candidates[0]]
    groups.sort(key=group_score, reverse=True)
    return sorted(groups[0], key=lambda item: item["x"])


def pairwise_distances(group: list[dict]) -> list[float]:
    distances: list[float] = []
    for a, b in itertools.combinations(group, 2):
        distances.append(math.hypot(float(a["x"]) - float(b["x"]), float(a["y"]) - float(b["y"])))
    return distances


def group_metrics(group: list[dict], crop: np.ndarray) -> dict:
    if not group:
        return {}
    xs = [float(item["x"]) for item in group]
    ys = [float(item["y"]) for item in group]
    areas = [int(item["area"]) for item in group]
    max_luma = [int(item["max_luma"]) for item in group]
    distances = pairwise_distances(group)
    centroid_x = statistics.mean(xs)
    centroid_y = statistics.mean(ys)
    overlay_relation, overlay_distance = nearest_overlay_distance(crop, centroid_x, centroid_y)
    sorted_group = sorted(group, key=lambda item: item["x"])
    d12 = d23 = d13 = ""
    if len(sorted_group) >= 3:
        d12 = math.hypot(sorted_group[0]["x"] - sorted_group[1]["x"], sorted_group[0]["y"] - sorted_group[1]["y"])
        d23 = math.hypot(sorted_group[1]["x"] - sorted_group[2]["x"], sorted_group[1]["y"] - sorted_group[2]["y"])
        d13 = math.hypot(sorted_group[0]["x"] - sorted_group[2]["x"], sorted_group[0]["y"] - sorted_group[2]["y"])
    return {
        "group_size": len(group),
        "centroid_x": centroid_x,
        "centroid_y": centroid_y,
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "span_x": max(xs) - min(xs),
        "span_y": max(ys) - min(ys),
        "mean_area": statistics.mean(areas),
        "sum_area": sum(areas),
        "max_luma": max(max_luma),
        "mean_luma": statistics.mean(float(item["mean_luma"]) for item in group),
        "mean_pair_distance": statistics.mean(distances) if distances else "",
        "max_pair_distance": max(distances) if distances else "",
        "d12": d12,
        "d23": d23,
        "d13": d13,
        "overlay_relation": overlay_relation,
        "nearest_overlay_px": overlay_distance,
    }


def classify_group(group: list[dict], metrics: dict) -> tuple[str, str]:
    size = int(metrics.get("group_size", 0) or 0)
    if size >= 3:
        max_pair = float(metrics.get("max_pair_distance", 999.0) or 999.0)
        max_luma = int(metrics.get("max_luma", 0) or 0)
        sum_area = int(metrics.get("sum_area", 0) or 0)
        if max_pair <= 115 and max_luma >= 170 and sum_area >= 35:
            return "high", "three compact bright contrast areas detected as a tight group"
        return "medium", "three contrast areas detected, but spacing or brightness is less conservative"
    if size == 2:
        if int(metrics.get("sum_area", 0) or 0) < 35 or int(metrics.get("max_luma", 0) or 0) < 170:
            return "low", "two weak compact candidates detected; possible background or overlay residue"
        return "medium", "two compact bright areas detected; possible partial formation visibility"
    if size == 1:
        return "low", "only one compact bright candidate detected"
    return "none", "no compact bright formation candidate survived overlay suppression"


def add_label(img: np.ndarray, text: str, width: int | None = None) -> np.ndarray:
    out = img.copy()
    label_width = width or out.shape[1]
    cv2.rectangle(out, (0, 0), (min(label_width, out.shape[1]), 36), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_crop(crop: np.ndarray, second: float, phase: Phase, group: list[dict], confidence: str) -> np.ndarray:
    out = crop.copy()
    colors = [(0, 0, 255), (0, 220, 255), (255, 0, 255), (255, 255, 0)]
    if group:
        pts = []
        for index, candidate in enumerate(group):
            color = colors[index % len(colors)]
            x = int(round(candidate["x"]))
            y = int(round(candidate["y"]))
            pts.append((x, y))
            cv2.rectangle(
                out,
                (candidate["bbox_x"], candidate["bbox_y"]),
                (candidate["bbox_x"] + candidate["bbox_w"], candidate["bbox_y"] + candidate["bbox_h"]),
                color,
                2,
            )
            cv2.drawMarker(out, (x, y), color, markerType=cv2.MARKER_CROSS, markerSize=24, thickness=2)
            cv2.circle(out, (x, y), 13, color, 2)
        for a, b in itertools.combinations(pts, 2):
            cv2.line(out, a, b, (255, 255, 255), 1)
    label = f"{VIDEO_ID} t={second:05.1f}s {phase.name}; {confidence}; n={len(group)}"
    return add_label(out, label)


def crop_group_patch(crop: np.ndarray, group: list[dict], size: int = 220) -> np.ndarray:
    h, w = crop.shape[:2]
    if group:
        cx = int(round(statistics.mean(float(item["x"]) for item in group)))
        cy = int(round(statistics.mean(float(item["y"]) for item in group)))
    else:
        cx = CROP_CENTER_X
        cy = CROP_CENTER_Y
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return crop[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(patch: np.ndarray, second: float, confidence: str) -> np.ndarray:
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (210, 210), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    cv2.circle(out, (210, 210), 50, (0, 0, 255), 2)
    return add_label(out, f"{VIDEO_ID} t={second:05.1f}s {confidence}", width=420)


def write_contact_sheets(paths: list[Path], out_dir: Path, prefix: str, cols: int, thumb_width: int) -> list[Path]:
    ensure_dir(out_dir)
    written: list[Path] = []
    page_size = cols * 4
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


def numeric(row: dict, key: str) -> float | None:
    value = row.get(key, "")
    if value == "":
        return None
    return float(value)


def summarize(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    for phase in PHASES:
        subset = [row for row in rows if row["phase"] == phase.name]
        if not subset:
            continue
        counts = Counter(row["confidence"] for row in subset)
        triples = [row for row in subset if row["group_size"] == 3]
        triple_seconds = [float(row["approx_second"]) for row in triples]
        mean_pair = [numeric(row, "mean_pair_distance") for row in triples]
        mean_pair = [value for value in mean_pair if value is not None]
        max_pair = [numeric(row, "max_pair_distance") for row in triples]
        max_pair = [value for value in max_pair if value is not None]
        d12 = [numeric(row, "d12") for row in triples]
        d12 = [value for value in d12 if value is not None]
        d23 = [numeric(row, "d23") for row in triples]
        d23 = [value for value in d23 if value is not None]
        d13 = [numeric(row, "d13") for row in triples]
        d13 = [value for value in d13 if value is not None]
        output.append(
            {
                "phase": phase.name,
                "start_second": phase.start,
                "end_second": phase.end,
                "samples": len(subset),
                "high": counts.get("high", 0),
                "medium": counts.get("medium", 0),
                "low": counts.get("low", 0),
                "none": counts.get("none", 0),
                "three_component_rows": len(triples),
                "first_three_component_second": min(triple_seconds) if triple_seconds else "",
                "last_three_component_second": max(triple_seconds) if triple_seconds else "",
                "median_mean_pair_distance": round(statistics.median(mean_pair), 3) if mean_pair else "",
                "median_max_pair_distance": round(statistics.median(max_pair), 3) if max_pair else "",
                "median_d12": round(statistics.median(d12), 3) if d12 else "",
                "median_d23": round(statistics.median(d23), 3) if d23 else "",
                "median_d13": round(statistics.median(d13), 3) if d13 else "",
                "phase_note": phase.note,
            }
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone PR47 formation visual pass for DOD_111689142.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--sample-rate", type=float, default=5.0)
    parser.add_argument("--start", type=float, default=0.0)
    parser.add_argument("--end", type=float, default=None)
    args = parser.parse_args()

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 30.0)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = total_frames / fps if fps else 0.0
    end = args.end if args.end is not None else min(duration, PHASES[-1].end)

    annotated_dir = OUT_ROOT / "annotated-center-crops"
    patch_dir = OUT_ROOT / "formation-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in (annotated_dir, patch_dir, sheet_dir):
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    step = 1.0 / args.sample_rate
    sample_index = 0
    second = args.start
    while second <= end + 1e-6:
        frame_index = int(round(second * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            break
        crop = center_crop(frame)
        phase = phase_for(second)
        candidates = extract_candidates(crop)
        group = select_group(candidates)
        metrics = group_metrics(group, crop)
        confidence, note = classify_group(group, metrics)

        row = {
            "video": VIDEO_NAME,
            "release_id": RELEASE_ID,
            "approx_second": round(second, 3),
            "frame_index": frame_index,
            "phase": phase.name,
            "confidence": confidence,
            "candidate_count": len(candidates),
            "group_size": metrics.get("group_size", 0) if metrics else 0,
            "centroid_x_crop": round(metrics.get("centroid_x", 0.0), 3) if metrics else "",
            "centroid_y_crop": round(metrics.get("centroid_y", 0.0), 3) if metrics else "",
            "centroid_x_full": round(CROP_X0 + metrics["centroid_x"], 3) if metrics else "",
            "centroid_y_full": round(CROP_Y0 + metrics["centroid_y"], 3) if metrics else "",
            "span_x": round(metrics.get("span_x", 0.0), 3) if metrics else "",
            "span_y": round(metrics.get("span_y", 0.0), 3) if metrics else "",
            "sum_area": round(metrics.get("sum_area", 0.0), 3) if metrics else "",
            "mean_area": round(metrics.get("mean_area", 0.0), 3) if metrics else "",
            "max_luma": metrics.get("max_luma", "") if metrics else "",
            "mean_luma": round(metrics.get("mean_luma", 0.0), 3) if metrics else "",
            "mean_pair_distance": round(metrics.get("mean_pair_distance", 0.0), 3) if metrics and metrics.get("mean_pair_distance") != "" else "",
            "max_pair_distance": round(metrics.get("max_pair_distance", 0.0), 3) if metrics and metrics.get("max_pair_distance") != "" else "",
            "d12": round(metrics.get("d12", 0.0), 3) if metrics and metrics.get("d12") != "" else "",
            "d23": round(metrics.get("d23", 0.0), 3) if metrics and metrics.get("d23") != "" else "",
            "d13": round(metrics.get("d13", 0.0), 3) if metrics and metrics.get("d13") != "" else "",
            "overlay_relation": metrics.get("overlay_relation", "") if metrics else "",
            "nearest_overlay_px": round(metrics.get("nearest_overlay_px", 0.0), 3) if metrics and metrics.get("nearest_overlay_px") is not None else "",
            "note": note,
        }
        for index in range(3):
            if index < len(group):
                candidate = group[index]
                row[f"p{index + 1}_x_crop"] = round(candidate["x"], 3)
                row[f"p{index + 1}_y_crop"] = round(candidate["y"], 3)
                row[f"p{index + 1}_area"] = candidate["area"]
                row[f"p{index + 1}_max_luma"] = candidate["max_luma"]
            else:
                row[f"p{index + 1}_x_crop"] = ""
                row[f"p{index + 1}_y_crop"] = ""
                row[f"p{index + 1}_area"] = ""
                row[f"p{index + 1}_max_luma"] = ""
        rows.append(row)

        write_image = sample_index % max(1, int(round(args.sample_rate))) == 0 or confidence == "high"
        if write_image:
            safe_second = f"{second:06.1f}".replace(".", "p")
            annotated = annotate_crop(crop, second, phase, group, confidence)
            annotated_path = annotated_dir / f"{VIDEO_ID}_t{safe_second}.jpg"
            cv2.imwrite(str(annotated_path), annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            annotated_paths.append(annotated_path)

            patch = annotate_patch(crop_group_patch(crop, group), second, confidence)
            patch_path = patch_dir / f"{VIDEO_ID}_t{safe_second}_patch.jpg"
            cv2.imwrite(str(patch_path), patch, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            patch_paths.append(patch_path)

        sample_index += 1
        second = args.start + sample_index * step

    cap.release()

    detail_path = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-formation-review-dod111689142.csv")
    summary_path = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-formation-summary.csv")
    metadata_path = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111689142-metadata.txt")
    assets_path = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-formation-assets.csv")

    fieldnames = [
        "video",
        "release_id",
        "approx_second",
        "frame_index",
        "phase",
        "confidence",
        "candidate_count",
        "group_size",
        "centroid_x_crop",
        "centroid_y_crop",
        "centroid_x_full",
        "centroid_y_full",
        "span_x",
        "span_y",
        "sum_area",
        "mean_area",
        "max_luma",
        "mean_luma",
        "mean_pair_distance",
        "max_pair_distance",
        "d12",
        "d23",
        "d13",
        "overlay_relation",
        "nearest_overlay_px",
        "note",
        "p1_x_crop",
        "p1_y_crop",
        "p1_area",
        "p1_max_luma",
        "p2_x_crop",
        "p2_y_crop",
        "p2_area",
        "p2_max_luma",
        "p3_x_crop",
        "p3_y_crop",
        "p3_area",
        "p3_max_luma",
    ]
    write_csv(detail_path, fieldnames, rows)

    summary_rows = summarize(rows)
    write_csv(
        summary_path,
        [
            "phase",
            "start_second",
            "end_second",
            "samples",
            "high",
            "medium",
            "low",
            "none",
            "three_component_rows",
            "first_three_component_second",
            "last_three_component_second",
            "median_mean_pair_distance",
            "median_max_pair_distance",
            "median_d12",
            "median_d23",
            "median_d13",
            "phase_note",
        ],
        summary_rows,
    )

    crop_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-annotated", cols=3, thumb_width=480)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-patches", cols=4, thumb_width=240)

    metadata_path.write_text(
        "\n".join(
            [
                f"source_video={args.video}",
                f"video_id={VIDEO_ID}",
                f"release_id={RELEASE_ID}",
                f"fps={fps}",
                f"total_frames={total_frames}",
                f"duration_seconds={duration}",
                f"frame_width={width}",
                f"frame_height={height}",
                f"sample_rate={args.sample_rate}",
                f"review_start={args.start}",
                f"review_end={end}",
                "note=OpenCV source video metadata and local review settings; not incident metadata.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    asset_rows = [
        {"artifact_type": "detail_csv", "path": str(detail_path).replace("\\", "/"), "note": "per-sample formation review"},
        {"artifact_type": "summary_csv", "path": str(summary_path).replace("\\", "/"), "note": "phase-level formation summary"},
        {"artifact_type": "metadata", "path": str(metadata_path).replace("\\", "/"), "note": "OpenCV source video metadata"},
    ]
    for path in crop_sheets:
        asset_rows.append({"artifact_type": "annotated_sheet", "path": str(path).replace("\\", "/"), "note": "annotated center-crop contact sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "patch_sheet", "path": str(path).replace("\\", "/"), "note": "formation patch sheet"})
    write_csv(assets_path, ["artifact_type", "path", "note"], asset_rows)

    print(f"wrote {detail_path}")
    print(f"wrote {summary_path}")
    print(f"wrote {assets_path}")
    print(f"wrote {metadata_path}")


if __name__ == "__main__":
    main()
