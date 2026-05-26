from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source-files-not-included"


REPORT_ID = "DoW-UAP-D32"
OUT_ROOT = Path("research/ufo-derived/video-motion-pass/pr31-pr33-d32-glare-review")
DEFAULT_VIDEOS = {
    "DOW-UAP-PR31": SOURCE_ROOT / "DOD_111688970.mp4",
    "DOW-UAP-PR32": SOURCE_ROOT / "DOD_111688997.mp4",
    "DOW-UAP-PR33": SOURCE_ROOT / "DOD_111689005.mp4",
}


@dataclass(frozen=True)
class VideoSpec:
    release_id: str
    video_id: str
    video_name: str
    default_path: Path
    dvids_phase_note: str


SPECS = [
    VideoSpec(
        release_id="DOW-UAP-PR31",
        video_id="DOD_111688970",
        video_name="DOD_111688970.mp4",
        default_path=DEFAULT_VIDEOS["DOW-UAP-PR31"],
        dvids_phase_note="DVIDS: within first second, indistinct multi-colored area moves right-to-left across top edge",
    ),
    VideoSpec(
        release_id="DOW-UAP-PR32",
        video_id="DOD_111688997",
        video_name="DOD_111688997.mp4",
        default_path=DEFAULT_VIDEOS["DOW-UAP-PR32"],
        dvids_phase_note="DVIDS: 2s-4s, irregular white/red half-oval glare/halo region near top edge",
    ),
    VideoSpec(
        release_id="DOW-UAP-PR33",
        video_id="DOD_111689005",
        video_name="DOD_111689005.mp4",
        default_path=DEFAULT_VIDEOS["DOW-UAP-PR33"],
        dvids_phase_note="DVIDS: 1s-3s, two semi-transparent irregular orange overlays persist briefly over background",
    ),
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def fallback_path(spec: VideoSpec) -> Path:
    return OUT_ROOT / "source" / spec.video_name


def open_capture(spec: VideoSpec, override: Path | None = None) -> tuple[Path, cv2.VideoCapture]:
    candidates = [override or spec.default_path]
    fallback = fallback_path(spec)
    if fallback not in candidates:
        candidates.append(fallback)
    tried: list[str] = []
    for candidate in candidates:
        tried.append(str(candidate))
        cap = cv2.VideoCapture(str(candidate))
        if cap.isOpened():
            return candidate, cap
        cap.release()
    raise RuntimeError(f"Could not open any source video for {spec.release_id}: {tried}")


def phase_for(spec: VideoSpec, second: float) -> tuple[str, str]:
    if spec.release_id == "DOW-UAP-PR31":
        if second <= 1.15:
            return "top-edge crossing interval", spec.dvids_phase_note
        return "post-crossing context", "after DVIDS-described first-second top-edge event; retained as control context"
    if spec.release_id == "DOW-UAP-PR32":
        if 2.0 <= second <= 4.05:
            return "top-edge halo interval", spec.dvids_phase_note
        return "context outside halo interval", "outside DVIDS-described 2s-4s top-edge halo interval"
    if second <= 2.7:
        return "orange-overlay interval", spec.dvids_phase_note
    return "post-overlay context", "after DVIDS-described orange overlay interval; retained as control context"


def build_gray_frames(video: Path) -> list[np.ndarray]:
    cap = cv2.VideoCapture(str(video))
    frames: list[np.ndarray] = []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    cap.release()
    if not frames:
        raise RuntimeError(f"No frames decoded from {video}")
    return frames


def median_background(gray_frames: list[np.ndarray]) -> np.ndarray:
    stack = np.stack(gray_frames, axis=0)
    return np.median(stack, axis=0).astype(np.uint8)


def component_summary(mask: np.ndarray) -> dict:
    raw = mask.astype(np.uint8) * 255
    raw = cv2.morphologyEx(raw, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    raw = cv2.morphologyEx(raw, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(raw, connectivity=8)
    best: dict | None = None
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 6:
            continue
        cx, cy = centroids[label]
        item = {
            "component_count": labels_count - 1,
            "max_component_area": int(area),
            "max_component_x": int(x),
            "max_component_y": int(y),
            "max_component_w": int(w),
            "max_component_h": int(h),
            "max_component_center_x": float(cx),
            "max_component_center_y": float(cy),
        }
        if best is None or item["max_component_area"] > best["max_component_area"]:
            best = item
    if best is None:
        return {
            "component_count": 0,
            "max_component_area": 0,
            "max_component_x": "",
            "max_component_y": "",
            "max_component_w": "",
            "max_component_h": "",
            "max_component_center_x": "",
            "max_component_center_y": "",
        }
    return best


def metrics_for_frame(frame: np.ndarray, background: np.ndarray) -> dict:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    diff = cv2.absdiff(gray, background)

    top_band = np.zeros(gray.shape, dtype=bool)
    top_band[:220, :] = True
    warm = (sat > 60) & (val > 90) & ((hue <= 28) | (hue >= 165))
    orange = (sat > 70) & (val > 120) & (hue <= 22)
    red = (sat > 70) & (val > 110) & ((hue <= 10) | (hue >= 170))
    top_residual = (diff > 12) & top_band

    warm_top = warm & top_band
    warm_top_summary = component_summary(warm_top)
    orange_summary = component_summary(orange)
    top_residual_summary = component_summary(top_residual)
    return {
        "top_warm_area_px": int(warm_top.sum()),
        "top_warm_component_area_px": warm_top_summary["max_component_area"],
        "top_warm_component_center_x": warm_top_summary["max_component_center_x"],
        "top_warm_component_center_y": warm_top_summary["max_component_center_y"],
        "orange_area_px": int(orange.sum()),
        "orange_component_area_px": orange_summary["max_component_area"],
        "orange_component_center_x": orange_summary["max_component_center_x"],
        "orange_component_center_y": orange_summary["max_component_center_y"],
        "red_area_px": int(red.sum()),
        "top_residual_area_px": int(top_residual.sum()),
        "top_residual_component_area_px": top_residual_summary["max_component_area"],
        "top_residual_component_w_px": top_residual_summary["max_component_w"],
        "top_residual_component_h_px": top_residual_summary["max_component_h"],
        "top_residual_component_center_x": top_residual_summary["max_component_center_x"],
        "top_residual_component_center_y": top_residual_summary["max_component_center_y"],
        "top_band_mean_luma": float(gray[:220, :].mean()),
        "top_band_absdiff_p99": float(np.percentile(diff[:220, :], 99)),
    }


def classify_artifact(spec: VideoSpec, second: float, metrics: dict) -> tuple[str, str, str]:
    phase, _ = phase_for(spec, second)
    if spec.release_id == "DOW-UAP-PR31":
        top_warm = int(metrics["top_warm_area_px"])
        if phase == "top-edge crossing interval" and top_warm >= 90:
            return "medium", "top-edge warm-color artifact", "DVIDS first-second top-edge crossing proxy recovered; very small and glare/control-like"
        if phase == "top-edge crossing interval":
            return "low", "top-edge context", "DVIDS interval retained, but warm-color artifact is weak or not sampled at this instant"
        return "low", "post-event context", "post-crossing context; no object track inferred"

    if spec.release_id == "DOW-UAP-PR32":
        area = int(metrics["top_residual_component_area_px"])
        width = metrics["top_residual_component_w_px"]
        height = metrics["top_residual_component_h_px"]
        width_num = int(width) if width != "" else 0
        height_num = int(height) if height != "" else 0
        if phase == "top-edge halo interval" and area >= 5000 and width_num >= 180 and height_num >= 50:
            return "medium", "top-edge broad halo/glare residual", "broad top-edge residual aligns with DVIDS 2s-4s halo interval; panning/glare confounds dominate"
        if phase == "top-edge halo interval" and area >= 1200:
            return "low", "top-edge residual context", "weak broad top-edge residual within DVIDS interval; retained as control context"
        return "low", "context outside halo interval", "outside the strongest DVIDS halo interval or too weak for artifact support"

    orange_area = int(metrics["orange_area_px"])
    if phase == "orange-overlay interval" and orange_area >= 10_000:
        return "high", "large orange overlay artifact", "large saturated orange overlay area recovered; strongly supports DVIDS overlay/glare-control description"
    if phase == "orange-overlay interval" and orange_area >= 1_000:
        return "medium", "orange overlay artifact", "orange overlay recovered but smaller or transitional"
    return "low", "post-overlay context", "no significant orange overlay; retained as context only"


def sample_rows_for_spec(spec: VideoSpec, override: Path | None = None) -> tuple[Path, list[dict], float, int, float]:
    source_video, cap = open_capture(spec, override)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if fps else 0.0
    cap.release()

    gray_frames = build_gray_frames(source_video)
    background = median_background(gray_frames)
    cap = cv2.VideoCapture(str(source_video))
    sample_seconds = list(np.arange(0.0, max(0.0, duration - 1.0 / fps) + 0.001, 0.2))
    if not sample_seconds or sample_seconds[-1] < duration - 0.15:
        sample_seconds.append(duration - 1.0 / fps)

    rows: list[dict] = []
    for nominal_second in sample_seconds:
        second = min(float(nominal_second), max(0.0, duration - 1.0 / fps))
        frame_index = min(total_frames - 1, max(0, int(round(second * fps))))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        actual_second = frame_index / fps
        phase, phase_note = phase_for(spec, actual_second)
        metrics = metrics_for_frame(frame, background)
        quality, artifact_type, notes = classify_artifact(spec, actual_second, metrics)
        row = {
            "video": spec.video_name,
            "release_id": spec.release_id,
            "report_id": REPORT_ID,
            "frame_index": frame_index,
            "second": round(actual_second, 3),
            "phase": phase,
            "phase_note": phase_note,
            "artifact_candidate": quality in {"high", "medium"},
            "review_quality": quality,
            "artifact_type": artifact_type,
            "top_warm_area_px": metrics["top_warm_area_px"],
            "top_warm_component_area_px": metrics["top_warm_component_area_px"],
            "top_warm_component_center_x": round(float(metrics["top_warm_component_center_x"]), 3) if metrics["top_warm_component_center_x"] != "" else "",
            "top_warm_component_center_y": round(float(metrics["top_warm_component_center_y"]), 3) if metrics["top_warm_component_center_y"] != "" else "",
            "orange_area_px": metrics["orange_area_px"],
            "orange_component_area_px": metrics["orange_component_area_px"],
            "orange_component_center_x": round(float(metrics["orange_component_center_x"]), 3) if metrics["orange_component_center_x"] != "" else "",
            "orange_component_center_y": round(float(metrics["orange_component_center_y"]), 3) if metrics["orange_component_center_y"] != "" else "",
            "red_area_px": metrics["red_area_px"],
            "top_residual_area_px": metrics["top_residual_area_px"],
            "top_residual_component_area_px": metrics["top_residual_component_area_px"],
            "top_residual_component_w_px": metrics["top_residual_component_w_px"],
            "top_residual_component_h_px": metrics["top_residual_component_h_px"],
            "top_residual_component_center_x": round(float(metrics["top_residual_component_center_x"]), 3) if metrics["top_residual_component_center_x"] != "" else "",
            "top_residual_component_center_y": round(float(metrics["top_residual_component_center_y"]), 3) if metrics["top_residual_component_center_y"] != "" else "",
            "top_band_mean_luma": round(float(metrics["top_band_mean_luma"]), 6),
            "top_band_absdiff_p99": round(float(metrics["top_band_absdiff_p99"]), 6),
            "notes": notes,
        }
        rows.append(row)
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
        if second <= previous + 0.25:
            previous = second
            continue
        intervals.append((start, previous))
        start = second
        previous = second
    intervals.append((start, previous))
    return "; ".join(f"{start:.1f}s-{end:.1f}s" for start, end in intervals)


def numeric_summary(metric: str, values: list[float], note: str) -> dict:
    if not values:
        return {"metric": metric, "value": "", "note": note}
    if len(values) == 1:
        return {"metric": metric, "value": round(values[0], 3), "note": f"{note}; single supported value"}
    mean = statistics.fmean(values)
    stdev = statistics.pstdev(values)
    return {
        "metric": metric,
        "value": round(statistics.median(values), 3),
        "note": f"median; mean={mean:.3f}; stdev={stdev:.3f}; {note}",
    }


def build_summary_rows(all_rows: list[dict], metadata: dict[str, dict]) -> list[dict]:
    rows_by_release: dict[str, list[dict]] = defaultdict(list)
    for row in all_rows:
        rows_by_release[row["release_id"]].append(row)

    summary: list[dict] = [
        {
            "metric": "report_id",
            "release_id": "ALL",
            "video": "",
            "value": REPORT_ID,
            "note": "D32 report describes light/glare and halo effects; aircrew assessed benign/no mission impact",
        }
    ]
    for spec in SPECS:
        rows = rows_by_release.get(spec.release_id, [])
        if not rows:
            continue
        supported = [row for row in rows if row["review_quality"] in {"high", "medium"}]
        counts = Counter(row["review_quality"] for row in rows)
        meta = metadata[spec.release_id]
        summary.extend(
            [
                {"metric": "video", "release_id": spec.release_id, "video": spec.video_name, "value": spec.video_name, "note": f"source video used: {meta['source_video']}"},
                {"metric": "duration_seconds", "release_id": spec.release_id, "video": spec.video_name, "value": round(float(meta["duration"]), 3), "note": f"fps={meta['fps']}; frames={meta['total_frames']}"},
                {"metric": "sample_count", "release_id": spec.release_id, "video": spec.video_name, "value": len(rows), "note": "5 fps full-clip samples"},
                {"metric": "supported_high_or_medium_rows", "release_id": spec.release_id, "video": spec.video_name, "value": len(supported), "note": "artifact-support rows, not object-track rows"},
                {"metric": "supported_intervals", "release_id": spec.release_id, "video": spec.video_name, "value": supported_intervals(rows), "note": "5 fps supported artifact interval(s)"},
            ]
        )
        if spec.release_id == "DOW-UAP-PR31":
            summary.append(numeric_summary("top_warm_area_px", [float(row["top_warm_area_px"]) for row in supported], "top-edge warm-color artifact area") | {"release_id": spec.release_id, "video": spec.video_name})
        elif spec.release_id == "DOW-UAP-PR32":
            summary.append(numeric_summary("top_residual_component_area_px", [float(row["top_residual_component_area_px"]) for row in supported], "broad top-edge residual component area") | {"release_id": spec.release_id, "video": spec.video_name})
            summary.append(numeric_summary("top_residual_component_w_px", [float(row["top_residual_component_w_px"]) for row in supported if row["top_residual_component_w_px"] != ""], "broad top-edge residual component width") | {"release_id": spec.release_id, "video": spec.video_name})
        else:
            summary.append(numeric_summary("orange_area_px", [float(row["orange_area_px"]) for row in supported], "saturated orange overlay area") | {"release_id": spec.release_id, "video": spec.video_name})
            summary.append(numeric_summary("orange_component_area_px", [float(row["orange_component_area_px"]) for row in supported], "largest orange overlay component area") | {"release_id": spec.release_id, "video": spec.video_name})
        for quality in sorted(counts):
            summary.append({"metric": f"quality_count: {quality}", "release_id": spec.release_id, "video": spec.video_name, "value": counts[quality], "note": "review quality"})
    return summary


def read_frame_at(video: Path, frame_index: int) -> np.ndarray | None:
    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    cap.release()
    return frame if ok else None


def draw_row(frame: np.ndarray, row: dict) -> np.ndarray:
    annotated = frame.copy()
    color = (0, 255, 0) if row["review_quality"] == "high" else (0, 200, 255) if row["review_quality"] == "medium" else (0, 128, 255)
    cv2.rectangle(annotated, (0, 0), (1919, 220), (0, 255, 255), 2)
    if row["release_id"] == "DOW-UAP-PR33" and row["orange_component_area_px"] not in {"", "0", 0}:
        cx = int(float(row["orange_component_center_x"]))
        cy = int(float(row["orange_component_center_y"]))
        radius = max(24, int(math.sqrt(float(row["orange_component_area_px"]) / math.pi)) + 12)
        cv2.circle(annotated, (cx, cy), radius, color, 3)
        cv2.drawMarker(annotated, (cx, cy), color, markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
    elif row["release_id"] == "DOW-UAP-PR31" and row["top_warm_component_area_px"] not in {"", "0", 0}:
        cx = int(float(row["top_warm_component_center_x"]))
        cy = int(float(row["top_warm_component_center_y"]))
        cv2.drawMarker(annotated, (cx, cy), color, markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
        cv2.circle(annotated, (cx, cy), 34, color, 3)
    elif row["top_residual_component_center_x"] != "":
        cx = int(float(row["top_residual_component_center_x"]))
        cy = int(float(row["top_residual_component_center_y"]))
        w = max(20, int(float(row["top_residual_component_w_px"])))
        h = max(20, int(float(row["top_residual_component_h_px"])))
        cv2.rectangle(annotated, (max(0, cx - w // 2), max(0, cy - h // 2)), (min(1919, cx + w // 2), min(1079, cy + h // 2)), color, 3)
    label = f'{row["release_id"]} {row["second"]:.1f}s {row["review_quality"]} {row["artifact_type"]}'
    cv2.putText(annotated, label, (40, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 4, cv2.LINE_AA)
    return annotated


def make_visual_assets(rows_by_release: dict[str, list[dict]], metadata: dict[str, dict]) -> list[dict]:
    assets: list[dict] = []
    for spec in SPECS:
        rows = rows_by_release[spec.release_id]
        source_video = Path(metadata[spec.release_id]["source_video"])
        release_dir = OUT_ROOT / spec.video_id
        ensure_dir(release_dir)
        assets.append({"release_id": spec.release_id, "artifact_type": "source_video", "path": str(source_video).replace("\\", "/"), "note": f"source video used for {spec.release_id}/D32 review"})
        full_images: list[np.ndarray] = []
        patch_images: list[np.ndarray] = []
        for row in rows:
            frame = read_frame_at(source_video, int(row["frame_index"]))
            if frame is None:
                continue
            annotated = draw_row(frame, row)
            full_images.append(cv2.resize(annotated, (384, 216), interpolation=cv2.INTER_AREA))
            if spec.release_id == "DOW-UAP-PR33":
                crop = annotated[320:850, 620:1680].copy()
                crop = cv2.resize(crop, (530, 265), interpolation=cv2.INTER_AREA)
            else:
                crop = annotated[0:260, 0:1920].copy()
                crop = cv2.resize(crop, (640, 140), interpolation=cv2.INTER_AREA)
            cv2.putText(crop, f'{row["second"]:.1f}s {row["review_quality"]}', (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
            patch_images.append(crop)

        if full_images:
            full_rows = []
            for index in range(0, len(full_images), 4):
                chunk = full_images[index : index + 4]
                while len(chunk) < 4:
                    chunk.append(np.zeros_like(full_images[0]))
                full_rows.append(np.hstack(chunk))
            full_path = release_dir / f"{spec.video_id}-d32-glare-annotated.jpg"
            cv2.imwrite(str(full_path), np.vstack(full_rows), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            assets.append({"release_id": spec.release_id, "artifact_type": "annotated_sheet", "path": str(full_path).replace("\\", "/"), "note": "5 fps full-frame artifact annotations"})

        if patch_images:
            patch_rows = []
            for index in range(0, len(patch_images), 2):
                chunk = patch_images[index : index + 2]
                while len(chunk) < 2:
                    chunk.append(np.zeros_like(patch_images[0]))
                patch_rows.append(np.hstack(chunk))
            patch_path = release_dir / f"{spec.video_id}-d32-glare-patches.jpg"
            cv2.imwrite(str(patch_path), np.vstack(patch_rows), [int(cv2.IMWRITE_JPEG_QUALITY), 92])
            assets.append({"release_id": spec.release_id, "artifact_type": "patch_sheet", "path": str(patch_path).replace("\\", "/"), "note": "top-edge or orange-overlay artifact patches"})
    return assets


def run(overrides: dict[str, Path]) -> None:
    all_rows: list[dict] = []
    metadata: dict[str, dict] = {}
    rows_by_release: dict[str, list[dict]] = {}
    for spec in SPECS:
        source_video, rows, fps, total_frames, duration = sample_rows_for_spec(spec, overrides.get(spec.release_id))
        all_rows.extend(rows)
        rows_by_release[spec.release_id] = rows
        metadata[spec.release_id] = {
            "source_video": str(source_video),
            "fps": fps,
            "total_frames": total_frames,
            "duration": duration,
        }

    review_path = Path("research/ufo-video-pr31-pr33-d32-glare-review.csv")
    summary_path = Path("research/ufo-video-pr31-pr33-d32-glare-review-summary.csv")
    assets_path = Path("research/ufo-video-pr31-pr33-d32-glare-review-assets.csv")

    write_csv(review_path, all_rows)
    write_csv(summary_path, build_summary_rows(all_rows, metadata))
    write_csv(assets_path, make_visual_assets(rows_by_release, metadata))

    print(f"wrote {review_path}")
    print(f"wrote {summary_path}")
    print(f"wrote {assets_path}")
    for spec in SPECS:
        counts = Counter(row["review_quality"] for row in rows_by_release[spec.release_id])
        print(f"{spec.release_id} {spec.video_name}: {dict(counts)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PR31-PR33/D32 glare, halo, and overlay control review")
    parser.add_argument("--pr31-video", type=Path, help="Path to DOD_111688970.mp4")
    parser.add_argument("--pr32-video", type=Path, help="Path to DOD_111688997.mp4")
    parser.add_argument("--pr33-video", type=Path, help="Path to DOD_111689005.mp4")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    override_map = {
        "DOW-UAP-PR31": args.pr31_video,
        "DOW-UAP-PR32": args.pr32_video,
        "DOW-UAP-PR33": args.pr33_video,
    }
    run({key: value for key, value in override_map.items() if value is not None})

