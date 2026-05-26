from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
ACQUISITION = DOCS / "ufo-overlay-measurement-p2-source-acquisition.csv"
ACQUISITION_MD = DOCS / "ufo-overlay-measurement-p2-source-acquisition.md"
OCR = DOCS / "ufo-overlay-measurement-p2-acquired-ocr-probe.csv"
OCR_MD = DOCS / "ufo-overlay-measurement-p2-acquired-ocr-probe.md"
REVIEW = DOCS / "ufo-overlay-measurement-p2-acquired-review.csv"
REVIEW_MD = DOCS / "ufo-overlay-measurement-p2-acquired-review.md"

ACQUISITION_FIELDS = [
    "record_id",
    "release_tag",
    "dvids_id",
    "dvids_url",
    "matched_terms",
    "source_video",
    "source_url",
    "local_path_not_redistributed",
    "source_exists_at_run",
    "source_bytes",
    "expected_bytes",
    "sha256",
    "opencv_width",
    "opencv_height",
    "opencv_fps",
    "opencv_frames",
    "opencv_duration_seconds",
    "source_media_boundary",
]

OCR_FIELDS = [
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
    "DOW-UAP-PR055": {
        "source_video": "DOD_111719732.mp4",
        "bytes": "17638967",
        "sha256": "39948c8102f6bdeba4baeff7239ca83a810eb7d5ee686934234965a49f8571a7",
        "ocr_rows": "8",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR057A": {
        "source_video": "DOD_111719752.mp4",
        "bytes": "32245123",
        "sha256": "43d114fa153fa86523832e35bc9731883a67dd6bc9ea1d34c7afd5a83fe5e570",
        "ocr_rows": "12",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR057B": {
        "source_video": "DOD_111719752.mp4",
        "bytes": "32245123",
        "sha256": "43d114fa153fa86523832e35bc9731883a67dd6bc9ea1d34c7afd5a83fe5e570",
        "ocr_rows": "12",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR062": {
        "source_video": "DOD_111719847.mp4",
        "bytes": "152419204",
        "sha256": "951b0da58cab77ef2aa2de357df6126cccc9c03823072189f6d83c8da7e5f850",
        "ocr_rows": "40",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR074": {
        "source_video": "DOD_111720775.mp4",
        "bytes": "77412815",
        "sha256": "d0b8800146dfc84e7d1fd40ff400c5d813cb8139dc7cfcf9b9e1ea189c6e8b47",
        "ocr_rows": "40",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR079": {
        "source_video": "DOD_111720899.mp4",
        "bytes": "68997343",
        "sha256": "88279ac587d31a8b1129426eea91175f193015a420e3774966ec3ab4e013ceb3",
        "ocr_rows": "36",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR083": {
        "source_video": "DOD_111720883.mp4",
        "bytes": "49591522",
        "sha256": "25da235c0b86f451f6a82e4589459707ad0897533d9aa8e4c8c57b099bb55b63",
        "ocr_rows": "40",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR088": {
        "source_video": "DOD_111720843.mp4",
        "bytes": "65470569",
        "sha256": "0e961dd8c5d4417c8a7319411674a5a3057fae0fd28c341aa2829b6cfc396a96",
        "ocr_rows": "40",
        "ocr_candidates": "0",
        "classification_effect": "bounded_acquired_ocr_no_meter_candidate",
    },
    "DOW-UAP-PR097": {
        "source_video": "DOD_111719813.mp4",
        "bytes": "102201405",
        "sha256": "0a3fa02a7ce357649d1a5d5b4bebc0a323b64101981fa10997eb0b579c710e90",
        "ocr_rows": "40",
        "ocr_candidates": "1",
        "classification_effect": "bounded_acquired_ocr_false_ocr_candidate",
    },
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


def by_record(rows: list[dict[str, str]], path: Path) -> dict[str, dict[str, str]]:
    mapped = {row["record_id"]: row for row in rows}
    if set(mapped) != set(EXPECTED):
        raise SystemExit(f"Unexpected record IDs in {path}: {sorted(mapped)}")
    return mapped


def require_nonempty(row: dict[str, str], fields: list[str], row_id: str) -> None:
    for field in fields:
        if not row.get(field, "").strip():
            raise SystemExit(f"Empty {field} in {row_id}")


def validate_acquisition() -> None:
    rows = by_record(read_rows(ACQUISITION, ACQUISITION_FIELDS), ACQUISITION)
    for record_id, expected in EXPECTED.items():
        row = rows[record_id]
        require_nonempty(row, ACQUISITION_FIELDS, record_id)
        if row["source_video"] != expected["source_video"]:
            raise SystemExit(f"Unexpected source video for {record_id}: {row['source_video']}")
        if row["source_bytes"] != expected["bytes"] or row["expected_bytes"] != expected["bytes"]:
            raise SystemExit(f"Unexpected source bytes for {record_id}")
        if row["sha256"] != expected["sha256"]:
            raise SystemExit(f"Unexpected SHA-256 for {record_id}: {row['sha256']}")
        if row["source_exists_at_run"] != "yes":
            raise SystemExit(f"Source was not present at manifest build for {record_id}")
        if "source MP4 retained outside Git" not in row["source_media_boundary"]:
            raise SystemExit(f"Source-media boundary missing for {record_id}")
        if str(ROOT).lower() in row["local_path_not_redistributed"].lower():
            raise SystemExit(f"Source path appears under repo root for {record_id}")


def validate_ocr() -> None:
    rows = read_rows(OCR, OCR_FIELDS)
    counts = Counter(row["record_id"] for row in rows)
    candidate_counts = Counter(row["record_id"] for row in rows if row["meter_label_candidate"] == "yes")
    for record_id, expected in EXPECTED.items():
        if str(counts[record_id]) != expected["ocr_rows"]:
            raise SystemExit(f"Unexpected OCR row count for {record_id}: {counts[record_id]}")
        if str(candidate_counts[record_id]) != expected["ocr_candidates"]:
            raise SystemExit(f"Unexpected OCR candidate count for {record_id}: {candidate_counts[record_id]}")
    for row in rows:
        record_id = row["record_id"]
        require_nonempty(
            row,
            [
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
                "meter_label_candidate",
                "source_media_boundary",
            ],
            f"{record_id}:{row['second']}:{row['roi']}",
        )
        if row["roi"] not in CONTROLLED_ROIS:
            raise SystemExit(f"Unexpected ROI for {record_id}: {row['roi']}")
        if row["sample_step_seconds"] != "30":
            raise SystemExit(f"Unexpected sample step for {record_id}: {row['sample_step_seconds']}")
        if row["source_sha256"] != EXPECTED[record_id]["sha256"]:
            raise SystemExit(f"OCR row SHA drift for {record_id}")
        if "source MP4 retained outside Git" not in row["source_media_boundary"]:
            raise SystemExit(f"OCR source boundary missing for {record_id}")

    candidate_rows = [row for row in rows if row["meter_label_candidate"] == "yes"]
    if len(candidate_rows) != 1 or candidate_rows[0]["record_id"] != "DOW-UAP-PR097":
        raise SystemExit("Expected exactly one PR097 OCR candidate row")


def validate_review() -> None:
    rows = by_record(read_rows(REVIEW, REVIEW_FIELDS), REVIEW)
    for record_id, expected in EXPECTED.items():
        row = rows[record_id]
        require_nonempty(row, REVIEW_FIELDS, record_id)
        if row["source_video"] != expected["source_video"]:
            raise SystemExit(f"Unexpected review source video for {record_id}: {row['source_video']}")
        if row["ocr_rows"] != expected["ocr_rows"]:
            raise SystemExit(f"Unexpected review OCR row count for {record_id}: {row['ocr_rows']}")
        if row["ocr_meter_candidate_rows"] != expected["ocr_candidates"]:
            raise SystemExit(f"Unexpected review candidate count for {record_id}: {row['ocr_meter_candidate_rows']}")
        if row["classification_effect"] != expected["classification_effect"]:
            raise SystemExit(f"Unexpected classification effect for {record_id}: {row['classification_effect']}")
        if row["physical_claim_status"] != "not_promoted":
            raise SystemExit(f"Physical claim status changed for {record_id}")
        if "not an exhaustive all-frame absence claim" not in row["evidence_boundary"]:
            raise SystemExit(f"Review boundary too broad for {record_id}")
    if "N-marker/texture OCR noise" not in rows["DOW-UAP-PR097"]["meter_label_result"]:
        raise SystemExit("PR097 false-candidate rationale missing")


def validate_markdown() -> None:
    for path in [ACQUISITION_MD, OCR_MD, REVIEW_MD]:
        if not path.exists():
            raise SystemExit(f"Missing markdown artifact: {path}")
    review_text = REVIEW_MD.read_text(encoding="utf-8")
    for term in [
        "False OCR candidate",
        "not a visible meter-suffix label",
        "not an exhaustive all-frame absence claim",
        "No new meter-label candidate was promoted",
    ]:
        if term not in review_text:
            raise SystemExit(f"Missing review text: {term}")


def main() -> int:
    validate_acquisition()
    validate_ocr()
    validate_review()
    validate_markdown()
    print("Validated P2 source acquisition and acquired OCR review for 9 records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
