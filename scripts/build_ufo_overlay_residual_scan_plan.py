from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path, PureWindowsPath


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
DEFAULT_AUDIT = DOCS / "ufo-overlay-measurement-audit.csv"
DEFAULT_CLASSIFICATION = DOCS / "ufo-overlay-measurement-classification.csv"
DEFAULT_P1_REVIEW = DOCS / "ufo-overlay-measurement-p1-review.csv"
DEFAULT_P1_ACQUISITION = DOCS / "ufo-overlay-measurement-p1-source-acquisition.csv"
DEFAULT_P2_PROBE = DOCS / "ufo-overlay-measurement-p2-local-ocr-probe.csv"
DEFAULT_P2_SOURCE_PREFLIGHT = DOCS / "ufo-overlay-measurement-p2-source-preflight.csv"
DEFAULT_P2_SOURCE_ACQUISITION = DOCS / "ufo-overlay-measurement-p2-source-acquisition.csv"
DEFAULT_P2_ACQUIRED_REVIEW = DOCS / "ufo-overlay-measurement-p2-acquired-review.csv"
DEFAULT_RESIDUAL_SOURCE_PREFLIGHT = DOCS / "ufo-overlay-measurement-residual-source-preflight.csv"
DEFAULT_RESIDUAL_LOCAL_REVIEW = DOCS / "ufo-overlay-measurement-residual-local-review.csv"
DEFAULT_RESIDUAL_REMOTE_REVIEW = DOCS / "ufo-overlay-measurement-residual-remote-review.csv"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-residual-scan-plan.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-residual-scan-plan.md"


