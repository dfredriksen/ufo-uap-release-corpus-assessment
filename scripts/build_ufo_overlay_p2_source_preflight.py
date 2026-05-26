from __future__ import annotations

import argparse
import csv
import html
import re
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "research"
DEFAULT_RESIDUAL_PLAN = DOCS / "ufo-overlay-measurement-residual-scan-plan.csv"
DEFAULT_OUTPUT = DOCS / "ufo-overlay-measurement-p2-source-preflight.csv"
DEFAULT_SUMMARY = DOCS / "ufo-overlay-measurement-p2-source-preflight.md"

FIELDNAMES = [
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
    "mp4_content_type",
    "source_acquisition_status",
    "recommended_next_action",
    "accessed_utc",
]

USER_AGENT = "ufo-uap-release-corpus-assessment/overlay-p2-preflight (+https://github.com/dfredriksen/ufo-uap-release-corpus-assessment)"


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def fetch_text(url: str, timeout: int) -> tuple[str, str, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            content = response.read().decode(charset, errors="replace")
            return f"http_{response.status}", response.geturl(), content
    except urllib.error.HTTPError as exc:
        return f"http_{exc.code}", url, ""
    except urllib.error.URLError as exc:
        return f"url_error:{exc.reason}", url, ""
    except TimeoutError:
        return "timeout", url, ""


def head_url(url: str, timeout: int) -> tuple[str, str, str]:
    if not url:
        return "", "", ""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return (
                f"http_{response.status}",
                response.headers.get("Content-Length", ""),
                response.headers.get("Content-Type", ""),
            )
    except urllib.error.HTTPError as exc:
        return f"http_{exc.code}", "", exc.headers.get("Content-Type", "")
    except urllib.error.URLError as exc:
        return f"url_error:{exc.reason}", "", ""
    except TimeoutError:
        return "timeout", "", ""


def meta_content(page: str, property_name: str) -> str:
    pattern = re.compile(
        rf'<meta\s+[^>]*(?:property|name)=["\']{re.escape(property_name)}["\'][^>]*content=["\']([^"\']*)["\']',
        re.IGNORECASE,
    )
    match = pattern.search(page)
    return html.unescape(match.group(1)).strip() if match else ""


def first_match(page: str, pattern: str) -> str:
    match = re.search(pattern, page, re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return html.unescape(match.group(1)).strip()


def embedded_mp4(page: str) -> str:
    match = re.search(r"https?://[^\"'<> ]+/video/[^\"'<> ]+?\.mp4", page, re.IGNORECASE)
    return match.group(0) if match else ""


def extract_page_metadata(page: str) -> dict[str, str]:
    description = meta_content(page, "og:description")
    return {
        "title": meta_content(page, "og:title"),
        "filename": first_match(page, r"<td>\s*Filename:\s*</td>\s*<td>\s*([^<]+)\s*</td>"),
        "duration": first_match(description, r"Video Duration:\s*([0-9:]+)")
        or first_match(page, r"Video Duration:\s*([0-9:]+)"),
        "mp4": embedded_mp4(page),
    }


def content_length_mb(content_length: str) -> str:
    try:
        return f"{int(content_length) / (1024 * 1024):.2f}"
    except ValueError:
        return ""


def build_rows(residual_plan: Path, timeout: int) -> list[dict[str, str]]:
    accessed = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rows: list[dict[str, str]] = []
    for target in read_csv(residual_plan):
        priority_band = clean(target.get("priority_band"))
        current_status = clean(target.get("current_lane_status"))
        has_local_source = bool(clean(target.get("local_source_hint")))
        if (
            priority_band != "P2"
            or current_status not in {"metadata_only_unclassified", "source_preflighted_not_acquired"}
            or has_local_source
        ):
            continue

        page_status, resolved_url, page = fetch_text(clean(target.get("dvids_url")), timeout)
        metadata = extract_page_metadata(page) if page else {"title": "", "filename": "", "duration": "", "mp4": ""}
        head_status, content_length, content_type = head_url(metadata["mp4"], timeout)
        acquisition_status = "embedded_public_mp4_found_not_downloaded" if metadata["mp4"] else "no_embedded_public_mp4_found"
        if head_status and not head_status.startswith("http_2"):
            acquisition_status = f"{acquisition_status}; head_{head_status}"
        rows.append(
            {
                "residual_id": clean(target.get("residual_id")),
                "record_id": clean(target.get("record_id")),
                "release_tag": clean(target.get("release_tag")),
                "dvids_id": clean(target.get("dvids_id")),
                "dvids_url": clean(target.get("dvids_url")),
                "matched_terms": clean(target.get("matched_terms")),
                "priority_band": priority_band,
                "current_lane_status": current_status,
                "page_fetch_status": page_status,
                "resolved_page_url": resolved_url,
                "dvids_title": metadata["title"],
                "dvids_filename": metadata["filename"],
                "dvids_duration": metadata["duration"],
                "embedded_public_mp4_url": metadata["mp4"],
                "mp4_head_status": head_status,
                "mp4_content_length": content_length,
                "mp4_content_length_mb": content_length_mb(content_length),
                "mp4_content_type": content_type,
                "source_acquisition_status": acquisition_status,
                "recommended_next_action": "If disk space permits, acquire source MP4 outside the repo, hash it, then run display-focused OCR/contact-sheet review before classification.",
                "accessed_utc": accessed,
            }
        )
    rows.sort(key=lambda row: (row["record_id"], row["residual_id"]))
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(path: Path, rows: list[dict[str, str]]) -> None:
    by_status = Counter(row["source_acquisition_status"].split(";")[0] for row in rows)
    total_bytes = sum(int(row["mp4_content_length"]) for row in rows if row["mp4_content_length"].isdigit())
    lines = [
        "# Overlay Measurement P2 Source Preflight",
        "",
        "Owner: Dan Fredriksen",
        "Generated by: `scripts/build_ufo_overlay_p2_source_preflight.py`",
        "Scope: unlocalized P2 residual overlay source-acquisition targets",
        "",
        "## Purpose",
        "",
        "This preflight records whether the remaining unreviewed P2 residual rows expose public DVIDS page metadata and embedded public MP4 URLs. It does not download or redistribute source media.",
        "",
        "## Summary",
        "",
        f"- P2 source pages checked: `{len(rows)}`",
        f"- Total advertised MP4 size: `{total_bytes / (1024 * 1024):.2f} MB`",
    ]
    for status, count in sorted(by_status.items()):
        lines.append(f"- `{status}`: `{count}`")
    lines.extend(
        [
            "",
            "## Source Size Queue",
            "",
            "| Record ID | DVIDS filename | MP4 size MB | Duration |",
            "|---|---|---:|---:|",
        ]
    )
    for row in sorted(rows, key=lambda item: float(item["mp4_content_length_mb"] or 0)):
        lines.append(
            f"| `{row['record_id']}` | `{row['dvids_filename']}` | `{row['mp4_content_length_mb'] or 'unknown'}` | `{row['dvids_duration']}` |"
        )
    lines.extend(
        [
            "",
            "## Use Boundary",
            "",
            "Rows in this preflight are acquisition/provenance leads, not overlay findings. A row remains unclassified until the source MP4 is retained outside the repo, hashed, frame-reviewed, and classified under `research/ufo-overlay-measurement-classification.csv`.",
            "",
            "Supporting table:",
            "",
            "- `research/ufo-overlay-measurement-p2-source-preflight.csv`",
            "",
            "Validation:",
            "",
            "- `scripts/validate_overlay_p2_source_preflight.py`",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Preflight P2 residual DVIDS source pages for embedded public MP4 URLs.")
    parser.add_argument("--residual-plan", type=Path, default=DEFAULT_RESIDUAL_PLAN)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--timeout", type=int, default=20)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rows = build_rows(args.residual_plan, args.timeout)
    write_csv(args.output, rows)
    write_summary(args.summary_output, rows)
    print(f"Wrote {len(rows)} P2 preflight rows to {args.output}")
    print(f"Wrote summary to {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
