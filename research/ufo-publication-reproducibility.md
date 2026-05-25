# UFO Publication Reproducibility

This note defines the curated public boundary and the minimal run order needed to audit the corpus from a fresh clone.

## Publication Boundary

The public repo should contain the paper-grade outputs and the artifacts needed to verify them:

- `paper.md` or the final publication draft
- cited `research/*.md` source-review and synthesis artifacts
- `review-packets/` editorial QA outputs
- `figures/*.svg` publication figures and the figure validation note
- `scripts/` repeatable analysis and validation scripts
- `requirements.txt`
- `requirements-lock.txt`
- `CITATION.cff`
- `.github/workflows/publication.yml`
- `research/ufo-claim-traceability.csv`
- acquisition manifests and gap tables for source material

Suggested publish-set examples from this workspace:

- `README.md`
- `requirements.txt`
- `requirements-lock.txt`
- `scripts/`
- `figures/`
- `research/ufo-claim-traceability.csv`
- `research/ufo-final-scientific-report.md`
- `research/ufo-final-report-consistency-check.md`
- `research/ufo-release-02-synthesis.md`
- `research/ufo-source-acquisition-manifest.csv`
- `research/ufo-source-acquisition-gaps.csv`
- `review-packets/` if the paper version carries editorial QA artifacts

The public repo should not contain:

- original source MP4s, PDFs, images, or audio files
- `research/ufo-derived/`
- caches, virtual environments, bytecode, or other local temp products
- large throwaway contact-sheet or extraction artifacts that are not cited by the paper

## Required Environment

- Python 3.11 or newer for general reproduction with `requirements.txt`
- Python 3.14.x for the frozen publication snapshot in `requirements-lock.txt`
- `python -m pip install -r requirements.txt`
- `requirements-lock.txt` captures the frozen dependency snapshot verified for the publication run
- Optional: a local `ffprobe` or `ffmpeg` binary for video metadata scripts that call one

The figure generator requires `numpy`, `opencv-python`, `pandas`, and `matplotlib`.

## Source Acquisition Manifests

Two companion outputs document source provenance:

- `research/ufo-source-acquisition-manifest.csv`
- `research/ufo-source-acquisition-gaps.csv`

The manifest records:

- the recorded source path
- the expected local path used for acquisition
- the local file size
- the filesystem byte count, when the file is present
- the SHA-256 hash, when the file is present
- the canonical release URL, when a release asset can be matched back to the local file
- the release record IDs and titles that map to the file

The gap table records release assets that are not currently represented as exact local filename matches in the inventory.
The acquisition gap table is part of the reproducibility boundary because it shows which official release assets still require filename reconciliation even when the local corpus is fully hashed.
The claim traceability table records representative claims, supporting artifacts, claim types, and the status of each claim's evidentiary ceiling.

## Rebuild Order

Run the corpus from the bottom up:

1. Build the source acquisition manifest.
2. Rebuild the coverage map and summary tables.
3. Refresh the release metadata tables for Release 01 and Release 02.
4. Regenerate the publication figures.
5. Run the path-hygiene validator.
6. Re-run any targeted video or document review script only if the source file is locally available.
7. Use `.github/workflows/publication.yml` as the published CI sequence for the basic validation pass.

Representative commands:

```powershell
python scripts/build_ufo_source_acquisition_manifest.py
powershell -ExecutionPolicy Bypass -File scripts/ufo_build_file_coverage_map.ps1
python scripts/war_gov_ufo_manifest_metadata.py
python scripts/war_gov_ufo_manifest_metadata.py --release-date 5/22/26 --release-tag release-02
python scripts/generate_publication_figures.py
python scripts/validate_publication_paths.py
```

If the source files live somewhere other than `I:\My Drive\UFO`, pass the alternate root to the acquisition script with `--source-root`.

## Validation Notes

- The review packets are editorial QA, not independent evidence.
- The public MP4s and PDFs are lossy release artifacts; image-plane motion alone does not establish true speed or maneuvering.
- Any claim that depends on raw telemetry, slant range, platform motion, or gimbal state remains source-request work, not a public-release reconstruction.

