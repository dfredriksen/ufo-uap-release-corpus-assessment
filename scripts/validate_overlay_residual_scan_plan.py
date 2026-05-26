from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from build_ufo_overlay_residual_scan_plan import (
    DEFAULT_AUDIT,
    DEFAULT_CLASSIFICATION,
    DEFAULT_P1_ACQUISITION,
    DEFAULT_P1_REVIEW,
    DEFAULT_P2_PROBE,
    DEFAULT_P2_SOURCE_ACQUISITION,
    DEFAULT_P2_SOURCE_PREFLIGHT,
    DEFAULT_P2_ACQUIRED_REVIEW,
    DEFAULT_RESIDUAL_SOURCE_PREFLIGHT,
    DEFAULT_RESIDUAL_LOCAL_REVIEW,
    DEFAULT_RESIDUAL_REMOTE_REVIEW,
    DEFAULT_OUTPUT,
    DEFAULT_SUMMARY,
    FIELDNAMES,
    build_rows,
    load_classified_status,
    load_p1_local_sources,
    load_p1_review_status,
    load_p2_probe_status,
    load_p2_source_acquisition,
    load_p2_acquired_review_status,
    load_p2_source_preflight,
    load_residual_source_preflight,
    load_residual_local_review_status,
    load_residual_remote_review_status,
    read_csv,
    write_csv,
    write_summary,
)


CONTROLLED_PRIORITY_BANDS = {"P1", "P2", "P3", "P4", "P5"}
CONTROLLED_STATUSES = {
    "metadata_only_unclassified",
    "classified_negative_control:no_matching_label",
    "classified_positive_overlay_candidate",
    "bounded_p1_review_false_ocr_candidate",
    "bounded_p1_review_no_meter_candidate",
    "bounded_p2_local_ocr_no_candidate",
    "bounded_p2_local_ocr_candidate_requires_review",
    "source_preflighted_not_acquired",
    "bounded_p2_acquired_ocr_no_meter_candidate",
    "bounded_p2_acquired_ocr_false_ocr_candidate",
    "bounded_residual_local_ocr_no_meter_candidate",
    "bounded_residual_local_ocr_false_ocr_candidate",
    "bounded_residual_remote_ocr_no_meter_candidate",
    "bounded_residual_remote_ocr_false_ocr_candidate",
}

EXPECTED_P1_REVIEWED_STATUSES = {
    "DOW-UAP-PR052": "bounded_p1_review_no_meter_candidate",
    "DOW-UAP-PR058": "bounded_p1_review_false_ocr_candidate",
    "DOW-UAP-PR069": "bounded_p1_review_no_meter_candidate",
    "DOW-UAP-PR073": "bounded_p1_review_no_meter_candidate",
}

EXPECTED_P2_LOCAL_OCR_STATUSES = {
    "DOW-UAP-PR27": "bounded_p2_local_ocr_no_candidate",
    "DOW-UAP-PR35": "bounded_p2_local_ocr_no_candidate",
    "DOW-UAP-PR38": "bounded_p2_local_ocr_no_candidate",
    "DOW-UAP-PR40": "bounded_p2_local_ocr_no_candidate",
    "DOW-UAP-PR42": "bounded_p2_local_ocr_no_candidate",
    "DOW-UAP-PR49": "bounded_p2_local_ocr_no_candidate",
}

EXPECTED_P2_SOURCE_PREFLIGHTED_STATUSES = {
    "DOW-UAP-PR055",
    "DOW-UAP-PR057A",
    "DOW-UAP-PR057B",
    "DOW-UAP-PR062",
    "DOW-UAP-PR074",
    "DOW-UAP-PR079",
    "DOW-UAP-PR083",
    "DOW-UAP-PR088",
    "DOW-UAP-PR097",
}

EXPECTED_P2_ACQUIRED_REVIEW_STATUSES = {
    "DOW-UAP-PR055": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR057A": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR057B": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR062": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR074": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR079": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR083": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR088": "bounded_p2_acquired_ocr_no_meter_candidate",
    "DOW-UAP-PR097": "bounded_p2_acquired_ocr_false_ocr_candidate",
}

EXPECTED_RESIDUAL_SOURCE_PREFLIGHTED_COUNT = 0

