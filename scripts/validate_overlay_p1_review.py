from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
ACQUISITION = DOCS / "ufo-overlay-measurement-p1-source-acquisition.csv"
SAMPLES = DOCS / "ufo-overlay-measurement-p1-quicklook-samples.csv"
REVIEW = DOCS / "ufo-overlay-measurement-p1-review.csv"
REVIEW_MD = DOCS / "ufo-overlay-measurement-p1-review.md"
OCR_PROBE = DOCS / "ufo-overlay-measurement-p1-ocr-probe.csv"
PR059_SURVEY = DOCS / "ufo-overlay-measurement-pr059-label-survey.md"
PR059_INTERVALS = DOCS / "ufo-overlay-measurement-pr059-label-intervals.csv"

ACQUISITION_FIELDS = [
    "case",
    "record_id",
    "video",
    "source_url",
    "dvids_url",
    "local_path_not_redistributed",
    "bytes",
    "sha256",
    "opencv_width",
    "opencv_height",
    "opencv_fps",
    "opencv_frames",
    "opencv_duration_seconds",
    "matched_terms",
]

SAMPLE_FIELDS = [
    "case",
    "record_id",
    "video",
    "second",
    "frame_index",
    "manual_overlay_review_status",
    "notes",
]

REVIEW_FIELDS = [
    "case",
    "record_id",
    "release_tag",
    "source_video",
    "source_bytes",
    "source_sha256",
    "source_url",
    "dvids_url",
    "review_basis",
    "sampled_seconds",
    "sample_count",
    "quicklook_sheet_count",
    "focus_sheet_count",
    "ocr_probe_rows",
    "ocr_meter_candidate_rows",
    "visible_overlay_elements",
    "meter_label_result",
    "classification_effect",
    "physical_claim_status",
    "evidence_boundary",
]

EXPECTED = {
    "PR052": {
        "record_id": "DOW-UAP-PR052",
        "video": "DOD_111719718.mp4",
        "bytes": "513739591",
        "sha256": "e67b3a3b3d863ef88cc8c4e6b73e9c9bff896506a2962956ed70f508fd8815f5",
        "sample_count": "496",
        "quicklook_sheet_count": "25",
        "focus_sheet_count": "42",
        "ocr_probe_rows": "68",
        "ocr_meter_candidate_rows": "0",
        "classification_effect": "quicklook_review_no_meter_candidate",
    },
    "PR058": {
        "record_id": "DOW-UAP-PR058",
        "video": "DOD_111719800.mp4",
        "bytes": "222778312",
        "sha256": "610d6dc9da3c72c6a273e2458962fbef10f7caacf2107f7eb9c567d9b289a2e0",
        "sample_count": "649",
        "quicklook_sheet_count": "33",
        "focus_sheet_count": "55",
        "ocr_probe_rows": "88",
        "ocr_meter_candidate_rows": "1",
        "classification_effect": "quicklook_review_false_ocr_candidate",
    },
    "PR059": {
        "record_id": "DOW-UAP-PR059",
        "video": "DOD_111719809.mp4",
        "bytes": "71526914",
        "sha256": "11698020b966a3b38178f9ab66272f49d4400feb178fb269229009fbb08b3365",
        "sample_count": "292",
        "quicklook_sheet_count": "15",
        "focus_sheet_count": "25",
        "ocr_probe_rows": "40",
        "ocr_meter_candidate_rows": "1",
        "classification_effect": "promoted_positive_overlay_candidate",
    },
    "PR069": {
        "record_id": "DOW-UAP-PR069",
        "video": "DOD_111720700.mp4",
        "bytes": "14735885",
        "sha256": "7e81fd782a5b98af5cb941b6e5cce865f15324dea41b8c4cf4577f3d02c3fd66",
        "sample_count": "30",
        "quicklook_sheet_count": "2",
        "focus_sheet_count": "3",
        "ocr_probe_rows": "4",
        "ocr_meter_candidate_rows": "0",
        "classification_effect": "quicklook_review_no_meter_candidate",
    },
    "PR073": {
        "record_id": "DOW-UAP-PR073",
        "video": "DOD_111720765.mp4",
        "bytes": "2347351",
        "sha256": "19538301dd75d63746d3a3cc2da7cdd0418f0372130984b68030a4bb1eb7f48e",
        "sample_count": "89",
        "quicklook_sheet_count": "5",
        "focus_sheet_count": "8",
        "ocr_probe_rows": "12",
        "ocr_meter_candidate_rows": "0",
        "classification_effect": "quicklook_review_no_meter_candidate",
    },
}

CONTROLLED_CLASSIFICATION_EFFECTS = {
    "promoted_positive_overlay_candidate",
    "quicklook_review_false_ocr_candidate",
    "quicklook_review_no_meter_candidate",
}
CONTROLLED_PHYSICAL_STATUSES = {"not_promoted"}
CONTROLLED_SAMPLE_STATUSES = {"sampled_for_manual_sheet_review"}


