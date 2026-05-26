from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source-files-not-included"


VIDEO_ID = "DOD_111689011"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR34"
REPORT_ID = "DoW-UAP-D33"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111689011.mp4"
DEFAULT_PHASE_TRACK = Path("research/ufo-video-dod_111689011-phase-track.csv")
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr34-d33-manual-track") / VIDEO_ID


@dataclass
class SourceRow:
    sample_index: int
    second: float
    frame_index: int
    phase: str
    source_x: float
    source_y: float
    source_confidence: str
    source_overlay_relation: str
    source_bbox_w: str
    source_bbox_h: str
    source_area: str
    source_candidate_count: str


@dataclass
class TrackRow:
    source: SourceRow
    manual_x: float
    manual_y: float
    manual_status: str
    manual_quality: str
    caveat: str
    nearest_prev_second: float | None = None
    nearest_next_second: float | None = None


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def is_top_edge_false_positive(row: SourceRow) -> bool:
    return row.source_y < 50.0 and row.source_x > 1700.0


def load_source_rows(path: Path, start: float, end: float) -> list[SourceRow]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    selected: list[SourceRow] = []
    for row in rows:
        second = float(row["approx_second"])
        if start <= second <= end:
            selected.append(
                SourceRow(
                    sample_index=int(row["sample_index"]),
                    second=second,
                    frame_index=int(row["source_frame_index"]),
                    phase=row["phase"],
                    source_x=float(row["candidate_x"]),
                    source_y=float(row["candidate_y"]),
                    source_confidence=row["review_confidence"],
                    source_overlay_relation=row["overlay_relation"],
                    source_bbox_w=row["bbox_w"],
                    source_bbox_h=row["bbox_h"],
                    source_area=row["area"],
                    source_candidate_count=row["candidate_count"],
                )
            )
    selected.sort(key=lambda item: item.second)
    return selected


def interpolate_row(row: SourceRow, valid_rows: list[SourceRow]) -> TrackRow:
    previous = [candidate for candidate in valid_rows if candidate.second < row.second]
    following = [candidate for candidate in valid_rows if candidate.second > row.second]
    if not previous or not following:
        return TrackRow(
            source=row,
            manual_x=row.source_x,
            manual_y=row.source_y,
            manual_status="excluded_source_detection",
            manual_quality="excluded",
            caveat="source detection rejected and no bounding valid detections were available for interpolation",
        )

    prev_row = max(previous, key=lambda item: item.second)
    next_row = min(following, key=lambda item: item.second)
    alpha = (row.second - prev_row.second) / (next_row.second - prev_row.second)
    manual_x = prev_row.source_x + (next_row.source_x - prev_row.source_x) * alpha
    manual_y = prev_row.source_y + (next_row.source_y - prev_row.source_y) * alpha
    gap = next_row.second - prev_row.second
    return TrackRow(
        source=row,
        manual_x=manual_x,
        manual_y=manual_y,
        manual_status="interpolated_detector_dropout",
        manual_quality="interpolated",
        caveat=f"source detector selected recurring top-edge artifact; interpolated across {gap:.1f}s bounded by accepted detections",
        nearest_prev_second=prev_row.second,
        nearest_next_second=next_row.second,
    )


def build_track(source_rows: list[SourceRow]) -> list[TrackRow]:
    valid_rows = [row for row in source_rows if not is_top_edge_false_positive(row)]
    track: list[TrackRow] = []
    for row in source_rows:
        if is_top_edge_false_positive(row):
            track.append(interpolate_row(row, valid_rows))
            continue

        if row.source_confidence == "high":
            quality = "high"
        elif row.source_confidence == "medium":
            quality = "medium"
        else:
            quality = "low"
        caveat = "accepted detector-centered mark after false-top-edge rejection pass"
        if "near" in row.source_overlay_relation or "intersects" in row.source_overlay_relation:
            caveat += "; close to colored sensor symbology"
        track.append(
            TrackRow(
                source=row,
                manual_x=row.source_x,
                manual_y=row.source_y,
                manual_status="accepted_detector_mark",
                manual_quality=quality,
                caveat=caveat,
            )
        )
    return track


def angle_degrees(dx: float, dy: float) -> float:
    return math.degrees(math.atan2(dy, dx))


