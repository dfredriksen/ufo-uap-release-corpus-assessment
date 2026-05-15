from __future__ import annotations

import csv
import math
from pathlib import Path

import cv2
import numpy as np


VIDEO_ID = "DOD_111689030"
SOURCE_VIDEO = Path(r"source-files-not-included/DOD_111689030.mp4")
DETECTOR_CSV = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030.csv")
OUT_ROOT = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/manual-validation") / VIDEO_ID


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def center_crop(frame: np.ndarray, width: int = 960, height: int = 540) -> tuple[np.ndarray, int, int]:
    h, w = frame.shape[:2]
    x0 = max(0, (w - width) // 2)
    y0 = max(0, (h - height) // 2)
    return frame[y0 : y0 + height, x0 : x0 + width], x0, y0


def add_label(img: np.ndarray, label: str) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (260, 28), (0, 0, 0), -1)
    cv2.putText(out, label, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def crop_patch(frame: np.ndarray, x: int, y: int, size: int = 160) -> np.ndarray:
    h, w = frame.shape[:2]
    half = size // 2
    x0 = max(0, min(w - size, x - half))
    y0 = max(0, min(h - size, y - half))
    return frame[y0 : y0 + size, x0 : x0 + size]


def write_contact_sheets(paths: list[Path], out_dir: Path, prefix: str, cols: int, thumb_width: int) -> list[Path]:
    ensure_dir(out_dir)
    written: list[Path] = []
    if not paths:
        return written
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
        for i, thumb in enumerate(thumbs):
            row = i // cols
            col = i % cols
            y = row * thumb_h
            x = col * thumb_width
            sheet[y : y + thumb.shape[0], x : x + thumb.shape[1]] = thumb
        out = out_dir / f"{prefix}-{page:02d}.jpg"
        cv2.imwrite(str(out), sheet, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        written.append(out)
    return written


def load_rows() -> list[dict]:
    with DETECTOR_CSV.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    selected = []
    for row in rows:
        second = float(row["sample_second"])
        if 50 <= second <= 87:
            selected.append(row)
    return selected


def main() -> None:
    raw_dir = OUT_ROOT / "raw-onefps"
    patch_dir = OUT_ROOT / "candidate-patches-onefps"
    sheet_dir = OUT_ROOT / "sheets"
    ensure_dir(raw_dir)
    ensure_dir(patch_dir)
    ensure_dir(sheet_dir)

    rows = load_rows()
    target_frames = {int(row["source_frame_index"]): row for row in rows}

    cap = cv2.VideoCapture(str(SOURCE_VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {SOURCE_VIDEO}")

    raw_paths: list[Path] = []
    patch_paths: list[Path] = []
    emitted_rows: list[dict] = []

    frame_index = 0
    while frame_index <= max(target_frames):
        ok, frame = cap.read()
        if not ok:
            break
        if frame_index in target_frames:
            row = target_frames[frame_index]
            second = float(row["sample_second"])
            label = f"t={second:05.1f}s f={frame_index:05d}"
            crop, _, _ = center_crop(frame)
            raw_path = raw_dir / f"t{int(second):04d}_raw.jpg"
            cv2.imwrite(str(raw_path), add_label(crop, label), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
            raw_paths.append(raw_path)

            patch_path = ""
            if row["best_x"] and row["best_y"]:
                x = int(row["best_x"])
                y = int(row["best_y"])
                patch = crop_patch(frame, x, y)
                patch = cv2.resize(patch, (480, 480), interpolation=cv2.INTER_CUBIC)
                patch_path_obj = patch_dir / f"t{int(second):04d}_patch.jpg"
                cv2.imwrite(str(patch_path_obj), add_label(patch, label), [int(cv2.IMWRITE_JPEG_QUALITY), 94])
                patch_paths.append(patch_path_obj)
                patch_path = str(patch_path_obj).replace("\\", "/")

            emitted_rows.append(
                {
                    "sample_second": f"{second:.1f}",
                    "source_frame_index": frame_index,
                    "detector_best_x": row["best_x"],
                    "detector_best_y": row["best_y"],
                    "detector_confidence": row["confidence"],
                    "raw_crop_path": str(raw_path).replace("\\", "/"),
                    "candidate_patch_path": patch_path,
                }
            )
        frame_index += 1

    cap.release()

    raw_sheets = write_contact_sheets(raw_paths, sheet_dir, f"{VIDEO_ID}-manual-raw-onefps", cols=4, thumb_width=480)
    patch_sheets = write_contact_sheets(patch_paths, sheet_dir, f"{VIDEO_ID}-manual-patches-onefps", cols=5, thumb_width=240)

    index_path = Path("https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-manual-review-assets.csv")
    with index_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sample_second",
                "source_frame_index",
                "detector_best_x",
                "detector_best_y",
                "detector_confidence",
                "raw_crop_path",
                "candidate_patch_path",
            ],
        )
        writer.writeheader()
        writer.writerows(emitted_rows)

    print(f"rows={len(emitted_rows)}")
    print(f"raw_sheets={len(raw_sheets)}")
    print(f"patch_sheets={len(patch_sheets)}")
    print(f"index={index_path}")


if __name__ == "__main__":
    main()