def read_rows(path: Path, expected_fields: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_fields:
            raise SystemExit(f"Unexpected columns in {path}: {reader.fieldnames}")
        rows = list(reader)
    if not rows:
        raise SystemExit(f"No rows in {path}")
    return rows


def require_expected_cases(rows: list[dict[str, str]], path: Path) -> dict[str, dict[str, str]]:
    by_case = {row["case"]: row for row in rows}
    if set(by_case) != set(EXPECTED):
        raise SystemExit(f"Unexpected cases in {path}: {sorted(by_case)}")
    return by_case


def require_nonempty(row: dict[str, str], path: Path) -> None:
    for field, value in row.items():
        if not value.strip():
            raise SystemExit(f"Empty {field} in {path} row {row.get('case', '<unknown>')}")


def validate_acquisition() -> None:
    rows = read_rows(ACQUISITION, ACQUISITION_FIELDS)
    by_case = require_expected_cases(rows, ACQUISITION)
    root_text = str(ROOT).lower()
    for case, expected in EXPECTED.items():
        row = by_case[case]
        require_nonempty(row, ACQUISITION)
        if row["record_id"] != expected["record_id"]:
            raise SystemExit(f"Unexpected record_id for {case}: {row['record_id']}")
        if row["video"] != expected["video"]:
            raise SystemExit(f"Unexpected video for {case}: {row['video']}")
        if row["bytes"] != expected["bytes"]:
            raise SystemExit(f"Unexpected byte count for {case}: {row['bytes']}")
        if row["sha256"] != expected["sha256"]:
            raise SystemExit(f"Unexpected SHA-256 for {case}: {row['sha256']}")
        if not row["source_url"].startswith("https://"):
            raise SystemExit(f"Unexpected source URL for {case}: {row['source_url']}")
        if "dvidshub.net/video/" not in row["dvids_url"]:
            raise SystemExit(f"Unexpected DVIDS URL for {case}: {row['dvids_url']}")
        if str(row["local_path_not_redistributed"]).lower().startswith(root_text):
            raise SystemExit(f"Local source path appears to be under repo root for {case}")


def validate_samples() -> None:
    rows = read_rows(SAMPLES, SAMPLE_FIELDS)
    counts = Counter(row["case"] for row in rows)
    for case, expected in EXPECTED.items():
        if str(counts[case]) != expected["sample_count"]:
            raise SystemExit(f"Unexpected sample count for {case}: {counts[case]}")
    for row in rows:
        if row["case"] not in EXPECTED:
            raise SystemExit(f"Unexpected sample case: {row['case']}")
        if row["manual_overlay_review_status"] not in CONTROLLED_SAMPLE_STATUSES:
            raise SystemExit(f"Unexpected sample status for {row['case']}: {row['manual_overlay_review_status']}")
        if "source media not redistributed" not in row["notes"]:
            raise SystemExit(f"Sample note loses source-media boundary for {row['case']}")


def validate_review() -> None:
    rows = read_rows(REVIEW, REVIEW_FIELDS)
    by_case = require_expected_cases(rows, REVIEW)
    for case, expected in EXPECTED.items():
        row = by_case[case]
        require_nonempty(row, REVIEW)
        if row["record_id"] != expected["record_id"]:
            raise SystemExit(f"Unexpected review record_id for {case}: {row['record_id']}")
        if row["source_video"] != expected["video"]:
            raise SystemExit(f"Unexpected review source video for {case}: {row['source_video']}")
        if row["source_bytes"] != expected["bytes"]:
            raise SystemExit(f"Unexpected review byte count for {case}: {row['source_bytes']}")
        if row["source_sha256"] != expected["sha256"]:
            raise SystemExit(f"Unexpected review SHA-256 for {case}: {row['source_sha256']}")
        if row["sample_count"] != expected["sample_count"]:
            raise SystemExit(f"Unexpected review sample count for {case}: {row['sample_count']}")
        if row["quicklook_sheet_count"] != expected["quicklook_sheet_count"]:
            raise SystemExit(f"Unexpected quicklook sheet count for {case}: {row['quicklook_sheet_count']}")
        if row["focus_sheet_count"] != expected["focus_sheet_count"]:
            raise SystemExit(f"Unexpected focus sheet count for {case}: {row['focus_sheet_count']}")
        if row["ocr_probe_rows"] != expected["ocr_probe_rows"]:
            raise SystemExit(f"Unexpected OCR row count for {case}: {row['ocr_probe_rows']}")
        if row["ocr_meter_candidate_rows"] != expected["ocr_meter_candidate_rows"]:
            raise SystemExit(f"Unexpected OCR candidate count for {case}: {row['ocr_meter_candidate_rows']}")
        if row["classification_effect"] != expected["classification_effect"]:
            raise SystemExit(f"Unexpected classification effect for {case}: {row['classification_effect']}")
        if row["physical_claim_status"] not in CONTROLLED_PHYSICAL_STATUSES:
            raise SystemExit(f"Unexpected physical claim status for {case}: {row['physical_claim_status']}")
        if case == "PR059" and "positive measurement-like overlay candidate" not in row["meter_label_result"]:
            raise SystemExit("PR059 review row does not preserve positive finding")
        if case != "PR059" and "label" not in row["meter_label_result"]:
            raise SystemExit(f"Review result loses meter-label boundary for {case}")
        if "not an exhaustive all-frame OCR pass" not in row["evidence_boundary"] and "public MP4 lacks label dictionary" not in row["evidence_boundary"]:
            raise SystemExit(f"Evidence boundary is too broad for {case}")


def validate_markdown() -> None:
    if not REVIEW_MD.exists():
        raise SystemExit(f"Missing file: {REVIEW_MD}")
    text = REVIEW_MD.read_text(encoding="utf-8")
    required_terms = [
        "one-frame-per-second",
        "not an exhaustive all-frame OCR pass",
        "physical reconstruction",
        "ufo-overlay-measurement-p1-review.csv",
        "PR069",
        "PR073",
        "PR059",
        "Promoted to positive overlay candidate",
    ]
    for term in required_terms:
        if term not in text:
            raise SystemExit(f"Missing required review text: {term}")

    for path in [OCR_PROBE, PR059_SURVEY, PR059_INTERVALS]:
        if not path.exists():
            raise SystemExit(f"Missing supporting P1 review artifact: {path}")


def main() -> int:
    validate_acquisition()
    validate_samples()
    validate_review()
    validate_markdown()
    print("Validated P1 quicklook review for five P1 targets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
