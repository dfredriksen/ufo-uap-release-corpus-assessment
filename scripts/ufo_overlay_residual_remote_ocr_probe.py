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
DEFAULT_PREFLIGHT = DOCS / "ufo-overlay-measurement-residual-source-preflight.csv"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-residual-remote-ocr-probe.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-residual-remote-ocr-probe.md"
DEFAULT_CANDIDATE_DIR = DOCS / "ufo-derived" / "overlay-measurement-audit" / "residual-remote-candidate-review"

FIELDNAMES = [
    "record_id",
    "release_tag",
    "dvids_id",
    "dvids_filename",
    "source_url",
    "expected_bytes",
    "dvids_duration",
    "sample_step_seconds",
    "second",
    "roi",
    "frame_extract_status",
    "frame_width",
    "frame_height",
    "ocr_text",
    "normalized_text",
    "meter_label_candidate",
    "candidate_rule",
    "candidate_image_not_redistributed",
    "source_media_boundary",
]

METER_PATTERN = re.compile(
    r"(?<![A-Z0-9])(?:<\s*)?\d{1,3}\s*M\b|\bM\s*\d{1,3}(?![A-Z0-9])|(?<![A-Z0-9])SM(?![A-Z0-9])",
    re.IGNORECASE,
)


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_text(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9<]+", " ", value).strip().upper()


def parse_duration_seconds(value: str) -> int:
    parts = [int(part) for part in clean(value).split(":") if part.isdigit()]
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds
    if len(parts) == 1:
        return parts[0]
    return 0


def sample_seconds(duration_seconds: int, sample_step_seconds: int) -> list[int]:
    if duration_seconds <= 0:
        return [0]
    return list(range(0, duration_seconds + 1, sample_step_seconds)) or [0]


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


