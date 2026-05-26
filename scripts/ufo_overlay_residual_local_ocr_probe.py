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
DEFAULT_RESIDUAL_PLAN = DOCS / "ufo-overlay-measurement-residual-scan-plan.csv"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-residual-local-ocr-probe.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-residual-local-ocr-probe.md"

FIELDNAMES = [
    "record_id",
    "release_tag",
    "video_name",
    "source_path_not_redistributed",
    "source_exists_at_run",
    "source_bytes",
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


def targets(residual_plan: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in read_csv(residual_plan):
        if clean(row.get("current_lane_status")) != "metadata_only_unclassified":
            continue
        if not clean(row.get("local_source_hint")):
            continue
        rows.append(row)
    return rows


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


def analyze_target(target: dict[str, str], sample_step_seconds: int, tesseract_cmd: str, psm: str) -> list[dict[str, str]]:
    source_path = Path(clean(target.get("local_source_hint")))
    if not source_path.exists():
        return [
            {
                "record_id": clean(target.get("record_id")),
                "release_tag": clean(target.get("release_tag")),
                "video_name": clean(target.get("video_name")),
                "source_path_not_redistributed": public_source_hint(source_path),
                "source_exists_at_run": "no",
                "source_bytes": "",
                "opencv_width": "",
                "opencv_height": "",
                "opencv_fps": "",
                "opencv_frames": "",
                "opencv_duration_seconds": "",
                "sample_step_seconds": str(sample_step_seconds),
                "second": "",
                "frame_index": "",
                "roi": "source_missing",
                "ocr_text": "",
                "normalized_text": "",
                "meter_label_candidate": "not_run",
                "candidate_rule": "",
                "source_media_boundary": "source MP4 is not redistributed; missing source prevents local OCR probe",
            }
        ]

    cap = cv2.VideoCapture(str(source_path))
    if not cap.isOpened():
        raise SystemExit(f"Could not open source video: {source_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration = frame_count / fps if fps else 0.0
    source_bytes = source_path.stat().st_size

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
                    "record_id": clean(target.get("record_id")),
                    "release_tag": clean(target.get("release_tag")),
                    "video_name": clean(target.get("video_name")),
                    "source_path_not_redistributed": public_source_hint(source_path),
                    "source_exists_at_run": "yes",
                    "source_bytes": str(source_bytes),
                    "opencv_width": str(width),
                    "opencv_height": str(height),
                    "opencv_fps": f"{fps:.3f}",
                    "opencv_frames": str(frame_count),
                    "opencv_duration_seconds": f"{duration:.3f}",
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
        "# Overlay Measurement Residual Local OCR Probe",
        "",
        "Owner: Dan Fredriksen",
        "Scope: remaining metadata-only residual rows with local source paths",
        "Status: bounded OCR triage artifact; no derived media committed",
        "",
        "## Purpose",
        "",
        "This artifact records a display-focused local OCR probe over remaining metadata-only residual rows that already had non-redistributed local source paths. It is a triage layer for telemetry-like display text, not a frame-level absence proof.",
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
            "- `research/ufo-overlay-measurement-residual-local-ocr-probe.csv`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OCR over remaining local-source residual overlay targets.")
    parser.add_argument("--residual-plan", type=Path, default=DEFAULT_RESIDUAL_PLAN)
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
    for target in targets(args.residual_plan):
        target_rows = analyze_target(target, args.sample_step_seconds, args.tesseract_cmd, args.psm)
        rows.extend(target_rows)
        print(f"Probed {target['record_id']} with {len(target_rows)} OCR rows")
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows, args.sample_step_seconds)
    print(f"Wrote {len(rows)} OCR probe rows to {args.output}")
    print(f"Wrote OCR probe summary to {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
