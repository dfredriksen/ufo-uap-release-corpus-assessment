from __future__ import annotations

import csv
import math
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "source-files-not-included"


VIDEO_ID = "DOD_111688816"
VIDEO_NAME = f"{VIDEO_ID}.mp4"
RELEASE_ID = "DOW-UAP-PR26"
REPORT_ID = "DoW-UAP-D12"
DEFAULT_VIDEO = SOURCE_ROOT / "DOD_111688816.mp4"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def add_label(img: np.ndarray, text: str) -> np.ndarray:
    out = img.copy()
    cv2.rectangle(out, (0, 0), (min(out.shape[1], 1120), 34), (0, 0, 0), -1)
    cv2.putText(out, text, (8, 23), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1, cv2.LINE_AA)
    return out


def red_or_orange_mask(frame: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]
    red_or_orange = (hue <= 24) | (hue >= 170)
    return ((sat > 60) & (val > 60) & red_or_orange).astype(np.uint8) * 255


def contact_sheet(images: list[np.ndarray], cols: int = 4, thumb_width: int = 480) -> np.ndarray:
    thumbs = []
    for img in images:
        scale = thumb_width / img.shape[1]
        thumbs.append(cv2.resize(img, (thumb_width, int(img.shape[0] * scale)), interpolation=cv2.INTER_AREA))
    thumb_h = max(thumb.shape[0] for thumb in thumbs)
    rows = math.ceil(len(thumbs) / cols)
    sheet = np.zeros((rows * thumb_h, cols * thumb_width, 3), dtype=np.uint8)
    for idx, thumb in enumerate(thumbs):
        row = idx // cols
        col = idx % cols
        y = row * thumb_h
        x = col * thumb_width
        sheet[y : y + thumb.shape[0], x : x + thumb.shape[1]] = thumb
    return sheet


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path.cwd()
    research = root / "docs" / "research"
    out_root = research / "ufo-derived" / "video-hard-pair-phase-review" / VIDEO_ID
    frame_dir = out_root / "sample-frames"
    ensure_dir(frame_dir)

    cap = cv2.VideoCapture(str(DEFAULT_VIDEO))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open {DEFAULT_VIDEO}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps else 0.0

    sample_seconds = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, min(42.5, max(0.0, duration - 0.5))]
    rows: list[dict] = []
    labeled_images: list[np.ndarray] = []
    previous_gray: np.ndarray | None = None

    for idx, second in enumerate(sample_seconds):
        frame_index = min(int(round(second * fps)), max(0, frame_count - 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mask = red_or_orange_mask(frame)
        red_pixels = int(np.count_nonzero(mask))
        red_bbox = ""
        pts = cv2.findNonZero(mask)
        if pts is not None:
            x, y, w, h = cv2.boundingRect(pts)
            red_bbox = f"{x},{y},{w},{h}"

        if previous_gray is None:
            mean_abs_diff = ""
            changed_px_pct = ""
        else:
            diff = cv2.absdiff(gray, previous_gray)
            mean_abs_diff = round(float(diff.mean()), 3)
            changed_px_pct = round(float((diff > 12).sum()) * 100.0 / diff.size, 4)

        label = f"{VIDEO_ID} t={second:04.1f}s red_px={red_pixels}"
        labeled = add_label(frame, label)
        frame_path = frame_dir / f"frame_{idx:02d}_{second:04.1f}s.jpg"
        cv2.imwrite(str(frame_path), labeled, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        labeled_images.append(labeled)
        rows.append(
            {
                "video": VIDEO_NAME,
                "release_id": RELEASE_ID,
                "report_id": REPORT_ID,
                "sample_index": idx,
                "approx_second": f"{second:.1f}",
                "source_frame_index": frame_index,
                "mean_abs_diff_from_previous_sample": mean_abs_diff,
                "changed_pixels_gt12_pct_from_previous_sample": changed_px_pct,
                "red_or_orange_pixel_count": red_pixels,
                "red_or_orange_bbox_x_y_w_h": red_bbox,
                "sample_frame_path": str(frame_path).replace("\\", "/"),
            }
        )
        previous_gray = gray

    cap.release()

    sheet_path = out_root / f"{VIDEO_ID}-sample-contact-sheet.jpg"
    cv2.imwrite(str(sheet_path), contact_sheet(labeled_images), [int(cv2.IMWRITE_JPEG_QUALITY), 92])

    sample_csv = research / "ufo-video-pr26-d12-still-review-dod111688816.csv"
    write_csv(
        sample_csv,
        [
            "video",
            "release_id",
            "report_id",
            "sample_index",
            "approx_second",
            "source_frame_index",
            "mean_abs_diff_from_previous_sample",
            "changed_pixels_gt12_pct_from_previous_sample",
            "red_or_orange_pixel_count",
            "red_or_orange_bbox_x_y_w_h",
            "sample_frame_path",
        ],
        rows,
    )

    diffs = [float(row["mean_abs_diff_from_previous_sample"]) for row in rows if row["mean_abs_diff_from_previous_sample"] != ""]
    changed = [float(row["changed_pixels_gt12_pct_from_previous_sample"]) for row in rows if row["changed_pixels_gt12_pct_from_previous_sample"] != ""]
    summary_rows = [
        {"metric": "video", "value": VIDEO_NAME, "note": "local source video"},
        {"metric": "release_report_pair", "value": f"{RELEASE_ID} / {REPORT_ID}", "note": "DVIDS-stated report pairing"},
        {"metric": "duration_seconds", "value": round(duration, 3), "note": "OpenCV video duration"},
        {"metric": "frame_count", "value": frame_count, "note": "OpenCV frame count"},
        {"metric": "frame_size", "value": f"{width}x{height}", "note": "OpenCV frame size"},
        {"metric": "sample_count", "value": len(rows), "note": "sampled frames"},
        {"metric": "mean_abs_diff_median", "value": round(float(np.median(diffs)), 3) if diffs else "", "note": "between sampled frames; high values imply video pan/zoom/scene motion rather than a single frozen still"},
        {"metric": "changed_px_gt12_pct_median", "value": round(float(np.median(changed)), 4) if changed else "", "note": "between sampled frames"},
        {"metric": "max_red_or_orange_pixel_count", "value": max(int(row["red_or_orange_pixel_count"]) for row in rows), "note": "red/orange overlay presence proxy"},
        {"metric": "sample_contact_sheet", "value": str(sheet_path).replace("\\", "/"), "note": "review sheet"},
    ]
    summary_csv = research / "ufo-video-pr26-d12-still-review-summary.csv"
    write_csv(summary_csv, ["metric", "value", "note"], summary_rows)

    asset_rows = [
        {"artifact_type": "sample_csv", "path": str(sample_csv).replace("\\", "/"), "note": "PR26/D12 sampled-frame still-image review"},
        {"artifact_type": "summary_csv", "path": str(summary_csv).replace("\\", "/"), "note": "PR26/D12 still-image review summary"},
        {"artifact_type": "contact_sheet", "path": str(sheet_path).replace("\\", "/"), "note": "PR26/D12 sampled-frame contact sheet"},
    ]
    asset_csv = research / "ufo-video-pr26-d12-still-review-assets.csv"
    write_csv(asset_csv, ["artifact_type", "path", "note"], asset_rows)

    print(f"{VIDEO_ID}: fps={fps:.3f} frames={frame_count} duration={duration:.2f}s samples={len(rows)}")
    print(f"sample_csv={sample_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"asset_csv={asset_csv}")


if __name__ == "__main__":
    main()

