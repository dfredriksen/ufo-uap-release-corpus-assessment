from __future__ import annotations

import csv
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


DEFAULT_FFPROBE = Path(
    r"C:\Users\Dan\AppData\Local\Microsoft\WinGet\Packages"
    r"\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe"
    r"\ffmpeg-8.1.1-full_build\bin\ffprobe.exe"
)


@dataclass(frozen=True)
class Phase:
    name: str
    start: float
    end: float
    dvids_anchor: str


@dataclass(frozen=True)
class Case:
    video_id: str
    report_id: str
    release_id: str
    video_path: Path
    sample_rate: float
    phases: tuple[Phase, ...]


CASES = (
    Case(
        video_id="DOD_111689011",
        report_id="DoW-UAP-D33",
        release_id="DOW-UAP-PR34",
        video_path=Path(r"source-files-not-included/DOD_111689011.mp4"),
        sample_rate=2.0,
        phases=(
            Phase("pre-entry/context", 0.0, 3.9, "Before DVIDS 00:04 entry note"),
            Phase("entry from bottom-left quarter", 4.0, 6.9, "DVIDS: 00:04 area of contrast enters from bottom-left quarter"),
            Phase("horizontal back-and-forth tracking", 7.0, 19.9, "DVIDS: 00:07-00:19 area of contrast moves back and forth as sensor pans"),
            Phase("generally centered in FOV", 20.0, 59.9, "DVIDS: 00:20-01:00 area remains generally centered"),
            Phase("blue-reticle designation", 60.0, 121.9, "DVIDS: 01:00-02:01 blue reticle designates and synchronizes with contrast area"),
            Phase("contrast-filter interval", 122.0, 141.9, "DVIDS: 02:02-02:21 contrast filter differentiates area from background"),
            Phase("lock-loss transition", 142.0, 146.9, "DVIDS: 02:22 area becomes indistinguishable and reticle drops lock"),
            Phase("post-loss zoom/contrast cycling", 147.0, 177.0, "DVIDS: 02:27-02:57 rapid zoom and contrast cycling after lock loss"),
        ),
    ),
    Case(
        video_id="DOD_111689022",
        report_id="DoW-UAP-D35",
        release_id="DOW-UAP-PR35",
        video_path=Path(r"source-files-not-included/DOD_111689022-1920x1080-9000k.mp4"),
        sample_rate=2.0,
        phases=(
            Phase("pre-zoom/context", 0.0, 1.9, "Before DVIDS 00:02 zoom note"),
            Phase("zoom-in near center", 2.0, 2.9, "DVIDS: 00:02 sensor narrows FOV to zoom on central area of contrast"),
            Phase("ocean-background track", 3.0, 19.9, "DVIDS: 00:03-00:19 sensor tracks area of contrast against ocean background"),
            Phase("land-transition/loss", 20.0, 24.0, "DVIDS: 00:20 area becomes indistinguishable as background transitions to land"),
        ),
    ),
)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def phase_for(case: Case, second: float) -> Phase:
    for phase in case.phases:
        if phase.start <= second <= phase.end:
            return phase
    return case.phases[-1]


def colored_overlay_mask(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    cyan_blue = (hue >= 78) & (hue <= 112)
    green = (hue >= 45) & (hue < 78)
    mask = ((sat > 70) & (val > 70) & (cyan_blue | green)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)
    return mask


def nearest_overlay_distance(frame: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    mask = colored_overlay_mask(frame)
    pts = cv2.findNonZero(mask)
    if pts is None:
        return "no colored reticle/overlay detected", None
    arr = pts.reshape(-1, 2)
    if len(arr) == 0:
        return "no colored reticle/overlay detected", None
    distances = np.sqrt((arr[:, 0] - x) ** 2 + (arr[:, 1] - y) ** 2)
    nearest = float(distances.min())
    if nearest <= 5:
        return "intersects colored reticle/overlay", nearest
    if nearest <= 35:
        return "near colored reticle/overlay", nearest
    return "separate from colored reticle/overlay", nearest


def detect_compact_contrast(frame: np.ndarray, case: Case) -> dict:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    center_x = w / 2
    center_y = h / 2

    low_sat = hsv[:, :, 1] < 55
    not_overlay = colored_overlay_mask(frame) == 0
    not_redaction = gray > 28
    valid = low_sat & not_overlay & not_redaction
    if int(valid.sum()) < 1000:
        return {}

    bright_threshold = max(150, min(int(np.percentile(gray[valid], 99.72)), 240))
    bright = ((gray >= bright_threshold) & valid).astype(np.uint8) * 255
    bright = cv2.medianBlur(bright, 3)
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(bright, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, bw, bh, area = stats[label]
        if area < 3 or area > 450:
            continue
        if bw > 45 or bh > 45:
            continue
        aspect = bw / bh if bh else 99.0
        if aspect < 0.18 or aspect > 5.5:
            continue
        cx, cy = centroids[label]
        values = gray[labels == label]
        max_luma = int(values.max())
        mean_luma = float(values.mean())
        distance = math.hypot(float(cx) - center_x, float(cy) - center_y)

        # D35 has clouds/land; favor central small points more strongly than in D33.
        distance_penalty = 0.00065 if case.video_id == "DOD_111689011" else 0.00115
        score = (2.0 * max_luma / 255.0) + (mean_luma / 255.0) + min(area, 120) / 120.0 - distance_penalty * distance
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
                "candidate_count": 0,
                "score": score,
            }
        )

    if not candidates:
        return {}
    candidates.sort(key=lambda candidate: candidate["score"], reverse=True)
    best = candidates[0]
    best["candidate_count"] = len(candidates)
    return best


def classify_detection(candidate: dict, relation: str, phase: Phase, case: Case) -> str:
    if not candidate:
        return "none"
    max_luma = int(candidate["max_luma"])
    area = int(candidate["area"])
    candidate_count = int(candidate["candidate_count"])
    if case.video_id == "DOD_111689022" and "land-transition" in phase.name:
        return "low"
    if max_luma >= 210 and area >= 8 and candidate_count <= 20:
        return "high"
    if max_luma >= 180 and area >= 5:
        return "medium"
    return "low"


def add_label(img: np.ndarray, text: str, width: int = 680) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 32), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, candidate: dict, label: str) -> np.ndarray:
    out = frame.copy()
    if candidate:
        x = int(round(candidate["x"]))
        y = int(round(candidate["y"]))
        cv2.drawMarker(out, (x, y), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=28, thickness=2)
        cv2.circle(out, (x, y), 24, (0, 0, 255), 2)
        cv2.line(out, (960, 540), (x, y), (255, 255, 0), 2)
    return add_label(out, label)


