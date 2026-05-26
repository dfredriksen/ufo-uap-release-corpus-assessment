from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
DERIVED = DOCS / "ufo-derived" / "overlay-measurement-audit" / "DOD_111719809-pr059-label-survey"
DEFAULT_VIDEO = ROOT / "source-files-not-included" / "DOD_111719809.mp4"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-pr059-label-survey-samples.csv"


def make_contact_sheet(tiles: list[np.ndarray], output: Path, columns: int = 4) -> None:
    if not tiles:
        return
    tile_h, tile_w = tiles[0].shape[:2]
    rows = (len(tiles) + columns - 1) // columns
    canvas = np.zeros((rows * tile_h, columns * tile_w, 3), dtype=np.uint8)
    for index, tile in enumerate(tiles):
        y = (index // columns) * tile_h
        x = (index % columns) * tile_w
        canvas[y : y + tile_h, x : x + tile_w] = tile
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def label_crop(frame: np.ndarray) -> np.ndarray:
    height, width = frame.shape[:2]
    x1 = int(width * 0.20)
    x2 = int(width * 0.95)
    y1 = int(height * 0.12)
    y2 = int(height * 0.88)
    return frame[y1:y2, x1:x2]


def format_tile(frame: np.ndarray, label: str) -> np.ndarray:
    crop = label_crop(frame)
    tile = cv2.resize(crop, (520, 300), interpolation=cv2.INTER_CUBIC)
    cv2.putText(tile, label, (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.82, (0, 0, 255), 2, cv2.LINE_AA)
    return tile


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PR059 source-resolution label survey crops.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--derived-root", type=Path, default=DERIVED)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--sample-step-seconds", type=int, default=1)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.video.exists():
        raise SystemExit(f"Missing source video: {args.video}")
    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {args.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if fps else 0.0
    max_second = int(duration)

    rows: list[dict[str, str]] = []
    tiles: list[np.ndarray] = []
    sheet_start: int | None = None
    for second in range(0, max_second + 1, args.sample_step_seconds):
        frame_index = int(round(second * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        if sheet_start is None:
            sheet_start = second
        tiles.append(format_tile(frame, f"PR059 {second:03d}s"))
        if len(tiles) >= 16:
            sheet = args.derived_root / f"pr059_label_survey_{sheet_start:03d}_{second:03d}.jpg"
            make_contact_sheet(tiles, sheet)
            tiles = []
            sheet_start = None
        rows.append(
            {
                "case": "PR059",
                "record_id": "DOW-UAP-PR059",
                "video": args.video.name,
                "second": str(second),
                "frame_index": str(frame_index),
                "crop_strategy": "source_resolution_right_center_track_box_and_label_region",
                "manual_label_review_status": "pending_interval_review",
                "notes": "Source media retained outside Git; crop sheets under ignored research/ufo-derived/.",
            }
        )
    if tiles and sheet_start is not None:
        sheet = args.derived_root / f"pr059_label_survey_{sheet_start:03d}_{max_second:03d}.jpg"
        make_contact_sheet(tiles, sheet)
    cap.release()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} PR059 label-survey sample rows to {args.output}")
    print(f"Wrote PR059 label-survey sheets under {args.derived_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
