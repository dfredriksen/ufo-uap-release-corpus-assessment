from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
OCR = DOCS / "ufo-overlay-measurement-residual-local-ocr-probe.csv"
OCR_MD = DOCS / "ufo-overlay-measurement-residual-local-ocr-probe.md"
REVIEW = DOCS / "ufo-overlay-measurement-residual-local-review.csv"
REVIEW_MD = DOCS / "ufo-overlay-measurement-residual-local-review.md"

OCR_FIELDS = [
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

REVIEW_FIELDS = [
    "record_id",
    "release_tag",
    "source_video",
    "review_basis",
    "ocr_rows",
    "ocr_meter_candidate_rows",
    "visible_overlay_elements",
    "meter_label_result",
    "classification_effect",
    "physical_claim_status",
    "evidence_boundary",
    "support_note",
]

EXPECTED = {
    "DOW-UAP-PR19": ("4", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR21": ("4", "1", "bounded_residual_local_ocr_false_ocr_candidate"),
    "DOW-UAP-PR22": ("4", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR23": ("4", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR26": ("8", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR28": ("12", "1", "bounded_residual_local_ocr_false_ocr_candidate"),
    "DOW-UAP-PR29": ("4", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR37": ("4", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR39": ("4", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR41": ("16", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR43": ("4", "1", "bounded_residual_local_ocr_false_ocr_candidate"),
    "DOW-UAP-PR46": ("4", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR47": ("16", "0", "bounded_residual_local_ocr_no_meter_candidate"),
    "DOW-UAP-PR48": ("16", "2", "bounded_residual_local_ocr_false_ocr_candidate"),
}

CONTROLLED_ROIS = {"center_reticle", "upper_display_strip", "lower_display_strip", "right_display_strip"}


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


def validate_ocr() -> None:
    rows = read_rows(OCR, OCR_FIELDS)
    counts = Counter(row["record_id"] for row in rows)
    candidate_counts = Counter(row["record_id"] for row in rows if row["meter_label_candidate"] == "yes")
    if set(counts) != set(EXPECTED):
        raise SystemExit(f"Unexpected OCR record IDs: {sorted(counts)}")
    for record_id, (ocr_rows, candidates, _) in EXPECTED.items():
        if str(counts[record_id]) != ocr_rows:
            raise SystemExit(f"Unexpected OCR row count for {record_id}: {counts[record_id]}")
        if str(candidate_counts[record_id]) != candidates:
            raise SystemExit(f"Unexpected OCR candidate count for {record_id}: {candidate_counts[record_id]}")
    if sum(candidate_counts.values()) != 5:
        raise SystemExit("Expected exactly 5 residual-local OCR candidate rows")
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
        if row["source_exists_at_run"] != "yes":
            raise SystemExit(f"Residual local OCR row lacks source access: {row_id}")
        if row["roi"] not in CONTROLLED_ROIS:
            raise SystemExit(f"Unexpected ROI in {row_id}: {row['roi']}")
        if row["sample_step_seconds"] != "30":
            raise SystemExit(f"Unexpected sample step in {row_id}: {row['sample_step_seconds']}")
        if "source MP4 retained outside Git" not in row["source_media_boundary"]:
            raise SystemExit(f"Source boundary missing in {row_id}")


def validate_review() -> None:
    rows = {row["record_id"]: row for row in read_rows(REVIEW, REVIEW_FIELDS)}
    if set(rows) != set(EXPECTED):
        raise SystemExit(f"Unexpected review record IDs: {sorted(rows)}")
    for record_id, (ocr_rows, candidates, effect) in EXPECTED.items():
        row = rows[record_id]
        require_nonempty(row, REVIEW_FIELDS, record_id)
        if row["ocr_rows"] != ocr_rows:
            raise SystemExit(f"Unexpected review OCR row count for {record_id}: {row['ocr_rows']}")
        if row["ocr_meter_candidate_rows"] != candidates:
            raise SystemExit(f"Unexpected review candidate count for {record_id}: {row['ocr_meter_candidate_rows']}")
        if row["classification_effect"] != effect:
            raise SystemExit(f"Unexpected classification effect for {record_id}: {row['classification_effect']}")
        if row["physical_claim_status"] != "not_promoted":
            raise SystemExit(f"Physical claim status changed for {record_id}")
        if "not an exhaustive all-frame absence claim" not in row["evidence_boundary"]:
            raise SystemExit(f"Review boundary too broad for {record_id}")
    false_rows = [row for row in rows.values() if row["classification_effect"].endswith("false_ocr_candidate")]
    if len(false_rows) != 4:
        raise SystemExit("Expected four false-candidate review rows")


def validate_markdown() -> None:
    for path in [OCR_MD, REVIEW_MD]:
        if not path.exists():
            raise SystemExit(f"Missing markdown artifact: {path}")
    text = REVIEW_MD.read_text(encoding="utf-8")
    for term in [
        "No new meter-label candidate was promoted",
        "False OCR candidate",
        "not an exhaustive all-frame absence claim",
        "direction-marker, reticle, terrain/edge, or texture OCR noise",
    ]:
        if term not in text:
            raise SystemExit(f"Missing residual local review text: {term}")


def main() -> int:
    validate_ocr()
    validate_review()
    validate_markdown()
    print("Validated residual local OCR review for 14 records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
