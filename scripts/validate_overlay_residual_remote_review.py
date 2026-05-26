from __future__ import annotations

import csv
import tempfile
from collections import Counter
from pathlib import Path

from build_ufo_overlay_residual_remote_review import (
    DEFAULT_OCR,
    FIELDNAMES as REVIEW_FIELDS,
    build_rows,
    write_csv,
    write_summary,
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
OCR = DOCS / "ufo-overlay-measurement-residual-remote-ocr-probe.csv"
OCR_MD = DOCS / "ufo-overlay-measurement-residual-remote-ocr-probe.md"
REVIEW = DOCS / "ufo-overlay-measurement-residual-remote-review.csv"
REVIEW_MD = DOCS / "ufo-overlay-measurement-residual-remote-review.md"

OCR_FIELDS = [
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

EXPECTED_RECORDS = 36
EXPECTED_OCR_ROWS = 1096
EXPECTED_CANDIDATE_ROWS = 8
EXPECTED_FALSE_CANDIDATE_RECORDS = {
    "DOW-UAP-PR060": 3,
    "DOW-UAP-PR061": 1,
    "DOW-UAP-PR067": 1,
    "DOW-UAP-PR090": 1,
    "DOW-UAP-PR095": 1,
    "DOW-UAP-PR096": 1,
}
CONTROLLED_ROIS = {
    "center_reticle",
    "upper_display_strip",
    "lower_display_strip",
    "right_display_strip",
}


def read_rows(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing artifact: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != fields:
            raise SystemExit(f"Unexpected columns in {path}: {reader.fieldnames}")
        rows = list(reader)
    if not rows:
        raise SystemExit(f"No rows in {path}")
    return rows


def require_nonempty(row: dict[str, str], fields: list[str], row_id: str) -> None:
    for field in fields:
        if not row.get(field, "").strip():
            raise SystemExit(f"Empty {field} in {row_id}")


def validate_ocr() -> tuple[Counter[str], Counter[str]]:
    rows = read_rows(OCR, OCR_FIELDS)
    if len(rows) != EXPECTED_OCR_ROWS:
        raise SystemExit(f"Unexpected residual remote OCR row count: {len(rows)}")
    counts = Counter(row["record_id"] for row in rows)
    candidate_counts = Counter(row["record_id"] for row in rows if row["meter_label_candidate"] == "yes")
    if len(counts) != EXPECTED_RECORDS:
        raise SystemExit(f"Unexpected residual remote record count: {len(counts)}")
    if sum(candidate_counts.values()) != EXPECTED_CANDIDATE_ROWS:
        raise SystemExit(f"Unexpected residual remote OCR candidate count: {sum(candidate_counts.values())}")
    if dict(candidate_counts) != EXPECTED_FALSE_CANDIDATE_RECORDS:
        raise SystemExit(f"Unexpected residual remote candidate distribution: {dict(candidate_counts)}")

    for row in rows:
        row_id = f"{row['record_id']}:{row['second']}:{row['roi']}"
        require_nonempty(
            row,
            [
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
                "meter_label_candidate",
                "source_media_boundary",
            ],
            row_id,
        )
        if row["release_tag"] != "release-02":
            raise SystemExit(f"Unexpected release tag in {row_id}: {row['release_tag']}")
        if row["sample_step_seconds"] != "30":
            raise SystemExit(f"Unexpected sample step in {row_id}: {row['sample_step_seconds']}")
        if row["frame_extract_status"] != "ok":
            raise SystemExit(f"Unexpected frame extraction status in {row_id}: {row['frame_extract_status']}")
        if row["roi"] not in CONTROLLED_ROIS:
            raise SystemExit(f"Unexpected ROI in {row_id}: {row['roi']}")
        if row["meter_label_candidate"] not in {"yes", "no"}:
            raise SystemExit(f"Unexpected candidate flag in {row_id}: {row['meter_label_candidate']}")
        if "not retained or redistributed" not in row["source_media_boundary"]:
            raise SystemExit(f"Source boundary missing in {row_id}")
        candidate_image = row["candidate_image_not_redistributed"]
        if row["meter_label_candidate"] == "yes":
            if not candidate_image.startswith("research/ufo-derived/"):
                raise SystemExit(f"Candidate image path must stay in ignored derived tree for {row_id}")
            if Path(candidate_image).is_absolute():
                raise SystemExit(f"Candidate image path should be repo-relative for {row_id}")
        elif candidate_image:
            raise SystemExit(f"Non-candidate row has candidate image path in {row_id}")
    return counts, candidate_counts


def validate_review(ocr_counts: Counter[str], candidate_counts: Counter[str]) -> None:
    rows = {row["record_id"]: row for row in read_rows(REVIEW, REVIEW_FIELDS)}
    if set(rows) != set(ocr_counts):
        raise SystemExit("Residual remote review record IDs do not match OCR probe")
    false_rows = 0
    no_candidate_rows = 0
    for record_id, row in rows.items():
        require_nonempty(row, REVIEW_FIELDS, record_id)
        if row["ocr_rows"] != str(ocr_counts[record_id]):
            raise SystemExit(f"Review OCR count drift for {record_id}: {row['ocr_rows']}")
        if row["ocr_meter_candidate_rows"] != str(candidate_counts[record_id]):
            raise SystemExit(f"Review candidate count drift for {record_id}: {row['ocr_meter_candidate_rows']}")
        if row["physical_claim_status"] != "not_promoted":
            raise SystemExit(f"Physical claim status changed for {record_id}")
        if "source MP4 not retained or hashed" not in row["evidence_boundary"]:
            raise SystemExit(f"Remote review boundary omits source-acquisition caveat for {record_id}")
        if "not an exhaustive all-frame absence claim" not in row["evidence_boundary"]:
            raise SystemExit(f"Remote review boundary too broad for {record_id}")
        support = ROOT / row["support_note"]
        if not support.exists():
            raise SystemExit(f"Missing support artifact for {record_id}: {support}")
        if candidate_counts[record_id]:
            false_rows += 1
            if row["classification_effect"] != "bounded_residual_remote_ocr_false_ocr_candidate":
                raise SystemExit(f"Unexpected false-candidate status for {record_id}")
            if "rejected" not in row["meter_label_result"]:
                raise SystemExit(f"False-candidate row lacks rejection note for {record_id}")
        else:
            no_candidate_rows += 1
            if row["classification_effect"] != "bounded_residual_remote_ocr_no_meter_candidate":
                raise SystemExit(f"Unexpected no-candidate status for {record_id}")
    if false_rows != len(EXPECTED_FALSE_CANDIDATE_RECORDS):
        raise SystemExit(f"Unexpected false-candidate review row count: {false_rows}")
    if no_candidate_rows != EXPECTED_RECORDS - len(EXPECTED_FALSE_CANDIDATE_RECORDS):
        raise SystemExit(f"Unexpected no-candidate review row count: {no_candidate_rows}")


def validate_markdown() -> None:
    for path in [OCR_MD, REVIEW_MD]:
        if not path.exists():
            raise SystemExit(f"Missing markdown artifact: {path}")
    ocr_text = OCR_MD.read_text(encoding="utf-8")
    review_text = REVIEW_MD.read_text(encoding="utf-8")
    for term in [
        "Cases probed: `36`",
        "OCR/probe rows: `1096`",
        "Meter-label candidate rows: `8`",
        "does not retain source MP4s",
    ]:
        if term not in ocr_text:
            raise SystemExit(f"Missing residual remote OCR text: {term}")
    for term in [
        "No new meter-label candidate was promoted",
        "source MP4 not retained or hashed",
        "does not replace source acquisition",
        "not an exhaustive all-frame absence claim",
    ]:
        if term not in review_text:
            raise SystemExit(f"Missing residual remote review text: {term}")


def compare_rows(committed: list[dict[str, str]], generated: list[dict[str, str]]) -> None:
    if committed != generated:
        raise SystemExit("Residual remote review CSV is stale; rerun scripts/build_ufo_overlay_residual_remote_review.py")


def compare_summary(committed: Path, generated: Path) -> None:
    committed_lines = committed.read_text(encoding="utf-8").splitlines()
    generated_lines = generated.read_text(encoding="utf-8").splitlines()
    if committed_lines != generated_lines:
        raise SystemExit("Residual remote review summary is stale; rerun scripts/build_ufo_overlay_residual_remote_review.py")


def validate_generated_review() -> None:
    committed_rows = read_rows(REVIEW, REVIEW_FIELDS)
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        generated_csv = temp_root / "ufo-overlay-measurement-residual-remote-review.csv"
        generated_md = temp_root / "ufo-overlay-measurement-residual-remote-review.md"
        generated_rows = build_rows(DEFAULT_OCR)
        write_csv(generated_csv, generated_rows)
        write_summary(generated_md, generated_rows)
        compare_rows(committed_rows, read_rows(generated_csv, REVIEW_FIELDS))
        compare_summary(REVIEW_MD, generated_md)


def main() -> int:
    ocr_counts, candidate_counts = validate_ocr()
    validate_review(ocr_counts, candidate_counts)
    validate_markdown()
    validate_generated_review()
    print("Validated residual remote OCR review for 36 records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
