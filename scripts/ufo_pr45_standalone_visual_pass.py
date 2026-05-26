from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source-files-not-included"


VIDEO_ID = "DOD_111689123"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR45"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111689123.mp4"
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr45-standalone") / VIDEO_ID

CROP_WIDTH = 960
CROP_HEIGHT = 540
CROP_X0 = 480
CROP_Y0 = 270
CROP_CENTER_X = CROP_WIDTH // 2
CROP_CENTER_Y = CROP_HEIGHT // 2
SEARCH_X_RADIUS = 300
SEARCH_Y_TOP = 160
SEARCH_Y_BOTTOM = 245


@dataclass(frozen=True)
class Phase:
    name: str
    start: float
    end: float
    note: str


PHASES = (
    Phase(
        "initial lock / small contrast",
        0.0,
        17.9,
        "Small or weak central contrast inside/near the track ring; reticle graphics are a major confound.",
    ),
    Phase(
        "contrast-transition interval",
        18.0,
        34.9,
        "Sensor/background contrast changes while the central area remains near the reticle.",
    ),
    Phase(
        "growth interval",
        35.0,
        50.9,
        "Central contrast area becomes larger and brighter in the public clip.",
    ),
    Phase(
        "late large-return / exit-adjacent interval",
        51.0,
        58.5,
        "Largest visible central contrast area; clip ends before any independent geometry is recoverable.",
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
    red = (hue <= 20) | (hue >= 165)
    magenta = (hue >= 130) & (hue <= 165)
    green_cyan = (hue >= 45) & (hue <= 115)
    mask = ((sat > 55) & (val > 50) & (red | magenta | green_cyan)).astype(np.uint8) * 255
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


def detect_central_contrast(crop: np.ndarray) -> dict:
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)

    x0 = max(0, CROP_CENTER_X - SEARCH_X_RADIUS)
    x1 = min(CROP_WIDTH, CROP_CENTER_X + SEARCH_X_RADIUS + 1)
    y0 = max(0, CROP_CENTER_Y - SEARCH_Y_TOP)
    y1 = min(CROP_HEIGHT, CROP_CENTER_Y + SEARCH_Y_BOTTOM + 1)
    roi = gray[y0:y1, x0:x1]
    roi_hsv = hsv[y0:y1, x0:x1]
    overlay = colored_overlay_mask(crop)[y0:y1, x0:x1]

    low_sat = roi_hsv[:, :, 1] < 105
    not_overlay = overlay == 0
    not_black_redaction = roi > 38
    valid = low_sat & not_overlay & not_black_redaction
    if int(valid.sum()) < 250:
        return {}

    values = roi[valid]
    median = float(np.median(values))
    p995 = float(np.percentile(values, 99.5))
    threshold = int(max(median + 22.0, min(p995, 218.0), 82.0))

    mask = ((roi >= threshold) & valid).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 3)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((4, 4), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        bx, by, bw, bh, area = stats[label]
        if area < 4 or area > 9500:
            continue
        if bw > 280 or bh > 190:
            continue
        aspect = max(bw / max(1, bh), bh / max(1, bw))
        if aspect > 8.0:
            continue
        cx, cy = centroids[label]
        full_x = x0 + float(cx)
        full_y = y0 + float(cy)
        component_values = roi[labels == label]
        max_luma = int(component_values.max())
        mean_luma = float(component_values.mean())
        dist = math.hypot(full_x - CROP_CENTER_X, full_y - CROP_CENTER_Y)
        contrast = mean_luma - median

        center_bonus = max(0.0, 1.0 - dist / 330.0)
        area_bonus = min(area, 1800) / 1800.0
        score = (max_luma / 255.0) * 2.0 + (contrast / 90.0) + area_bonus + center_bonus

        candidates.append(
            {
                "x": full_x,
                "y": full_y,
                "bbox_x": int(x0 + bx),
                "bbox_y": int(y0 + by),
                "bbox_w": int(bw),
                "bbox_h": int(bh),
                "area": int(area),
                "max_luma": max_luma,
                "mean_luma": mean_luma,
                "local_median": median,
                "contrast_vs_local_median": contrast,
                "threshold": threshold,
                "distance_from_reticle_center": dist,
                "candidate_count": 0,
                "score": score,
            }
        )

    if not candidates:
        return {}
    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    best["candidate_count"] = len(candidates)
    return best


def bbox_intersects_reticle(candidate: dict) -> str:
    if not candidate:
        return "no candidate"
    x0 = candidate["bbox_x"]
    y0 = candidate["bbox_y"]
    x1 = x0 + candidate["bbox_w"]
    y1 = y0 + candidate["bbox_h"]
    vertical = x0 <= CROP_CENTER_X + 6 and x1 >= CROP_CENTER_X - 6
    horizontal = y0 <= CROP_CENTER_Y + 6 and y1 >= CROP_CENTER_Y - 6
    center_box = x0 <= CROP_CENTER_X + 28 and x1 >= CROP_CENTER_X - 28 and y0 <= CROP_CENTER_Y + 24 and y1 >= CROP_CENTER_Y - 24
    if center_box:
        return "overlaps central reticle box"
    if vertical or horizontal:
        return "overlaps reticle line"
    return "separate from reticle center"


def classify_candidate(candidate: dict, overlay_relation: str, reticle_relation: str) -> tuple[str, str]:
    if not candidate:
        return "none", "no low-saturation central contrast component survived overlay suppression"

    area = int(candidate["area"])
    max_luma = int(candidate["max_luma"])
    contrast = float(candidate["contrast_vs_local_median"])
    dist = float(candidate["distance_from_reticle_center"])
    bbox_w = int(candidate["bbox_w"])
    bbox_h = int(candidate["bbox_h"])

    if area >= 160 and max_luma >= 150 and contrast >= 18 and dist <= 95:
        note = "large or growing central contrast component; still reticle-confounded"
        return "high", note
    if area >= 35 and max_luma >= 125 and contrast >= 12 and dist <= 130:
        note = "compact central contrast component, but reticle/overlay may contribute"
        return "medium", note
    if area >= 8 and max_luma >= 105 and bbox_w <= 60 and bbox_h <= 45:
        note = "weak central candidate; likely mixed with reticle graphics or background texture"
        return "low", note
    if overlay_relation.startswith("intersects") or reticle_relation != "separate from reticle center":
        return "low", "candidate is present but too confounded by tracking graphics for independent use"
    return "low", "candidate does not meet conservative size/contrast thresholds"


def add_label(img: np.ndarray, text: str, width: int | None = None) -> np.ndarray:
    out = img.copy()
    label_width = width or out.shape[1]
    cv2.rectangle(out, (0, 0), (min(label_width, out.shape[1]), 36), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_crop(crop: np.ndarray, second: float, phase: Phase, candidate: dict, confidence: str) -> np.ndarray:
    out = crop.copy()
    cv2.rectangle(
        out,
        (CROP_CENTER_X - SEARCH_X_RADIUS, CROP_CENTER_Y - SEARCH_Y_TOP),
        (CROP_CENTER_X + SEARCH_X_RADIUS, CROP_CENTER_Y + SEARCH_Y_BOTTOM),
        (255, 255, 0),
        1,
    )
    cv2.drawMarker(out, (CROP_CENTER_X, CROP_CENTER_Y), (255, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=22, thickness=1)
    if candidate:
        x = int(round(candidate["x"]))
        y = int(round(candidate["y"]))
        cv2.rectangle(
            out,
            (candidate["bbox_x"], candidate["bbox_y"]),
            (candidate["bbox_x"] + candidate["bbox_w"], candidate["bbox_y"] + candidate["bbox_h"]),
            (0, 0, 255),
            2,
        )
        cv2.drawMarker(out, (x, y), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
        cv2.circle(out, (x, y), 18, (0, 0, 255), 2)
    label = f"{VIDEO_ID} t={second:05.1f}s {phase.name}; {confidence}"
    return add_label(out, label)


def crop_patch(crop: np.ndarray, candidate: dict, size: int = 180) -> np.ndarray:
    h, w = crop.shape[:2]
    if candidate:
        cx = int(round(candidate["x"]))
        cy = int(round(candidate["y"]))
    else:
        cx = CROP_CENTER_X
        cy = CROP_CENTER_Y
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return crop[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(patch: np.ndarray, second: float, confidence: str) -> np.ndarray:
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (210, 210), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=32, thickness=2)
    cv2.circle(out, (210, 210), 44, (0, 0, 255), 2)
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


def summarize(rows: list[dict]) -> list[dict]:
    output: list[dict] = []
    for phase in PHASES:
        subset = [row for row in rows if row["phase"] == phase.name]
        if not subset:
            continue
        counts = Counter(row["confidence"] for row in subset)
        detected = [row for row in subset if row["confidence"] != "none"]
        high_or_medium_seconds = [float(row["approx_second"]) for row in subset if row["confidence"] in {"high", "medium"}]
        areas = [int(row["area_px"]) for row in detected if row["area_px"]]
        widths = [int(row["bbox_w"]) for row in detected if row["bbox_w"]]
        heights = [int(row["bbox_h"]) for row in detected if row["bbox_h"]]
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
                "high_or_medium": counts.get("high", 0) + counts.get("medium", 0),
                "median_area_px": round(statistics.median(areas), 3) if areas else "",
                "max_area_px": max(areas) if areas else "",
                "median_bbox_w": round(statistics.median(widths), 3) if widths else "",
                "median_bbox_h": round(statistics.median(heights), 3) if heights else "",
                "first_high_or_medium_second": min(high_or_medium_seconds) if high_or_medium_seconds else "",
                "last_high_or_medium_second": max(high_or_medium_seconds) if high_or_medium_seconds else "",
                "phase_note": phase.note,
            }
        )
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Standalone PR45 visual pass for DOD_111689123.")
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
    patch_dir = OUT_ROOT / "contrast-patches"
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
        candidate = detect_central_contrast(crop)
        if candidate:
            overlay_relation, overlay_distance = nearest_overlay_distance(crop, candidate["x"], candidate["y"])
        else:
            overlay_relation, overlay_distance = "no candidate", None
        reticle_relation = bbox_intersects_reticle(candidate)
        confidence, note = classify_candidate(candidate, overlay_relation, reticle_relation)

        row = {
            "video": VIDEO_NAME,
            "release_id": RELEASE_ID,
            "approx_second": round(second, 3),
            "frame_index": frame_index,
            "phase": phase.name,
            "confidence": confidence,
            "candidate_x_crop": round(candidate.get("x", float("nan")), 3) if candidate else "",
            "candidate_y_crop": round(candidate.get("y", float("nan")), 3) if candidate else "",
            "candidate_x_full": round(CROP_X0 + candidate["x"], 3) if candidate else "",
            "candidate_y_full": round(CROP_Y0 + candidate["y"], 3) if candidate else "",
            "bbox_x": candidate.get("bbox_x", "") if candidate else "",
            "bbox_y": candidate.get("bbox_y", "") if candidate else "",
            "bbox_w": candidate.get("bbox_w", "") if candidate else "",
            "bbox_h": candidate.get("bbox_h", "") if candidate else "",
            "area_px": candidate.get("area", "") if candidate else "",
            "max_luma": candidate.get("max_luma", "") if candidate else "",
            "mean_luma": round(candidate.get("mean_luma", 0.0), 3) if candidate else "",
            "local_median_luma": round(candidate.get("local_median", 0.0), 3) if candidate else "",
            "contrast_vs_local_median": round(candidate.get("contrast_vs_local_median", 0.0), 3) if candidate else "",
            "threshold": candidate.get("threshold", "") if candidate else "",
            "distance_from_reticle_center": round(candidate.get("distance_from_reticle_center", 0.0), 3) if candidate else "",
            "candidate_count": candidate.get("candidate_count", "") if candidate else "",
            "overlay_relation": overlay_relation,
            "nearest_overlay_px": round(overlay_distance, 3) if overlay_distance is not None else "",
            "reticle_relation": reticle_relation,
            "note": note,
        }
        rows.append(row)

        # Keep every one-second representative image plus all high rows for audit sheets.
        write_image = sample_index % max(1, int(round(args.sample_rate))) == 0 or confidence == "high"
        if write_image:
            safe_second = f"{second:06.1f}".replace(".", "p")
            annotated = annotate_crop(crop, second, phase, candidate, confidence)
            annotated_path = annotated_dir / f"{VIDEO_ID}_t{safe_second}.jpg"
            cv2.imwrite(str(annotated_path), annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            annotated_paths.append(annotated_path)

            patch = annotate_patch(crop_patch(crop, candidate), second, confidence)
            patch_path = patch_dir / f"{VIDEO_ID}_t{safe_second}_patch.jpg"
            cv2.imwrite(str(patch_path), patch, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            patch_paths.append(patch_path)

        sample_index += 1
        second = args.start + sample_index * step

    cap.release()

    detail_path = Path("research/ufo-video-pr45-standalone-review-dod111689123.csv")
    summary_path = Path("research/ufo-video-pr45-standalone-summary.csv")
    metadata_path = Path("research/ufo-video-dod_111689123-metadata.txt")
    assets_path = Path("research/ufo-video-pr45-standalone-assets.csv")

    fieldnames = [
        "video",
        "release_id",
        "approx_second",
        "frame_index",
        "phase",
        "confidence",
        "candidate_x_crop",
        "candidate_y_crop",
        "candidate_x_full",
        "candidate_y_full",
        "bbox_x",
        "bbox_y",
        "bbox_w",
        "bbox_h",
        "area_px",
        "max_luma",
        "mean_luma",
        "local_median_luma",
        "contrast_vs_local_median",
        "threshold",
        "distance_from_reticle_center",
        "candidate_count",
        "overlay_relation",
        "nearest_overlay_px",
        "reticle_relation",
        "note",
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
            "high_or_medium",
            "median_area_px",
            "max_area_px",
            "median_bbox_w",
            "median_bbox_h",
            "first_high_or_medium_second",
            "last_high_or_medium_second",
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
        {"artifact_type": "detail_csv", "path": str(detail_path).replace("\\", "/"), "note": "per-sample central contrast review"},
        {"artifact_type": "summary_csv", "path": str(summary_path).replace("\\", "/"), "note": "phase-level review summary"},
        {"artifact_type": "metadata", "path": str(metadata_path).replace("\\", "/"), "note": "OpenCV source video metadata"},
    ]
    for path in crop_sheets:
        asset_rows.append({"artifact_type": "annotated_sheet", "path": str(path).replace("\\", "/"), "note": "annotated center-crop contact sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "patch_sheet", "path": str(path).replace("\\", "/"), "note": "central contrast patch sheet"})
    write_csv(assets_path, ["artifact_type", "path", "note"], asset_rows)

    print(f"wrote {detail_path}")
    print(f"wrote {summary_path}")
    print(f"wrote {assets_path}")
    print(f"wrote {metadata_path}")


if __name__ == "__main__":
    main()

