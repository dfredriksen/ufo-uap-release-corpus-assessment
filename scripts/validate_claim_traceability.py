from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACEABILITY = ROOT / "research" / "ufo-claim-traceability.csv"
EXPECTED_COLUMNS = ["claim", "paper_section", "support_artifact", "claim_type", "status"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the claim traceability table.")
    parser.add_argument("--path", type=Path, default=DEFAULT_TRACEABILITY)
    parser.add_argument("--expected-rows", type=int, default=8)
    args = parser.parse_args()

    with args.path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit(f"{args.path} has no data rows")

    columns = list(rows[0].keys())
    if columns != EXPECTED_COLUMNS:
        raise SystemExit(f"{args.path} columns {columns!r} do not match expected {EXPECTED_COLUMNS!r}")

    if len(rows) != args.expected_rows:
        raise SystemExit(f"{args.path} has {len(rows)} data rows, expected {args.expected_rows}")

    for idx, row in enumerate(rows, start=1):
        for column in EXPECTED_COLUMNS:
            if not row.get(column):
                raise SystemExit(f"{args.path} row {idx} has empty value for {column!r}")

    print(f"Validated {args.path} with {len(rows)} rows and {len(columns)} columns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