EXPECTED_RESIDUAL_LOCAL_REVIEW_STATUSES = {
    "DOW-UAP-PR19": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR21": "bounded_residual_local_ocr_false_ocr_candidate",
    "DOW-UAP-PR22": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR23": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR26": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR28": "bounded_residual_local_ocr_false_ocr_candidate",
    "DOW-UAP-PR29": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR37": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR39": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR41": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR43": "bounded_residual_local_ocr_false_ocr_candidate",
    "DOW-UAP-PR46": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR47": "bounded_residual_local_ocr_no_meter_candidate",
    "DOW-UAP-PR48": "bounded_residual_local_ocr_false_ocr_candidate",
}

EXPECTED_RESIDUAL_REMOTE_FALSE_CANDIDATE_STATUSES = {
    "DOW-UAP-PR060",
    "DOW-UAP-PR061",
    "DOW-UAP-PR067",
    "DOW-UAP-PR090",
    "DOW-UAP-PR095",
    "DOW-UAP-PR096",
}

EXPECTED_RESIDUAL_REMOTE_REVIEWED_COUNT = 36


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDNAMES:
            raise SystemExit(f"Unexpected columns in {path}: {reader.fieldnames}")
        return list(reader)


def require_nonempty(row: dict[str, str], fields: list[str], row_id: str) -> None:
    for field in fields:
        if not row.get(field, "").strip():
            raise SystemExit(f"Empty {field} in residual row {row_id}")


