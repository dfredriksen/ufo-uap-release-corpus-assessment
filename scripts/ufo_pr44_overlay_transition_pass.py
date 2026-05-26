from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = ROOT / "source-files-not-included" / "DOD_111689115.mp4"
DEFAULT_OUT_DIR = ROOT / "research" / "ufo-derived" / "overlay-measurement-audit" / "DOD_111689115-transition"
DEFAULT_INDEX = ROOT / "research" / "ufo-overlay-measurement-pr44-transition-pass.csv"
DEFAULT_CONTACT_SHEET = DEFAULT_OUT_DIR / "pr44_overlay_transition_contact_sheet.jpg"


def crop_overlay(frame: np.ndarray) -> np.ndarray:
    """Crop the PR44 reticle/label region identified in the prior one-second pass."""
    height, width = frame.shape[:2]
    x0 = max(0, min(width, 850))
    y0 = max(0, min(height, 450))
    x1 = max(x0, min(width, 1120))
    y1 = max(y0, min(height, 650))
    return frame[y0:y1, x0:x1].copy()


def add_frame_label(image: np.ndarray, label: str) -> np.ndarray:
    out = image.copy()
    cv2.putText(out, label, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2, cv2.LINE_AA)
    return out


def make_contact_sheet(crops: list[np.ndarray], labels: list[str], output: Path, columns: int = 5) -> None:
    if not crops:
        return
    tile_w, tile_h = 220, 160
    rows = (len(crops) + columns - 1) // columns
    canvas = np.zeros((rows * tile_h, columns * tile_w, 3), dtype=np.uint8)
    for index, crop in enumerate(crops):
        tile = cv2.resize(crop, (tile_w, tile_h), interpolation=cv2.INTER_AREA)
        tile = add_frame_label(tile, labels[index])
        y = (index // columns) * tile_h
        x = (index % columns) * tile_w
        canvas[y : y + tile_h, x : x + tile_w] = tile
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract PR44 high-rate overlay-label transition crops.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--start-second", type=float, default=232.0)
    parser.add_argument("--end-second", type=float, default=235.0)
    parser.add_argument("--sample-rate-hz", type=float, default=5.0)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--index-output", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--contact-sheet", type=Path, default=DEFAULT_CONTACT_SHEET)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.video.exists():
        raise SystemExit(f"Missing source video: {args.video}")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    step = 1.0 / args.sample_rate_hz

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, str]] = []
    crops: list[np.ndarray] = []
    labels: list[str] = []

    sample_index = 0
    second = args.start_second
    while second <= args.end_second + 1e-9:
        frame_index = int(round(second * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            second += step
            sample_index += 1
            continue
        crop = crop_overlay(frame)
        crop_name = f"DOD_111689115_t{second:08.3f}_f{frame_index:06d}_overlay_transition.jpg"
        crop_path = args.out_dir / crop_name
        cv2.imwrite(str(crop_path), crop, [int(cv2.IMWRITE_JPEG_QUALITY), 94])
        rows.append(
            {
                "case": "PR44",
                "video": args.video.name,
                "record_id": "DOW-UAP-PR44",
                "sample_index": str(sample_index),
                "second": f"{second:.3f}",
                "frame_index": str(frame_index),
                "sample_rate_hz": f"{args.sample_rate_hz:g}",
                "crop_artifact": str(crop_path.relative_to(ROOT)),
                "manual_label_text": "",
                "manual_read_confidence": "",
                "semantics_status": "unresolved",
                "notes": "High-rate transition crop; manual label classification required.",
            }
        )
        crops.append(crop)
        labels.append(f"{second:.1f}s f{frame_index}")
        second += step
        sample_index += 1

    cap.release()

    args.index_output.parent.mkdir(parents=True, exist_ok=True)
    with args.index_output.open("w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "case",
            "video",
            "record_id",
            "sample_index",
            "second",
            "frame_index",
            "sample_rate_hz",
            "crop_artifact",
            "manual_label_text",
            "manual_read_confidence",
            "semantics_status",
            "notes",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    make_contact_sheet(crops, labels, args.contact_sheet)
    print(f"Wrote {len(rows)} transition crops to {args.out_dir}")
    print(f"Wrote index to {args.index_output}")
    print(f"Wrote contact sheet to {args.contact_sheet}")


if __name__ == "__main__":
    main()
