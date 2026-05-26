from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath

try:
    import cv2
    import numpy as np
except ImportError:  # pragma: no cover - validated by runtime checks when video scanning is requested.
    cv2 = None
    np = None


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"

DEFAULT_RELEASE_MANIFESTS = [
    RESEARCH / "war-gov-ufo-release-01-manifest-normalized.csv",
    RESEARCH / "war-gov-ufo-release-02-manifest-normalized.csv",
]
DEFAULT_UNIQUE_VIDEOS = RESEARCH / "ufo-unique-video-review-list.csv"
DEFAULT_CORRELATION_MATRIX = RESEARCH / "ufo-report-video-correlation-matrix.csv"
DEFAULT_PR44_OVERLAY = RESEARCH / "ufo-video-source-overlay-dod111689115.csv"
DEFAULT_OUTPUT = RESEARCH / "ufo-overlay-measurement-audit.csv"
DEFAULT_SUMMARY = RESEARCH / "ufo-overlay-measurement-audit.md"
DEFAULT_DERIVED_ROOT = RESEARCH / "ufo-derived" / "overlay-measurement-audit"
PR44_PERSISTENCE_CSV = RESEARCH / "ufo-overlay-measurement-pr44-label-persistence.csv"

MEASUREMENT_TERMS = re.compile(
    r"\b(?:\d+(?:\.\d+)?\s*(?:m|M|meter|meters|ft|feet|nm|NM|km|KM|kts|knots|mph)|"
    r"range|slant|reticle|track(?:ing)? box|gate|fov|field-of-view|zoom|sensor display|"
    r"visual elements of the sensor display)\b",
    re.IGNORECASE,
)

OVERLAY_TERMS = re.compile(
    r"\b(?:reticle|sensor display|visual elements|zoom|field-of-view|fov|threshold|"
    r"enhancement|sharpened|contrast|inverted|motion tracked|replay|altered)\b",
    re.IGNORECASE,
)


FIELDNAMES = [
    "candidate_id",
    "record_id",
    "release_tag",
    "video_name",
    "dvids_id",
    "dvids_url",
    "source_basis",
    "source_status",
    "approx_second",
    "frame_index",
    "label_text_observed",
    "label_family",
    "candidate_class",
    "classification_status",
    "alteration_status",
    "fresh_clone_reproducible",
    "local_source_path",
    "crop_path",
    "evidence_detail",
    "ambiguity_notes",
    "next_action",
]


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


@dataclass
class Candidate:
    candidate_id: str
    record_id: str
    release_tag: str
    video_name: str
    dvids_id: str
    dvids_url: str
    source_basis: str
    source_status: str
    approx_second: str
    frame_index: str
    label_text_observed: str
    label_family: str
    candidate_class: str
    classification_status: str
    alteration_status: str
    fresh_clone_reproducible: str
    local_source_path: str
    crop_path: str
    evidence_detail: str
    ambiguity_notes: str
    next_action: str

    def row(self) -> dict[str, str]:
        row = {field: getattr(self, field) for field in FIELDNAMES}
        row["local_source_path"] = public_source_hint(row["local_source_path"])
        row["crop_path"] = public_derived_hint(row["crop_path"])
        return row


def public_source_hint(value: str) -> str:
    if not value:
        return ""
    name = path_basename(value)
    if name.lower().endswith(".mp4"):
        return f"source-files-not-included/{name}"
    return value.replace("\\", "/")


def public_derived_hint(value: str) -> str:
    if not value:
        return ""
    normalized = value.replace("\\", "/")
    lowered = normalized.lower()
    for marker in ("research/ufo-derived/", "ufo-derived/"):
        index = lowered.find(marker)
        if index >= 0:
            suffix = normalized[index:]
            return suffix if suffix.startswith("research/") else f"research/{suffix}"
    return normalized


def path_basename(value: object) -> str:
    text = clean(value)
    if not text:
        return ""
    if "\\" in text or ":" in text:
        return PureWindowsPath(text).name
    return Path(text).name


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[Candidate]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row.row())


def release_tag_for(path: Path) -> str:
    match = re.search(r"release-(\d+)", path.name)
    if match:
        return f"release-{match.group(1)}"
    return "unknown"