def crop_patch(frame: np.ndarray, candidate: dict, size: int = 140) -> np.ndarray:
    h, w = frame.shape[:2]
    if not candidate:
        cx, cy = w // 2, h // 2
    else:
        cx, cy = int(round(candidate["x"])), int(round(candidate["y"]))
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


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
        thumb_h = max(t.shape[0] for t in thumbs)
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


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(case: Case, out_path: Path) -> None:
    lines = [f"video={case.video_path}", f"release_id={case.release_id}", f"report_id={case.report_id}"]
    if DEFAULT_FFPROBE.exists():
        result = subprocess.run(
            [
                str(DEFAULT_FFPROBE),
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=width,height,avg_frame_rate,codec_name",
                "-of",
                "default=noprint_wrappers=1",
                str(case.video_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        lines.append("ffprobe_output:")
        lines.extend(result.stdout.strip().splitlines())
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def process_case(case: Case, research: Path, derived_root: Path) -> tuple[list[dict], list[dict]]:
    case_root = derived_root / case.video_id
    frame_dir = case_root / "annotated-frames"
    patch_dir = case_root / "object-zoom-patches"
    sheet_dir = case_root / "sheets"
    for path in [frame_dir, patch_dir, sheet_dir]:
        ensure_dir(path)

    cap = cv2.VideoCapture(str(case.video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {case.video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps if fps else 0.0

    sample_count = int(math.floor(duration * case.sample_rate)) + 1
    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []
    for sample_index in range(sample_count):
        second = round(sample_index / case.sample_rate, 2)
        source_frame_index = min(int(round(second * fps)), max(0, frame_count - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame_index)
        ok, frame = cap.read()
        if not ok:
            continue

        phase = phase_for(case, second)
        candidate = detect_compact_contrast(frame, case)
        if candidate:
            relation, nearest_overlay = nearest_overlay_distance(frame, candidate["x"], candidate["y"])
        else:
            relation, nearest_overlay = "no candidate", None
        confidence = classify_detection(candidate, relation, phase, case)

        label = f"{case.video_id} t={second:05.1f}s conf={confidence}"
        annotated = annotate_frame(frame, candidate, label)
        patch = annotate_patch(crop_patch(frame, candidate), label)

        frame_path = frame_dir / f"frame_{sample_index:04d}_annotated.jpg"
        patch_path = patch_dir / f"frame_{sample_index:04d}_patch.jpg"
        cv2.imwrite(str(frame_path), annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        cv2.imwrite(str(patch_path), patch, [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        annotated_paths.append(frame_path)
        patch_paths.append(patch_path)

        rows.append(
            {
                "video": f"{case.video_id}.mp4",
                "release_id": case.release_id,
                "report_id": case.report_id,
                "sample_index": sample_index,
                "approx_second": f"{second:.2f}",
                "source_frame_index": source_frame_index,
                "phase": phase.name,
                "dvids_anchor": phase.dvids_anchor,
                "candidate_x": "" if not candidate else round(float(candidate["x"]), 1),
                "candidate_y": "" if not candidate else round(float(candidate["y"]), 1),
                "dx_from_frame_center": "" if not candidate else round(float(candidate["x"]) - 960, 1),
                "dy_from_frame_center": "" if not candidate else round(float(candidate["y"]) - 540, 1),
                "bbox_w": "" if not candidate else candidate["bbox_w"],
                "bbox_h": "" if not candidate else candidate["bbox_h"],
                "area": "" if not candidate else candidate["area"],
                "max_luma": "" if not candidate else candidate["max_luma"],
                "mean_luma": "" if not candidate else round(float(candidate["mean_luma"]), 2),
                "candidate_count": "" if not candidate else candidate["candidate_count"],
                "nearest_colored_overlay_px": "" if nearest_overlay is None else round(nearest_overlay, 2),
                "overlay_relation": relation,
                "review_confidence": confidence,
                "annotated_frame_path": str(frame_path).replace("\\", "/"),
                "zoom_patch_path": str(patch_path).replace("\\", "/"),
            }
        )

    cap.release()

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{case.video_id}-phase-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{case.video_id}-phase-patches", cols=8, thumb_width=180)

    track_csv = research / f"ufo-video-{case.video_id.lower()}-phase-track.csv"
    fieldnames = [
        "video",
        "release_id",
        "report_id",
        "sample_index",
        "approx_second",
        "source_frame_index",
        "phase",
        "dvids_anchor",
        "candidate_x",
        "candidate_y",
        "dx_from_frame_center",
        "dy_from_frame_center",
        "bbox_w",
        "bbox_h",
        "area",
        "max_luma",
        "mean_luma",
        "candidate_count",
        "nearest_colored_overlay_px",
        "overlay_relation",
        "review_confidence",
        "annotated_frame_path",
        "zoom_patch_path",
    ]
    write_csv(track_csv, fieldnames, rows)

    summary_rows: list[dict] = []
    for phase in case.phases:
        phase_rows = [row for row in rows if row["phase"] == phase.name]
        if not phase_rows:
            continue
        high = sum(1 for row in phase_rows if row["review_confidence"] == "high")
        medium = sum(1 for row in phase_rows if row["review_confidence"] == "medium")
        low = sum(1 for row in phase_rows if row["review_confidence"] == "low")
        none = sum(1 for row in phase_rows if row["review_confidence"] == "none")
        near_or_intersects = sum(
            1
            for row in phase_rows
            if row["overlay_relation"] in {"near colored reticle/overlay", "intersects colored reticle/overlay"}
        )
        summary_rows.append(
            {
                "video": f"{case.video_id}.mp4",
                "release_id": case.release_id,
                "report_id": case.report_id,
                "phase": phase.name,
                "start_second": phase.start,
                "end_second": phase.end,
                "sample_count": len(phase_rows),
                "high_count": high,
                "medium_count": medium,
                "low_count": low,
                "none_count": none,
                "near_or_intersects_overlay_count": near_or_intersects,
                "dvids_anchor": phase.dvids_anchor,
            }
        )

    summary_csv = research / f"ufo-video-{case.video_id.lower()}-phase-summary.csv"
    write_csv(
        summary_csv,
        [
            "video",
            "release_id",
            "report_id",
            "phase",
            "start_second",
            "end_second",
            "sample_count",
            "high_count",
            "medium_count",
            "low_count",
            "none_count",
            "near_or_intersects_overlay_count",
            "dvids_anchor",
        ],
        summary_rows,
    )

    metadata_path = research / f"ufo-video-{case.video_id.lower()}-metadata.txt"
    write_metadata(case, metadata_path)

    index_rows = [
        {"video": case.video_id, "artifact_type": "metadata", "path": str(metadata_path).replace("\\", "/"), "note": "source metadata"},
        {"video": case.video_id, "artifact_type": "phase_track_csv", "path": str(track_csv).replace("\\", "/"), "note": "phase-aligned sample table"},
        {"video": case.video_id, "artifact_type": "phase_summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "phase summary"},
    ]
    for path in annotated_sheets:
        index_rows.append({"video": case.video_id, "artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "annotated phase-review sheet"})
    for path in patch_sheets:
        index_rows.append({"video": case.video_id, "artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "candidate zoom-patch sheet"})

    return summary_rows, index_rows


def main() -> None:
    root = Path.cwd()
    research = root / "docs" / "research"
    derived_root = research / "ufo-derived" / "video-hard-pair-phase-review"
    all_summary_rows: list[dict] = []
    all_index_rows: list[dict] = []
    for case in CASES:
        summary, index = process_case(case, research, derived_root)
        all_summary_rows.extend(summary)
        all_index_rows.extend(index)
        print(f"{case.video_id}: phases={len(summary)} artifacts={len(index)}")

    write_csv(
        research / "ufo-video-pr34-pr35-phase-summary.csv",
        [
            "video",
            "release_id",
            "report_id",
            "phase",
            "start_second",
            "end_second",
            "sample_count",
            "high_count",
            "medium_count",
            "low_count",
            "none_count",
            "near_or_intersects_overlay_count",
            "dvids_anchor",
        ],
        all_summary_rows,
    )
    write_csv(
        research / "ufo-video-pr34-pr35-phase-review-assets.csv",
        ["video", "artifact_type", "path", "note"],
        all_index_rows,
    )
    print("summary=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-pr35-phase-summary.csv")
    print("assets=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-pr35-phase-review-assets.csv")


if __name__ == "__main__":
    main()