def validate_rows(rows: list[dict[str, str]]) -> None:
    if not rows:
        raise SystemExit("Residual scan plan has no rows")
    seen: set[str] = set()
    positives = {"P1": 0, "P2": 0, "P3": 0, "P4": 0, "P5": 0}
    by_record: dict[str, dict[str, str]] = {}
    for row in rows:
        row_id = row["residual_id"]
        if row_id in seen:
            raise SystemExit(f"Duplicate residual_id: {row_id}")
        seen.add(row_id)
        by_record[row["record_id"]] = row
        require_nonempty(
            row,
            [
                "priority_rank",
                "residual_id",
                "record_id",
                "release_tag",
                "dvids_id",
                "dvids_url",
                "matched_terms",
                "priority_band",
                "priority_reason",
                "current_lane_status",
                "source_availability_class",
                "recommended_scan_mode",
                "recommended_crop_strategy",
                "publication_boundary",
                "next_action",
            ],
            row_id,
        )
        if row["priority_band"] not in CONTROLLED_PRIORITY_BANDS:
            raise SystemExit(f"Unexpected priority band in {row_id}: {row['priority_band']}")
        if row["current_lane_status"] not in CONTROLLED_STATUSES:
            raise SystemExit(f"Unexpected current lane status in {row_id}: {row['current_lane_status']}")
        if row["current_lane_status"] == "classified_positive_overlay_candidate":
            if "physical measurement" not in row["publication_boundary"]:
                raise SystemExit(f"Positive publication boundary does not preserve physical-claim caveat in {row_id}")
        elif row["current_lane_status"].startswith("bounded_p1_review"):
            if "not an exhaustive all-frame absence claim" not in row["publication_boundary"]:
                raise SystemExit(f"P1 bounded-review boundary is too broad in {row_id}")
            if row["priority_band"] != "P3":
                raise SystemExit(f"P1 bounded-review follow-up should be P3 in {row_id}")
            if not row["local_source_hint"].strip():
                raise SystemExit(f"P1 bounded-review row lacks source-acquisition hint in {row_id}")
        elif row["current_lane_status"].startswith("bounded_p2_local_ocr"):
            if "not an exhaustive frame-level absence claim" not in row["publication_boundary"]:
                raise SystemExit(f"P2 bounded-OCR boundary is too broad in {row_id}")
            if row["priority_band"] != "P3":
                raise SystemExit(f"P2 bounded-OCR follow-up should be P3 in {row_id}")
            if not row["local_source_hint"].strip():
                raise SystemExit(f"P2 bounded-OCR row lacks source-acquisition hint in {row_id}")
        elif row["current_lane_status"] == "source_preflighted_not_acquired":
            if "Public source URL is localized" not in row["publication_boundary"]:
                raise SystemExit(f"P2 source-preflight boundary is missing in {row_id}")
            if row["priority_band"] != "P2":
                raise SystemExit(f"P2 source-preflight row should remain P2 in {row_id}")
            if row["source_availability_class"] != "embedded_public_mp4_preflighted_not_downloaded":
                raise SystemExit(f"Unexpected source availability class in {row_id}: {row['source_availability_class']}")
            if not row["video_name"].endswith(".mp4"):
                raise SystemExit(f"P2 source-preflight row lacks localized MP4 filename in {row_id}: {row['video_name']}")
        elif row["current_lane_status"].startswith("bounded_p2_acquired_ocr"):
            if "not an exhaustive frame-level absence claim" not in row["publication_boundary"]:
                raise SystemExit(f"P2 acquired-OCR boundary is too broad in {row_id}")
            if row["priority_band"] != "P3":
                raise SystemExit(f"P2 acquired-OCR follow-up should be P3 in {row_id}")
            if not row["local_source_hint"].strip():
                raise SystemExit(f"P2 acquired-OCR row lacks source-acquisition hint in {row_id}")
        elif row["current_lane_status"].startswith("bounded_residual_local_ocr"):
            if "not an exhaustive frame-level absence claim" not in row["publication_boundary"]:
                raise SystemExit(f"Residual local-OCR boundary is too broad in {row_id}")
            if row["priority_band"] != "P3":
                raise SystemExit(f"Residual local-OCR follow-up should be P3 in {row_id}")
            if not row["local_source_hint"].strip():
                raise SystemExit(f"Residual local-OCR row lacks source-acquisition hint in {row_id}")
        elif row["current_lane_status"].startswith("bounded_residual_remote_ocr"):
            if "not an exhaustive frame-level absence claim" not in row["publication_boundary"]:
                raise SystemExit(f"Residual remote-OCR boundary is too broad in {row_id}")
            if "not retained or hashed" not in row["publication_boundary"]:
                raise SystemExit(f"Residual remote-OCR boundary omits source-retention caveat in {row_id}")
            if row["priority_band"] != "P3":
                raise SystemExit(f"Residual remote-OCR follow-up should be P3 in {row_id}")
            if row["source_availability_class"] != "remote_public_mp4_sampled_not_retained":
                raise SystemExit(f"Residual remote-OCR row has wrong availability class in {row_id}")
            if not row["video_name"].endswith(".mp4"):
                raise SystemExit(f"Residual remote-OCR row lacks localized MP4 filename in {row_id}: {row['video_name']}")
        elif "visible label" not in row["publication_boundary"]:
            raise SystemExit(f"Publication boundary does not preserve visible-label caveat in {row_id}")
        positives[row["priority_band"]] += 1

    for record_id, expected_status in EXPECTED_P1_REVIEWED_STATUSES.items():
        row = by_record.get(record_id)
        if not row:
            raise SystemExit(f"Missing reviewed P1 residual row: {record_id}")
        if row["current_lane_status"] != expected_status:
            raise SystemExit(
                f"Reviewed P1 status drift for {record_id}: {row['current_lane_status']} != {expected_status}"
            )

    for record_id, expected_status in EXPECTED_P2_LOCAL_OCR_STATUSES.items():
        row = by_record.get(record_id)
        if not row:
            raise SystemExit(f"Missing local-OCR P2 residual row: {record_id}")
        if row["current_lane_status"] != expected_status:
            raise SystemExit(
                f"P2 local OCR status drift for {record_id}: {row['current_lane_status']} != {expected_status}"
            )

    for record_id in EXPECTED_P2_SOURCE_PREFLIGHTED_STATUSES:
        row = by_record.get(record_id)
        if not row:
            raise SystemExit(f"Missing preflighted P2 residual row: {record_id}")
        if row["current_lane_status"] not in {
            "source_preflighted_not_acquired",
            "bounded_p2_acquired_ocr_no_meter_candidate",
            "bounded_p2_acquired_ocr_false_ocr_candidate",
        }:
            raise SystemExit(f"P2 source-preflight status drift for {record_id}: {row['current_lane_status']}")

    for record_id, expected_status in EXPECTED_P2_ACQUIRED_REVIEW_STATUSES.items():
        row = by_record.get(record_id)
        if not row:
            raise SystemExit(f"Missing acquired-review P2 residual row: {record_id}")
        if row["current_lane_status"] != expected_status:
            raise SystemExit(
                f"P2 acquired-review status drift for {record_id}: {row['current_lane_status']} != {expected_status}"
            )

    residual_preflighted = [
        row
        for row in rows
        if row["current_lane_status"] == "source_preflighted_not_acquired"
    ]
    if len(residual_preflighted) != EXPECTED_RESIDUAL_SOURCE_PREFLIGHTED_COUNT:
        raise SystemExit(f"Unexpected residual source-preflighted count: {len(residual_preflighted)}")
    for row in residual_preflighted:
        if row["priority_band"] != "P2":
            raise SystemExit(f"Residual source-preflighted row should be P2: {row['record_id']}")
        if row["source_availability_class"] != "embedded_public_mp4_preflighted_not_downloaded":
            raise SystemExit(f"Residual source-preflighted row has wrong availability class: {row['record_id']}")

    residual_remote_reviewed = [
        row
        for row in rows
        if row["current_lane_status"].startswith("bounded_residual_remote_ocr")
    ]
    if len(residual_remote_reviewed) != EXPECTED_RESIDUAL_REMOTE_REVIEWED_COUNT:
        raise SystemExit(f"Unexpected residual remote-reviewed count: {len(residual_remote_reviewed)}")
    false_remote = {
        row["record_id"]
        for row in residual_remote_reviewed
        if row["current_lane_status"] == "bounded_residual_remote_ocr_false_ocr_candidate"
    }
    if false_remote != EXPECTED_RESIDUAL_REMOTE_FALSE_CANDIDATE_STATUSES:
        raise SystemExit(f"Unexpected residual remote false-candidate records: {sorted(false_remote)}")

    for record_id, expected_status in EXPECTED_RESIDUAL_LOCAL_REVIEW_STATUSES.items():
        row = by_record.get(record_id)
        if not row:
            raise SystemExit(f"Missing residual-local review row: {record_id}")
        if row["current_lane_status"] != expected_status:
            raise SystemExit(
                f"Residual local review status drift for {record_id}: {row['current_lane_status']} != {expected_status}"
            )

    if any(row["current_lane_status"] == "metadata_only_unclassified" for row in rows):
        raise SystemExit("No residual row should remain metadata_only_unclassified after source preflight/local/remote OCR review")

    if positives["P1"] != 0:
        raise SystemExit(f"P1 queue should be fully advanced; got P1={positives['P1']}")
    if positives["P2"] != 0:
        raise SystemExit(f"P2 queue should be fully advanced by remote OCR triage; got P2={positives['P2']}")
    if sum(positives.values()) != len(rows):
        raise SystemExit("Priority-band counts do not sum to row count")