def video_name_from_record(record: dict[str, str]) -> str:
    asset = record.get("asset_filename", "").strip()
    if asset.lower().endswith(".mp4"):
        return asset
    local = path_basename(record.get("local_source_path", ""))
    if local.lower().endswith(".mp4"):
        return local
    return ""


def normalize_record_id(value: str) -> str:
    value = value.upper().strip()
    match = re.fullmatch(r"DOW-UAP-PR0*(\d+)([A-Z]?)", value)
    if match:
        number = int(match.group(1))
        prefix = f"DOW-UAP-PR{number:03d}" if number >= 50 else f"DOW-UAP-PR{number}"
        return f"{prefix}{match.group(2)}"
    return value


def build_release_lookup(manifest_paths: list[Path]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for manifest in manifest_paths:
        tag = release_tag_for(manifest)
        for row in read_csv(manifest):
            raw_record_id = row.get("record_id", "").strip()
            if not raw_record_id:
                continue
            record_id = normalize_record_id(raw_record_id)
            row = dict(row)
            row["release_tag"] = tag
            lookup[record_id.upper()] = row
            lookup[normalize_record_id(record_id)] = row
            dvids_id = row.get("dvids_video_id", "").strip()
            if dvids_id:
                lookup[f"DVIDS:{dvids_id}"] = row
    return lookup


def build_video_lookup(path: Path) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for row in read_csv(path):
        for key in (row.get("canonical_name", ""), row.get("selected_name", "")):
            if key:
                lookup[key.lower()] = row
    return lookup


def build_record_video_lookup(correlation_path: Path) -> dict[str, str]:
    lookup: dict[str, str] = {}
    for row in read_csv(correlation_path):
        local_file = row.get("local_file", "").strip()
        if not local_file.lower().endswith(".mp4"):
            continue
        source_path = str(Path(local_file))
        for record_id in re.findall(r"DOW-UAP-PR0*\d+[A-Za-z]?", row.get("official_release_or_report", "")):
            lookup[normalize_record_id(record_id)] = source_path
            lookup[record_id.upper()] = source_path
    return lookup


def known_pr44_candidates(pr44_overlay_path: Path, release_lookup: dict[str, dict[str, str]]) -> list[Candidate]:
    rows = read_csv(pr44_overlay_path)
    release = release_lookup.get("DOW-UAP-PR044") or release_lookup.get("DOW-UAP-PR44") or {}
    candidates: list[Candidate] = []
    for idx, row in enumerate(rows, start=1):
        second = row.get("approx_second", "")
        candidates.append(
            Candidate(
                candidate_id=f"PR44-KNOWN-{idx:03d}",
                record_id="DOW-UAP-PR44",
                release_tag=release.get("release_tag", "release-01"),
                video_name=row.get("video", "DOD_111689115.mp4"),
                dvids_id=release.get("dvids_video_id", ""),
                dvids_url=release.get("dvids_url", "https://www.dvidshub.net/video/1006104"),
                source_basis="repo-local PR44 source-overlay extraction index",
                source_status="repo-local-derived-index; source crops excluded",
                approx_second=second,
                frame_index="",
                label_text_observed="10M/10m-like",
                label_family="meter-like overlay",
                candidate_class="explicit measurement-like overlay candidate",
                classification_status="semantics unresolved",
                alteration_status="not flagged as altered in release review",
                fresh_clone_reproducible="partial: CSV row is committed; source crop requires excluded local media/cache",
                local_source_path="",
                crop_path=public_derived_hint(row.get("overlay_zoom", "")),
                evidence_detail=f"Source-overlay index row at approx second {second}; OCR path {public_derived_hint(row.get('ocr_text', ''))}",
                ambiguity_notes="Could be meter readout, range gate, track-box parameter, generic sensor annotation, or OCR artifact.",
                next_action="Re-extract source-resolution crops and run adjacent-frame label-persistence review.",
            )
        )
    return candidates


def known_pr051_candidate(release_lookup: dict[str, dict[str, str]]) -> Candidate:
    release = release_lookup.get("DOW-UAP-PR051", {})
    return Candidate(
        candidate_id="PR051-USERFRAME-001",
        record_id="DOW-UAP-PR051",
        release_tag=release.get("release_tag", "release-02"),
        video_name="DOD_111719715",
        dvids_id=release.get("dvids_video_id", "1007707"),
        dvids_url=release.get("dvids_url", "https://www.dvidshub.net/video/1007707"),
        source_basis="user-provided frame in review thread",
        source_status="not repo-local source artifact",
        approx_second="unknown",
        frame_index="unknown",
        label_text_observed="5m-style",
        label_family="meter-like overlay",
        candidate_class="explicit measurement-like overlay candidate",
        classification_status="semantics unresolved",
        alteration_status="official public description says digitally altered before upload",
        fresh_clone_reproducible="no: requires official media acquisition or retained frame source",
        local_source_path=release.get("local_source_path", ""),
        crop_path="",
        evidence_detail="Conversation-frame observation: bright object/track near reticle with visible 5m-style annotation.",
        ambiguity_notes="Could be object-size estimate, range readout, gate/track-box parameter, zoom/reticle state, or alteration/replay artifact.",
        next_action="Acquire/hash official asset, isolate least-altered/original-resolution interval, and test adjacent-frame label persistence.",
    )


def known_pr059_candidate(release_lookup: dict[str, dict[str, str]]) -> Candidate:
    release = release_lookup.get("DOW-UAP-PR059", {})
    return Candidate(
        candidate_id="PR059-KNOWN-001",
        record_id="DOW-UAP-PR059",
        release_tag=release.get("release_tag", "release-02"),
        video_name="DOD_111719809.mp4",
        dvids_id=release.get("dvids_video_id", "1007727"),
        dvids_url=release.get("dvids_url", "https://www.dvidshub.net/video/1007727"),
        source_basis="P1 quicklook/OCR probe plus dedicated PR059 label survey",
        source_status="repo-local review tables; source crops excluded",
        approx_second="23-277",
        frame_index="",
        label_text_observed="36M/33M/10M/<4M/2M/23M-style sequence",
        label_family="meter-suffix-like overlay",
        candidate_class="explicit measurement-like overlay candidate",
        classification_status="semantics unresolved",
        alteration_status="not flagged as altered in release review",
        fresh_clone_reproducible="partial: review tables are committed; source crops require excluded local media/cache",
        local_source_path="",
        crop_path="research/ufo-overlay-measurement-pr059-label-intervals.csv",
        evidence_detail="PR059 label survey found persistent target-adjacent M/m-style suffix labels from about 23-277s.",
        ambiguity_notes="Could be range, object size, gate/track-box parameter, zoom/display state, track quality, or another sensor annotation.",
        next_action="Request sensor/display symbology documentation and native metadata before assigning physical meaning.",
    )


def metadata_scan_candidates(
    manifest_paths: list[Path],
    video_lookup: dict[str, dict[str, str]],
    record_video_lookup: dict[str, str],
) -> list[Candidate]:
    candidates: list[Candidate] = []
    for manifest in manifest_paths:
        tag = release_tag_for(manifest)
        for row in read_csv(manifest):
            if row.get("type", "").upper() != "VID":
                continue
            raw_record_id = row.get("record_id", "").strip()
            if not raw_record_id:
                continue
            record_id = normalize_record_id(raw_record_id)
            text = " ".join([row.get("title", ""), row.get("description_blurb", "")])
            has_measurement = bool(MEASUREMENT_TERMS.search(text))
            has_overlay = bool(OVERLAY_TERMS.search(text))
            if not (has_measurement or has_overlay):
                continue
            video_name = video_name_from_record(row)
            local = ""
            manifest_local = row.get("local_source_path", "")
            if manifest_local.lower().endswith(".mp4"):
                local = manifest_local
                if not video_name:
                    video_name = path_basename(local)
            mapped_local = record_video_lookup.get(normalize_record_id(record_id), "")
            if mapped_local:
                local = mapped_local
                video_name = path_basename(mapped_local)
            if not local and video_name:
                local = video_lookup.get(video_name.lower(), {}).get("source_path", "")
            terms = sorted(set(match.group(0).lower() for match in OVERLAY_TERMS.finditer(text)))
            measurement_terms = sorted(set(match.group(0) for match in MEASUREMENT_TERMS.finditer(text)))
            altered = "yes" if re.search(r"digitally altered|altered", text, re.IGNORECASE) else "no"
            candidates.append(
                Candidate(
                    candidate_id=f"{record_id}-METADATA-001",
                    record_id=record_id,
                    release_tag=tag,
                    video_name=video_name,
                    dvids_id=row.get("dvids_video_id", ""),
                    dvids_url=row.get("dvids_url", ""),
                    source_basis="official manifest/DVIDS description text",
                    source_status="metadata-only scan target",
                    approx_second="",
                    frame_index="",
                    label_text_observed="",
                    label_family="unknown pending frame scan",
                    candidate_class="overlay/measurement scan target",
                    classification_status="no explicit frame-level label confirmed in repo",
                    alteration_status=altered,
                    fresh_clone_reproducible="yes: derived from committed manifest text",
                    local_source_path=local,
                    crop_path="",
                    evidence_detail=f"Matched terms: {', '.join(measurement_terms or terms)}",
                    ambiguity_notes="Manifest text indicates display/reticle/zoom/alteration context but does not itself prove a measurement label is visible.",
                    next_action="Run local-media frame scan and manual crop review if the source MP4 is available.",
                )
            )
    return candidates


def seconds_from_duration(value: str) -> int:
    value = value.strip()
    if not value:
        return 0
    parts = value.split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(float(parts[2]))
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(float(parts[1]))
        return int(float(parts[0]))
    except ValueError:
        return 0


def classify_textlike_region(frame) -> tuple[bool, str, tuple[int, int, int, int] | None]:
    if cv2 is None or np is None:
        raise RuntimeError("opencv-python and numpy are required for --scan-local-video")
    height, width = frame.shape[:2]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 180)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3))
    grouped = cv2.dilate(edges, kernel, iterations=1)
    labels_count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(grouped, connectivity=8)
    regions: list[tuple[int, int, int, int, int]] = []
    for label in range(1, labels_count):
        x, y, w, h, area = stats[label]
        if area < 80 or area > 8000:
            continue
        if w < 16 or w > width * 0.30:
            continue
        if h < 8 or h > height * 0.12:
            continue
        central = width * 0.20 <= x <= width * 0.80 and height * 0.15 <= y <= height * 0.85
        overlay_band = y < height * 0.18 or y > height * 0.82
        if central or overlay_band:
            regions.append((x, y, w, h, area))
    if not regions:
        return False, "no textlike overlay cluster detected", None
    best = max(regions, key=lambda region: region[4])
    return True, f"{len(regions)} textlike overlay clusters detected", best[:4]


