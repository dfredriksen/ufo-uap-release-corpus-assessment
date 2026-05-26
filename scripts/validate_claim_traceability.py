from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRACEABILITY = ROOT / "research" / "ufo-claim-traceability.csv"
DEFAULT_PAPER = ROOT / "paper.md"
EXPECTED_COLUMNS = ["claim", "paper_section", "support_artifact", "claim_type", "status"]
ALLOWED_CLAIM_TYPES = {
    "Local image-plane observation",
    "Source-reported operational context",
    "Pattern / narrative synthesis",
    "Methodological limitation",
    "Tranche-level synthesis",
    "Display-overlay observation",
    "Bounded OCR triage",
}
ALLOWED_STATUSES = {
    "Not physical kinematics",
    "Key values remain report-derived",
    "Needs raw data",
    "Needs raw imagery and timing",
    "Not kinematics",
    "Telemetry and platform data required",
    "No hard new pairing",
    "Not physical measurement",
    "No residual promotion under bounded triage",
    "Falsifiable with source docs/raw telemetry",
}


def load_paper_sections(path: Path) -> set[str]:
    sections: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            match = re.match(r"^#{1,6}\s+Finding(?:s)?\s+([0-9]+)(?:-([0-9]+))?:", line)
            if match:
                start = int(match.group(1))
                end = int(match.group(2) or match.group(1))
                for number in range(start, end + 1):
                    sections.add(f"Finding {number}")
    return sections


def validate_paper_section(value: str, known_sections: set[str]) -> None:
    text = value.strip()
    if text in known_sections:
        return
    match = re.fullmatch(r"Findings?\s+([0-9]+)(?:-([0-9]+))?", text)
    if not match:
        raise SystemExit(f"Unsupported paper_section value: {value!r}")
    start = int(match.group(1))
    end = int(match.group(2) or match.group(1))
    for number in range(start, end + 1):
        if f"Finding {number}" not in known_sections:
            raise SystemExit(f"Paper section {value!r} does not match a finding heading in the paper")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the claim traceability table.")
    parser.add_argument("--path", type=Path, default=DEFAULT_TRACEABILITY)
    parser.add_argument("--paper", type=Path, default=DEFAULT_PAPER)
    parser.add_argument("--min-rows", type=int, default=8)
    args = parser.parse_args()

    with args.path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if not rows:
        raise SystemExit(f"{args.path} has no data rows")

    columns = list(rows[0].keys())
    if columns != EXPECTED_COLUMNS:
        raise SystemExit(f"{args.path} columns {columns!r} do not match expected {EXPECTED_COLUMNS!r}")

    if len(rows) < args.min_rows:
        raise SystemExit(f"{args.path} has {len(rows)} data rows, expected at least {args.min_rows}")

    known_sections = load_paper_sections(args.paper)
    if not known_sections:
        raise SystemExit(f"No finding headings found in {args.paper}")

    for idx, row in enumerate(rows, start=1):
        for column in EXPECTED_COLUMNS:
            if not row.get(column):
                raise SystemExit(f"{args.path} row {idx} has empty value for {column!r}")
        support_path = ROOT / row["support_artifact"]
        if not support_path.exists():
            raise SystemExit(f"Missing support artifact: {support_path}")
        if row["claim_type"] not in ALLOWED_CLAIM_TYPES:
            raise SystemExit(f"Unsupported claim_type on row {idx}: {row['claim_type']!r}")
        if row["status"] not in ALLOWED_STATUSES:
            raise SystemExit(f"Unsupported status on row {idx}: {row['status']!r}")
        validate_paper_section(row["paper_section"], known_sections)

    print(f"Validated {args.path} with {len(rows)} rows and {len(columns)} columns.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
