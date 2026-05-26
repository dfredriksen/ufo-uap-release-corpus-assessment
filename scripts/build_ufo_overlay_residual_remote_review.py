from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
DEFAULT_OCR = DOCS / "ufo-overlay-measurement-residual-remote-ocr-probe.csv"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-residual-remote-review.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-residual-remote-review.md"

FIELDNAMES = [
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

FALSE_CANDIDATE_NOTES = {
    "DOW-UAP-PR060": (
        "display crops with terrain/shoreline texture, black redaction blocks, direction markers, and reticle geometry",
        "three OCR candidates at 60s, 90s, and 210s were manually checked and rejected as terrain/shoreline/display-geometry OCR noise; not visible meter labels",
    ),
    "DOW-UAP-PR061": (
        "center reticle crop with terrain texture and direction markers",
        "one OCR candidate at 30s was manually checked and rejected as terrain/reticle OCR noise; not a visible meter label",
    ),
    "DOW-UAP-PR067": (
        "center reticle crop over vessel/wake scene with direction markers",
        "one OCR candidate at 210s was manually checked and rejected as vessel/wake/reticle OCR noise; not a visible meter label",
    ),
    "DOW-UAP-PR090": (
        "center reticle crop over field texture and direction marker",
        "one OCR candidate at 90s was manually checked and rejected as field/reticle OCR noise; not a visible meter label",
    ),
    "DOW-UAP-PR095": (
        "center reticle crop over low-texture field and direction marker",
        "one OCR candidate at 90s was manually checked and rejected as field/reticle OCR noise; not a visible meter label",
    ),
    "DOW-UAP-PR096": (
        "center reticle crop over field texture and direction marker",
        "one OCR candidate at 30s was manually checked and rejected as field/reticle OCR noise; not a visible meter label",
    ),
}


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def source_video(row: dict[str, str]) -> str:
    filename = clean(row.get("dvids_filename"))
    return f"{filename}.mp4" if filename and not filename.lower().endswith(".mp4") else filename


def build_rows(ocr: Path) -> list[dict[str, str]]:
    ocr_rows = read_csv(ocr)
    rows_by_record: dict[str, list[dict[str, str]]] = {}
    for row in ocr_rows:
        rows_by_record.setdefault(clean(row.get("record_id")), []).append(row)

    output: list[dict[str, str]] = []
    for record_id, rows in sorted(rows_by_record.items()):
        first = rows[0]
        candidate_count = sum(1 for row in rows if row["meter_label_candidate"] == "yes")
        if candidate_count:
            visible_elements, result = FALSE_CANDIDATE_NOTES[record_id]
            review_basis = "30_second_remote_frame_display_focused_ocr_probe_plus_manual_candidate_crop_review"
            effect = "bounded_residual_remote_ocr_false_ocr_candidate"
            boundary = (
                "Bounded remote-frame OCR triage plus manual candidate crop review only; "
                "source MP4 not retained or hashed; not an exhaustive all-frame absence claim."
            )
        else:
            visible_elements = "remote display/reticle crops with no promoted meter-label candidate"
            result = (
                "no explicit PR44/PR051/PR059-style meter-label candidate promoted in bounded residual-remote OCR review"
            )
            review_basis = "30_second_remote_frame_display_focused_ocr_probe"
            effect = "bounded_residual_remote_ocr_no_meter_candidate"
            boundary = (
                "Bounded remote-frame OCR triage only; source MP4 not retained or hashed; "
                "not an exhaustive all-frame absence claim."
            )
        output.append(
            {
                "record_id": record_id,
                "release_tag": clean(first.get("release_tag")),
                "source_video": source_video(first),
                "review_basis": review_basis,
                "ocr_rows": str(len(rows)),
                "ocr_meter_candidate_rows": str(candidate_count),
                "visible_overlay_elements": visible_elements,
                "meter_label_result": result,
                "classification_effect": effect,
                "physical_claim_status": "not_promoted",
                "evidence_boundary": boundary,
                "support_note": "research/ufo-overlay-measurement-residual-remote-ocr-probe.md",
            }
        )
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    by_effect = Counter(row["classification_effect"] for row in rows)
    candidate_rows = [row for row in rows if row["classification_effect"].endswith("false_ocr_candidate")]
    total_ocr_rows = sum(int(row["ocr_rows"]) for row in rows)
    total_candidates = sum(int(row["ocr_meter_candidate_rows"]) for row in rows)
    lines = [
        "# Overlay Measurement Residual Remote Review",
        "",
        "Owner: Dan Fredriksen",
        "Created: 2026-05-26",
        "Scope: Release 02 residual rows with preflighted public MP4 URLs but no retained local source MP4",
        "Status: bounded remote OCR/manual-candidate review complete; no new positive overlay candidate promoted",
        "",
        "## Purpose",
        "",
        "This review records the classification effect of the residual remote-frame OCR probe.",
        "",
        "The question was:",
        "",
        "> Do the remaining Release 02 source-preflighted residual public MP4s contain PR44/PR051/PR059-style or related meter-suffix overlay labels at the bounded 30-second display-focused remote OCR cadence?",
        "",
        "## OCR Review",
        "",
        f"- Records covered: `{len(rows)}`",
        f"- OCR/probe rows: `{total_ocr_rows}`",
        f"- Meter-label candidate rows: `{total_candidates}`",
        f"- Records with OCR candidates: `{len(candidate_rows)}`",
    ]
    for effect, count in sorted(by_effect.items()):
        lines.append(f"- `{effect}`: `{count}`")
    lines.extend(
        [
            "",
            "Supporting artifact:",
            "",
            "- `research/ufo-overlay-measurement-residual-remote-ocr-probe.md`",
            "",
            "## Manual Candidate Review",
            "",
            "The eight OCR candidates were reviewed from ignored local candidate crops. All were rejected as terrain, field, shoreline, vessel/wake, reticle, direction-marker, display-geometry, or compression/contrast OCR noise.",
            "",
            "Candidate records:",
            "",
        ]
    )
    for row in candidate_rows:
        lines.append(
            f"- `{row['record_id']}`: `{row['ocr_meter_candidate_rows']}` candidate row(s); {row['meter_label_result']}"
        )
    lines.extend(
        [
            "",
            "## Findings",
            "",
            "| Record ID | OCR rows | OCR candidates | Classification effect |",
            "|---|---:|---:|---|",
        ]
    )
    for row in rows:
        effect = (
            "False OCR candidate; not promoted"
            if row["classification_effect"].endswith("false_ocr_candidate")
            else "Not promoted"
        )
        lines.append(
            f"| `{row['record_id']}` | `{row['ocr_rows']}` | `{row['ocr_meter_candidate_rows']}` | {effect} |"
        )
    lines.extend(
        [
            "",
            "Machine-readable review table:",
            "",
            "- `research/ufo-overlay-measurement-residual-remote-review.csv`",
            "",
            "## Evidence Boundary",
            "",
            "This review supports the statement:",
            "",
            "> The 36 remaining Release 02 source-preflighted residual public MP4s were triaged with a bounded 30-second display-focused remote-frame OCR pass. No new meter-label candidate was promoted.",
            "",
            "The source MP4 not retained or hashed caveat is material: this is a remote triage result, not a source-acquisition result.",
            "",
            "This review does not support these broader statements:",
            "",
            "- every frame of every residual Release 02 video has been OCR-reviewed",
            "- the residual Release 02 videos contain no telemetry labels of any kind",
            "- the residual corpus has been exhaustively cleared for measurement overlays",
            "- source MP4s have been acquired, retained, or hashed",
            "",
            "Use the result as bounded remote triage only. This is not an exhaustive all-frame absence claim and does not replace source acquisition.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build manual review artifact for residual remote OCR candidates.")
    parser.add_argument("--ocr", type=Path, default=DEFAULT_OCR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_rows(args.ocr)
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows)
    print(f"Wrote {len(rows)} residual remote review rows to {args.output}")
    print(f"Wrote residual remote review summary to {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
