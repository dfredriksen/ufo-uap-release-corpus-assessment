from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111688825"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR27"
REPORT_ID = "DoW-UAP-D23"
DEFAULT_VIDEO = Path(r"source-files-not-included/DOD_111688825.mp4")
DEFAULT_PHASE_TRACK = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688825-phase-track.csv")
OUT_ROOT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-manual-validation") / VIDEO_ID


CATEGORY_COLORS = {
    "true_compact_return_candidate": (0, 0, 255),
    "reticle_overlay_artifact": (255, 0, 255),
    "shoreline_terrain_artifact": (255, 120, 0),
    "water_texture_artifact": (0, 165, 255),
    "frame_edge_artifact": (120, 120, 120),
    "uncertain": (0, 255, 255),
    "uncertain_no_candidate": (0, 255, 255),
}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def as_float(value: str) -> float | None:
    if value == "" or value is None:
        return None
    return float(value)


def as_int(value: str) -> int | None:
    if value == "" or value is None:
        return None
    return int(float(value))


def load_rows(path: Path, start: float, end: float) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    selected = []
    for row in rows:
        second = float(row["approx_second"])
        if start <= second <= end:
            selected.append(row)
    selected.sort(key=lambda item: float(item["approx_second"]))
    return selected


def candidate_values(row: dict) -> dict:
    return {
        "x": as_float(row["candidate_x"]),
        "y": as_float(row["candidate_y"]),
        "bbox_w": as_int(row["bbox_w"]),
        "bbox_h": as_int(row["bbox_h"]),
        "area": as_int(row["area"]),
        "max_luma": as_int(row["max_luma"]),
        "mean_luma": as_float(row["mean_luma"]),
        "candidate_count": as_int(row["candidate_count"]),
        "overlay_distance": as_float(row["nearest_colored_overlay_px"]),
    }


def is_missing(candidate: dict) -> bool:
    return candidate["x"] is None or candidate["y"] is None


def near_frame_edge(candidate: dict, width: int, height: int) -> bool:
    if is_missing(candidate):
        return False
    x = float(candidate["x"])
    y = float(candidate["y"])
    return x <= 28 or x >= width - 28 or y <= 28 or y >= height - 28


def near_reticle(candidate: dict, row: dict) -> bool:
    if is_missing(candidate):
        return False
    relation = row["overlay_relation"]
    distance = candidate["overlay_distance"]
    if relation == "intersects colored reticle/overlay":
        return True
    if distance is not None and distance <= 18:
        return True
    x = float(candidate["x"])
    y = float(candidate["y"])
    # Cyan reticle and black/redaction graphics dominate the center during PR27.
    return abs(x - 960.0) <= 85 and abs(y - 540.0) <= 75 and distance is not None and distance <= 35


def likely_shoreline_or_terrain(candidate: dict, second: float, phase: str) -> bool:
    if is_missing(candidate):
        return False
    x = float(candidate["x"])
    y = float(candidate["y"])
    if second < 136.0:
        return True
    if phase == "pan to center" and y < 470:
        return True
    # Early zoom frames still contain shoreline/terrain at the upper edge.
    return second < 140.0 and y < 470


def compact_hot_point(candidate: dict) -> bool:
    if is_missing(candidate):
        return False
    bw = candidate["bbox_w"] or 999
    bh = candidate["bbox_h"] or 999
    area = candidate["area"] or 9999
    max_luma = candidate["max_luma"] or 0
    mean_luma = candidate["mean_luma"] or 0.0
    count = candidate["candidate_count"] or 999
    return bw <= 10 and bh <= 10 and area <= 65 and max_luma >= 225 and mean_luma >= 185 and count <= 40


def likely_water_texture(candidate: dict) -> bool:
    if is_missing(candidate):
        return False
    bw = candidate["bbox_w"] or 999
    bh = candidate["bbox_h"] or 999
    area = candidate["area"] or 9999
    max_luma = candidate["max_luma"] or 0
    mean_luma = candidate["mean_luma"] or 0.0
    count = candidate["candidate_count"] or 0
    elongated_or_large = bw > 16 or bh > 16 or area > 120
    low_contrast = max_luma < 215 or mean_luma < 185
    cluttered = count > 45
    return elongated_or_large or low_contrast or cluttered