def extract_remote_frame(source_url: str, second: int, ffmpeg_cmd: str, timeout_seconds: int) -> tuple[str, Path | None]:
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
        frame_path = Path(temp.name)
    frame_path.unlink(missing_ok=True)
    command = [
        ffmpeg_cmd,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        str(second),
        "-i",
        source_url,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        str(frame_path),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        frame_path.unlink(missing_ok=True)
        return "timeout", None
    if result.returncode != 0 or not frame_path.exists() or frame_path.stat().st_size == 0:
        frame_path.unlink(missing_ok=True)
        detail = "failed"
        if result.stderr.strip():
            detail = re.sub(r"\s+", " ", result.stderr.strip())[:120]
        return f"ffmpeg_error:{detail}", None
    return "ok", frame_path


def candidate_image_path(candidate_dir: Path, row: dict[str, str], roi_name: str) -> Path:
    safe_second = clean(row["second"]).replace(".", "_")
    name = f"{row['record_id']}_{safe_second}s_{roi_name}.png"
    return candidate_dir / name


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def analyze_record(
    record: dict[str, str],
    sample_step_seconds: int,
    ffmpeg_cmd: str,
    tesseract_cmd: str,
    psm: str,
    frame_timeout_seconds: int,
    candidate_dir: Path | None,
) -> list[dict[str, str]]:
    duration_seconds = parse_duration_seconds(clean(record.get("dvids_duration")))
    rows: list[dict[str, str]] = []
    for second in sample_seconds(duration_seconds, sample_step_seconds):
        status, frame_path = extract_remote_frame(
            clean(record.get("embedded_public_mp4_url")),
            second,
            ffmpeg_cmd,
            frame_timeout_seconds,
        )
        if frame_path is None:
            rows.append(
                {
                    "record_id": clean(record.get("record_id")),
                    "release_tag": clean(record.get("release_tag")),
                    "dvids_id": clean(record.get("dvids_id")),
                    "dvids_filename": clean(record.get("dvids_filename")),
                    "source_url": clean(record.get("embedded_public_mp4_url")),
                    "expected_bytes": clean(record.get("mp4_content_length")),
                    "dvids_duration": clean(record.get("dvids_duration")),
                    "sample_step_seconds": str(sample_step_seconds),
                    "second": str(second),
                    "roi": "frame_extract",
                    "frame_extract_status": status,
                    "frame_width": "",
                    "frame_height": "",
                    "ocr_text": "",
                    "normalized_text": "",
                    "meter_label_candidate": "not_run",
                    "candidate_rule": "",
                    "candidate_image_not_redistributed": "",
                    "source_media_boundary": "public source MP4 sampled remotely; source MP4 not retained or redistributed",
                }
            )
            continue
        try:
            frame = cv2.imread(str(frame_path))
            if frame is None:
                rows.append(
                    {
                        "record_id": clean(record.get("record_id")),
                        "release_tag": clean(record.get("release_tag")),
                        "dvids_id": clean(record.get("dvids_id")),
                        "dvids_filename": clean(record.get("dvids_filename")),
                        "source_url": clean(record.get("embedded_public_mp4_url")),
                        "expected_bytes": clean(record.get("mp4_content_length")),
                        "dvids_duration": clean(record.get("dvids_duration")),
                        "sample_step_seconds": str(sample_step_seconds),
                        "second": str(second),
                        "roi": "frame_decode",
                        "frame_extract_status": "opencv_decode_failed",
                        "frame_width": "",
                        "frame_height": "",
                        "ocr_text": "",
                        "normalized_text": "",
                        "meter_label_candidate": "not_run",
                        "candidate_rule": "",
                        "candidate_image_not_redistributed": "",
                        "source_media_boundary": "public source MP4 sampled remotely; source MP4 not retained or redistributed",
                    }
                )
                continue
            height, width = frame.shape[:2]
            for roi_name, roi in rois(frame).items():
                text = run_tesseract(prepare_for_ocr(roi), tesseract_cmd, psm)
                normalized = normalize_text(text)
                candidate = bool(METER_PATTERN.search(normalized))
                candidate_path = ""
                base_row = {
                    "record_id": clean(record.get("record_id")),
                    "release_tag": clean(record.get("release_tag")),
                    "dvids_id": clean(record.get("dvids_id")),
                    "dvids_filename": clean(record.get("dvids_filename")),
                    "source_url": clean(record.get("embedded_public_mp4_url")),
                    "expected_bytes": clean(record.get("mp4_content_length")),
                    "dvids_duration": clean(record.get("dvids_duration")),
                    "sample_step_seconds": str(sample_step_seconds),
                    "second": str(second),
                }
                if candidate and candidate_dir is not None:
                    candidate_dir.mkdir(parents=True, exist_ok=True)
                    path = candidate_image_path(candidate_dir, base_row, roi_name)
                    cv2.imwrite(str(path), roi)
                    candidate_path = repo_relative(path)
                rows.append(
                    {
                        **base_row,
                        "roi": roi_name,
                        "frame_extract_status": "ok",
                        "frame_width": str(width),
                        "frame_height": str(height),
                        "ocr_text": " ".join(text.split()),
                        "normalized_text": normalized,
                        "meter_label_candidate": "yes" if candidate else "no",
                        "candidate_rule": METER_PATTERN.pattern if candidate else "",
                        "candidate_image_not_redistributed": candidate_path,
                        "source_media_boundary": "public source MP4 sampled remotely; source MP4 not retained or redistributed",
                    }
                )
        finally:
            frame_path.unlink(missing_ok=True)
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
    by_status = Counter(row["frame_extract_status"] for row in rows)
    candidate_rows = [row for row in rows if row["meter_label_candidate"] == "yes"]
    rows_with_frames = [row for row in rows if row["frame_extract_status"] == "ok"]
    lines = [
        "# Overlay Measurement Residual Remote OCR Probe",
        "",
        "Owner: Dan Fredriksen",
        "Scope: Release 02 residual rows with preflighted public MP4 URLs but no retained local source MP4",
        "Status: bounded remote-frame OCR triage artifact; no source MP4 or derived media committed",
        "",
        "## Purpose",
        "",
        "This artifact records a display-focused OCR probe over residual Release 02 public MP4 URLs using temporary remote frame extraction. It is a triage layer for telemetry-like display text, not a source-acquisition manifest and not a frame-level absence proof.",
        "",
        "## Summary",
        "",
        f"- Cases probed: `{len(by_record)}`",
        f"- Sample step: `{sample_step_seconds}` seconds",
        f"- OCR/probe rows: `{len(rows)}`",
        f"- Successful ROI OCR rows: `{len(rows_with_frames)}`",
        f"- Meter-label candidate rows: `{len(candidate_rows)}`",
    ]
    for status, count in sorted(by_candidate.items()):
        lines.append(f"- `{status}` candidate rows: `{count}`")
    lines.extend(["", "Frame extraction status:"])
    for status, count in sorted(by_status.items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(
        [
            "",
            "## Case Coverage",
            "",
            "| Record ID | Probe rows | Candidate rows |",
            "|---|---:|---:|",
        ]
    )
    candidate_counts = Counter(row["record_id"] for row in candidate_rows)
    for record_id, count in sorted(by_record.items()):
        lines.append(f"| `{record_id}` | `{count}` | `{candidate_counts.get(record_id, 0)}` |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This probe samples public source URLs directly and does not retain source MP4s. Candidate rows require manual crop/frame review before classification. Non-candidate rows do not prove absence of telemetry labels, and remote sampling does not replace source acquisition, hashing, or all-frame review.",
            "",
            "Supporting table:",
            "",
            "- `research/ufo-overlay-measurement-residual-remote-ocr-probe.csv`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run remote-frame OCR over residual preflighted public MP4 URLs.")
    parser.add_argument("--preflight", type=Path, default=DEFAULT_PREFLIGHT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--sample-step-seconds", type=int, default=30)
    parser.add_argument("--ffmpeg-cmd", default="ffmpeg")
    parser.add_argument("--tesseract-cmd", default="tesseract")
    parser.add_argument("--psm", default="11")
    parser.add_argument("--frame-timeout-seconds", type=int, default=45)
    parser.add_argument("--record-id", action="append", default=[])
    parser.add_argument("--max-records", type=int, default=0)
    parser.add_argument("--candidate-dir", type=Path, default=DEFAULT_CANDIDATE_DIR)
    parser.add_argument("--no-candidate-images", action="store_true")
    return parser.parse_args()


def selected_records(preflight: Path, requested_ids: list[str], max_records: int) -> list[dict[str, str]]:
    requested = set(requested_ids)
    records = [
        row
        for row in read_csv(preflight)
        if clean(row.get("source_acquisition_status")) == "embedded_public_mp4_found_not_downloaded"
        and clean(row.get("embedded_public_mp4_url"))
        and (not requested or clean(row.get("record_id")) in requested)
    ]
    records.sort(key=lambda row: (float(clean(row.get("mp4_content_length_mb")) or 0.0), clean(row.get("record_id"))))
    if max_records > 0:
        return records[:max_records]
    return records


def main() -> int:
    args = parse_args()
    if args.sample_step_seconds <= 0:
        raise SystemExit("--sample-step-seconds must be positive")
    if args.frame_timeout_seconds <= 0:
        raise SystemExit("--frame-timeout-seconds must be positive")
    candidate_dir = None if args.no_candidate_images else args.candidate_dir
    rows: list[dict[str, str]] = []
    records = selected_records(args.preflight, args.record_id, args.max_records)
    for record in records:
        record_rows = analyze_record(
            record,
            args.sample_step_seconds,
            args.ffmpeg_cmd,
            args.tesseract_cmd,
            args.psm,
            args.frame_timeout_seconds,
            candidate_dir,
        )
        rows.extend(record_rows)
        candidate_count = sum(1 for row in record_rows if row["meter_label_candidate"] == "yes")
        print(f"Probed {record['record_id']} with {len(record_rows)} rows and {candidate_count} OCR candidates")
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows, args.sample_step_seconds)
    print(f"Wrote {len(rows)} remote OCR rows to {args.output}")
    print(f"Wrote remote OCR summary to {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
