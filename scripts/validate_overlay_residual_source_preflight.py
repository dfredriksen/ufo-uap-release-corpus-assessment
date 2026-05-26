from __future__ import annotations

import csv
from pathlib import Path

from build_ufo_overlay_residual_source_preflight import DEFAULT_OUTPUT, DEFAULT_SUMMARY, FIELDNAMES


EXPECTED_COUNT = 36


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing residual source preflight CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDNAMES:
            raise SystemExit(f"Unexpected columns in {path}: {reader.fieldnames}")
        rows = list(reader)
    if len(rows) != EXPECTED_COUNT:
        raise SystemExit(f"Expected {EXPECTED_COUNT} residual source preflight rows, found {len(rows)}")
    return rows


def require_nonempty(row: dict[str, str], fields: list[str], row_id: str) -> None:
    for field in fields:
        if not row.get(field, "").strip():
            raise SystemExit(f"Empty {field} in residual preflight row {row_id}")


def validate_rows(rows: list[dict[str, str]]) -> None:
    seen: set[str] = set()
    for row in rows:
        row_id = row["record_id"]
        if row_id in seen:
            raise SystemExit(f"Duplicate residual preflight record_id: {row_id}")
        seen.add(row_id)
        require_nonempty(
            row,
            [
                "residual_id",
                "record_id",
                "release_tag",
                "dvids_id",
                "dvids_url",
                "matched_terms",
                "priority_band",
                "current_lane_status",
                "page_fetch_status",
                "resolved_page_url",
                "dvids_title",
                "dvids_filename",
                "dvids_duration",
                "embedded_public_mp4_url",
                "mp4_head_status",
                "mp4_content_length",
                "mp4_content_length_mb",
                "source_acquisition_status",
                "recommended_next_action",
                "accessed_utc",
            ],
            row_id,
        )
        if row["release_tag"] != "release-02":
            raise SystemExit(f"Unexpected release tag for residual preflight row {row_id}: {row['release_tag']}")
        if row["priority_band"] not in {"P2", "P3"}:
            raise SystemExit(f"Unexpected residual preflight priority band for {row_id}: {row['priority_band']}")
        if row["current_lane_status"] not in {
            "metadata_only_unclassified",
            "source_preflighted_not_acquired",
            "bounded_residual_remote_ocr_no_meter_candidate",
            "bounded_residual_remote_ocr_false_ocr_candidate",
        }:
            raise SystemExit(f"Unexpected residual preflight status for {row_id}: {row['current_lane_status']}")
        if row["page_fetch_status"] != "http_200":
            raise SystemExit(f"Unexpected page fetch status for {row_id}: {row['page_fetch_status']}")
        if row["mp4_head_status"] != "http_200":
            raise SystemExit(f"Unexpected MP4 HEAD status for {row_id}: {row['mp4_head_status']}")
        if row["source_acquisition_status"] != "embedded_public_mp4_found_not_downloaded":
            raise SystemExit(f"Unexpected source status for {row_id}: {row['source_acquisition_status']}")
        if not row["embedded_public_mp4_url"].startswith("https://"):
            raise SystemExit(f"Unexpected MP4 URL for {row_id}: {row['embedded_public_mp4_url']}")
        try:
            if int(row["mp4_content_length"]) <= 0:
                raise ValueError
            if float(row["mp4_content_length_mb"]) <= 0:
                raise ValueError
        except ValueError:
            raise SystemExit(f"Invalid MP4 content length for {row_id}") from None
        if "outside the repo" not in row["recommended_next_action"]:
            raise SystemExit(f"Recommended next action loses source-media boundary for {row_id}")


def validate_summary() -> None:
    if not DEFAULT_SUMMARY.exists():
        raise SystemExit(f"Missing residual source preflight summary: {DEFAULT_SUMMARY}")
    text = DEFAULT_SUMMARY.read_text(encoding="utf-8")
    for term in [
        "Residual source pages checked: `36`",
        "Release 02 rows: `36`",
        "embedded_public_mp4_found_not_downloaded",
        "not overlay findings",
        "does not download or redistribute source media",
    ]:
        if term not in text:
            raise SystemExit(f"Missing residual source preflight text: {term}")


def main() -> int:
    rows = read_rows(DEFAULT_OUTPUT)
    validate_rows(rows)
    validate_summary()
    print(f"Validated residual source preflight with {len(rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