def scan_local_video_candidates(
    metadata_rows: list[Candidate],
    output_root: Path,
    sample_step_seconds: int,
    max_seconds_per_video: int,
    progress_every: int,
) -> list[Candidate]:
    if cv2 is None or np is None:
        raise SystemExit("opencv-python and numpy are required for --scan-local-video")
    candidates: list[Candidate] = []
    seen_videos: set[str] = set()
    for video_number, base in enumerate(metadata_rows, start=1):
        if not base.local_source_path or base.local_source_path in seen_videos:
            continue
        seen_videos.add(base.local_source_path)
        source = Path(base.local_source_path)
        if not source.exists():
            continue
        cap = cv2.VideoCapture(str(source))
        if not cap.isOpened():
            continue
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        duration = int(frame_count / fps) if fps else 0
        limit = min(duration, max_seconds_per_video) if max_seconds_per_video > 0 else duration
        video_root = output_root / source.stem
        video_root.mkdir(parents=True, exist_ok=True)
        video_candidates = 0
        print(
            f"Scanning {video_number}: {base.record_id} {source.name} "
            f"duration={duration}s limit={limit}s step={sample_step_seconds}s"
        )
        for second in range(0, max(limit, 0) + 1, max(sample_step_seconds, 1)):
            if progress_every > 0 and second > 0 and second % progress_every == 0:
                print(f"  {base.record_id}: reached {second}s, candidates={video_candidates}")
            frame_index = int(second * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ok, frame = cap.read()
            if not ok:
                continue
            detected, detail, bbox = classify_textlike_region(frame)
            if not detected or bbox is None:
                continue
            x, y, w, h = bbox
            pad = 20
            x0 = max(0, x - pad)
            y0 = max(0, y - pad)
            x1 = min(frame.shape[1], x + w + pad)
            y1 = min(frame.shape[0], y + h + pad)
            crop = frame[y0:y1, x0:x1]
            crop_path = video_root / f"{source.stem}_t{second:05d}_overlay_candidate.jpg"
            cv2.imwrite(str(crop_path), crop, [int(cv2.IMWRITE_JPEG_QUALITY), 94])
            video_candidates += 1
            candidates.append(
                Candidate(
                    candidate_id=f"{base.record_id}-SCAN-{second:05d}",
                    record_id=base.record_id,
                    release_tag=base.release_tag,
                    video_name=base.video_name or source.name,
                    dvids_id=base.dvids_id,
                    dvids_url=base.dvids_url,
                    source_basis="local-media textlike overlay scan",
                    source_status="repo-local derived crop; source media excluded",
                    approx_second=str(second),
                    frame_index=str(frame_index),
                    label_text_observed="unread by script",
                    label_family="candidate overlay text cluster",
                    candidate_class="computer-vision textlike overlay candidate",
                    classification_status="requires manual/OCR review",
                    alteration_status=base.alteration_status,
                    fresh_clone_reproducible="no: requires excluded source media",
                    local_source_path=str(source),
                    crop_path=str(crop_path),
                    evidence_detail=detail,
                    ambiguity_notes="Computer-vision textlike cluster detection is a triage cue, not OCR or telemetry validation.",
                    next_action="Manually inspect crop and, if measurement-like, add label-persistence rows around adjacent frames.",
                )
            )
        cap.release()
        print(f"Completed {base.record_id}: {video_candidates} local-media candidates")
    return candidates


def write_summary(path: Path, rows: list[Candidate], scanned_video: bool) -> None:
    counts_by_class = Counter(row.candidate_class for row in rows)
    counts_by_status = Counter(row.classification_status for row in rows)
    explicit = [row for row in rows if row.candidate_class == "explicit measurement-like overlay candidate"]
    metadata = [row for row in rows if row.candidate_class == "overlay/measurement scan target"]
    local_scan = [row for row in rows if row.candidate_class == "computer-vision textlike overlay candidate"]

    lines = [
        "# UFO Overlay Measurement Audit",
        "",
        "Owner: Dan Fredriksen",
        "Generated by: `scripts/build_ufo_overlay_measurement_audit.py`",
        "Status: measurement-overlay exploitation lane index",
        "",
        "## Purpose",
        "",
        "This audit tracks visible measurement-like overlays, reticle annotations, sensor-display labels, and frame-scan targets across the public UAP release corpus.",
        "",
        "It does not treat visible labels such as `5m`, `10m`, or `10M` as physical object measurements until label semantics, frame persistence, and source provenance are resolved.",
        "",
        "## Current Result",
        "",
        f"- Total rows: `{len(rows)}`",
        f"- Explicit measurement-like overlay candidates: `{len(explicit)}`",
        f"- Metadata-only scan targets: `{len(metadata)}`",
        f"- Local-media textlike scan candidates: `{len(local_scan)}`",
        f"- Local-media scan mode used: `{'yes' if scanned_video else 'no'}`",
        "",
    ]
    if PR44_PERSISTENCE_CSV.exists() and not scanned_video:
        lines.extend(
            [
                "## Exploitation Addendum",
                "",
                "The first focused local-media exploitation pass has been completed for PR44. It generated a PR44-specific local scan table and a manual label-persistence table:",
                "",
                "- `research/ufo-overlay-measurement-pr44-local-scan.csv`",
                "- `research/ufo-overlay-measurement-pr44-local-scan.md`",
                "- `research/ufo-overlay-measurement-pr44-label-persistence.csv`",
                "- `research/ufo-overlay-measurement-pr44-label-persistence.md`",
                "",
                "Manual review found a persistent meter-like label beside the PR44 reticle/track box: `11M` from about `230-233s`, then `10M` from about `234-249s`. The label is telemetry-like, but its semantics remain unresolved.",
                "",
            ]
        )
    lines.extend(["## Candidate Classes", ""])
    for key, count in sorted(counts_by_class.items()):
        lines.append(f"- `{key}`: `{count}`")
    lines.extend(["", "## Classification Status", ""])
    for key, count in sorted(counts_by_status.items()):
        lines.append(f"- `{key}`: `{count}`")
    lines.extend(
        [
            "",
            "## Explicit Measurement-Like Candidates",
            "",
            "| Candidate | Case | Label | Status | Next action |",
            "|---|---|---|---|---|",
        ]
    )
    for row in explicit:
        lines.append(
            f"| `{row.candidate_id}` | `{row.record_id}` | `{row.label_text_observed}` | "
            f"{row.classification_status} | {row.next_action} |"
        )
    lines.extend(
        [
            "",
            "## Use Rules",
            "",
            "- Treat this file as a triage and exploitation index, not as a claim that labels are physical size/range measurements.",
            "- Promote a row only after the source interval is isolated, adjacent frames show label persistence, and display semantics are classified.",
            "- Keep altered/replayed Release 02 intervals out of physical kinematic reconstruction unless original unaltered frames and telemetry are obtained.",
            "- Source crops under `research/ufo-derived/` are intentionally excluded from Git.",
            "",
            "## Rebuild",
            "",
            "Fresh-clone metadata and known-candidate rebuild:",
            "",
            "```powershell",
            "python scripts/build_ufo_overlay_measurement_audit.py",
            "```",
            "",
            "Local-media scan, when excluded MP4s are present:",
            "",
            "```powershell",
            "python scripts/build_ufo_overlay_measurement_audit.py --scan-local-video --sample-step-seconds 1",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the UAP measurement-overlay exploitation audit.")
    parser.add_argument("--release-manifest", action="append", type=Path, dest="release_manifests")
    parser.add_argument("--unique-videos", type=Path, default=DEFAULT_UNIQUE_VIDEOS)
    parser.add_argument("--correlation-matrix", type=Path, default=DEFAULT_CORRELATION_MATRIX)
    parser.add_argument("--pr44-overlay", type=Path, default=DEFAULT_PR44_OVERLAY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--derived-root", type=Path, default=DEFAULT_DERIVED_ROOT)
    parser.add_argument("--scan-local-video", action="store_true")
    parser.add_argument(
        "--record-id",
        action="append",
        default=[],
        help="Limit metadata/local-media scan to one or more release record IDs, such as DOW-UAP-PR44.",
    )
    parser.add_argument("--sample-step-seconds", type=int, default=1)
    parser.add_argument("--max-seconds-per-video", type=int, default=0)
    parser.add_argument("--progress-every-seconds", type=int, default=30)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest_paths = args.release_manifests or DEFAULT_RELEASE_MANIFESTS
    release_lookup = build_release_lookup(manifest_paths)
    video_lookup = build_video_lookup(args.unique_videos)
    record_video_lookup = build_record_video_lookup(args.correlation_matrix)

    rows: list[Candidate] = []
    rows.extend(known_pr44_candidates(args.pr44_overlay, release_lookup))
    rows.append(known_pr051_candidate(release_lookup))
    rows.append(known_pr059_candidate(release_lookup))

    metadata_rows = metadata_scan_candidates(manifest_paths, video_lookup, record_video_lookup)
    if args.record_id:
        wanted = {normalize_record_id(record_id) for record_id in args.record_id}
        metadata_rows = [row for row in metadata_rows if normalize_record_id(row.record_id) in wanted]
    explicit_ids = {row.record_id for row in rows}
    rows.extend(row for row in metadata_rows if row.record_id not in explicit_ids)

    if args.scan_local_video:
        rows.extend(
            scan_local_video_candidates(
                metadata_rows=metadata_rows,
                output_root=args.derived_root,
                sample_step_seconds=args.sample_step_seconds,
                max_seconds_per_video=args.max_seconds_per_video,
                progress_every=args.progress_every_seconds,
            )
        )

    rows.sort(key=lambda row: (row.release_tag, row.record_id, row.candidate_id))
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows, args.scan_local_video)
    print(f"Wrote {len(rows)} rows to {args.output}")
    print(f"Wrote summary to {args.summary_output}")


if __name__ == "__main__":
    main()
