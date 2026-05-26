from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research"
DEFAULT_SOURCE_MANIFEST = RESEARCH / "ufo-file-manifest.csv"
DEFAULT_RELEASE_MANIFESTS = [
    ("release-01", RESEARCH / "war-gov-ufo-release-01-manifest-normalized.csv"),
    ("release-02", RESEARCH / "war-gov-ufo-release-02-manifest-normalized.csv"),
]
DEFAULT_OUTPUT = RESEARCH / "ufo-source-acquisition-manifest.csv"
DEFAULT_GAPS = RESEARCH / "ufo-source-acquisition-gaps.csv"
DEFAULT_SUMMARY = RESEARCH / "ufo-source-acquisition-summary.md"
DEFAULT_SOURCE_ROOT = ROOT / "source-files-not-included"


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def parse_int(value: object) -> int | None:
    text = clean(value)
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        return None


def normalize_filename(value: object) -> str:
    return Path(clean(value)).name.casefold()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_source_path(recorded_path: str, source_root: Path | None, use_recorded_paths: bool) -> Path | None:
    if use_recorded_paths and recorded_path:
        candidate = Path(recorded_path)
        if candidate.exists():
            return candidate
    if source_root and recorded_path:
        fallback = source_root / Path(recorded_path).name
        if fallback.exists():
            return fallback
    return None


