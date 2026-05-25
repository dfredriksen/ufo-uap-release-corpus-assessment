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


VIDEO_ID = "DOD_111689115"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR44"
DEFAULT_VIDEO = Path(r"I:\My Drive\UFO\DOD_111689115.mp4")
DEFAULT_SEED_TRACK = Path("research/ufo-video-object-position-dod111689115.csv")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr44-standalone") / VIDEO_ID

CROP_WIDTH = 960
CROP_HEIGHT = 540
CROP_X0 = 480
CROP_Y0 = 270


@dataclass
class Seed:
    second: float
    x: float
    y: float
    confidence: str
    note: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_seeds(path: Path, start: float, end: float) -> list[Seed]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    seeds: list[Seed] = []
    for row in rows:
        second = float(row["second_index"])
        if not (start <= second <= end):
            continue
        if not row["best_x"] or not row["best_y"]:
            continue
        seeds.append(
            Seed(
                second=second,
                x=float(row["best_x"]),
                y=float(row["best_y"]),
                confidence=row["confidence"],
                note=row["note"],
            )
        )
    seeds.sort(key=lambda seed: seed.second)
    return seeds


def center_crop(frame: np.ndarray) -> np.ndarray:
    return frame[CROP_Y0 : CROP_Y0 + CROP_HEIGHT, CROP_X0 : CROP_X0 + CROP_WIDTH].copy()


def phase_for(second: float) -> tuple[str, str]:
    if 154.0 <= second < 205.0:
        return (
            "primary sustained point-return interval",
            "Within DVIDS 00:31-03:24 sensor focus/track interval",
        )
    if 205.0 <= second <= 243.0:
        return (
            "reticle-cycling continued point-return interval",
            "Within DVIDS 03:25-04:23 changing reticle/field-of-view interval",
        )
    return ("outside dense PR44 interval", "Outside selected dense interval")


def interpolate_seed(seeds: list[Seed], second: float) -> tuple[float, float, str, str, float, float]:
    before = [seed for seed in seeds if seed.second <= second]
    after = [seed for seed in seeds if seed.second >= second]
    prev_seed = max(before, key=lambda seed: seed.second) if before else seeds[0]
    next_seed = min(after, key=lambda seed: seed.second) if after else seeds[-1]
    if prev_seed.second == next_seed.second:
        return prev_seed.x, prev_seed.y, prev_seed.confidence, prev_seed.note, prev_seed.second, next_seed.second
    alpha = (second - prev_seed.second) / (next_seed.second - prev_seed.second)
    x = prev_seed.x + (next_seed.x - prev_seed.x) * alpha
    y = prev_seed.y + (next_seed.y - prev_seed.y) * alpha
    confidence = prev_seed.confidence if prev_seed.confidence == next_seed.confidence else "interpolated"
    return x, y, confidence, "interpolated between one-fps seed detections", prev_seed.second, next_seed.second


