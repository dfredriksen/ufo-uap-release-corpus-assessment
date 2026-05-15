from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111688825"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR27"
REPORT_ID = "DoW-UAP-D23"
DEFAULT_VIDEO = Path(r"source-files-not-included/DOD_111688825.mp4")


@dataclass(frozen=True)
class Phase:
    name: str
    start: float
    end: float
    step: float
    dvids_anchor: str
    roi: str


PHASES = (
    Phase(
        "no-content / scene context lead-in",
        0.0,
        115.5,
        4.0,
        "DVIDS: 00:00-01:55 no content",
        "full",
    ),
    Phase(
        "initial right-side contrast",
        116.0,
        123.5,
        0.5,
        "DVIDS: 01:56 contrast becomes distinguishable near center-right",
        "right_center",
    ),
    Phase(
        "pan to center",
        124.0,
        133.5,
        0.5,
        "DVIDS: 02:04 IR sensor pans to center on contrast",
        "center_80",
    ),
    Phase(
        "zoom and centered track",
        134.0,
        206.5,
        0.5,
        "DVIDS: 02:14 zoom; 02:15-03:26 contrast remains generally centered",
        "center_70",
    ),
    Phase(
        "sensor-motion loss and reacquisition",
        207.0,
        297.0,
        0.5,
        "DVIDS: 03:27-04:57 sensor motion repeatedly loses/reacquires contrast",
        "full",
    ),
)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def sample_seconds() -> list[tuple[float, Phase]]:
    samples: list[tuple[float, Phase]] = []
    for phase in PHASES:
        idx = 0
        while True:
            second = round(phase.start + idx * phase.step, 2)
            if second > phase.end + 1e-6:
                break
            samples.append((second, phase))
            idx += 1
    seen: set[float] = set()
    deduped: list[tuple[float, Phase]] = []
    for second, phase in samples:
        if second in seen:
            continue
        seen.add(second)
        deduped.append((second, phase))
    return deduped