def load_local_inventory(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_release_assets(path: Path, release_tag: str) -> list[dict[str, str]]:
    assets: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            asset_filename = clean(row.get("asset_filename"))
            if not asset_filename:
                continue
            assets.append(
                {
                    "release_tag": release_tag,
                    "record_id": clean(row.get("record_id")),
                    "title": clean(row.get("title")),
                    "type": clean(row.get("type")),
                    "agency": clean(row.get("agency")),
                    "asset_filename": asset_filename,
                    "asset_url": clean(row.get("asset_url")),
                    "asset_extension": clean(row.get("asset_extension")),
                    "local_exact_filename_match": clean(row.get("local_exact_filename_match")).casefold(),
                    "local_bytes": clean(row.get("local_bytes")),
                    "local_source_path": clean(row.get("local_source_path")),
                    "release_date": clean(row.get("release_date")),
                }
            )
    return assets


def build_release_index(assets: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for asset in assets:
        index[normalize_filename(asset["asset_filename"])].append(asset)
    return index


def select_release_matches(
    name: str, local_bytes: int | None, release_index: dict[str, list[dict[str, str]]]
) -> tuple[list[dict[str, str]], str]:
    candidates = release_index.get(normalize_filename(name), [])
    if not candidates:
        return [], "legacy_local_only"
    if len(candidates) == 1:
        return candidates, "release_exact"

    if local_bytes is not None:
        exact_size = [
            asset
            for asset in candidates
            if parse_int(asset.get("local_bytes")) is not None
            and parse_int(asset.get("local_bytes")) == local_bytes
        ]
        if len(exact_size) == 1:
            return exact_size, "release_exact_size"
        if len(exact_size) > 1:
            return exact_size, "release_ambiguous_size"

    return candidates, "release_ambiguous"


def join_unique(values: list[str]) -> str:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return " | ".join(seen)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    path: Path,
    generated_utc: str,
    local_rows: int,
    hashed_rows: int,
    matched_rows: int,
    legacy_rows: int,
    missing_rows: int,
    gaps_rows: int,
    release_manifest_count: int,
) -> None:
    lines = [
        "# UFO Source Acquisition Summary",
        "",
        f"- Generated: {generated_utc}",
        f"- Local inventory rows: {local_rows}",
        f"- Hashed local rows: {hashed_rows}",
        f"- Release-matched local rows: {matched_rows}",
        f"- Legacy local-only rows: {legacy_rows}",
        f"- Missing local rows: {missing_rows}",
        f"- Release assets requiring exact-match reconciliation: {gaps_rows}",
        f"- Release manifests indexed: {release_manifest_count}",
        "",
        "The acquisition manifest captures local file paths, file sizes, SHA-256 hashes, and any canonical release URLs that map back to the local inventory by exact basename or exact basename plus size.",
        "The gap table lists release assets that are not currently represented as an exact local filename match in the inventory.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a source acquisition manifest for the UFO corpus.")
    parser.add_argument("--source-manifest", type=Path, default=DEFAULT_SOURCE_MANIFEST)
    parser.add_argument(
        "--release-manifest",
        action="append",
        nargs=2,
        metavar=("RELEASE_TAG", "PATH"),
        help="Add a release manifest index entry. May be repeated.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gaps-output", type=Path, default=DEFAULT_GAPS)
    parser.add_argument("--summary-output", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=None,
        help="Directory containing source files by basename. Omit for manifest-only missing-file audit.",
    )
    parser.add_argument(
        "--use-recorded-paths",
        action="store_true",
        help="Also honor absolute source_path values recorded in the local inventory.",
    )
    args = parser.parse_args()

    release_manifests = args.release_manifest or [(tag, path) for tag, path in DEFAULT_RELEASE_MANIFESTS]
    release_assets: list[dict[str, str]] = []
    for release_tag, manifest_path in release_manifests:
        release_assets.extend(load_release_assets(Path(manifest_path), release_tag))
    release_index = build_release_index(release_assets)

    local_inventory = load_local_inventory(args.source_manifest)
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    output_rows: list[dict[str, str]] = []
    gap_rows: list[dict[str, str]] = []
    hashed_rows = 0
    matched_rows = 0
    legacy_rows = 0
    missing_rows = 0

    for row in local_inventory:
        name = clean(row.get("name"))
        extension = clean(row.get("extension"))
        recorded_path = clean(row.get("source_path"))
        inventory_bytes = parse_int(row.get("bytes"))
        filesystem_path = resolve_source_path(recorded_path, args.source_root, args.use_recorded_paths)
        file_exists = filesystem_path is not None
        filesystem_bytes = filesystem_path.stat().st_size if filesystem_path else None
        file_hash = sha256_file(filesystem_path) if filesystem_path else ""
        sha_status = "hashed" if file_hash else "missing"
        if file_hash:
            hashed_rows += 1
        else:
            missing_rows += 1

        matches, match_status = select_release_matches(name, inventory_bytes, release_index)
        if matches:
            matched_rows += 1
        else:
            legacy_rows += 1

        canonical_urls = join_unique([asset["asset_url"] for asset in matches])
        release_tags = join_unique([asset["release_tag"] for asset in matches])
        release_ids = join_unique([asset["record_id"] for asset in matches])
        release_titles = join_unique([asset["title"] for asset in matches])
        release_filenames = join_unique([asset["asset_filename"] for asset in matches])
        notes: list[str] = []
        if matches and match_status.startswith("release_exact"):
            notes.append("release manifest basename match")
        elif matches:
            notes.append("release manifest basename collision")
        else:
            notes.append("legacy local inventory only")
        if not file_exists:
            notes.append("source file not currently accessible on disk")

        output_rows.append(
            {
                "name": name,
                "extension": extension,
                "source_path": recorded_path,
                "expected_local_path": str(filesystem_path or recorded_path),
                "file_exists": "yes" if file_exists else "no",
                "inventory_bytes": str(inventory_bytes or ""),
                "filesystem_bytes": str(filesystem_bytes or ""),
                "last_write_time": clean(row.get("last_write_time")),
                "accessed_utc": generated_utc,
                "sha256": file_hash,
                "sha256_status": sha_status,
                "canonical_source_url": canonical_urls,
                "release_tags": release_tags,
                "release_record_ids": release_ids,
                "release_titles": release_titles,
                "release_asset_filenames": release_filenames,
                "match_status": match_status,
                "match_note": "; ".join(notes),
            }
        )

    for asset in release_assets:
        if asset["local_exact_filename_match"] == "yes" and asset["local_source_path"]:
            continue
        reason = "no exact local filename match"
        if asset["local_exact_filename_match"] == "yes" and not asset["local_source_path"]:
            reason = "exact match claimed but local path missing"
        elif asset["local_exact_filename_match"] != "yes" and asset["local_source_path"]:
            reason = "path recorded, but exact filename match not confirmed"
        gap_rows.append(
            {
                "release_tag": asset["release_tag"],
                "record_id": asset["record_id"],
                "title": asset["title"],
                "type": asset["type"],
                "agency": asset["agency"],
                "asset_filename": asset["asset_filename"],
                "asset_url": asset["asset_url"],
                "release_date": asset["release_date"],
                "local_exact_filename_match": asset["local_exact_filename_match"],
                "local_bytes": asset["local_bytes"],
                "local_source_path": asset["local_source_path"],
                "gap_reason": reason,
            }
        )

    output_rows.sort(key=lambda row: (row["name"].casefold(), row["extension"].casefold()))
    gap_rows.sort(key=lambda row: (row["release_tag"], row["record_id"], row["asset_filename"].casefold()))

    write_csv(
        args.output,
        output_rows,
        [
            "name",
            "extension",
            "source_path",
            "expected_local_path",
            "file_exists",
            "inventory_bytes",
            "filesystem_bytes",
            "last_write_time",
            "accessed_utc",
            "sha256",
            "sha256_status",
            "canonical_source_url",
            "release_tags",
            "release_record_ids",
            "release_titles",
            "release_asset_filenames",
            "match_status",
            "match_note",
        ],
    )
    write_csv(
        args.gaps_output,
        gap_rows,
        [
            "release_tag",
            "record_id",
            "title",
            "type",
            "agency",
            "asset_filename",
            "asset_url",
            "release_date",
            "local_exact_filename_match",
            "local_bytes",
            "local_source_path",
            "gap_reason",
        ],
    )
    write_summary(
        args.summary_output,
        generated_utc,
        len(local_inventory),
        hashed_rows,
        matched_rows,
        legacy_rows,
        missing_rows,
        len(gap_rows),
        len(release_manifests),
    )

    print(f"Wrote {args.output}")
    print(f"Wrote {args.gaps_output}")
    print(f"Wrote {args.summary_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

