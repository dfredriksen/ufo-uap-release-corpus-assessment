from __future__ import annotations

import csv
from pathlib import Path

from build_ufo_overlay_p1_source_preflight import DEFAULT_OUTPUT, FIELDNAMES
from build_ufo_overlay_residual_scan_plan import DEFAULT_OUTPUT as RESIDUAL_PLAN


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise SystemExit(f"Missing header in {path}")
        return list(reader)


def read_preflight(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != FIELDNAMES:
            raise SystemExit(f"Unexpected columns in {path}: {reader.fieldnames}")
        return list(reader)


def require_nonempty(row: dict[str, str], fields: list[str], row_id: str) -> None:
    for field in fields:
        if not row.get(field, "").strip():
            raise SystemExit(f"Empty {field} in P1 preflight row {row_id}")


def main() -> int:
    residual_rows = read_csv(RESIDUAL_PLAN)
    expected_ids = {
        row["record_id"]
        for row in residual_rows
        if row.get("priority_band") == "P1" or row.get("current_lane_status", "").startswith("bounded_p1_review")
    }
    preflight_rows = read_preflight(DEFAULT_OUTPUT)
    actual_ids = {row["record_id"] for row in preflight_rows}

    if actual_ids != expected_ids:
        raise SystemExit(f"P1 preflight record IDs do not match residual plan. expected={sorted(expected_ids)} actual={sorted(actual_ids)}")

    for row in preflight_rows:
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
                "source_acquisition_status",
                "recommended_next_action",
                "accessed_utc",
            ],
            row_id,
        )
        if row["priority_band"] != "P1":
            if not row["current_lane_status"].startswith("bounded_p1_review") or row["priority_band"] != "P3":
                raise SystemExit(f"Unexpected priority/status pair for {row_id}: {row['priority_band']} / {row['current_lane_status']}")
        if row["page_fetch_status"] != "http_200":
            raise SystemExit(f"Unexpected page fetch status for {row_id}: {row['page_fetch_status']}")
        if row["mp4_head_status"] != "http_200":
            raise SystemExit(f"Unexpected MP4 HEAD status for {row_id}: {row['mp4_head_status']}")
        if not row["embedded_public_mp4_url"].startswith("https://"):
            raise SystemExit(f"Unexpected embedded MP4 URL for {row_id}: {row['embedded_public_mp4_url']}")
        try:
            if int(row["mp4_content_length"]) <= 0:
                raise ValueError
        except ValueError:
            raise SystemExit(f"Invalid mp4_content_length for {row_id}: {row['mp4_content_length']}") from None
        if "outside the repo" not in row["recommended_next_action"]:
            raise SystemExit(f"Recommended next action does not preserve source-media boundary for {row_id}")

    print(f"Validated P1 source preflight with {len(preflight_rows)} rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
