from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-p2-local-ocr-probe.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-p2-local-ocr-probe.md"

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


EXPECTED_COUNTS = {
    "DOW-UAP-PR27": 40,
    "DOW-UAP-PR35": 4,
    "DOW-UAP-PR38": 16,
    "DOW-UAP-PR40": 12,
    "DOW-UAP-PR42": 40,
    "DOW-UAP-PR49": 16,
}

CONTROLLED_CANDIDATE_VALUES = {"yes", "no", "not_run"}
CONTROLLED_ROIS = {
    "center_reticle",
    "upper_display_strip",
    "lower_display_strip",
    "right_display_strip",
    "source_missing",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing P2 OCR probe CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDNAMES:
            raise SystemExit(f"Unexpected columns in {path}: {reader.fieldnames}")
        rows = list(reader)
    if not rows:
        raise SystemExit(f"No rows in {path}")
    return rows


def require_nonempty(row: dict[str, str], fields: list[str], row_id: str) -> None:
    for field in fields:
        if not row.get(field, "").strip():
            raise SystemExit(f"Empty {field} in P2 OCR row {row_id}")


def validate_rows(rows: list[dict[str, str]]) -> None:
    counts = Counter(row["record_id"] for row in rows)
    if dict(counts) != EXPECTED_COUNTS:
        raise SystemExit(f"Unexpected P2 OCR coverage: {dict(counts)}")

    candidate_count = 0
    for row in rows:
        row_id = f"{row['record_id']}:{row['second']}:{row['roi']}"
        require_nonempty(
            row,
            [
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
                "meter_label_candidate",
                "source_media_boundary",
            ],
            row_id,
        )
        if row["roi"] not in CONTROLLED_ROIS:
            raise SystemExit(f"Unexpected ROI in {row_id}: {row['roi']}")
        if row["meter_label_candidate"] not in CONTROLLED_CANDIDATE_VALUES:
            raise SystemExit(f"Unexpected candidate value in {row_id}: {row['meter_label_candidate']}")
        if row["sample_step_seconds"] != "30":
            raise SystemExit(f"Unexpected sample step in {row_id}: {row['sample_step_seconds']}")
        if row["source_exists_at_run"] != "yes":
            raise SystemExit(f"P2 committed probe should record successful local source access for {row_id}")
        if "source MP4 retained outside Git" not in row["source_media_boundary"]:
            raise SystemExit(f"Source-media boundary missing in {row_id}")
        if row["meter_label_candidate"] == "yes":
            candidate_count += 1
            if not row["candidate_rule"].strip():
                raise SystemExit(f"Candidate row lacks rule: {row_id}")

    if candidate_count != 0:
        raise SystemExit(f"P2 local OCR probe has unreviewed candidate rows: {candidate_count}")


def validate_summary() -> None:
    if not DEFAULT_SUMMARY.exists():
        raise SystemExit(f"Missing P2 OCR probe summary: {DEFAULT_SUMMARY}")
    text = DEFAULT_SUMMARY.read_text(encoding="utf-8")
    required_terms = [
        "P2 residual rows with local source paths",
        "Meter-label candidate rows: `0`",
        "not a frame-level absence proof",
        "does not cover P2 rows whose source videos are not yet localized",
    ]
    for term in required_terms:
        if term not in text:
            raise SystemExit(f"Missing required P2 OCR summary text: {term}")


def main() -> int:
    rows = read_rows(DEFAULT_OUTPUT)
    validate_rows(rows)
    validate_summary()
    print(f"Validated P2 local OCR probe with {len(rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
