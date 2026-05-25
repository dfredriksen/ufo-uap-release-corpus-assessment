from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path


OFFICIAL_MANIFEST_URL = "https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv"
OFFICIAL_UFO_PAGE = "https://www.war.gov/UFO/"
OFFICIAL_RELEASE_01_PAGE = "https://www.war.gov/News/Releases/Release/Article/4480582/department-of-war-releases-unidentified-anomalous-phenomena-files-in-historic-t/"
OFFICIAL_RELEASE_02_PAGE = "https://www.war.gov/News/Releases/Release/Article/4499305/department-of-war-publishes-second-release-of-unidentified-anomalous-phenomena/"

OUTPUT_RELEASE_01_TAG = "release-01"
OUTPUT_RELEASE_02_TAG = "release-02"
DEFAULT_RELEASE_DATE = "5/8/26"
RELEASE_01_DATE = "5/8/26"
RELEASE_02_DATE = "5/22/26"


def clean(value: str | None) -> str:
    return " ".join((value or "").replace("\ufeff", "").split()).strip()


def filename_from_url(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.unquote(Path(parsed.path).name)


def extension_from_filename(name: str) -> str:
    suffix = Path(name).suffix.lower()
    return suffix if suffix else ""


def source_basename(value: str) -> str:
    return value.casefold()


def document_family(title: str, row_type: str) -> str:
    lowered = title.lower()
    if row_type == "VID":
        if "unresolved uap report" in lowered:
            return "public-release video"
        if "audio excerpt" in lowered:
            return "audio/video media"
        return "video"
    if "mission report" in lowered:
        return "mission report"
    if "range fouler" in lowered:
        return "range fouler"
    if "email correspondence" in lowered or "email correspondance" in lowered:
        return "email correspondence"
    if "department of the air force report" in lowered:
        return "air force report"
    if "launch summary" in lowered:
        return "launch summary"
    if "photo" in lowered or row_type == "IMG":
        return "image/photo"
    if "transcript" in lowered or "audio" in lowered:
        return "transcript/audio"
    if (
        "general" in lowered
        or "incident summaries" in lowered
        or "numerical" in lowered
        or "records relating" in lowered
        or "flying discs" in lowered
        or "case file" in lowered
    ):
        return "historical archive file"
    return "other"


def record_identifier(title: str) -> str:
    patterns = [
        r"DOW-UAP-(?:PR|D)\d+[A-Z]?",
        r"NASA-UAP-D\d+[A-Z]?",
        r"DOS-UAP-D\d+[A-Z]?",
        r"CIA-UAP-D\d+[A-Z]?",
        r"DOE-UAP-D\d+[A-Z]?",
        r"ODNI-UAP-D\d+[A-Z]?",
    ]
    for pattern in patterns:
        match = re.search(pattern, title, flags=re.IGNORECASE)
        if match:
            return match.group(0).upper()
    return ""


def fetch_url_via_urllib(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
            "Accept": "text/csv,text/plain,*/*",
            "Referer": OFFICIAL_UFO_PAGE,
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read()
    return data.decode("utf-8-sig")


def fetch_url_via_node(url: str) -> str:
    node = shutil.which("node")
    if not node:
        raise RuntimeError("node executable not found")

    js = (
        "const url = "
        + json.dumps(url)
        + ";"
        + "const res = await fetch(url, {"
        + "headers: {"
        + "'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36',"
        + "'accept': 'text/csv,text/plain,*/*',"
        + "'referer': 'https://www.war.gov/UFO/'"
        + "}"
        + "});"
        + "if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);"
        + "process.stdout.write(await res.text());"
    )
    completed = subprocess.run(
        [node, "--input-type=module", "-e", js],
        capture_output=True,
        text=False,
        timeout=90,
        check=False,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        stdout = completed.stdout.decode("utf-8", errors="replace").strip()
        detail = stderr or stdout or f"exit code {completed.returncode}"
        raise RuntimeError(detail)
    return completed.stdout.decode("utf-8-sig", errors="replace")


def fetch_url(url: str) -> str:
    try:
        return fetch_url_via_urllib(url)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError):
        return fetch_url_via_node(url)


def load_manifest(args: argparse.Namespace) -> tuple[str, str, str]:
    if args.manifest_csv:
        return args.manifest_csv.read_text(encoding="utf-8-sig"), str(args.manifest_csv), "local manifest snapshot"

    return fetch_url(OFFICIAL_MANIFEST_URL), OFFICIAL_MANIFEST_URL, "official War.gov CSV endpoint"


def load_local_manifest(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return {source_basename(row["name"]): row for row in csv.DictReader(handle)}


def manifest_rows(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for index, row in enumerate(reader, start=1):
        title = clean(row.get("Title"))
        if not title:
            continue
        row["_source_row"] = str(index)
        rows.append(row)
    return rows


def filter_release_rows(rows: list[dict], release_date: str | None) -> list[dict]:
    if not release_date:
        return rows
    return [row for row in rows if clean(row.get("Release Date")) == release_date]


def normalize_rows(rows: list[dict], local_manifest: dict[str, dict], retrieval_source: str, retrieval_note: str) -> list[dict]:
    normalized: list[dict] = []
    for row in rows:
        title = clean(row.get("Title"))
        row_type = clean(row.get("Type"))
        asset_url = clean(row.get("PDF | Image Link"))
        thumbnail_url = clean(row.get("Modal Image"))
        asset_filename = filename_from_url(asset_url)
        thumbnail_filename = filename_from_url(thumbnail_url)
        local = local_manifest.get(source_basename(asset_filename))
        dvids_id = clean(row.get("DVIDS Video ID"))
        normalized.append(
            {
                "source_row": row["_source_row"],
                "manifest_retrieval_source": retrieval_source,
                "manifest_retrieval_note": retrieval_note,
                "record_id": record_identifier(title),
                "title": title,
                "type": row_type,
                "family": document_family(title, row_type),
                "agency": clean(row.get("Agency")),
                "release_date": clean(row.get("Release Date")),
                "incident_date": clean(row.get("Incident Date")),
                "incident_location": clean(row.get("Incident Location")),
                "redaction_flag": clean(row.get("Redaction")),
                "video_pairing": clean(row.get("Video Pairing")),
                "pdf_pairing": clean(row.get("PDF Pairing")),
                "dvids_video_id": dvids_id,
                "dvids_url": f"https://www.dvidshub.net/video/{dvids_id}" if dvids_id else "",
                "dvids_video_title": clean(row.get("Video Title")),
                "asset_url": asset_url,
                "asset_filename": asset_filename,
                "asset_extension": extension_from_filename(asset_filename),
                "thumbnail_url": thumbnail_url,
                "thumbnail_filename": thumbnail_filename,
                "local_exact_filename_match": "yes" if local else "no" if asset_filename else "",
                "local_bytes": local.get("bytes", "") if local else "",
                "local_source_path": local.get("source_path", "") if local else "",
                "description_blurb": clean(row.get("Description Blurb")),
            }
        )
    return normalized


def unique_asset_rows(normalized: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for row in normalized:
        asset_url = row["asset_url"]
        if not asset_url:
            continue
        key = asset_url.casefold()
        current = grouped.setdefault(
            key,
            {
                "asset_url": asset_url,
                "asset_filename": row["asset_filename"],
                "asset_extension": row["asset_extension"],
                "manifest_types": set(),
                "record_ids": set(),
                "titles": [],
                "agencies": set(),
                "local_exact_filename_match": row["local_exact_filename_match"],
                "local_bytes": row["local_bytes"],
                "local_source_path": row["local_source_path"],
            },
        )
        current["manifest_types"].add(row["type"])
        if row["record_id"]:
            current["record_ids"].add(row["record_id"])
        current["titles"].append(row["title"])
        current["agencies"].add(row["agency"])

    output = []
    for item in grouped.values():
        output.append(
            {
                "asset_url": item["asset_url"],
                "asset_filename": item["asset_filename"],
                "asset_extension": item["asset_extension"],
                "manifest_types": "; ".join(sorted(item["manifest_types"])),
                "record_ids": "; ".join(sorted(item["record_ids"])),
                "record_count": len(item["titles"]),
                "agencies": "; ".join(sorted(item["agencies"])),
                "local_exact_filename_match": item["local_exact_filename_match"],
                "local_bytes": item["local_bytes"],
                "local_source_path": item["local_source_path"],
                "titles": " | ".join(item["titles"]),
            }
        )
    return sorted(output, key=lambda row: (row["asset_extension"], row["asset_filename"].casefold()))


def summary_rows(normalized: list[dict], assets: list[dict]) -> list[dict]:
    summaries: list[dict] = []

    def add_counter(group: str, counter: Counter) -> None:
        for key, count in sorted(counter.items()):
            summaries.append({"summary_group": group, "summary_key": key or "(blank)", "count": count})

    add_counter("type", Counter(row["type"] for row in normalized))
    add_counter("agency", Counter(row["agency"] for row in normalized))
    add_counter("agency_type", Counter(f"{row['agency']} | {row['type']}" for row in normalized))
    add_counter("department_of_war_family", Counter(row["family"] for row in normalized if row["agency"] == "Department of War"))
    add_counter("redaction_flag", Counter(row["redaction_flag"] or "(blank)" for row in normalized))
    add_counter("local_asset_exact_match", Counter(row["local_exact_filename_match"] or "(no linked asset)" for row in normalized))

    summaries.extend(
        [
            {"summary_group": "manifest", "summary_key": "records", "count": len(normalized)},
            {"summary_group": "manifest", "summary_key": "records_with_dvids_video_id", "count": sum(1 for row in normalized if row["dvids_video_id"])},
            {"summary_group": "manifest", "summary_key": "records_with_asset_url", "count": sum(1 for row in normalized if row["asset_url"])},
            {"summary_group": "asset", "summary_key": "unique_linked_assets", "count": len(assets)},
            {"summary_group": "asset", "summary_key": "unique_linked_assets_exact_local_match", "count": sum(1 for row in assets if row["local_exact_filename_match"] == "yes")},
            {"summary_group": "asset", "summary_key": "unique_linked_assets_no_exact_local_match", "count": sum(1 for row in assets if row["local_exact_filename_match"] == "no")},
        ]
    )
    return summaries


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not fieldnames:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    widths = [max(len(str(row[index])) for row in rows) for index in range(len(rows[0]))]
    output = []
    for index, row in enumerate(rows):
        output.append("| " + " | ".join(str(value).ljust(widths[column]) for column, value in enumerate(row)) + " |")
        if index == 0:
            output.append("| " + " | ".join("-" * widths[column] for column in range(len(row))) + " |")
    return "\n".join(output)


def release_label_for_tag(release_tag: str) -> str:
    return " ".join(part.capitalize() for part in release_tag.replace("_", "-").split("-"))


def highlight_row_ids(release_date: str | None) -> set[str]:
    if release_date == RELEASE_02_DATE:
        return {
            "DOW-UAP-PR050",
            "DOW-UAP-PR051",
            "DOW-UAP-D017",
            "CIA-UAP-D001",
            "ODNI-UAP-D001",
            "NASA-UAP-D008",
            "DOE-UAP-D001",
            "DOW-UAP-PR057b",
            "DOW-UAP-PR065",
            "DOW-UAP-PR071",
            "DOW-UAP-PR075",
            "DOW-UAP-PR098",
        }
    return {"DOW-UAP-D44", "DOW-UAP-D57", "DOW-UAP-D58", "DOW-UAP-D50", "DOW-UAP-D51", "DOW-UAP-D52"}


def selected_rows_for_notes(normalized: list[dict], release_date: str | None) -> list[dict]:
    selected_ids = highlight_row_ids(release_date)
    selected = [row for row in normalized if row["record_id"] in selected_ids]
    if release_date == RELEASE_02_DATE:
        selected = sorted(selected, key=lambda row: (row["agency"], row["type"], row["title"]))
    return selected


def output_paths(release_tag: str) -> dict[str, Path]:
    prefix = f"research/war-gov-ufo-{release_tag}"
    return {
        "normalized": Path(f"{prefix}-manifest-normalized.csv"),
        "assets": Path(f"{prefix}-asset-coverage.csv"),
        "dow": Path(f"{prefix}-dow-documents.csv"),
        "summary": Path(f"{prefix}-metadata-summary.csv"),
        "notes": Path(f"{prefix}-metadata-notes.md"),
        "delta": Path(f"{prefix}-delta.csv"),
    }


def write_notes(
    normalized: list[dict],
    assets: list[dict],
    retrieval_source: str,
    retrieval_note: str,
    release_tag: str,
    release_date: str | None,
    output_map: dict[str, Path],
    delta_summary: list[dict],
    feed_counts: dict[str, int],
) -> None:
    type_counts = Counter(row["type"] for row in normalized)
    agency_counts = Counter(row["agency"] for row in normalized)
    dow_family_counts = Counter(row["family"] for row in normalized if row["agency"] == "Department of War")
    selected_rows = selected_rows_for_notes(normalized, release_date)
    selected_table = [["Record", "Type", "Incident date", "Location", "Pairing fields"]]
    for row in selected_rows:
        pairing = f"video={row['video_pairing'] or '-'}; pdf={row['pdf_pairing'] or '-'}"
        selected_table.append([row["record_id"], row["type"], row["incident_date"], row["incident_location"], pairing])

    release_label = release_label_for_tag(release_tag)
    output_lines = [f"- `{value.as_posix()}`" for value in output_map.values()]
    delta_lines = []
    if delta_summary:
        delta_lines = [f"- `{item['summary_key']}`: `{item['count']}`" for item in delta_summary]

    lines = [
        f"# War.gov UFO {release_label} Metadata Notes",
        "",
        "Owner: Dan Fredriksen",
        "Created: 2026-05-23",
        f"Official UFO page: `{OFFICIAL_UFO_PAGE}`",
        f"Official release 01 page: `{OFFICIAL_RELEASE_01_PAGE}`",
        f"Official release 02 page: `{OFFICIAL_RELEASE_02_PAGE}`",
        f"Official manifest endpoint: `{OFFICIAL_MANIFEST_URL}`",
        f"Manifest retrieval used for this snapshot: `{retrieval_source}`",
        f"Retrieval note: {retrieval_note}",
        "",
        "## Scope",
        "",
        f"This pass normalizes the War.gov UFO {release_label} manifest subset into repo-local research tables. It records the manifest metadata fields, official asset URLs, DVIDS IDs, and exact local filename coverage against `research/ufo-file-manifest.csv`.",
        "",
        "The live WAR.GOV feed is now a combined tranche index. This run filters the current feed by release date, so the output remains tranche-specific while still using the official source of record.",
        "",
        "## Outputs",
        "",
        *output_lines,
        "",
        "## Manifest Counts",
        "",
        markdown_table([["Type", "Rows"], *[[key, str(type_counts[key])] for key in sorted(type_counts)]]),
        "",
        markdown_table([["Agency", "Rows"], *[[key, str(agency_counts[key])] for key in sorted(agency_counts)]]),
        "",
        "Department of War family breakdown:",
        "",
        markdown_table([["Family", "Rows"], *[[key, str(dow_family_counts[key])] for key in sorted(dow_family_counts)]]),
        "",
        "## Local Asset Coverage",
        "",
        f"The manifest has `{sum(1 for row in normalized if row['asset_url'])}` rows with a linked asset URL and `{len(assets)}` unique linked asset URLs. Exact basename comparison against the local UFO manifest finds `{sum(1 for row in assets if row['local_exact_filename_match'] == 'yes')}` unique linked assets present locally and `{sum(1 for row in assets if row['local_exact_filename_match'] == 'no')}` without an exact local filename match.",
        "",
        "This is exact filename coverage only. It does not prove a file was not downloaded under a renamed basename, and it does not evaluate DVIDS-hosted MP4 video downloads because those are tracked separately in the release-index sweep.",
        "",
        "## Tranche Delta",
        "",
        "Release 02 is additive against the current live feed. It introduces a new tranche of records with no exact record-id or DVIDS-video-id overlap against Release 01 in the current combined feed snapshot.",
        "",
        delta_lines[0] if delta_lines else "- No explicit delta rows were generated for this run.",
        *delta_lines[1:],
        "",
        "## Initial Takeaways",
        "",
        f"- The live feed now contains both tranches: `{feed_counts.get('release_01', 0)}` Release 01 rows and `{feed_counts.get('release_02', 0)}` Release 02 rows, `{feed_counts.get('combined', 0)}` total records.",
        "- Release 02 broadens the corpus with more Department of War video records, plus NASA audio, DOE imagery/correspondence, CIA historical reporting, ODNI narrative material, and a new Sandia/PANTEX lane.",
        "- The new material is mostly additive evidence breadth, not a change in claim ceiling. The new tranche gives more report families to cross-check, but it still requires deeper source review before any stronger interpretation.",
        "- The most immediately interesting Release 02 rows are the PANTEX imagery, Sandia Base correspondence, CIA USSR report, ODNI USPER narrative, Apollo 12 audio, and the modern PR050-PR099 video cluster.",
        "",
        "## Selected Report Rows",
        "",
        markdown_table(selected_table),
        "",
        "## Next Work",
        "",
        "Use the normalized manifest as the upstream metadata layer for tranche synthesis. The next focused pass should compare the new Release 02 Department of War document rows against local extracted text, DVIDS page identities, exact local file coverage, and the existing evidence ladder before promoting any case.",
    ]
    output_map["notes"].write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_delta_rows(
    normalized: list[dict],
    previous_rows: list[dict],
    local_manifest: dict[str, dict],
) -> tuple[list[dict], list[dict]]:
    previous_record_ids = {row["record_id"] for row in previous_rows if row["record_id"]}
    previous_asset_urls = {row["asset_url"].casefold() for row in previous_rows if row["asset_url"]}
    previous_video_ids = {row["dvids_video_id"] for row in previous_rows if row["dvids_video_id"]}

    delta_rows: list[dict] = []
    delta_summary = Counter()

    for row in normalized:
        record_id = row["record_id"]
        asset_url = row["asset_url"]
        dvids_id = row["dvids_video_id"]
        status = "new"
        if record_id and record_id in previous_record_ids:
            status = "existing_record_id"
        elif asset_url and asset_url.casefold() in previous_asset_urls:
            status = "existing_asset_url"
        elif dvids_id and dvids_id in previous_video_ids:
            status = "existing_dvids_video_id"
        local_match = row["asset_filename"] and source_basename(row["asset_filename"]) in local_manifest
        delta_rows.append(
            {
                "record_id": record_id,
                "title": row["title"],
                "agency": row["agency"],
                "type": row["type"],
                "release_date": row["release_date"],
                "status": status,
                "asset_url": asset_url,
                "asset_filename": row["asset_filename"],
                "dvids_video_id": dvids_id,
                "local_exact_filename_match": "yes" if local_match else "no" if row["asset_filename"] else "",
            }
        )
        delta_summary[status] += 1

    summary_rows_delta = [{"summary_key": key, "count": count} for key, count in sorted(delta_summary.items())]
    return delta_rows, summary_rows_delta


def run(args: argparse.Namespace) -> None:
    manifest_text, retrieval_source, retrieval_note = load_manifest(args)
    raw_rows = manifest_rows(manifest_text)
    local_manifest = load_local_manifest(args.local_manifest)
    release_rows = filter_release_rows(raw_rows, args.release_date)
    normalized = normalize_rows(release_rows, local_manifest, retrieval_source, retrieval_note)
    assets = unique_asset_rows(normalized)
    dow_documents = [row for row in normalized if row["agency"] == "Department of War"]
    summaries = summary_rows(normalized, assets)
    output_map = output_paths(args.release_tag)

    previous_release_date = RELEASE_01_DATE if args.release_date == RELEASE_02_DATE else None
    previous_rows = filter_release_rows(raw_rows, previous_release_date)
    previous_normalized = normalize_rows(previous_rows, local_manifest, retrieval_source, retrieval_note) if previous_rows else []
    delta_rows, delta_summary = build_delta_rows(normalized, previous_normalized, local_manifest)
    feed_counts = {
        "combined": len(raw_rows),
        "release_01": len(filter_release_rows(raw_rows, RELEASE_01_DATE)),
        "release_02": len(filter_release_rows(raw_rows, RELEASE_02_DATE)),
    }

    write_csv(output_map["normalized"], normalized)
    write_csv(output_map["assets"], assets)
    write_csv(output_map["dow"], dow_documents)
    write_csv(output_map["summary"], summaries)
    write_csv(output_map["delta"], delta_rows)
    write_notes(normalized, assets, retrieval_source, retrieval_note, args.release_tag, args.release_date, output_map, delta_summary, feed_counts)

    print(f"Wrote {output_map['normalized']}")
    print(f"Wrote {output_map['assets']}")
    print(f"Wrote {output_map['dow']}")
    print(f"Wrote {output_map['summary']}")
    print(f"Wrote {output_map['delta']}")
    print(f"Wrote {output_map['notes']}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize War.gov UFO release manifest metadata.")
    parser.add_argument("--manifest-csv", type=Path, help="Optional local copy of uap-data.csv or a tranche snapshot.")
    parser.add_argument("--local-manifest", type=Path, default=Path("research/ufo-file-manifest.csv"))
    parser.add_argument("--release-date", default=DEFAULT_RELEASE_DATE, help="Release date filter in M/D/YY format.")
    parser.add_argument("--release-tag", default=OUTPUT_RELEASE_01_TAG, help="Output tag such as release-01 or release-02.")
    return parser.parse_args()


if __name__ == "__main__":
    run(parse_args())

