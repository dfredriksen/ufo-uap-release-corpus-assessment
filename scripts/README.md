# Scripts

These scripts are repeatable analysis passes copied from the working planning repo.

Most scripts expect public-release source videos to exist under `I:\My Drive\UFO`. Where supported, pass an alternate source path with the script's `--video` argument.

The scripts do not modify source videos. They write derived CSVs and visual artifacts under `research/`.

The publication build uses the pinned dependencies in `requirements.txt` and the frozen snapshot in `requirements-lock.txt`.

`scripts/war_gov_ufo_manifest_metadata.py` reads the live combined WAR.GOV feed and can be filtered to a tranche with `--release-date` plus a matching `--release-tag`, for example `--release-date 5/22/26 --release-tag release-02`.

`scripts/build_ufo_source_acquisition_manifest.py` writes a fresh-clone acquisition manifest plus a gap table for release assets that are not exact local filename matches.

`scripts/validate_publication_paths.py` checks for accidental GitHub URLs embedded inside filesystem path constructors in Python and PowerShell scripts.

`scripts/generate_publication_figures.py` rebuilds the SVG publication figures from the repo-local CSVs and writes a validation note under `figures/`.

The publication CI workflow in `.github/workflows/publication.yml` reruns the path validator, figure generator, and acquisition-manifest builder with a missing source root to confirm graceful degradation.