def angle_delta(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def add_label(img: np.ndarray, text: str, width: int = 760) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 34), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def draw_crosshair(img: np.ndarray, x: float, y: float, color: tuple[int, int, int], radius: int = 23) -> None:
    point = (int(round(x)), int(round(y)))
    cv2.drawMarker(img, point, color, markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    cv2.circle(img, point, radius, color, 2)


def crop_patch(frame: np.ndarray, x: float, y: float, size: int = 150) -> np.ndarray:
    h, w = frame.shape[:2]
    half = size // 2
    cx = int(round(x))
    cy = int(round(y))
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(patch: np.ndarray, label: str, interpolated: bool) -> np.ndarray:
    out = cv2.resize(patch, (420, 420), interpolation=cv2.INTER_CUBIC)
    color = (0, 255, 255) if interpolated else (0, 0, 255)
    cv2.drawMarker(out, (210, 210), color, markerType=cv2.MARKER_CROSS, markerSize=34, thickness=2)
    cv2.circle(out, (210, 210), 46, color, 2)
    return add_label(out, label, width=420)


def annotate_frame(frame: np.ndarray, track_row: TrackRow, prior_points: list[tuple[int, int]]) -> np.ndarray:
    out = frame.copy()
    if len(prior_points) >= 2:
        cv2.polylines(out, [np.array(prior_points, dtype=np.int32)], False, (255, 255, 0), 2)

    source = track_row.source
    if is_top_edge_false_positive(source):
        draw_crosshair(out, source.source_x, source.source_y, (0, 165, 255), radius=16)
    color = (0, 255, 255) if track_row.manual_status.startswith("interpolated") else (0, 0, 255)
    draw_crosshair(out, track_row.manual_x, track_row.manual_y, color)
    cv2.line(out, (960, 540), (int(round(track_row.manual_x)), int(round(track_row.manual_y))), (255, 255, 0), 1)
    label = (
        f"{VIDEO_ID} t={source.second:05.1f}s "
        f"{track_row.manual_quality} {track_row.manual_status.replace('_', '-')}"
    )
    return add_label(out, label)


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


def compute_step_metrics(track: list[TrackRow]) -> list[dict]:
    metrics: list[dict] = []
    for index, row in enumerate(track):
        if index == 0:
            metrics.append({"step_px": "", "rate_px_s": "", "heading_deg": ""})
            continue
        prev = track[index - 1]
        dt = row.source.second - prev.source.second
        dx = row.manual_x - prev.manual_x
        dy = row.manual_y - prev.manual_y
        step = math.hypot(dx, dy)
        metrics.append(
            {
                "step_px": round(step, 2),
                "rate_px_s": round(step / dt, 2) if dt else "",
                "heading_deg": round(angle_degrees(dx, dy), 2),
            }
        )
    return metrics


def compute_turn_events(track: list[TrackRow], half_window_samples: int = 3, threshold_deg: float = 60.0) -> list[dict]:
    vector_rows: list[dict] = []
    for index in range(half_window_samples, len(track) - half_window_samples):
        before = track[index - half_window_samples]
        after = track[index + half_window_samples]
        dx = after.manual_x - before.manual_x
        dy = after.manual_y - before.manual_y
        span = after.source.second - before.source.second
        distance = math.hypot(dx, dy)
        vector_rows.append(
            {
                "track_index": index,
                "center_second": track[index].source.second,
                "heading_deg": angle_degrees(dx, dy),
                "span_seconds": span,
                "span_distance_px": distance,
            }
        )

    events: list[dict] = []
    for index in range(1, len(vector_rows)):
        previous = vector_rows[index - 1]
        current = vector_rows[index]
        delta = angle_delta(previous["heading_deg"], current["heading_deg"])
        if delta < threshold_deg:
            continue
        if previous["span_distance_px"] < 30.0 or current["span_distance_px"] < 30.0:
            continue
        events.append(
            {
                "event_id": f"PR34-T{len(events) + 1:02d}",
                "approx_second": f"{current['center_second']:.1f}",
                "phase": track[current["track_index"]].source.phase,
                "heading_before_deg": round(previous["heading_deg"], 1),
                "heading_after_deg": round(current["heading_deg"], 1),
                "heading_delta_deg": round(delta, 1),
                "vector_span_seconds": round(current["span_seconds"], 1),
                "previous_span_distance_px": round(previous["span_distance_px"], 1),
                "current_span_distance_px": round(current["span_distance_px"], 1),
                "interpretation": "sharp image-plane heading change; not a real-world turn without sensor geometry",
            }
        )
    return events


def draw_trajectory_plot(track: list[TrackRow], events: list[dict], out_path: Path) -> None:
    ensure_dir(out_path.parent)
    canvas = np.full((1080, 1920, 3), 36, dtype=np.uint8)
    cv2.line(canvas, (960, 0), (960, 1080), (70, 70, 70), 1)
    cv2.line(canvas, (0, 540), (1920, 540), (70, 70, 70), 1)
    points = [(int(round(row.manual_x)), int(round(row.manual_y))) for row in track]
    if len(points) >= 2:
        cv2.polylines(canvas, [np.array(points, dtype=np.int32)], False, (255, 255, 0), 2)

    for row, point in zip(track, points):
        if row.manual_status.startswith("interpolated"):
            cv2.circle(canvas, point, 5, (0, 255, 255), -1)
        else:
            cv2.circle(canvas, point, 4, (0, 0, 255), -1)

    event_times = {float(event["approx_second"]): event["event_id"] for event in events}
    for row, point in zip(track, points):
        event_id = event_times.get(round(row.source.second, 1))
        if not event_id:
            continue
        cv2.circle(canvas, point, 22, (255, 255, 255), 2)
        cv2.putText(canvas, event_id, (point[0] + 10, point[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    cv2.rectangle(canvas, (0, 0), (1120, 48), (0, 0, 0), -1)
    cv2.putText(
        canvas,
        "PR34/D33 DOD_111689011 manual-review track, 4.0s-59.0s; yellow points are interpolated detector dropouts",
        (12, 31),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.72,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    cv2.imwrite(str(out_path), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def generate_assets(video_path: Path, track: list[TrackRow]) -> tuple[list[Path], list[Path]]:
    annotated_dir = OUT_ROOT / "annotated-frames"
    patch_dir = OUT_ROOT / "object-zoom-patches"
    sheet_dir = OUT_ROOT / "sheets"
    for directory in [annotated_dir, patch_dir, sheet_dir]:
        ensure_dir(directory)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {video_path}")

    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    prior_points: list[tuple[int, int]] = []
    for index, row in enumerate(track):
        cap.set(cv2.CAP_PROP_POS_FRAMES, row.source.frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        prior_points.append((int(round(row.manual_x)), int(round(row.manual_y))))
        recent_points = prior_points[-20:]
        annotated = annotate_frame(frame, row, recent_points)
        patch_label = f"{VIDEO_ID} t={row.source.second:05.1f}s {row.manual_quality}"
        patch = annotate_patch(crop_patch(frame, row.manual_x, row.manual_y), patch_label, row.manual_status.startswith("interpolated"))

        annotated_path = annotated_dir / f"frame_{index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{index:04d}_patch.jpg"
        cv2.imwrite(str(annotated_path), annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), patch, [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(annotated_path)
        patch_paths.append(patch_path)

    cap.release()
    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-manual-track-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-manual-track-patches", cols=8, thumb_width=180)
    return annotated_sheets, patch_sheets


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a bounded PR34/D33 manual-review track for DOD_111689011.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--phase-track", type=Path, default=DEFAULT_PHASE_TRACK)
    parser.add_argument("--start", type=float, default=4.0)
    parser.add_argument("--end", type=float, default=59.0)
    args = parser.parse_args()

    source_rows = load_source_rows(args.phase_track, args.start, args.end)
    if not source_rows:
        raise RuntimeError(f"No phase-track rows found in {args.phase_track} for {args.start}-{args.end}s")

    track = build_track(source_rows)
    step_metrics = compute_step_metrics(track)
    turn_events = compute_turn_events(track)
    annotated_sheets, patch_sheets = generate_assets(args.video, track)

    trajectory_plot = OUT_ROOT / "sheets" / f"{VIDEO_ID}-manual-track-trajectory.jpg"
    draw_trajectory_plot(track, turn_events, trajectory_plot)

    track_rows: list[dict] = []
    for index, (row, metrics) in enumerate(zip(track, step_metrics)):
        source = row.source
        track_rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "report_id": REPORT_ID,
                "sample_index": index,
                "approx_second": f"{source.second:.1f}",
                "source_frame_index": source.frame_index,
                "phase": source.phase,
                "source_candidate_x": round(source.source_x, 1),
                "source_candidate_y": round(source.source_y, 1),
                "source_review_confidence": source.source_confidence,
                "source_overlay_relation": source.source_overlay_relation,
                "source_bbox_w": source.source_bbox_w,
                "source_bbox_h": source.source_bbox_h,
                "source_area": source.source_area,
                "source_candidate_count": source.source_candidate_count,
                "source_detection_status": "rejected_top_edge_artifact" if is_top_edge_false_positive(source) else "accepted_source_detection",
                "manual_x_full_frame": round(row.manual_x, 1),
                "manual_y_full_frame": round(row.manual_y, 1),
                "dx_from_frame_center": round(row.manual_x - 960.0, 1),
                "dy_from_frame_center": round(row.manual_y - 540.0, 1),
                "manual_status": row.manual_status,
                "manual_quality": row.manual_quality,
                "nearest_prev_second": "" if row.nearest_prev_second is None else f"{row.nearest_prev_second:.1f}",
                "nearest_next_second": "" if row.nearest_next_second is None else f"{row.nearest_next_second:.1f}",
                "step_from_previous_px": metrics["step_px"],
                "image_plane_rate_px_s": metrics["rate_px_s"],
                "step_heading_deg": metrics["heading_deg"],
                "caveat": row.caveat,
                "annotated_frame_path": str(OUT_ROOT / "annotated-frames" / f"frame_{index:04d}_annotated.jpg").replace("\\", "/"),
                "zoom_patch_path": str(OUT_ROOT / "object-zoom-patches" / f"frame_{index:04d}_patch.jpg").replace("\\", "/"),
            }
        )

    track_csv = Path("research/ufo-video-pr34-d33-manual-track-dod111689011.csv")
    track_fields = list(track_rows[0].keys())
    write_csv(track_csv, track_fields, track_rows)

    turn_csv = Path("research/ufo-pr34-d33-image-plane-turn-events.csv")
    write_csv(
        turn_csv,
        [
            "event_id",
            "approx_second",
            "phase",
            "heading_before_deg",
            "heading_after_deg",
            "heading_delta_deg",
            "vector_span_seconds",
            "previous_span_distance_px",
            "current_span_distance_px",
            "interpretation",
        ],
        turn_events,
    )

    accepted = [row for row in track if row.manual_status == "accepted_detector_mark"]
    interpolated = [row for row in track if row.manual_status == "interpolated_detector_dropout"]
    excluded = [row for row in track if row.manual_status.startswith("excluded")]
    rates = [float(row["image_plane_rate_px_s"]) for row in track_rows if row["image_plane_rate_px_s"] != ""]
    path_length = sum(float(row["step_from_previous_px"]) for row in track_rows if row["step_from_previous_px"] != "")
    net_displacement = math.hypot(track[-1].manual_x - track[0].manual_x, track[-1].manual_y - track[0].manual_y)
    status_counts = Counter(row.manual_status for row in track)
    quality_counts = Counter(row.manual_quality for row in track)

    summary_rows = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_report_pair", "value": f"{RELEASE_ID} / {REPORT_ID}", "note": "DVIDS hard-paired release/report lane"},
        {"metric": "interval", "value": f"{args.start:.1f}s-{args.end:.1f}s", "note": "bounded pre-reticle PR34/D33 manual-review interval"},
        {"metric": "sample_count", "value": len(track), "note": "2 fps rows inherited from phase pass"},
        {"metric": "accepted_detector_marks", "value": len(accepted), "note": "source detections retained after false-top-edge rejection"},
        {"metric": "interpolated_detector_dropouts", "value": len(interpolated), "note": "short gaps where the source detector selected recurring top-edge artifact"},
        {"metric": "excluded_rows", "value": len(excluded), "note": "rows without enough neighbors for interpolation"},
        {"metric": "net_displacement_px", "value": round(net_displacement, 2), "note": "image-plane displacement from first to last manual-review point"},
        {"metric": "path_length_px", "value": round(path_length, 2), "note": "sum of image-plane step distances across manual-review track"},
        {"metric": "path_average_rate_px_s", "value": round(path_length / (args.end - args.start), 2), "note": "image-plane path rate; not real-world speed"},
        {"metric": "median_step_rate_px_s", "value": round(float(np.median(rates)), 2), "note": "median 0.5s image-plane step rate"},
        {"metric": "sharp_image_plane_turn_events", "value": len(turn_events), "note": "smoothed heading changes >=60 deg; not real-world turns without sensor geometry"},
    ]
    for key, value in sorted(status_counts.items()):
        summary_rows.append({"metric": f"manual_status: {key}", "value": value, "note": "track row status"})
    for key, value in sorted(quality_counts.items()):
        summary_rows.append({"metric": f"manual_quality: {key}", "value": value, "note": "track row quality"})

    summary_csv = Path("research/ufo-pr34-d33-manual-track-summary.csv")
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows: list[dict] = [
        {"artifact_type": "manual_track_csv", "path": str(track_csv).replace("\\", "/"), "note": "bounded PR34/D33 manual-review track"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "manual-review count and image-plane motion summary"},
        {"artifact_type": "turn_events_csv", "path": str(turn_csv).replace("\\", "/"), "note": "smoothed image-plane heading-change events"},
        {"artifact_type": "trajectory_plot", "path": str(trajectory_plot).replace("\\", "/"), "note": "manual-review track overview plot"},
    ]
    for path in annotated_sheets:
        asset_rows.append({"artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "manual-review annotated frame sheet"})
    for path in patch_sheets:
        asset_rows.append({"artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "manual-review zoom-patch sheet"})

    asset_csv = Path("research/ufo-video-pr34-d33-manual-track-assets.csv")
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"video={args.video}")
    print(f"interval={args.start:.1f}-{args.end:.1f}s")
    print(f"samples={len(track)} accepted={len(accepted)} interpolated={len(interpolated)} excluded={len(excluded)}")
    print(f"turn_events={len(turn_events)}")
    print(f"track_csv={track_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"turn_csv={turn_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

