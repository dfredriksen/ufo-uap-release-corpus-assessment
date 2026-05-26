from __future__ import annotations

import argparse
import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
SOURCE_ROOT = ROOT / "source-files-not-included"
DERIVED = DOCS / "ufo-derived" / "overlay-measurement-audit"
DEFAULT_ACQUISITION = DOCS / "ufo-overlay-measurement-p1-source-acquisition.csv"
DEFAULT_SAMPLES = DOCS / "ufo-overlay-measurement-p1-quicklook-samples.csv"


@dataclass(frozen=True)
class Case:
    case: str
    record_id: str
    video: Path
    source_url: str
    dvids_url: str
    matched_terms: str


CASES = [
    Case(
        case="PR052",
        record_id="DOW-UAP-PR052",
        video=SOURCE_ROOT / "DOD_111719718.mp4",
        source_url="https://d34w7g4gy10iej.cloudfront.net/video/2605/DOD_111719718/DOD_111719718.mp4",
        dvids_url="https://www.dvidshub.net/video/1007708/dow-uap-pr052-uap-uso-formation-callsign-mission",
        matched_terms="Visual elements of the sensor display, zoom",
    ),
    Case(
        case="PR058",
        record_id="DOW-UAP-PR058",
        video=SOURCE_ROOT / "DOD_111719800.mp4",
        source_url="https://d34w7g4gy10iej.cloudfront.net/video/2605/DOD_111719800/DOD_111719800.mp4",
        dvids_url="https://www.dvidshub.net/video/1007723/dow-uap-pr058-callsign-mission-uap",
        matched_terms="Visual elements of the sensor display",
    ),
    Case(
        case="PR059",
        record_id="DOW-UAP-PR059",
        video=SOURCE_ROOT / "DOD_111719809.mp4",
        source_url="https://d34w7g4gy10iej.cloudfront.net/video/2605/DOD_111719809/DOD_111719809.mp4",
        dvids_url="https://www.dvidshub.net/video/1007727/dow-uap-pr059-nag-uap-1-jun-20",
        matched_terms="field-of-view, reticle, zoom",
    ),
    Case(
        case="PR069",
        record_id="DOW-UAP-PR069",
        video=SOURCE_ROOT / "DOD_111720700.mp4",
        source_url="https://d34w7g4gy10iej.cloudfront.net/video/2605/DOD_111720700/DOD_111720700.mp4",
        dvids_url="https://www.dvidshub.net/video/1007781/dow-uap-pr069-f-18-flir-uap",
        matched_terms="reticle",
    ),
    Case(
        case="PR073",
        record_id="DOW-UAP-PR073",
        video=SOURCE_ROOT / "DOD_111720765.mp4",
        source_url="https://d34w7g4gy10iej.cloudfront.net/video/2605/DOD_111720765/DOD_111720765.mp4",
        dvids_url="https://www.dvidshub.net/video/1007790/dow-uap-pr073-iir-1-655-s0053-23-several-unidentified-aerial-phenomenon-encountered-vicinity-columbus-oh",
        matched_terms="field-of-view, sensor display, zoom",
    ),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def public_source_hint(path: Path) -> str:
    return f"source-files-not-included/{path.name}"


def make_contact_sheet(tiles: list[np.ndarray], output: Path, columns: int = 5) -> None:
    if not tiles:
        return
    tile_w, tile_h = tiles[0].shape[1], tiles[0].shape[0]
    rows = (len(tiles) + columns - 1) // columns
    canvas = np.zeros((rows * tile_h, columns * tile_w, 3), dtype=np.uint8)
    for index, tile in enumerate(tiles):
        y = (index // columns) * tile_h
        x = (index % columns) * tile_w
        canvas[y : y + tile_h, x : x + tile_w] = tile
    output.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output), canvas, [int(cv2.IMWRITE_JPEG_QUALITY), 92])