def classify_row(row: dict, width: int, height: int) -> tuple[str, str, str]:
    second = float(row["approx_second"])
    phase = row["phase"]
    candidate = candidate_values(row)
    if is_missing(candidate):
        return "uncertain_no_candidate", "low", "no compact candidate was detected in the phase pass"
    if near_frame_edge(candidate, width, height):
        return "frame_edge_artifact", "artifact", "candidate is on or adjacent to frame/black-border edge"
    if likely_shoreline_or_terrain(candidate, second, phase):
        return "shoreline_terrain_artifact", "artifact", "candidate falls in early shoreline/terrain transition area"
    if near_reticle(candidate, row):
        if compact_hot_point(candidate) and (candidate["overlay_distance"] or 999) > 18:
            return "uncertain", "low", "compact point is too close to reticle/overlay for strong validation"
        return "reticle_overlay_artifact", "artifact", "candidate is near or intersects colored reticle/overlay graphics"
    if compact_hot_point(candidate):
        return "true_compact_return_candidate", "medium", "compact hot point separated from frame edge and colored overlay"
    if likely_water_texture(candidate):
        return "water_texture_artifact", "artifact", "candidate geometry/luminance/clutter matches water or sensor texture"
    return "uncertain", "low", "candidate is visible but not compact/separated enough for validation"


