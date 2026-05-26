from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
CLASSIFICATION = DOCS / "ufo-overlay-measurement-classification.csv"
SOURCE_REQUESTS = DOCS / "ufo-overlay-measurement-source-requests.csv"
CLASSIFICATION_MD = DOCS / "ufo-overlay-measurement-classification.md"
COMPLETION_AUDIT = DOCS / "ufo-overlay-measurement-completion-audit.md"

CLASSIFICATION_COLUMNS = [
    "classification_id",
    "case",
    "record_id",
    "release",
    "overlay_candidate",
    "interval_seconds",
    "evidence_polarity",
    "visibility_status",
    "manual_read",
    "confidence",
    "display_association",
    "classification",
    "physical_claim_status",
    "support_artifact",
    "source_request_id",
    "notes",
]

SOURCE_REQUEST_COLUMNS = [
    "request_id",
    "cases",
    "claim_to_test",
    "required_source_data",
    "why_needed",
    "current_status",
    "promotion_condition",
    "support_artifact",
]

CONTROLLED = {
    "evidence_polarity": {"positive", "negative_control"},
    "visibility_status": {"persistent", "persistent_transition", "repeated", "intermittent", "absent"},
    "confidence": {"high", "medium", "low"},
    "classification": {
        "unresolved_display_annotation",
        "display_state_associated",
        "altered_replay_overlay_candidate",
        "no_matching_label",
    },
    "physical_claim_status": {"not_promoted"},
    "current_status": {"missing"},
}

EXPECTED_POSITIVE_CASES = {"PR44", "PR051", "PR059"}


def read_csv(path: Path, expected_columns: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing CSV: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != expected_columns:
            raise SystemExit(f"Unexpected columns in {path}: {reader.fieldnames}")
        rows = list(reader)
    if not rows:
        raise SystemExit(f"No rows in {path}")
    return rows


def require_nonempty(row: dict[str, str], fields: list[str], row_id: str) -> None:
    for field in fields:
        if not row.get(field, "").strip():
            raise SystemExit(f"Empty {field} in {row_id}")


def require_known(field: str, value: str, row_id: str) -> None:
    allowed = CONTROLLED[field]
    if value not in allowed:
        raise SystemExit(f"Unexpected {field}={value!r} in {row_id}; expected one of {sorted(allowed)}")


def require_artifact(path_text: str, row_id: str) -> None:
    artifact = ROOT / path_text
    if not artifact.exists():
        raise SystemExit(f"Missing support artifact for {row_id}: {artifact}")


def validate_narrative_docs(positive_cases: set[str]) -> None:
    missing_cases = EXPECTED_POSITIVE_CASES - positive_cases
    if missing_cases:
        raise SystemExit(f"Missing expected positive overlay cases: {sorted(missing_cases)}")

    for path in [CLASSIFICATION_MD, COMPLETION_AUDIT]:
        if not path.exists():
            raise SystemExit(f"Missing narrative artifact: {path}")
        text = path.read_text(encoding="utf-8")
        for case in EXPECTED_POSITIVE_CASES:
            if case not in text:
                raise SystemExit(f"{path.name} does not mention positive case {case}")
        if "two positive measurement-like overlay cases" in text:
            raise SystemExit(f"{path.name} still describes only two positive overlay cases")

    classification_text = CLASSIFICATION_MD.read_text(encoding="utf-8")
    if "Cite PR44, PR051, and PR059" not in classification_text:
        raise SystemExit("Classification publication guidance does not cite PR44, PR051, and PR059 together")

    completion_text = COMPLETION_AUDIT.read_text(encoding="utf-8")
    if "three positive measurement-like overlay cases" not in completion_text:
        raise SystemExit("Completion audit publication guidance does not describe three positive cases")


def main() -> int:
    classifications = read_csv(CLASSIFICATION, CLASSIFICATION_COLUMNS)
    requests = read_csv(SOURCE_REQUESTS, SOURCE_REQUEST_COLUMNS)
    request_ids = {row["request_id"] for row in requests}

    if len(request_ids) != len(requests):
        raise SystemExit("Duplicate source request IDs found")

    positives = 0
    controls = 0
    positive_cases: set[str] = set()
    seen_ids: set[str] = set()
    for row in classifications:
        row_id = row["classification_id"]
        if row_id in seen_ids:
            raise SystemExit(f"Duplicate classification_id: {row_id}")
        seen_ids.add(row_id)
        require_nonempty(
            row,
            [
                "classification_id",
                "case",
                "record_id",
                "release",
                "overlay_candidate",
                "interval_seconds",
                "evidence_polarity",
                "visibility_status",
                "confidence",
                "display_association",
                "classification",
                "physical_claim_status",
                "support_artifact",
                "source_request_id",
                "notes",
            ],
            row_id,
        )
        for field in [
            "evidence_polarity",
            "visibility_status",
            "confidence",
            "classification",
            "physical_claim_status",
        ]:
            require_known(field, row[field], row_id)
        if row["source_request_id"] not in request_ids:
            raise SystemExit(f"Unknown source_request_id in {row_id}: {row['source_request_id']}")
        require_artifact(row["support_artifact"], row_id)
        if row["evidence_polarity"] == "positive":
            positives += 1
            positive_cases.add(row["case"])
            if not row["manual_read"].strip():
                raise SystemExit(f"Positive row lacks manual_read: {row_id}")
        if row["evidence_polarity"] == "negative_control":
            controls += 1
            if row["classification"] != "no_matching_label":
                raise SystemExit(f"Negative control is not classified as no_matching_label: {row_id}")

    if positives < 3:
        raise SystemExit("Expected at least three positive overlay candidates")
    if controls < 3:
        raise SystemExit("Expected at least three negative controls")

    for row in requests:
        row_id = row["request_id"]
        require_nonempty(row, SOURCE_REQUEST_COLUMNS, row_id)
        require_known("current_status", row["current_status"], row_id)
        require_artifact(row["support_artifact"], row_id)

    validate_narrative_docs(positive_cases)

    print(f"Validated {len(classifications)} overlay classifications and {len(requests)} source requests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
