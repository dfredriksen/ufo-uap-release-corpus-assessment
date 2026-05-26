from __future__ import annotations

import csv
from pathlib import Path

from build_ufo_overlay_p2_source_preflight import DEFAULT_OUTPUT, DEFAULT_SUMMARY, FIELDNAMES


EXPECTED_RECORD_IDS = {
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


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing P2 source preflight CSV: {path}")
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
            raise SystemExit(f"Empty {field} in P2 preflight row {row_id}")


def validate_rows(rows: list[dict[str, str]]) -> None:
    actual = {row["record_id"] for row in rows}
    if actual != EXPECTED_RECORD_IDS:
        raise SystemExit(f"Unexpected P2 preflight record IDs: {sorted(actual)}")

    for row in rows:
        row_id = row["record_id"]
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
        if row["priority_band"] != "P2":
            raise SystemExit(f"Unexpected priority band for {row_id}: {row['priority_band']}")
        if row["current_lane_status"] not in {"metadata_only_unclassified", "source_preflighted_not_acquired"}:
            raise SystemExit(f"Unexpected lane status for {row_id}: {row['current_lane_status']}")
        if row["page_fetch_status"] != "http_200":
            raise SystemExit(f"Unexpected page fetch status for {row_id}: {row['page_fetch_status']}")
        if row["mp4_head_status"] != "http_200":
            raise SystemExit(f"Unexpected MP4 HEAD status for {row_id}: {row['mp4_head_status']}")
        if not row["embedded_public_mp4_url"].startswith("https://"):
            raise SystemExit(f"Unexpected embedded MP4 URL for {row_id}: {row['embedded_public_mp4_url']}")
        if row["source_acquisition_status"] != "embedded_public_mp4_found_not_downloaded":
            raise SystemExit(f"Unexpected source acquisition status for {row_id}: {row['source_acquisition_status']}")
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
        raise SystemExit(f"Missing P2 source preflight summary: {DEFAULT_SUMMARY}")
    text = DEFAULT_SUMMARY.read_text(encoding="utf-8")
    required_terms = [
        "P2 source pages checked: `9`",
        "embedded_public_mp4_found_not_downloaded",
        "not overlay findings",
        "retained outside the repo",
        "ufo-overlay-measurement-p2-source-preflight.csv",
    ]
    for term in required_terms:
        if term not in text:
            raise SystemExit(f"Missing required P2 source preflight text: {term}")


def main() -> int:
    rows = read_rows(DEFAULT_OUTPUT)
    validate_rows(rows)
    validate_summary()
    print(f"Validated P2 source preflight with {len(rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
