from __future__ import annotations

import argparse
import csv
import re
import subprocess
import tempfile
from pathlib import Path

import cv2


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
DEFAULT_ACQUISITION = DOCS / "ufo-overlay-measurement-p1-source-acquisition.csv"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-p1-ocr-probe.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-p1-ocr-probe.md"

METER_PATTERN = re.compile(r"(\d{1,3}\s*M\b|\bM\s*\d{1,3}|\bSM\b)", re.IGNORECASE)


def read_acquisition(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader)


def normalize_text(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", " ", value).strip().upper()


def focus_crop(frame, case_name: str):
    height, width = frame.shape[:2]
    if case_name == "PR073":
        return frame[int(height * 0.30) : int(height * 0.68), 0:width]
    if case_name == "PR069":
        return frame[int(height * 0.16) : int(height * 0.84), int(width * 0.18) : int(width * 0.82)]
    return frame[int(height * 0.12) : int(height * 0.88), int(width * 0.12) : int(width * 0.88)]


def lower_center_crop(frame):
    height, width = frame.shape[:2]
    return frame[int(height * 0.45) : int(height * 0.90), int(width * 0.20) : int(width * 0.80)]


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


def analyze_case(case: dict[str, str], sample_step_seconds: int, tesseract_cmd: str, psm: str) -> list[dict[str, str]]:
    case_name = case["case"]
    video_path = Path(case["local_path_not_redistributed"])
    if not video_path.exists():
        raise SystemExit(f"Missing source video: {video_path}")
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = frame_count / fps if fps else 0.0
    rows: list[dict[str, str]] = []
    max_second = int(duration)
    for second in range(0, max_second + 1, sample_step_seconds):
        frame_index = int(round(second * fps))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            continue
        rois = {
            "focus_crop": focus_crop(frame, case_name),
            "lower_center_crop": lower_center_crop(frame),
        }
        for roi_name, roi in rois.items():
            text = run_tesseract(prepare_for_ocr(roi), tesseract_cmd, psm)
            normalized = normalize_text(text)
            candidate = bool(METER_PATTERN.search(normalized))
            rows.append(
                {
                    "case": case_name,
                    "record_id": case["record_id"],
                    "video": case["video"],
                    "second": str(second),
                    "frame_index": str(frame_index),
                    "roi": roi_name,
                    "ocr_text": " ".join(text.split()),
                    "normalized_text": normalized,
                    "meter_label_candidate": "yes" if candidate else "no",
                    "candidate_rule": METER_PATTERN.pattern if candidate else "",
                    "tesseract_psm": psm,
                    "sample_step_seconds": str(sample_step_seconds),
                    "source_media_boundary": "source MP4 retained outside Git; OCR text only committed",
                }
            )
    cap.release()
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit(f"No rows to write: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]], sample_step_seconds: int) -> None:
    cases = sorted({row["case"] for row in rows})
    candidate_rows = [row for row in rows if row["meter_label_candidate"] == "yes"]
    lines = [
        "# Overlay Measurement P1 OCR Probe",
        "",
        "Owner: Dan Fredriksen",
        "Scope: optional local OCR triage over P1 residual source MP4s",
        "Status: bounded text-probe artifact",
        "",
        "## Purpose",
        "",
        "This artifact records a local Tesseract OCR probe over sampled P1 residual video crops. It is a triage layer for manual review, not a substitute for frame-level visual validation.",
        "",
        "## Summary",
        "",
        f"- Cases probed: `{len(cases)}`",
        f"- Sample step: `{sample_step_seconds}` seconds",
        f"- OCR rows: `{len(rows)}`",
        f"- Meter-label candidate rows: `{len(candidate_rows)}`",
        "",
        "## Boundary",
        "",
        "OCR text can be noisy on compressed sensor-display footage. Candidate rows require manual frame review before classification. Non-candidate rows do not prove absence of telemetry text.",
        "",
        "Supporting table:",
        "",
        "- `research/ufo-overlay-measurement-p1-ocr-probe.csv`",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded OCR probe over P1 overlay quicklook targets.")
    parser.add_argument("--acquisition", type=Path, default=DEFAULT_ACQUISITION)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--sample-step-seconds", type=int, default=5)
    parser.add_argument("--tesseract-cmd", default="tesseract")
    parser.add_argument("--psm", default="11")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.sample_step_seconds <= 0:
        raise SystemExit("--sample-step-seconds must be positive")
    rows: list[dict[str, str]] = []
    for case in read_acquisition(args.acquisition):
        case_rows = analyze_case(case, args.sample_step_seconds, args.tesseract_cmd, args.psm)
        rows.extend(case_rows)
        print(f"Probed {case['case']} with {len(case_rows)} OCR rows")
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows, args.sample_step_seconds)
    print(f"Wrote {len(rows)} OCR probe rows to {args.output}")
    print(f"Wrote OCR probe summary to {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