FIELDNAMES = [
    "priority_rank",
    "residual_id",
    "record_id",
    "release_tag",
    "video_name",
    "dvids_id",
    "dvids_url",
    "matched_terms",
    "priority_band",
    "priority_reason",
    "current_lane_status",
    "local_source_hint",
    "source_availability_class",
    "recommended_scan_mode",
    "recommended_crop_strategy",
    "publication_boundary",
    "next_action",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def public_source_hint(value: str) -> str:
    value = clean(value).replace("\\", "/")
    if not value:
        return ""
    name = path_basename(value)
    if name.lower().endswith(".mp4"):
        return f"source-files-not-included/{name}"
    return value


def path_basename(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    if "\\" in text or ":" in text:
        return PureWindowsPath(text).name
    return Path(text).name


def matched_terms(row: dict[str, str]) -> list[str]:
    detail = clean(row.get("evidence_detail"))
    if not detail.lower().startswith("matched terms:"):
        return []
    return [term.strip().casefold() for term in detail.split(":", 1)[1].split(",") if term.strip()]


def load_classified_status(path: Path) -> dict[str, str]:
    status: dict[str, str] = {}
    if not path.exists():
        return status
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        polarity = clean(row.get("evidence_polarity"))
        classification = clean(row.get("classification"))
        if not record_id:
            continue
        if polarity == "positive":
            status[record_id] = "classified_positive_overlay_candidate"
        elif polarity == "negative_control" and status.get(record_id) != "classified_positive_overlay_candidate":
            status[record_id] = f"classified_negative_control:{classification}"
    return status


def load_p1_review_status(path: Path) -> dict[str, str]:
    status: dict[str, str] = {}
    if not path.exists():
        return status
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        effect = clean(row.get("classification_effect"))
        if not record_id:
            continue
        if effect == "promoted_positive_overlay_candidate":
            status[record_id] = "classified_positive_overlay_candidate"
        elif effect == "quicklook_review_false_ocr_candidate":
            status[record_id] = "bounded_p1_review_false_ocr_candidate"
        elif effect == "quicklook_review_no_meter_candidate":
            status[record_id] = "bounded_p1_review_no_meter_candidate"
    return status


def load_p1_local_sources(path: Path) -> dict[str, str]:
    sources: dict[str, str] = {}
    if not path.exists():
        return sources
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        local_path = clean(row.get("local_path_not_redistributed"))
        if record_id and local_path:
            sources[record_id] = local_path
    return sources


def load_p2_probe_status(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    rows_by_record: dict[str, list[dict[str, str]]] = {}
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        if record_id:
            rows_by_record.setdefault(record_id, []).append(row)

    status: dict[str, str] = {}
    for record_id, rows in rows_by_record.items():
        candidates = {clean(row.get("meter_label_candidate")) for row in rows}
        if "yes" in candidates:
            status[record_id] = "bounded_p2_local_ocr_candidate_requires_review"
        elif candidates == {"no"}:
            status[record_id] = "bounded_p2_local_ocr_no_candidate"
    return status


def load_p2_source_preflight(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, str]] = {}
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        if record_id and clean(row.get("source_acquisition_status")) == "embedded_public_mp4_found_not_downloaded":
            rows[record_id] = row
    return rows


def load_residual_source_preflight(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, str]] = {}
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        if record_id and clean(row.get("source_acquisition_status")) == "embedded_public_mp4_found_not_downloaded":
            rows[record_id] = row
    return rows


def load_p2_source_acquisition(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    rows: dict[str, dict[str, str]] = {}
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        if record_id and clean(row.get("source_exists_at_run")) == "yes":
            rows[record_id] = row
    return rows


def load_p2_acquired_review_status(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    status: dict[str, str] = {}
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        effect = clean(row.get("classification_effect"))
        if not record_id:
            continue
        if effect == "bounded_acquired_ocr_no_meter_candidate":
            status[record_id] = "bounded_p2_acquired_ocr_no_meter_candidate"
        elif effect == "bounded_acquired_ocr_false_ocr_candidate":
            status[record_id] = "bounded_p2_acquired_ocr_false_ocr_candidate"
    return status


def load_residual_local_review_status(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    status: dict[str, str] = {}
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        effect = clean(row.get("classification_effect"))
        if not record_id:
            continue
        if effect == "bounded_residual_local_ocr_no_meter_candidate":
            status[record_id] = "bounded_residual_local_ocr_no_meter_candidate"
        elif effect == "bounded_residual_local_ocr_false_ocr_candidate":
            status[record_id] = "bounded_residual_local_ocr_false_ocr_candidate"
    return status


def load_residual_remote_review_status(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    status: dict[str, str] = {}
    for row in read_csv(path):
        record_id = clean(row.get("record_id"))
        effect = clean(row.get("classification_effect"))
        if not record_id:
            continue
        if effect == "bounded_residual_remote_ocr_no_meter_candidate":
            status[record_id] = "bounded_residual_remote_ocr_no_meter_candidate"
        elif effect == "bounded_residual_remote_ocr_false_ocr_candidate":
            status[record_id] = "bounded_residual_remote_ocr_false_ocr_candidate"
    return status


def priority_for(row: dict[str, str], current_status: str) -> tuple[int, str, str, str, str]:
    terms = set(matched_terms(row))
    release = clean(row.get("release_tag"))
    local_source = clean(row.get("local_source_path"))

    if current_status.startswith("classified_negative_control"):
        return (
            4,
            "P4",
            "Already scanned as a PR44-style negative control; residual work is limited to non-PR44 geometry.",
            "classification/control follow-up only",
            "manual review only if a non-PR44 label geometry is suspected",
        )

    if current_status == "classified_positive_overlay_candidate":
        return (
            1,
            "P1",
            "Already promoted as a visible overlay candidate; residual work shifts to display semantics and raw-data requests.",
            "source documentation and raw/native-metadata follow-up",
            "preserve dedicated label-survey crops; do not infer physical meaning from public pixels",
        )

    if current_status.startswith("bounded_p1_review"):
        return (
            3,
            "P3",
            "P1 source was acquired and bounded quicklook/OCR review is complete; residual work is only for exhaustive all-frame OCR or alternate label geometry.",
            "optional exhaustive all-frame OCR or alternate label-geometry review",
            "reuse prior full-frame/focus sheets; add PR051/PR059-style label-geometry crops before dense OCR",
        )

    if current_status.startswith("bounded_p2_local_ocr"):
        return (
            3,
            "P3",
            "P2 local source was sampled with display-focused OCR; residual work is manual contact-sheet review, alternate geometry, or denser OCR.",
            "optional manual contact-sheet review or denser OCR if a stronger absence claim is needed",
            "reuse center/reticle and display-strip ROIs; add case-specific crops before any promotion decision",
        )

    if current_status == "source_preflighted_not_acquired":
        return (
            2,
            "P2",
            "Public source MP4 URL and size are localized, but source video is not yet retained outside Git or frame-reviewed.",
            "acquire source outside Git, hash it, then run display-focused OCR/contact-sheet review",
            "center/reticle crop plus border scan for zoom-state labels",
        )

    if current_status.startswith("bounded_p2_acquired_ocr"):
        return (
            3,
            "P3",
            "P2 source was acquired outside Git and sampled with display-focused OCR; residual work is manual contact-sheet review, alternate geometry, or denser OCR.",
            "optional manual contact-sheet review or denser OCR if a stronger absence claim is needed",
            "reuse center/reticle and display-strip ROIs; add case-specific crops before any promotion decision",
        )

    if current_status.startswith("bounded_residual_local_ocr"):
        return (
            3,
            "P3",
            "Residual local source was sampled with display-focused OCR; residual work is manual contact-sheet review, alternate geometry, or denser OCR.",
            "optional manual contact-sheet review or denser OCR if a stronger absence claim is needed",
            "reuse center/reticle and display-strip ROIs; add case-specific crops before any promotion decision",
        )

    if current_status.startswith("bounded_residual_remote_ocr"):
        return (
            3,
            "P3",
            "Residual public source URL was sampled remotely with display-focused OCR; residual work is source acquisition/hashing or denser OCR if a stronger claim is needed.",
            "optional source acquisition/hashing, manual contact-sheet review, or denser OCR if a stronger absence claim is needed",
            "reuse center/reticle and display-strip ROIs; add case-specific crops before any promotion decision",
        )

    if {"reticle", "sensor display", "visual elements of the sensor display", "range"} & terms:
        return (
            1,
            "P1",
            "Metadata directly names reticle, range, or sensor-display elements.",
            "one-second local-media overlay survey plus manual contact-sheet review",
            "reticle/display-centered crop presets; add non-PR44 presets if needed",
        )

    if "zoom" in terms:
        return (
            2,
            "P2",
            "Metadata names zoom/FOV context that can change apparent scale or label meaning.",
            "one-second local-media overlay survey when source media is available",
            "center/reticle crop plus border scan for zoom-state labels",
        )

    if {"altered", "contrast"} & terms or release == "release-02":
        return (
            3,
            "P3",
            "Metadata indicates altered/contrast/release-02 provenance where labels may be replay or enhancement artifacts.",
            "metadata-guided spot check before any dense scan",
            "first separate original, altered, replayed, thresholded, and zoomed intervals",
        )

    if local_source:
        return (
            3,
            "P3",
            "Generic FOV/display metadata target with a local source hint.",
            "low-frequency local-media survey if disk/source access permits",
            "broad center crop and overlay-border spot checks",
        )

    return (
        5,
        "P5",
        "Generic metadata-only target without local source path in the audit.",
        "defer until source acquisition improves",
        "no crop strategy until source media exists",
    )


def source_availability(row: dict[str, str], local_source_hint: str) -> str:
    if local_source_hint:
        return "local_source_path_listed_not_redistributed"
    if clean(row.get("video_name")):
        return "video_filename_known_source_not_localized"
    return "release_page_only_no_local_video_name"


def build_rows(
    audit_rows: list[dict[str, str]],
    classified: dict[str, str],
    p1_review_status: dict[str, str] | None = None,
    p1_local_sources: dict[str, str] | None = None,
    p2_probe_status: dict[str, str] | None = None,
    p2_source_preflight: dict[str, dict[str, str]] | None = None,
    p2_source_acquisition: dict[str, dict[str, str]] | None = None,
    p2_acquired_review_status: dict[str, str] | None = None,
    residual_source_preflight: dict[str, dict[str, str]] | None = None,
    residual_local_review_status: dict[str, str] | None = None,
    residual_remote_review_status: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    p1_review_status = p1_review_status or {}
    p1_local_sources = p1_local_sources or {}
    p2_probe_status = p2_probe_status or {}
    p2_source_preflight = p2_source_preflight or {}
    p2_source_acquisition = p2_source_acquisition or {}
    p2_acquired_review_status = p2_acquired_review_status or {}
    residual_source_preflight = residual_source_preflight or {}
    residual_local_review_status = residual_local_review_status or {}
    residual_remote_review_status = residual_remote_review_status or {}
    residuals = [
        row
        for row in audit_rows
        if clean(row.get("candidate_class")) == "overlay/measurement scan target"
    ]
    rows: list[dict[str, str]] = []
    for row in residuals:
        record_id = clean(row.get("record_id"))
        current_status = (
            classified.get(record_id)
            or p1_review_status.get(record_id)
            or p2_probe_status.get(record_id)
            or p2_acquired_review_status.get(record_id)
            or residual_local_review_status.get(record_id)
            or residual_remote_review_status.get(record_id)
            or ("source_preflighted_not_acquired" if record_id in p2_source_preflight else "")
            or ("source_preflighted_not_acquired" if record_id in residual_source_preflight else "")
            or "metadata_only_unclassified"
        )
        priority_sort, band, reason, scan_mode, crop_strategy = priority_for(row, current_status)
        source_acquisition = p2_source_acquisition.get(record_id, {})
        local_source_hint = public_source_hint(
            clean(row.get("local_source_path"))
            or p1_local_sources.get(record_id, "")
            or clean(source_acquisition.get("local_path_not_redistributed"))
        )
        source_preflight = p2_source_preflight.get(record_id) or residual_source_preflight.get(record_id, {})
        video_name = clean(row.get("video_name"))
        if not video_name and source_acquisition:
            video_name = clean(source_acquisition.get("source_video"))
        if not video_name and source_preflight:
            preflight_filename = clean(source_preflight.get("dvids_filename"))
            video_name = f"{preflight_filename}.mp4" if preflight_filename and not preflight_filename.lower().endswith(".mp4") else preflight_filename
        if current_status.startswith("bounded_p1_review"):
            publication_boundary = (
                "Bounded P1 review did not promote a visible label; this is not an exhaustive all-frame absence claim."
            )
            next_action = (
                "Run exhaustive all-frame OCR or alternate label-geometry review only if a stronger absence claim is needed; keep derived crops out of Git."
            )
        elif current_status.startswith("bounded_p2_local_ocr"):
            publication_boundary = (
                "Bounded P2 local OCR did not promote a visible label; this is not an exhaustive frame-level absence claim."
            )
            next_action = (
                "Run manual contact-sheet review, alternate label-geometry crops, or denser OCR only if a stronger absence claim is needed; keep derived crops out of Git."
            )
        elif current_status == "source_preflighted_not_acquired":
            publication_boundary = (
                "Public source URL is localized, but this row is not a visible-label finding until source-frame review confirms one."
            )
            next_action = (
                "Acquire the preflighted MP4 outside Git when disk space permits, hash it, and run display-focused OCR/contact-sheet review."
            )
        elif current_status.startswith("bounded_p2_acquired_ocr"):
            publication_boundary = (
                "Bounded acquired-source P2 OCR did not promote a visible label; this is not an exhaustive frame-level absence claim."
            )
            next_action = (
                "Run manual contact-sheet review, alternate label-geometry crops, or denser OCR only if a stronger absence claim is needed; keep derived crops out of Git."
            )
        elif current_status.startswith("bounded_residual_local_ocr"):
            publication_boundary = (
                "Bounded residual local-source OCR did not promote a visible label; this is not an exhaustive frame-level absence claim."
            )
            next_action = (
                "Run manual contact-sheet review, alternate label-geometry crops, or denser OCR only if a stronger absence claim is needed; keep derived crops out of Git."
            )
        elif current_status.startswith("bounded_residual_remote_ocr"):
            publication_boundary = (
                "Bounded residual remote-frame OCR did not promote a visible label; source MP4s were not retained or hashed, and this is not an exhaustive frame-level absence claim."
            )
            next_action = (
                "Acquire and hash source MP4 outside Git only if a stronger source-retained claim is needed; otherwise run alternate label-geometry crops or denser OCR as follow-up."
            )
        elif current_status == "classified_positive_overlay_candidate":
            publication_boundary = (
                "Already promoted under the classification matrix; do not treat the visible label as a physical measurement."
            )
            next_action = "Use source requests/display documentation to resolve semantics; keep derived crops out of Git."
        else:
            publication_boundary = "Do not treat this row as a visible label until frame-level review confirms one."
            next_action = "Run only when source media is available outside the publish set; keep derived crops out of Git."
        rows.append(
            {
                "priority_rank": str(priority_sort),
                "residual_id": clean(row.get("candidate_id")),
                "record_id": record_id,
                "release_tag": clean(row.get("release_tag")),
                "video_name": video_name,
                "dvids_id": clean(row.get("dvids_id")),
                "dvids_url": clean(row.get("dvids_url")),
                "matched_terms": clean(row.get("evidence_detail")).replace("Matched terms: ", ""),
                "priority_band": band,
                "priority_reason": reason,
                "current_lane_status": current_status,
                "local_source_hint": local_source_hint,
                "source_availability_class": (
                    "embedded_public_mp4_preflighted_not_downloaded"
                    if current_status == "source_preflighted_not_acquired"
                    else "remote_public_mp4_sampled_not_retained"
                    if current_status.startswith("bounded_residual_remote_ocr")
                    else source_availability(row, local_source_hint)
                ),
                "recommended_scan_mode": scan_mode,
                "recommended_crop_strategy": crop_strategy,
                "publication_boundary": publication_boundary,
                "next_action": next_action,
            }
        )
    rows.sort(key=lambda item: (int(item["priority_rank"]), item["release_tag"], item["record_id"], item["residual_id"]))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    by_priority = Counter(row["priority_band"] for row in rows)
    by_release = Counter(row["release_tag"] for row in rows)
    by_status = Counter(row["current_lane_status"] for row in rows)
    lines = [
        "# Overlay Measurement Residual Scan Plan",
        "",
        "Owner: Dan Fredriksen",
        "Generated by: `scripts/build_ufo_overlay_residual_scan_plan.py`",
        "Scope: metadata-derived overlay scan targets and their current lane status",
        "",
        "## Purpose",
        "",
        "This plan turns the metadata-derived overlay targets into an ordered follow-up queue with current lane status.",
        "Rows are not visible-label findings unless `current_lane_status` says they have been promoted in the classification matrix.",
        "",
        "## Summary",
        "",
        f"- Residual targets: `{len(rows)}`",
        f"- Release 01 targets: `{by_release.get('release-01', 0)}`",
        f"- Release 02 targets: `{by_release.get('release-02', 0)}`",
        "",
        "Priority bands:",
    ]
    for band in ["P1", "P2", "P3", "P4", "P5"]:
        lines.append(f"- `{band}`: `{by_priority.get(band, 0)}`")
    lines.extend(["", "Lane status:"])
    for status, count in sorted(by_status.items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(
        [
            "",
            "## Priority Rules",
            "",
            "- `P1`: direct reticle, range, or sensor-display metadata terms.",
            "- `P2`: zoom/FOV context likely to affect apparent scale or label interpretation.",
            "- `P3`: bounded-reviewed P1/P2 follow-up, altered/contrast/release-02 provenance, or generic local-source targets.",
            "- `P4`: already scanned as PR44-style negative controls; residual work is only for non-PR44 label geometry.",
            "- `P5`: source acquisition or localization must improve before scan work is meaningful.",
            "",
            "## Publication Boundary",
            "",
            "Rows in this plan are not visible-label findings. Promote a row only after source-frame review confirms a label and the classification matrix is updated under the existing decision rule.",
            "",
            "Supporting table:",
            "",
            "- `research/ufo-overlay-measurement-residual-scan-plan.csv`",
            "",
            "Validation:",
            "",
            "- `scripts/validate_overlay_residual_scan_plan.py`",
            "",
            "P1 source preflight:",
            "",
            "- `research/ufo-overlay-measurement-p1-source-preflight.md`",
            "",
            "P1 bounded review:",
            "",
            "- `research/ufo-overlay-measurement-p1-review.md`",
            "",
            "P2 local OCR probe:",
            "",
            "- `research/ufo-overlay-measurement-p2-local-ocr-probe.md`",
            "",
            "P2 source preflight:",
            "",
            "- `research/ufo-overlay-measurement-p2-source-preflight.md`",
            "",
            "P2 source acquisition and acquired review:",
            "",
            "- `research/ufo-overlay-measurement-p2-source-acquisition.md`",
            "- `research/ufo-overlay-measurement-p2-acquired-review.md`",
            "",
            "Residual source preflight:",
            "",
            "- `research/ufo-overlay-measurement-residual-source-preflight.md`",
            "",
            "Residual local OCR review:",
            "",
            "- `research/ufo-overlay-measurement-residual-local-review.md`",
            "",
            "Residual remote OCR review:",
            "",
            "- `research/ufo-overlay-measurement-residual-remote-review.md`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a prioritized residual overlay scan plan.")
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
    parser.add_argument("--p1-review", type=Path, default=DEFAULT_P1_REVIEW)
    parser.add_argument("--p1-acquisition", type=Path, default=DEFAULT_P1_ACQUISITION)
    parser.add_argument("--p2-probe", type=Path, default=DEFAULT_P2_PROBE)
    parser.add_argument("--p2-source-preflight", type=Path, default=DEFAULT_P2_SOURCE_PREFLIGHT)
    parser.add_argument("--p2-source-acquisition", type=Path, default=DEFAULT_P2_SOURCE_ACQUISITION)
    parser.add_argument("--p2-acquired-review", type=Path, default=DEFAULT_P2_ACQUIRED_REVIEW)
    parser.add_argument("--residual-source-preflight", type=Path, default=DEFAULT_RESIDUAL_SOURCE_PREFLIGHT)
    parser.add_argument("--residual-local-review", type=Path, default=DEFAULT_RESIDUAL_LOCAL_REVIEW)
    parser.add_argument("--residual-remote-review", type=Path, default=DEFAULT_RESIDUAL_REMOTE_REVIEW)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_rows(
        read_csv(args.audit),
        load_classified_status(args.classification),
        load_p1_review_status(args.p1_review),
        load_p1_local_sources(args.p1_acquisition),
        load_p2_probe_status(args.p2_probe),
        load_p2_source_preflight(args.p2_source_preflight),
        load_p2_source_acquisition(args.p2_source_acquisition),
        load_p2_acquired_review_status(args.p2_acquired_review),
        load_residual_source_preflight(args.residual_source_preflight),
        load_residual_local_review_status(args.residual_local_review),
        load_residual_remote_review_status(args.residual_remote_review),
    )
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows)
    print(f"Wrote {len(rows)} residual targets to {args.output}")
    print(f"Wrote summary to {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