def compare_rows(committed: list[dict[str, str]], generated: list[dict[str, str]]) -> None:
    if committed != generated:
        raise SystemExit("Residual scan plan CSV is stale; rerun scripts/build_ufo_overlay_residual_scan_plan.py")


def compare_summary(committed: Path, generated: Path) -> None:
    committed_lines = committed.read_text(encoding="utf-8").splitlines()
    generated_lines = generated.read_text(encoding="utf-8").splitlines()
    if committed_lines != generated_lines:
        raise SystemExit("Residual scan plan summary is stale; rerun scripts/build_ufo_overlay_residual_scan_plan.py")


def main() -> int:
    if not DEFAULT_OUTPUT.exists():
        raise SystemExit(f"Missing residual scan plan CSV: {DEFAULT_OUTPUT}")
    if not DEFAULT_SUMMARY.exists():
        raise SystemExit(f"Missing residual scan plan summary: {DEFAULT_SUMMARY}")

    committed_rows = read_rows(DEFAULT_OUTPUT)
    validate_rows(committed_rows)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_root = Path(temp_dir)
        generated_csv = temp_root / "ufo-overlay-measurement-residual-scan-plan.csv"
        generated_md = temp_root / "ufo-overlay-measurement-residual-scan-plan.md"
        generated_rows = build_rows(
            read_csv(DEFAULT_AUDIT),
            load_classified_status(DEFAULT_CLASSIFICATION),
            load_p1_review_status(DEFAULT_P1_REVIEW),
            load_p1_local_sources(DEFAULT_P1_ACQUISITION),
            load_p2_probe_status(DEFAULT_P2_PROBE),
            load_p2_source_preflight(DEFAULT_P2_SOURCE_PREFLIGHT),
            load_p2_source_acquisition(DEFAULT_P2_SOURCE_ACQUISITION),
            load_p2_acquired_review_status(DEFAULT_P2_ACQUIRED_REVIEW),
            load_residual_source_preflight(DEFAULT_RESIDUAL_SOURCE_PREFLIGHT),
            load_residual_local_review_status(DEFAULT_RESIDUAL_LOCAL_REVIEW),
            load_residual_remote_review_status(DEFAULT_RESIDUAL_REMOTE_REVIEW),
        )
        write_csv(generated_csv, generated_rows)
        write_summary(generated_md, generated_rows)
        compare_rows(committed_rows, read_rows(generated_csv))
        compare_summary(DEFAULT_SUMMARY, generated_md)

    print(f"Validated residual scan plan with {len(committed_rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
