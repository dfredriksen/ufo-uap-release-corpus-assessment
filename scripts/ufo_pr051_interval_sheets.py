from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VIDEO = ROOT / "source-files-not-included" / "DOD_111719715.mp4"
DEFAULT_OUTPUT = ROOT / "research" / "ufo-derived" / "overlay-measurement-audit" / "DOD_111719715-pr051-crops"


INTERVALS = {
    "original_label_004_021": range(4, 22),
    "altered_replay_030_050": range(30, 51, 4),
    "far_zoom_original_res_130_220": range(130, 230, 10),
    "reticle_lock_label_248_267": range(248, 268),
    "exit_replay_label_269_286": range(269, 287),
}


def crop_for_interval(frame: np.ndarray, interval_name: str) -> np.ndarray:
    if "reticle_lock" in interval_name:
        x1, y1, x2, y2 = 430, 250, 800, 520
    else:
        x1, y1, x2, y2 = 450, 230, 800, 460
    return frame[y1:y2, x1:x2]


def make_sheet(tiles: list[np.ndarray], output: Path, columns: int = 4) -> None:
    if not tiles:
        return
    tile_w, tile_h = 350, 230
    rows = (len(tiles) + columns - 1) // columns
    canvas = np.zeros((rows * tile_h, columns * tile_w, 3), dtype=np.uint8)
    for index, tile in enumerate(tiles):
        y = (index // columns) * tile_h
        x = (index % columns) * tile_w
        canvas[y : y + tile_h, x : x + tile_w] = tile
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 94])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate PR051 interval crop sheets for overlay-label review.")
    parser.add_argument("--video", type=Path, default=DEFAULT_VIDEO)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.video.exists():
        raise SystemExit(f"Missing source video: {args.video}")

    cap = cv2.VideoCapture(str(args.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {args.video}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    for interval_name, seconds in INTERVALS.items():
        tiles: list[np.ndarray] = []
        for second in seconds:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(second * fps)))
            ok, frame = cap.read()
            if not ok:
                continue
            crop = crop_for_interval(frame, interval_name)
            tile = cv2.resize(crop, (350, 230), interpolation=cv2.INTER_CUBIC)
            cv2.putText(tile, f"{second:03d}s", (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
            tiles.append(tile)
        make_sheet(tiles, args.output_dir / f"{interval_name}.jpg")

    cap.release()
    print(f"Wrote PR051 interval crop sheets to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
