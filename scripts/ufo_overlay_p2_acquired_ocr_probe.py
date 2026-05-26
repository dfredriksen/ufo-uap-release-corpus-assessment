from __future__ import annotations

import argparse
import csv
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
DEFAULT_ACQUISITION = DOCS / "ufo-overlay-measurement-p2-source-acquisition.csv"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-p2-acquired-ocr-probe.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-p2-acquired-ocr-probe.md"

FIELDNAMES = [
    "record_id",
    "release_tag",
    "source_video",
    "source_path_not_redistributed",
    "source_sha256",
    "opencv_width",
    "opencv_height",
    "opencv_fps",
    "opencv_frames",
    "opencv_duration_seconds",
    "sample_step_seconds",
    "second",
    "frame_index",
    "roi",
    "ocr_text",
    "normalized_text",
    "meter_label_candidate",
    "candidate_rule",
    "source_media_boundary",
]

METER_PATTERN = re.compile(
    r"(?<![A-Z0-9])(?:<\s*)?\d{1,3}\s*M\b|\bM\s*\d{1,3}(?![A-Z0-9])|(?<![A-Z0-9])SM(?![A-Z0-9])",
    re.IGNORECASE,
)


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def public_source_hint(path: Path) -> str:
    return f"source-files-not-included/{path.name}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_text(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9<]+", " ", value).strip().upper()


def rois(frame) -> dict[str, object]:
    height, width = frame.shape[:2]
    return {
        "center_reticle": frame[int(height * 0.18) : int(height * 0.82), int(width * 0.18) : int(width * 0.82)],
        "upper_display_strip": frame[0 : int(height * 0.25), 0:width],
        "lower_display_strip": frame[int(height * 0.72) : height, 0:width],
        "right_display_strip": frame[0:height, int(width * 0.68) : width],
    }


def prepare_for_ocr(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def run_tesseract(image, tesseract_cmd: str, psm: str) -> str:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        temp_path = Path(temp.name)
    try:
        cv2.imwrite(str(temp_path), image)
        result = subprocess.run(
            [tesseract_cmd, str(temp_path), "stdout", "--psm", psm],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        return result.stdout.strip()
    finally:
        temp_path.unlink(missing_ok=True)


def analyze_record(row: dict[str, str], sample_step_seconds: int, tesseract_cmd: str, psm: str) -> list[dict[str, str]]:
    source_path = Path(clean(row.get("local_path_not_redistributed")))
    if not source_path.exists():
        raise SystemExit(f"Missing source video: {source_path}")
    cap = cv2.VideoCapture(str(source_path))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {source_path}")
    fps = float(clean(row.get("opencv_fps")) or cap.get(cv2.CAP_PROP_FPS) or 30.0)
    frame_count = int(clean(row.get("opencv_frames")) or cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = float(clean(row.get("opencv_duration_seconds")) or (frame_count / fps if fps else 0.0))

    rows: list[dict[str, str]] = []
    for second in range(0, int(duration) + 1, sample_step_seconds):
        frame_index = min(int(round(second * fps)), max(frame_count - 1, 0))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        for roi_name, roi in rois(frame).items():
            text = run_tesseract(prepare_for_ocr(roi), tesseract_cmd, psm)
            normalized = normalize_text(text)
            candidate = bool(METER_PATTERN.search(normalized))
            rows.append(
                {
                    "record_id": clean(row.get("record_id")),
                    "release_tag": clean(row.get("release_tag")),
                    "source_video": clean(row.get("source_video")),
                    "source_path_not_redistributed": public_source_hint(source_path),
                    "source_sha256": clean(row.get("sha256")),
                    "opencv_width": clean(row.get("opencv_width")),
                    "opencv_height": clean(row.get("opencv_height")),
                    "opencv_fps": clean(row.get("opencv_fps")),
                    "opencv_frames": clean(row.get("opencv_frames")),
                    "opencv_duration_seconds": clean(row.get("opencv_duration_seconds")),
                    "sample_step_seconds": str(sample_step_seconds),
                    "second": str(second),
                    "frame_index": str(frame_index),
                    "roi": roi_name,
                    "ocr_text": " ".join(text.split()),
                    "normalized_text": normalized,
                    "meter_label_candidate": "yes" if candidate else "no",
                    "candidate_rule": METER_PATTERN.pattern if candidate else "",
                    "source_media_boundary": "source MP4 retained outside Git; OCR text only committed",
                }
            )
    cap.release()
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]], sample_step_seconds: int) -> None:
    by_record = Counter(row["record_id"] for row in rows)
    by_candidate = Counter(row["meter_label_candidate"] for row in rows)
    candidate_rows = [row for row in rows if row["meter_label_candidate"] == "yes"]
    lines = [
        "# Overlay Measurement P2 Acquired OCR Probe",
        "",
        "Owner: Dan Fredriksen",
        "Scope: preflighted Release 02 P2 source MP4s acquired outside Git",
        "Status: bounded OCR triage artifact; no derived media committed",
        "",
        "## Purpose",
        "",
        "This artifact records a display-focused local OCR probe over the preflighted P2 Release 02 videos after source acquisition outside the repository. It is a triage layer for telemetry-like display text, not a frame-level absence proof.",
        "",
        "## Summary",
        "",
        f"- Cases probed: `{len(by_record)}`",
        f"- Sample step: `{sample_step_seconds}` seconds",
        f"- OCR rows: `{len(rows)}`",
        f"- Meter-label candidate rows: `{len(candidate_rows)}`",
    ]
    for status, count in sorted(by_candidate.items()):
        lines.append(f"- `{status}` rows: `{count}`")
    lines.extend(
        [
            "",
            "## Case Coverage",
            "",
            "| Record ID | OCR rows |",
            "|---|---:|",
        ]
    )
    for record_id, count in sorted(by_record.items()):
        lines.append(f"| `{record_id}` | `{count}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "OCR text can be noisy on compressed public sensor-display footage. Candidate rows require manual frame/crop review before classification. Non-candidate rows do not prove absence of telemetry labels.",
            "",
            "Supporting table:",
            "",
            "- `research/ufo-overlay-measurement-p2-acquired-ocr-probe.csv`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OCR over acquired preflighted P2 overlay targets.")
    parser.add_argument("--acquisition", type=Path, default=DEFAULT_ACQUISITION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--sample-step-seconds", type=int, default=30)
    parser.add_argument("--tesseract-cmd", default="tesseract")
    parser.add_argument("--psm", default="11")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_step_seconds <= 0:
        raise SystemExit("--sample-step-seconds must be positive")
    rows: list[dict[str, str]] = []
    for record in read_csv(args.acquisition):
        record_rows = analyze_record(record, args.sample_step_seconds, args.tesseract_cmd, args.psm)
        rows.extend(record_rows)
        print(f"Probed {record['record_id']} with {len(record_rows)} OCR rows")
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows, args.sample_step_seconds)
    print(f"Wrote {len(rows)} OCR probe rows to {args.output}")
    print(f"Wrote OCR probe summary to {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