def add_label(img: np.ndarray, text: str, width: int = 1120) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 36), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def draw_marker(img: np.ndarray, x: float, y: float, color: tuple[int, int, int], radius: int = 24) -> None:
    point = (int(round(x)), int(round(y)))
    cv2.drawMarker(img, point, color, markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    cv2.circle(img, point, radius, color, 2)


def annotate_frame(frame: np.ndarray, row: dict, category: str, quality: str) -> np.ndarray:
    out = frame.copy()
    candidate = candidate_values(row)
    color = CATEGORY_COLORS.get(category, (0, 255, 255))
    if not is_missing(candidate):
        draw_marker(out, float(candidate["x"]), float(candidate["y"]), color)
        cv2.line(out, (960, 540), (int(round(float(candidate["x"]))), int(round(float(candidate["y"])))), (255, 255, 0), 1)
    label = f"{VIDEO_ID} t={float(row['approx_second']):05.1f}s {quality} {category.replace('_', '-')}"
    return add_label(out, label)


def crop_patch(frame: np.ndarray, row: dict, size: int = 160) -> np.ndarray:
    h, w = frame.shape[:2]
    candidate = candidate_values(row)
    if is_missing(candidate):
        cx, cy = w // 2, h // 2
    else:
        cx, cy = int(round(float(candidate["x"]))), int(round(float(candidate["y"])))
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(frame: np.ndarray, row: dict, category: str, quality: str) -> np.ndarray:
    patch = crop_patch(frame, row)
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    color = CATEGORY_COLORS.get(category, (0, 255, 255))
    draw_marker(out, 210, 210, color, radius=46)
    label = f"{VIDEO_ID} t={float(row['approx_second']):05.1f}s {category.replace('_', '-')}"
    return add_label(out, label, width=420)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


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
        for idx, thumb in enumerate(thumbs):
            row = idx // cols
            col = idx % cols
            y = row * thumb_h
            x = col * thumb_width
            sheet[y : y + thumb.shape[0], x : x + thumb.shape[1]] = thumb
        out = out_dir / f"{prefix}-{page:02d}.jpg"
        cv2.imwrite(str(out), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        written.append(out)
    return written


def compact_return_segments(rows: list[dict], max_gap: float = 1.0) -> list[dict]:
    accepted = [row for row in rows if row["manual_category"] == "true_compact_return_candidate"]
    if not accepted:
        return []
    segments: list[list[dict]] = []
    current = [accepted[0]]
    for row in accepted[1:]:
        previous = current[-1]
        if float(row["approx_second"]) - float(previous["approx_second"]) <= max_gap:
            current.append(row)
        else:
            segments.append(current)
            current = [row]
    segments.append(current)
    out = []
    for index, segment in enumerate(segments, 1):
        out.append(
            {
                "segment_id": f"PR27-C{index:02d}",
                "start_second": segment[0]["approx_second"],
                "end_second": segment[-1]["approx_second"],
                "duration_seconds": round(float(segment[-1]["approx_second"]) - float(segment[0]["approx_second"]), 2),
                "sample_count": len(segment),
                "phase_start": segment[0]["phase"],
                "phase_end": segment[-1]["phase"],
                "interpretation": "consecutive validated compact-return candidates; not a physical track without telemetry",
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Manual-validation layer for PR27/D23 DOD_111688825 phase-track rows.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--phase-track", type=Path, default=DEFAULT_PHASE_TRACK)
    parser.add_argument("--start", type=float, default=134.0)
    parser.add_argument("--end", type=float, default=297.0)
    args = parser.parse_args()

    source_rows = load_rows(args.phase_track, args.start, args.end)
    if not source_rows:
        raise RuntimeError(f"No source rows in {args.phase_track} for {args.start}-{args.end}s")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {args.video}")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "validation-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for path in (annotated_dir, patch_dir, sheet_dir):
        ensure_dir(path)

    validation_rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []

    for validation_index, row in enumerate(source_rows):
        category, quality, caveat = classify_row(row, width, height)
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(row["source_frame_index"]))
        ok, frame = cap.read()
        if not ok:
            continue
        annotated_path = annotated_dir / f"frame_{validation_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{validation_index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotate_frame(frame, row, category, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), annotate_patch(frame, row, category, quality), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)

        candidate = candidate_values(row)
        validation_rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "report_id": REPORT_ID,
                "validation_index": validation_index,
                "source_sample_index": row["sample_index"],
                "approx_second": row["approx_second"],
                "source_frame_index": row["source_frame_index"],
                "phase": row["phase"],
                "source_review_confidence": row["review_confidence"],
                "candidate_x": row["candidate_x"],
                "candidate_y": row["candidate_y"],
                "bbox_w": row["bbox_w"],
                "bbox_h": row["bbox_h"],
                "area": row["area"],
                "max_luma": row["max_luma"],
                "mean_luma": row["mean_luma"],
                "candidate_count": row["candidate_count"],
                "nearest_colored_overlay_px": row["nearest_colored_overlay_px"],
                "overlay_relation": row["overlay_relation"],
                "is_near_frame_edge": str(near_frame_edge(candidate, width, height)),
                "is_near_reticle_overlay": str(near_reticle(candidate, row)),
                "manual_category": category,
                "manual_quality": quality,
                "supports_visual_sequence": "yes" if category == "true_compact_return_candidate" else "no",
                "physical_kinematics_use": "no",
                "caveat": caveat,
                "annotated_frame_path": str(annotated_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )

    cap.release()

    validation_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-dod111688825.csv")
    write_csv(validation_csv, list(validation_rows[0].keys()), validation_rows)

    category_counts = Counter(row["manual_category"] for row in validation_rows)
    phase_counts: dict[tuple[str, str], int] = defaultdict(int)
    for row in validation_rows:
        phase_counts[(row["phase"], row["manual_category"])] += 1
    summary_rows: list[dict] = [
        {"metric": "video", "value": VIDEO_NAME, "scope": "manual validation", "note": "local source video"},
        {"metric": "release_report_pair", "value": f"{RELEASE_ID} / {REPORT_ID}", "scope": "manual validation", "note": "DVIDS hard-paired release/report lane"},
        {"metric": "interval", "value": f"{args.start:.1f}s-{args.end:.1f}s", "scope": "manual validation", "note": "active PR27/D23 review interval"},
        {"metric": "sample_count", "value": len(validation_rows), "scope": "manual validation", "note": "phase-track rows reviewed"},
    ]
    for category, count in sorted(category_counts.items()):
        summary_rows.append({"metric": f"manual_category_count: {category}", "value": count, "scope": "manual validation", "note": "category count"})
    for (phase, category), count in sorted(phase_counts.items()):
        summary_rows.append({"metric": f"phase_category_count: {phase} / {category}", "value": count, "scope": "manual validation", "note": "category count by phase"})

    segments = compact_return_segments(validation_rows)
    summary_rows.append({"metric": "compact_return_segments", "value": len(segments), "scope": "manual validation", "note": "validated compact-return runs with <=1.0s gaps"})
    if segments:
        longest = max(segments, key=lambda item: item["sample_count"])
        summary_rows.append(
            {
                "metric": "longest_compact_return_segment",
                "value": f"{longest['segment_id']} {longest['start_second']}-{longest['end_second']}s ({longest['sample_count']} samples)",
                "scope": "manual validation",
                "note": "not a physical track without telemetry",
            }
        )

    summary_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-summary.csv")
    write_csv(summary_csv, ["metric", "value", "scope", "note"], summary_rows)

    segments_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-compact-return-segments.csv")
    write_csv(
        segments_csv,
        ["segment_id", "start_second", "end_second", "duration_seconds", "sample_count", "phase_start", "phase_end", "interpretation"],
        segments,
    )

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-manual-validation-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-manual-validation-patches", cols=8, thumb_width=180)

    asset_rows: list[dict] = [
        {"artifact_type": "manual_validation_csv", "path": str(validation_csv).replace("\\", "/"), "note": "PR27/D23 category validation table"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR27/D23 validation category summary"},
        {"artifact_type": "segments_csv", "path": str(segments_csv).replace("\\", "/"), "note": "validated compact-return candidate segments"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "manual-validation annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "manual-validation zoom-patch sheet"})
    asset_csv = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"interval={args.start:.1f}-{args.end:.1f}s rows={len(validation_rows)}")
    print(f"category_counts={dict(category_counts)}")
    print(f"segments={len(segments)}")
    print(f"validation_csv={validation_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"segments_csv={segments_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()