def colored_overlay_mask(crop: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_green = (hue >= 45) & (hue <= 115)
    red_or_orange = (hue <= 25) | (hue >= 170)
    mask = ((sat > 65) & (val > 65) & (cyan_green | red_or_orange)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)


def nearest_overlay_distance(crop: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(crop)
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


def local_bright_refine(crop: np.ndarray, predicted_x: float, predicted_y: float, radius: int = 48) -> dict:
    h, w = crop.shape[:2]
    px = int(round(predicted_x))
    py = int(round(predicted_y))
    x0 = max(0, px - radius)
    x1 = min(w, px + radius + 1)
    y0 = max(0, py - radius)
    y1 = min(h, py + radius + 1)
    window = crop[y0:y1, x0:x1]
    if window.size == 0:
        return {}

    hsv = cv2.cvtColor(window, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(window, cv2.COLOR_BGR2GRAY)
    overlay = colored_overlay_mask(window) == 0
    low_sat = hsv[:, :, 1] < 80
    valid = low_sat & overlay & (gray > 35)
    if int(valid.sum()) < 8:
        return {}

    threshold = int(np.percentile(gray[valid], 99.55))
    threshold = max(170, min(threshold, 246))
    mask = ((gray >= threshold) & valid).astype(np.uint8) * 255
    mask = cv2.medianBlur(mask, 3)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        bx, by, bw, bh, area = stats[label]
        if area < 2 or area > 240:
            continue
        if bw > 28 or bh > 28:
            continue
        cx, cy = centroids[label]
        full_x = x0 + float(cx)
        full_y = y0 + float(cy)
        values = gray[labels == label]
        max_luma = int(values.max())
        mean_luma = float(values.mean())
        dist = math.hypot(full_x - predicted_x, full_y - predicted_y)
        score = (max_luma / 255.0) * 2.0 + (mean_luma / 255.0) + min(area, 60) / 60.0 - 1.1 * (dist / radius)
        candidates.append(
            {
                "x": full_x,
                "y": full_y,
                "bbox_w": int(bw),
                "bbox_h": int(bh),
                "area": int(area),
                "max_luma": max_luma,
                "mean_luma": mean_luma,
                "distance_from_prediction": dist,
                "score": score,
                "candidate_count": 0,
            }
        )
    if not candidates:
        return {}
    candidates.sort(key=lambda item: item["score"], reverse=True)
    best = candidates[0]
    best["candidate_count"] = len(candidates)
    return best


def classify_confidence(refined: dict, seed_confidence: str, relation: str) -> str:
    if not refined:
        return "low"
    dist = float(refined["distance_from_prediction"])
    max_luma = int(refined["max_luma"])
    if seed_confidence == "high" and dist <= 18 and max_luma >= 210 and not relation.startswith("intersects"):
        return "high"
    if dist <= 32 and max_luma >= 190:
        return "medium"
    return "low"


def add_label(img: np.ndarray, text: str, width: int = 760) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 34), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def crop_patch(crop: np.ndarray, x: float, y: float, size: int = 120) -> np.ndarray:
    h, w = crop.shape[:2]
    half = size // 2
    cx = int(round(x))
    cy = int(round(y))
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return crop[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_crop(crop: np.ndarray, x: float, y: float, px: float, py: float, label: str) -> np.ndarray:
    out = crop.copy()
    cv2.drawMarker(out, (int(round(px)), int(round(py))), (255, 0, 0), markerType=cv2.MARKER_CROSS, markerSize=24, thickness=2)
    cv2.circle(out, (int(round(px)), int(round(py))), 16, (255, 0, 0), 1)
    cv2.drawMarker(out, (int(round(x)), int(round(y))), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    cv2.circle(out, (int(round(x)), int(round(y))), 22, (0, 0, 255), 2)
    cv2.line(out, (CROP_WIDTH // 2, CROP_HEIGHT // 2), (int(round(x)), int(round(y))), (255, 255, 0), 1)
    return add_label(out, label)


def annotate_patch(patch: np.ndarray, label: str) -> np.ndarray:
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (210, 210), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=34, thickness=2)
    cv2.circle(out, (210, 210), 46, (0, 0, 255), 2)
    return add_label(out, label, width=420)


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
    return math.hypot(float(b["object_x_center_crop"]) - float(a["object_x_center_crop"]), float(b["object_y_center_crop"]) - float(a["object_y_center_crop"]))


def stats_for(name: str, rows: list[dict]) -> dict:
    if len(rows) < 2:
        raise ValueError(f"Need at least two rows for {name}")
    rows = sorted(rows, key=lambda row: float(row["approx_second"]))
    duration = float(rows[-1]["approx_second"]) - float(rows[0]["approx_second"])
    net = distance(rows[0], rows[-1])
    total_path = 0.0
    step_rates: list[float] = []
    for prev, curr in zip(rows, rows[1:]):
        dt = float(curr["approx_second"]) - float(prev["approx_second"])
        if dt <= 0:
            continue
        step = distance(prev, curr)
        total_path += step
        step_rates.append(step / dt)
    sorted_rates = sorted(step_rates)
    p95 = sorted_rates[int(round(0.95 * (len(sorted_rates) - 1)))] if sorted_rates else 0.0
    return {
        "track": name,
        "sample_count": len(rows),
        "start_second": rows[0]["approx_second"],
        "end_second": rows[-1]["approx_second"],
        "duration_second": round(duration, 3),
        "net_displacement_px": round(net, 3),
        "net_rate_px_s": round(net / duration, 3) if duration else "",
        "total_path_px": round(total_path, 3),
        "path_average_rate_px_s": round(total_path / duration, 3) if duration else "",
        "step_rate_mean_px_s": round(statistics.mean(step_rates), 3) if step_rates else "",
        "step_rate_median_px_s": round(statistics.median(step_rates), 3) if step_rates else "",
        "step_rate_p95_px_s": round(p95, 3),
    }


def draw_trajectory(rows: list[dict], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    canvas = np.full((CROP_HEIGHT, CROP_WIDTH, 3), 34, dtype=np.uint8)
    cv2.line(canvas, (CROP_WIDTH // 2, 0), (CROP_WIDTH // 2, CROP_HEIGHT), (70, 70, 70), 1)
    cv2.line(canvas, (0, CROP_HEIGHT // 2), (CROP_WIDTH, CROP_HEIGHT // 2), (70, 70, 70), 1)
    points = [(int(round(float(row["object_x_center_crop"]))), int(round(float(row["object_y_center_crop"])))) for row in rows]
    cv2.polylines(canvas, [np.array(points, dtype=np.int32)], False, (255, 255, 0), 2)
    for row, point in zip(rows, points):
        phase = row["phase"]
        color = (0, 0, 255) if phase.startswith("primary") else (0, 255, 255)
        cv2.circle(canvas, point, 2, color, -1)
    cv2.rectangle(canvas, (0, 0), (930, 38), (0, 0, 0), -1)
    cv2.putText(
        canvas,
        "PR44 DOD_111689115 dense seeded audit track, 154.0s-243.0s; red=primary, yellow=reticle phase",
        (8, 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    cv2.imwrite(str(out_path), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Dense PR44 standalone quantitative pass for DOD_111689115.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--seed-track", type=Path, default=DEFAULT_SEED_TRACK)
    parser.add_argument("--start", type=float, default=154.0)
    parser.add_argument("--end", type=float, default=243.0)
    parser.add_argument("--sample-rate", type=float, default=5.0)
    args = parser.parse_args()

    seeds = load_seeds(args.seed_track, args.start, args.end)
    if len(seeds) < 2:
        raise RuntimeError("Need at least two one-fps seed detections")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    annotated_dir = OUT_ROOT / "annotated-center-crops"
    patch_dir = OUT_ROOT / "object-zoom-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    sample_count = int(round((args.end - args.start) * args.sample_rate)) + 1
    for sample_index in range(sample_count):
        second = round(args.start + sample_index / args.sample_rate, 1)
        frame_index = min(int(round(second * fps)), max(0, total_frames - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        crop = center_crop(frame)
        predicted_x, predicted_y, seed_confidence, seed_note, prev_seed, next_seed = interpolate_seed(seeds, second)
        refined = local_bright_refine(crop, predicted_x, predicted_y)
        if refined:
            object_x = float(refined["x"])
            object_y = float(refined["y"])
            refinement_delta = float(refined["distance_from_prediction"])
            bbox_w = int(refined["bbox_w"])
            bbox_h = int(refined["bbox_h"])
            area = int(refined["area"])
            max_luma = int(refined["max_luma"])
            mean_luma = round(float(refined["mean_luma"]), 2)
            candidate_count = int(refined["candidate_count"])
            marking_basis = "interpolated one-fps seed plus local compact-bright refinement"
        else:
            object_x = predicted_x
            object_y = predicted_y
            refinement_delta = 0.0
            bbox_w = ""
            bbox_h = ""
            area = ""
            max_luma = ""
            mean_luma = ""
            candidate_count = ""
            marking_basis = "interpolated one-fps seed only; local compact-bright refinement failed"
        relation, nearest_overlay = nearest_overlay_distance(crop, object_x, object_y)
        confidence = classify_confidence(refined, seed_confidence, relation)
        phase, dvids_anchor = phase_for(second)

        label = f"{VIDEO_ID} t={second:05.1f}s conf={confidence}"
        annotated_path = annotated_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_crop(crop, object_x, object_y, predicted_x, predicted_y, label), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(crop_patch(crop, object_x, object_y), label), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)

        rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "sample_index": sample_index,
                "approx_second": f"{second:.1f}",
                "source_frame_index": frame_index,
                "phase": phase,
                "dvids_anchor": dvids_anchor,
                "object_x_center_crop": round(object_x, 1),
                "object_y_center_crop": round(object_y, 1),
                "object_x_full_frame": round(object_x + CROP_X0, 1),
                "object_y_full_frame": round(object_y + CROP_Y0, 1),
                "dx_from_crop_center": round(object_x - CROP_WIDTH / 2, 1),
                "dy_from_crop_center": round(object_y - CROP_HEIGHT / 2, 1),
                "predicted_x_center_crop": round(predicted_x, 1),
                "predicted_y_center_crop": round(predicted_y, 1),
                "prev_seed_second": f"{prev_seed:.1f}",
                "next_seed_second": f"{next_seed:.1f}",
                "seed_confidence": seed_confidence,
                "seed_note": seed_note,
                "refinement_delta_px": round(refinement_delta, 2),
                "object_bbox_w": bbox_w,
                "object_bbox_h": bbox_h,
                "object_component_area": area,
                "object_max_luma": max_luma,
                "object_mean_luma": mean_luma,
                "candidate_count": candidate_count,
                "nearest_colored_overlay_px": "" if nearest_overlay is None else round(nearest_overlay, 2),
                "overlay_relation": relation,
                "review_confidence": confidence,
                "marking_basis": marking_basis,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )
    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-pr44-dense-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-pr44-dense-patches", cols=8, thumb_width=180)
    trajectory_path = sheet_dir / f"{VIDEO_ID}-pr44-dense-trajectory.jpg"
    draw_trajectory(rows, trajectory_path)

    track_csv = Path("research/ufo-video-pr44-dense-track-dod111689115.csv")
    write_csv(track_csv, list(rows[0].keys()), rows)

    primary_rows = [row for row in rows if row["phase"].startswith("primary")]
    reticle_rows = [row for row in rows if row["phase"].startswith("reticle")]
    summary_rows = [
        stats_for("dense_seeded_pr44_primary_plus_reticle_154_243", rows),
        stats_for("dense_seeded_pr44_primary_154_204", primary_rows),
        stats_for("dense_seeded_pr44_reticle_205_243", reticle_rows),
    ]
    confidence_counts = Counter(row["review_confidence"] for row in rows)
    overlay_counts = Counter(row["overlay_relation"] for row in rows)
    for key, value in sorted(confidence_counts.items()):
        summary_rows.append({"track": f"confidence_count: {key}", "sample_count": value})
    for key, value in sorted(overlay_counts.items()):
        summary_rows.append({"track": f"overlay_count: {key}", "sample_count": value})

    summary_csv = Path("research/ufo-video-pr44-dense-track-summary.csv")
    write_csv(
        summary_csv,
        [
            "track",
            "sample_count",
            "start_second",
            "end_second",
            "duration_second",
            "net_displacement_px",
            "net_rate_px_s",
            "total_path_px",
            "path_average_rate_px_s",
            "step_rate_mean_px_s",
            "step_rate_median_px_s",
            "step_rate_p95_px_s",
        ],
        summary_rows,
    )

    asset_rows: list[dict] = [
        {"artifact_type": "dense_track_csv", "path": str(track_csv).replace("\\", "/"), "note": "5 fps seeded PR44 dense audit track"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR44 dense track image-plane summary"},
        {"artifact_type": "trajectory_plot", "path": str(trajectory_path).replace("\\", "/"), "note": "center-crop trajectory overview"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "dense annotated center-crop sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "dense object zoom-patch sheet"})

    asset_csv = Path("research/ufo-video-pr44-dense-track-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"fps={fps} total_frames={total_frames}")
    print(f"seed_count={len(seeds)} samples={len(rows)}")
    print(f"confidence_counts={dict(confidence_counts)}")
    print(f"track_csv={track_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

