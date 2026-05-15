from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111688954"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR28"
REPORT_ID = "DoW-UAP-D25"
REPORTED_DVIDS_LABEL = "DoW-UAP-D7"
DEFAULT_VIDEO = Path(r"source-files-not-included/DOD_111688954.mp4")


@dataclass(frozen=True)
class Phase:
    name: str
    start: float
    end: float
    dvids_anchor: str
    roi: str


PHASES = (
    Phase(
        "split EO/SWIR context",
        0.0,
        3.9,
        "Before DVIDS 00:04 contrast note; split electro-optical / SWIR display",
        "full",
    ),
    Phase(
        "split-screen right-frame contrast",
        4.0,
        9.9,
        "DVIDS: 00:04 area of contrast becomes distinguishable in center of right frame",
        "right_half",
    ),
    Phase(
        "full-screen SWIR track",
        10.0,
        55.9,
        "DVIDS: 00:10 display shifts to full-screen SWIR; 00:55 contrast remains generally centered",
        "full",
    ),
    Phase(
        "visible-spectrum loss",
        56.0,
        56.9,
        "DVIDS: 00:56 operator switches to visible spectrum and loses subject",
        "full",
    ),
    Phase(
        "SWIR black-hot non-reacquisition",
        57.0,
        65.5,
        "DVIDS: 00:57-01:05 switches to SWIR black-hot but does not reacquire area of contrast",
        "full",
    ),
)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def phase_for(second: float) -> Phase:
    for phase in PHASES:
        if phase.start <= second <= phase.end:
            return phase
    return PHASES[-1]


def colored_overlay_mask(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    green = (hue >= 45) & (hue <= 85)
    cyan_blue = (hue >= 86) & (hue <= 120)
    red_or_orange = (hue <= 24) | (hue >= 170)
    mask = ((sat > 65) & (val > 65) & (green | cyan_blue | red_or_orange)).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    return cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=1)


def roi_mask(shape: tuple[int, int], phase: Phase) -> np.ndarray:
    h, w = shape
    mask = np.zeros((h, w), dtype=np.uint8)
    if phase.roi == "right_half":
        mask[:, int(w * 0.5) :] = 1
    else:
        mask[:, :] = 1
    return mask.astype(bool)


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


def detect_compact_bright_contrast(frame: np.ndarray, phase: Phase) -> dict:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    center_x = w / 2
    center_y = h / 2

    valid = (
        (hsv[:, :, 1] < 70)
        & (colored_overlay_mask(frame) == 0)
        & (gray > 25)
        & roi_mask(gray.shape, phase)
    )
    if int(valid.sum()) < 1000:
        return {}

    threshold = max(145, min(int(np.percentile(gray[valid], 99.68)), 245))
    bright = ((gray >= threshold) & valid).astype(np.uint8) * 255
    bright = cv2.medianBlur(bright, 3)
    bright = cv2.morphologyEx(bright, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))

    labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(bright, connectivity=8)
    candidates: list[dict] = []
    for label in range(1, labels_count):
        x, y, bw, bh, area = stats[label]
        if area < 3 or area > 900:
            continue
        if bw > 75 or bh > 75:
            continue
        aspect = bw / bh if bh else 99.0
        if aspect < 0.12 or aspect > 8.0:
            continue
        cx, cy = centroids[label]
        values = gray[labels == label]
        max_luma = int(values.max())
        mean_luma = float(values.mean())
        distance = math.hypot(float(cx) - center_x, float(cy) - center_y)
        roi_bonus = 0.35 if phase.roi == "right_half" and cx > w * 0.5 else 0.0
        score = (
            2.1 * max_luma / 255.0
            + mean_luma / 255.0
            + min(int(area), 160) / 160.0
            + roi_bonus
            - 0.0008 * distance
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
    if phase.name in {"visible-spectrum loss", "SWIR black-hot non-reacquisition"}:
        return "low"
    max_luma = int(candidate["max_luma"])
    area = int(candidate["area"])
    count = int(candidate["candidate_count"])
    if max_luma >= 210 and area >= 8 and count <= 30 and relation != "intersects colored reticle/overlay":
        return "high"
    if max_luma >= 175 and area >= 5:
        return "medium"
    return "low"


def add_label(img: np.ndarray, text: str, width: int = 980) -> np.ndarray:
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

    sample_rate = 2.0
    sample_count = int(math.floor(min(duration, 65.5) * sample_rate)) + 1
    rows: list[dict] = []
    annotated_paths: list[Path] = []
    patch_paths: list[Path] = []

    for sample_index in range(sample_count):
        second = round(sample_index / sample_rate, 2)
        phase = phase_for(second)
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
                "report_id_working": REPORT_ID,
                "dvids_report_label": REPORTED_DVIDS_LABEL,
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

    track_csv = research / "ufo-video-dod_111688954-phase-track.csv"
    fieldnames = [
        "video",
        "release_id",
        "report_id_working",
        "dvids_report_label",
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
    for phase in PHASES:
        phase_rows = [row for row in rows if row["phase"] == phase.name]
        if not phase_rows:
            continue
        summary_rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "report_id_working": REPORT_ID,
                "dvids_report_label": REPORTED_DVIDS_LABEL,
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

    summary_csv = research / "ufo-video-dod_111688954-phase-summary.csv"
    write_csv(
        summary_csv,
        [
            "video",
            "release_id",
            "report_id_working",
            "dvids_report_label",
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

    metadata_path = research / "ufo-video-dod_111688954-metadata.txt"
    metadata_path.write_text(
        "\n".join(
            [
                f"video={VIDEO_NAME}",
                f"release_id={RELEASE_ID}",
                f"working_report_id={REPORT_ID}",
                f"dvids_report_label={REPORTED_DVIDS_LABEL}",
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

    write_csv(
        research / "ufo-video-pr28-d25-phase-review-assets.csv",
        ["video", "artifact_type", "path", "note"],
        index_rows,
    )

    print(f"{VIDEO_ID}: fps={fps:.3f} frames={frame_count} duration={duration:.2f}s phases={len(summary_rows)}")
    print("summary=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688954-phase-summary.csv")
    print("track=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688954-phase-track.csv")
    print("assets=https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr28-d25-phase-review-assets.csv")


if __name__ == "__main__":
    main()
