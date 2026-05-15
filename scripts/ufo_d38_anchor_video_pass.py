from __future__ import annotations

import argparse
import csv
import math
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689030"
DEFAULT_SOURCE = Path(r"source-files-not-included/DOD_111689030.mp4")
DEFAULT_FFPROBE = Path(shutil.which("ffprobe") or "ffprobe")


@dataclass
class SampleResult:
    frame_index: int
    sample_second: float
    source_frame_index: int
    crop_path: str
    candidate_count: int
    best_x: int | None
    best_y: int | None
    best_w: int | None
    best_h: int | None
    best_area: int | None
    best_mean: float | None
    best_max: int | None
    dx_from_center: int | None
    dy_from_center: int | None
    confidence: str
    notes: str


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def center_crop(frame: np.ndarray, width: int = 960, height: int = 540) -> tuple[np.ndarray, int, int]:
    h, w = frame.shape[:2]
    x0 = max(0, (w - width) // 2)
    y0 = max(0, (h - height) // 2)
    return frame[y0 : y0 + height, x0 : x0 + width], x0, y0


def classify_confidence(area: int | None, mean: float | None, max_value: int | None) -> str:
    if area is None or mean is None or max_value is None:
        return "none"
    if area >= 12 and max_value >= 235 and mean >= 205:
        return "strong"
    if area >= 8 and max_value >= 220 and mean >= 190:
        return "medium"
    return "weak"


def detect_compact_bright_candidate(crop: np.ndarray) -> tuple[list[dict], dict | None]:
    """Detect compact white-hot candidates while suppressing colored overlays.

    This is an audit detector, not a final tracker. It looks for compact, low-saturation,
    bright connected components and intentionally ignores larger bright structures such as
    the opening vessel/platform.
    """

    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

    # Low-saturation keeps sensor grayscale content and suppresses green/yellow/red symbology.
    low_sat = hsv[:, :, 1] < 42
    not_black = gray > 40
    valid = low_sat & not_black

    if int(valid.sum()) < 1000:
        return [], None

    valid_values = gray[valid]
    dynamic_threshold = int(np.percentile(valid_values, 99.75))
    threshold = max(175, min(dynamic_threshold, 245))
    bright = ((gray >= threshold) & valid).astype(np.uint8) * 255

    # Clean single-pixel noise without merging unrelated highlights too aggressively.
    bright = cv2.medianBlur(bright, 3)
    kernel = np.ones((2, 2), np.uint8)
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, kernel)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(bright, connectivity=8)
    candidates: list[dict] = []

    crop_h, crop_w = gray.shape
    center_x = crop_w // 2
    center_y = crop_h // 2

    for label in range(1, num_labels):
        x, y, w, h, area = stats[label]
        if area < 5 or area > 650:
            continue
        if w > 75 or h > 75:
            continue
        if w == 0 or h == 0:
            continue
        aspect = w / h
        if aspect < 0.20 or aspect > 5.0:
            continue

        component_mask = labels == label
        component_values = gray[component_mask]
        mean_value = float(component_values.mean())
        max_value = int(component_values.max())
        cx, cy = centroids[label]

        # Favor small, bright, compact components away from dense overlay zones.
        distance_penalty = 0.0008 * math.hypot(cx - center_x, cy - center_y)
        score = (max_value / 255.0) + (mean_value / 255.0) + min(area, 120) / 120.0 - distance_penalty
        candidates.append(
            {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
                "area": int(area),
                "mean": mean_value,
                "max": max_value,
                "cx": float(cx),
                "cy": float(cy),
                "score": float(score),
            }
        )

    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates, candidates[0] if candidates else None


def draw_label(crop: np.ndarray, label: str, candidate: dict | None = None) -> np.ndarray:
    annotated = crop.copy()
    cv2.rectangle(annotated, (0, 0), (210, 26), (0, 0, 0), -1)
    cv2.putText(annotated, label, (8, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    if candidate:
        x = candidate["x"]
        y = candidate["y"]
        w = candidate["w"]
        h = candidate["h"]
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
    return annotated


def write_contact_sheets(
    image_paths: list[Path],
    output_dir: Path,
    prefix: str,
    cols: int = 5,
    thumb_width: int = 384,
) -> list[Path]:
    ensure_dir(output_dir)
    written: list[Path] = []
    if not image_paths:
        return written

    for chunk_index, start in enumerate(range(0, len(image_paths), cols * 5)):
        chunk = image_paths[start : start + cols * 5]
        thumbs = []
        for path in chunk:
            img = cv2.imread(str(path))
            if img is None:
                continue
            scale = thumb_width / img.shape[1]
            thumb = cv2.resize(img, (thumb_width, int(img.shape[0] * scale)), interpolation=cv2.INTER_AREA)
            thumbs.append(thumb)
        if not thumbs:
            continue

        thumb_h = max(t.shape[0] for t in thumbs)
        rows = math.ceil(len(thumbs) / cols)
        sheet = np.zeros((rows * thumb_h, cols * thumb_width, 3), dtype=np.uint8)
        for i, thumb in enumerate(thumbs):
            row = i // cols
            col = i % cols
            y = row * thumb_h
            x = col * thumb_width
            sheet[y : y + thumb.shape[0], x : x + thumb.shape[1]] = thumb

        out = output_dir / f"{prefix}-{chunk_index:02d}.jpg"
        cv2.imwrite(str(out), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        written.append(out)
    return written


def sample_video(video_path: Path, out_dir: Path, sample_rate: float, max_width: int = 960) -> tuple[list[SampleResult], list[Path]]:
    ensure_dir(out_dir)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps else 0
    frame_step_seconds = 1.0 / sample_rate
    sample_count = int(math.floor(duration * sample_rate)) + 1
    targets: dict[int, list[tuple[int, float]]] = {}
    for sample_index in range(sample_count):
        sample_second = sample_index * frame_step_seconds
        source_frame_index = min(int(round(sample_second * fps)), max(0, total_frames - 1))
        targets.setdefault(source_frame_index, []).append((sample_index, sample_second))

    results: list[SampleResult] = []
    paths: list[Path] = []

    source_frame_index = 0
    while source_frame_index < total_frames:
        ok, frame = cap.read()
        if not ok:
            break

        if source_frame_index in targets:
            crop, x0, y0 = center_crop(frame, width=max_width, height=int(max_width * 9 / 16))
            candidates, best = detect_compact_bright_candidate(crop)
            for frame_index, sample_second in targets[source_frame_index]:
                label = f"t={sample_second:06.1f}s f={source_frame_index:05d}"
                annotated = draw_label(crop, label, best)

                out_path = out_dir / f"frame_{frame_index:04d}.jpg"
                cv2.imwrite(str(out_path), annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
                paths.append(out_path)

                if best:
                    full_x = x0 + int(round(best["cx"]))
                    full_y = y0 + int(round(best["cy"]))
                    dx = int(round(best["cx"] - crop.shape[1] / 2))
                    dy = int(round(best["cy"] - crop.shape[0] / 2))
                    confidence = classify_confidence(best["area"], best["mean"], best["max"])
                    notes = "compact low-saturation bright component; audit detector"
                    results.append(
                        SampleResult(
                            frame_index=frame_index,
                            sample_second=sample_second,
                            source_frame_index=source_frame_index,
                            crop_path=str(out_path).replace("\\", "/"),
                            candidate_count=len(candidates),
                            best_x=full_x,
                            best_y=full_y,
                            best_w=best["w"],
                            best_h=best["h"],
                            best_area=best["area"],
                            best_mean=round(float(best["mean"]), 2),
                            best_max=best["max"],
                            dx_from_center=dx,
                            dy_from_center=dy,
                            confidence=confidence,
                            notes=notes,
                        )
                    )
                else:
                    results.append(
                        SampleResult(
                            frame_index=frame_index,
                            sample_second=sample_second,
                            source_frame_index=source_frame_index,
                            crop_path=str(out_path).replace("\\", "/"),
                            candidate_count=0,
                            best_x=None,
                            best_y=None,
                            best_w=None,
                            best_h=None,
                            best_area=None,
                            best_mean=None,
                            best_max=None,
                            dx_from_center=None,
                            dy_from_center=None,
                            confidence="none",
                            notes="no compact low-saturation bright component detected",
                        )
                    )
        source_frame_index += 1

    cap.release()
    results.sort(key=lambda r: r.frame_index)
    paths.sort()
    return results, paths


def write_sample_csv(path: Path, rows: list[SampleResult]) -> None:
    ensure_dir(path.parent)
    fieldnames = [
        "frame_index",
        "sample_second",
        "source_frame_index",
        "crop_path",
        "candidate_count",
        "best_x",
        "best_y",
        "best_w",
        "best_h",
        "best_area",
        "best_mean",
        "best_max",
        "dx_from_center",
        "dy_from_center",
        "confidence",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def write_range_csv(path: Path, rows: list[SampleResult]) -> list[dict]:
    grouped: list[dict] = []
    active: dict | None = None

    for row in rows:
        is_active = row.confidence in {"medium", "strong"}
        if is_active and active is None:
            active = {
                "start_second": row.sample_second,
                "end_second": row.sample_second,
                "sample_count": 1,
                "strong_count": 1 if row.confidence == "strong" else 0,
                "medium_count": 1 if row.confidence == "medium" else 0,
            }
        elif is_active and active is not None:
            active["end_second"] = row.sample_second
            active["sample_count"] += 1
            if row.confidence == "strong":
                active["strong_count"] += 1
            else:
                active["medium_count"] += 1
        elif not is_active and active is not None:
            grouped.append(active)
            active = None

    if active is not None:
        grouped.append(active)

    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        fieldnames = ["start_second", "end_second", "sample_count", "strong_count", "medium_count"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(grouped)
    return grouped


def write_metadata(path: Path, video_path: Path, ffprobe: Path | None, fps: float, total_frames: int) -> None:
    lines = [
        f"source={video_path}",
        f"opencv_fps={fps}",
        f"opencv_frame_count={total_frames}",
        f"opencv_duration_seconds={total_frames / fps if fps else ''}",
    ]
    ffprobe_cmd = None
    if ffprobe:
        ffprobe_cmd = shutil.which(str(ffprobe)) or (str(ffprobe) if ffprobe.exists() else None)
    if ffprobe_cmd:
        result = subprocess.run(
            [
                ffprobe_cmd,
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=width,height,avg_frame_rate,codec_name",
                "-of",
                "default=noprint_wrappers=1",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        lines.append("ffprobe_output:")
        lines.extend(result.stdout.strip().splitlines())
        if result.stderr.strip():
            lines.append("ffprobe_stderr:")
            lines.extend(result.stderr.strip().splitlines())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate D38 anchor video analysis artifacts.")
    parser.add_argument("--video", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--ffprobe", type=Path, default=DEFAULT_FFPROBE)
    args = parser.parse_args()

    root = Path.cwd()
    research = root / "docs" / "research"
    derived = research / "ufo-derived" / "video-motion-pass"

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    metadata_path = research / "ufo-video-ffmpeg-metadata-dod111689030.txt"
    write_metadata(metadata_path, args.video, args.ffprobe, fps, total_frames)

    one_fps_dir = derived / "one-fps-center-crops" / VIDEO_ID
    five_fps_dir = derived / "high-rate" / VIDEO_ID / "fps5-center-crops"
    sheets_dir = derived / "segment-sheets" / VIDEO_ID

    one_rows, one_paths = sample_video(args.video, one_fps_dir, sample_rate=1.0)
    five_rows, five_paths = sample_video(args.video, five_fps_dir, sample_rate=5.0)

    write_sample_csv(research / "ufo-video-object-position-dod111689030.csv", one_rows)
    write_sample_csv(research / "ufo-video-object-position-dod111689030-fps5.csv", five_rows)
    one_ranges = write_range_csv(research / "ufo-video-object-position-dod111689030-ranges.csv", one_rows)
    five_ranges = write_range_csv(research / "ufo-video-object-position-dod111689030-fps5-ranges.csv", five_rows)

    one_sheets = write_contact_sheets(one_paths, sheets_dir, f"{VIDEO_ID}-onefps")

    # Write high-rate contact sheets only for the first few medium/strong windows to keep review bounded.
    high_rate_sheet_paths: list[Path] = []
    for i, window in enumerate(five_ranges[:8]):
        start = max(0, int(math.floor(window["start_second"] * 5)) - 10)
        end = min(len(five_paths), int(math.ceil(window["end_second"] * 5)) + 11)
        high_rate_sheet_paths.extend(
            write_contact_sheets(five_paths[start:end], sheets_dir, f"{VIDEO_ID}-fps5-window-{i:02d}", cols=5)
        )

    index_path = research / "ufo-video-d38-anchor-extraction-index.csv"
    with index_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["artifact_type", "path", "note"])
        writer.writeheader()
        for path in [metadata_path]:
            writer.writerow({"artifact_type": "metadata", "path": str(path).replace("\\", "/"), "note": "source video metadata"})
        for path in one_sheets:
            writer.writerow({"artifact_type": "one_fps_sheet", "path": str(path).replace("\\", "/"), "note": "1 fps center-crop contact sheet"})
        for path in high_rate_sheet_paths:
            writer.writerow({"artifact_type": "fps5_window_sheet", "path": str(path).replace("\\", "/"), "note": "5 fps sheet around detector-active window"})
        writer.writerow(
            {
                "artifact_type": "one_fps_csv",
                "path": "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030.csv",
                "note": "1 fps compact bright-candidate audit table",
            }
        )
        writer.writerow(
            {
                "artifact_type": "fps5_csv",
                "path": "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030-fps5.csv",
                "note": "5 fps compact bright-candidate audit table",
            }
        )

    print(f"video={args.video}")
    print(f"fps={fps}")
    print(f"frames={total_frames}")
    print(f"one_fps_samples={len(one_rows)}")
    print(f"five_fps_samples={len(five_rows)}")
    print(f"one_fps_active_ranges={len(one_ranges)}")
    print(f"five_fps_active_ranges={len(five_ranges)}")
    print(f"index={index_path}")


if __name__ == "__main__":
    main()