def format_tile(frame: np.ndarray, label: str, size: tuple[int, int] = (320, 180)) -> np.ndarray:
    tile = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)
    cv2.putText(tile, label, (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (0, 0, 255), 2, cv2.LINE_AA)
    return tile


def focus_crop(frame: np.ndarray, case_name: str) -> np.ndarray:
    height, width = frame.shape[:2]
    if case_name in {"PR052", "PR058", "PR059"}:
        x1 = int(width * 0.12)
        x2 = int(width * 0.88)
        y1 = int(height * 0.12)
        y2 = int(height * 0.88)
        return frame[y1:y2, x1:x2]
    if case_name == "PR073":
        y1 = int(height * 0.30)
        y2 = int(height * 0.68)
        return frame[y1:y2, 0:width]
    if case_name == "PR069":
        x1 = int(width * 0.18)
        x2 = int(width * 0.82)
        y1 = int(height * 0.16)
        y2 = int(height * 0.84)
        return frame[y1:y2, x1:x2]
    return frame


def analyze_case(case: Case, out_dir: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    if not case.video.exists():
        raise SystemExit(f"Missing source video: {case.video}")
    cap = cv2.VideoCapture(str(case.video))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {case.video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = frame_count / fps if fps else 0.0

    acquisition = {
        "case": case.case,
        "record_id": case.record_id,
        "video": case.video.name,
        "source_url": case.source_url,
        "dvids_url": case.dvids_url,
        "local_path_not_redistributed": public_source_hint(case.video),
        "bytes": str(case.video.stat().st_size),
        "sha256": sha256_file(case.video),
        "opencv_width": str(width),
        "opencv_height": str(height),
        "opencv_fps": f"{fps:.3f}",
        "opencv_frames": str(frame_count),
        "opencv_duration_seconds": f"{duration:.3f}",
        "matched_terms": case.matched_terms,
    }

    sample_rows: list[dict[str, str]] = []
    tiles: list[np.ndarray] = []
    focus_tiles: list[np.ndarray] = []
    sheet_start: int | None = None
    focus_sheet_start: int | None = None
    max_second = int(duration)
    for second in range(0, max_second + 1):
        frame_index = int(round(second * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        if sheet_start is None:
            sheet_start = second
        if focus_sheet_start is None:
            focus_sheet_start = second
        tiles.append(format_tile(frame, f"{case.case} {second:03d}s"))
        focus_tiles.append(format_tile(focus_crop(frame, case.case), f"{case.case} {second:03d}s", (480, 280)))
        if len(tiles) >= 20:
            sheet = out_dir / case.case / f"{case.case.lower()}_quicklook_{sheet_start:03d}_{second:03d}.jpg"
            make_contact_sheet(tiles, sheet)
            tiles = []
            sheet_start = None
        if len(focus_tiles) >= 12:
            sheet = out_dir / case.case / f"{case.case.lower()}_focus_{focus_sheet_start:03d}_{second:03d}.jpg"
            make_contact_sheet(focus_tiles, sheet, columns=3)
            focus_tiles = []
            focus_sheet_start = None
        sample_rows.append(
            {
                "case": case.case,
                "record_id": case.record_id,
                "video": case.video.name,
                "second": str(second),
                "frame_index": str(frame_index),
                "manual_overlay_review_status": "sampled_for_manual_sheet_review",
                "notes": "One-frame-per-second quicklook sample; manual conclusions are recorded separately; source media not redistributed.",
            }
        )
    if tiles and sheet_start is not None:
        sheet = out_dir / case.case / f"{case.case.lower()}_quicklook_{sheet_start:03d}_{max_second:03d}.jpg"
        make_contact_sheet(tiles, sheet)
    if focus_tiles and focus_sheet_start is not None:
        sheet = out_dir / case.case / f"{case.case.lower()}_focus_{focus_sheet_start:03d}_{max_second:03d}.jpg"
        make_contact_sheet(focus_tiles, sheet, columns=3)
    cap.release()
    return acquisition, sample_rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one-fps quicklook sheets for P1 overlay residuals.")
    parser.add_argument("--derived-root", type=Path, default=DERIVED / "p1-quicklook")
    parser.add_argument("--acquisition-output", type=Path, default=DEFAULT_ACQUISITION)
    parser.add_argument("--samples-output", type=Path, default=DEFAULT_SAMPLES)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    acquisition_rows: list[dict[str, str]] = []
    sample_rows: list[dict[str, str]] = []
    for case in CASES:
        acquisition, samples = analyze_case(case, args.derived_root)
        acquisition_rows.append(acquisition)
        sample_rows.extend(samples)
    write_csv(args.acquisition_output, acquisition_rows)
    write_csv(args.samples_output, sample_rows)
    print(f"Wrote {len(acquisition_rows)} acquisition rows to {args.acquisition_output}")
    print(f"Wrote {len(sample_rows)} quicklook sample rows to {args.samples_output}")
    print(f"Wrote contact sheets under {args.derived_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
