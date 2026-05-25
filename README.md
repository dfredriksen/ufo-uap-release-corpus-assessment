# UFO/UAP Release Corpus Assessment

This repository publishes a paper-oriented assessment of a public UFO/UAP release corpus.

![Publication Checks](https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/actions/workflows/publication.yml/badge.svg)

Main paper:

- [Scientific Assessment of the UFO/UAP Release Corpus](paper.md)

The repository includes generated analysis artifacts and scripts used during the assessment. It does not redistribute the original PDFs, videos, or images from the source corpus. Source files should be obtained from the official public release locations, including the War.gov UFO portal.

## Repository Structure

- `paper.md` - publication copy of the final scientific paper.
- `figures/` - validated publication figures and source CSVs used for theme and priority visualizations.
- `research/` - supporting notes, evidence tables, triage records, coverage audits, and case packets.
- `scripts/` - local analysis scripts used for coverage mapping, video review, geometry checks, and extraction attempts.
- `review-packets/` - packets prepared for external review and editorial improvement through ChatGPT Pro and Claude.
- `requirements.txt` - Python dependencies needed to regenerate the scripted outputs.
- `requirements-lock.txt` - full transitive dependency snapshot for the publication build.
- `.github/workflows/` - publication CI that reruns validators and figure generation.

## Core Conclusion

The corpus contains credible unresolved operational observations. The released evidence reviewed here is insufficient to determine origin, prove non-human technology, or independently reconstruct extraordinary physical performance.

## Source Data Notice

Original release media and documents are not included here. Some generated files preserve source filenames and public-source metadata so that readers can retrieve the underlying public records independently.

Large derived review artifacts such as frame extracts, contact sheets, and page-render images are also not redistributed. CSV and Markdown records may preserve their intended derived-artifact paths for reproducibility; the publication figures under `figures/` are included in the repository.

## Publication Boundary

The public repo is curated rather than a raw mirror of the working analysis tree. It includes the paper, supporting research notes, figures, scripts, review packets, and reproducibility helpers needed to audit the publication.

Key reproducibility artifacts:

- [Publication reproducibility note](research/ufo-publication-reproducibility.md)
- [Source acquisition manifest](research/ufo-source-acquisition-manifest.csv)
- [Source acquisition gap table](research/ufo-source-acquisition-gaps.csv)
- [Claim traceability table](research/ufo-claim-traceability.csv)
- [Frozen dependency snapshot](requirements-lock.txt)

Official context anchors:

- WAR.GOV UFO Release 01 and Release 02
- AARO UAP records
- NASA UAP terminology and FAQ pages

The release files and the public corpus should be interpreted as source evidence, not as proof of origin, non-human technology, or independently reconstructed physical performance.