def colored_overlay_mask(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    green = (hue >= 42) & (hue <= 88)
    cyan_blue = (hue >= 86) & (hue <= 125)
    red_or_orange = (hue <= 24) | (hue >= 170)
    mask = ((sat > 55) & (val > 55) & (green | cyan_blue | red_or_orange)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)


def roi_mask(shape: tuple[int, int], phase: Phase) -> np.ndarray:
    h, w = shape
    mask = np.zeros((h, w), dtype=np.uint8)
    if phase.roi == "right_half":
        mask[:, int(w * 0.50) :] = 1
    elif phase.roi == "right_center":
        mask[int(h * 0.25) : int(h * 0.80), int(w * 0.50) :] = 1
    elif phase.roi == "center_80":
        mask[int(h * 0.15) : int(h * 0.85), int(w * 0.10) : int(w * 0.90)] = 1
    elif phase.roi == "center_70":
        x0 = int(w * 0.15)
        x1 = int(w * 0.85)
        y0 = int(h * 0.12)
        y1 = int(h * 0.88)
        mask[y0:y1, x0:x1] = 1
    else:
        mask[:, :] = 1
    return mask.astype(bool)


def nearest_overlay_distance(frame: np.ndarray, x: float, y: float) -> tuple[str, float | None]:
    pts = cv2.findNonZero(colored_overlay_mask(frame))
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


def detect_compact_bright_contrast(frame: np.ndarray, phase: Phase) -> dict:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    center_x = w / 2
    center_y = h / 2

    valid = (
        (hsv[:, :, 1] < 70)
        & (colored_overlay_mask(frame) == 0)
        & (gray > 18)
        & roi_mask(gray.shape, phase)
    )
    if int(valid.sum()) < 1000:
        return {}

    threshold = max(150, min(int(np.percentile(gray[valid], 99.75)), 246))
    bright = ((gray >= threshold) & valid).astype(np.uint8) * 255
    bright = cv2.medianBlur(bright, 3)
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(bright, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, bw, bh, area = stats[label]
        if area < 3 or area > 950:
            continue
        if bw > 85 or bh > 85:
            continue
        aspect = bw / bh if bh else 99.0
        if aspect < 0.10 or aspect > 9.0:
            continue
        cx, cy = centroids[label]
        values = gray[labels == label]
        max_luma = int(values.max())
        mean_luma = float(values.mean())
        distance = math.hypot(float(cx) - center_x, float(cy) - center_y)
        center_bonus = 0.45 if phase.roi == "center_70" and distance < min(w, h) * 0.30 else 0.0
        right_bonus = 0.35 if phase.roi == "right_half" and cx > w * 0.50 else 0.0
        score = (
            2.1 * max_luma / 255.0
            + mean_luma / 255.0
            + min(int(area), 180) / 180.0
            + center_bonus
            + right_bonus
            - 0.00055 * distance
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


def classify_detection(candidate: dict, phase: Phase, relation: str) -> str:
    if not candidate:
        return "none"
    if phase.name == "no-content / scene context lead-in":
        return "low"
    max_luma = int(candidate["max_luma"])
    area = int(candidate["area"])
    count = int(candidate["candidate_count"])
    if max_luma >= 215 and area >= 7 and count <= 42 and relation != "intersects colored reticle/overlay":
        return "high"
    if max_luma >= 178 and area >= 5:
        return "medium"
    return "low"


def add_label(img: np.ndarray, text: str, width: int = 1100) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(width, out.shape[1]), 34), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def annotate_frame(frame: np.ndarray, candidate: dict, label: str) -> np.ndarray:
    out = frame.copy()
    if candidate:
        x = int(round(candidate["x"]))
        y = int(round(candidate["y"]))
        cv2.drawMarker(out, (x, y), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=30, thickness=2)
        cv2.circle(out, (x, y), 26, (0, 0, 255), 2)
        cv2.line(out, (out.shape[1] // 2, out.shape[0] // 2), (x, y), (255, 255, 0), 1)
    return add_label(out, label)


def crop_patch(frame: np.ndarray, candidate: dict, size: int = 160) -> np.ndarray:
    h, w = frame.shape[:2]
    if candidate:
        cx, cy = int(round(candidate["x"])), int(round(candidate["y"]))
    else:
        cx, cy = w // 2, h // 2
    half = size // 2
    x0 = max(0, min(w - size, cx - half))
    y0 = max(0, min(h - size, cy - half))
    return frame[y0 : y0 + size, x0 : x0 + size].copy()


def annotate_patch(patch: np.ndarray, label: str) -> np.ndarray:
    out = cv2.resize(patch, (440, 440), interpolation=cv2.INTER_CUBIC)
    cv2.drawMarker(out, (220, 220), (0, 0, 255), markerType=cv2.MARKER_CROSS, markerSize=34, thickness=2)
    cv2.circle(out, (220, 220), 48, (0, 0, 255), 2)
    return add_label(out, label, width=440)


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


def main() -> None:
    root = Path.cwd()
    research = root / "docs" / "research"
    out_root = research / "ufo-derived" / "video-hard-pair-phase-review" / VIDEO_ID
    frame_dir = out_root / "annotated-frames"
    patch_dir = out_root / "object-zoom-patches"
    sheet_dir = out_root / "sheets"
    for path in (frame_dir, patch_dir, sheet_dir):
        ensure_dir(path)

    cap = cv2.VideoCapture(str(DEFAULT_VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {DEFAULT_VIDEO}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps else 0.0

    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []

    for sample_index, (second, phase) in enumerate(sample_seconds()):
        if second > duration:
            continue
        source_frame_index = min(int(round(second * fps)), max(0, frame_count - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, source_frame_index)
        ok, frame = cap.read()
        if not ok:
            continue

        candidate = detect_compact_bright_contrast(frame, phase)
        if candidate:
            relation, nearest_overlay = nearest_overlay_distance(frame, candidate["x"], candidate["y"])
        else:
            relation, nearest_overlay = "no candidate", None
        confidence = classify_detection(candidate, phase, relation)
        label = f"{VIDEO_ID} t={second:05.1f}s {phase.name} conf={confidence}"
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
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "report_id": REPORT_ID,
                "sample_index": sample_index,
                "approx_second": f"{second:.2f}",
                "source_frame_index": source_frame_index,
                "phase": phase.name,
                "dvids_anchor": phase.dvids_anchor,
                "candidate_x": "" if not candidate else round(float(candidate["x"]), 1),
                "candidate_y": "" if not candidate else round(float(candidate["y"]), 1),
                "dx_from_frame_center": "" if not candidate else round(float(candidate["x"]) - width / 2, 1),
                "dy_from_frame_center": "" if not candidate else round(float(candidate["y"]) - height / 2, 1),
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
    track_csv = research / "ufo-video-dod_111688825-phase-track.csv"
    write_csv(track_csv, fieldnames, rows)

    summary_rows: list[dict] = []
    for phase in PHASES:
        phase_rows = [row for row in rows if row["phase"] == phase.name]
        if not phase_rows:
            continue
        summary_rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "report_id": REPORT_ID,
                "phase": phase.name,
                "start_second": phase.start,
                "end_second": phase.end,
                "sample_count": len(phase_rows),
                "high_count": sum(1 for row in phase_rows if row["review_confidence"] == "high"),
                "medium_count": sum(1 for row in phase_rows if row["review_confidence"] == "medium"),
                "low_count": sum(1 for row in phase_rows if row["review_confidence"] == "low"),
                "none_count": sum(1 for row in phase_rows if row["review_confidence"] == "none"),
                "near_or_intersects_overlay_count": sum(
                    1
                    for row in phase_rows
                    if row["overlay_relation"] in {"near colored reticle/overlay", "intersects colored reticle/overlay"}
                ),
                "dvids_anchor": phase.dvids_anchor,
            }
        )

    summary_csv = research / "ufo-video-dod_111688825-phase-summary.csv"
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

    metadata_path = research / "ufo-video-dod_111688825-metadata.txt"
    metadata_path.write_text(
        "\n".join(
            [
                f"video={VIDEO_NAME}",
                f"release_id={RELEASE_ID}",
                f"report_id={REPORT_ID}",
                f"path={DEFAULT_VIDEO}",
                f"fps={fps}",
                f"frame_count={frame_count}",
                f"width={width}",
                f"height={height}",
                f"duration_seconds={duration}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    annotated_sheets = write_contact_sheets(annotated_paths, sheet_dir, f"{VIDEO_ID}-phase-annotated", cols=5, thumb_width=384)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-phase-patches", cols=8, thumb_width=180)

    index_rows = [
        {"video": VIDEO_ID, "artifact_type": "metadata", "path": str(metadata_path).replace("\\", "/"), "note": "OpenCV source video metadata"},
        {"video": VIDEO_ID, "artifact_type": "phase_track_csv", "path": str(track_csv).replace("\\", "/"), "note": "phase-aligned sample table"},
        {"video": VIDEO_ID, "artifact_type": "phase_summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "phase summary"},
    ]
    for path in annotated_sheets:
        index_rows.append({"video": VIDEO_ID, "artifact_type": "annotated_contact_sheet", "path": str(path).replace("\\", "/"), "note": "annotated phase-review sheet"})
    for path in patch_sheets:
        index_rows.append({"video": VIDEO_ID, "artifact_type": "zoom_patch_contact_sheet", "path": str(path).replace("\\", "/"), "note": "candidate zoom-patch sheet"})

    assets_csv = research / "ufo-video-pr27-d23-phase-review-assets.csv"
    write_csv(assets_csv, ["video", "artifact_type", "path", "note"], index_rows)

    print(f"{VIDEO_ID}: fps={fps:.3f} frames={frame_count} duration={duration:.2f}s samples={len(rows)} phases={len(summary_rows)}")
    print("summary=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688825-phase-summary.csv")
    print("track=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688825-phase-track.csv")
    print("assets=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-phase-review-assets.csv")


if __name__ == "__main__":
    main()
