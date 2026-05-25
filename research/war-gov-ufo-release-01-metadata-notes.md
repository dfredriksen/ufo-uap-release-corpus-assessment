# War.gov UFO Release 01 Metadata Notes

Owner: Dan Fredriksen
Created: 2026-05-23
Official UFO page: `https://www.war.gov/UFO/`
Official release 01 page: `https://www.war.gov/News/Releases/Release/Article/4480582/department-of-war-releases-unidentified-anomalous-phenomena-files-in-historic-t/`
Official release 02 page: `https://www.war.gov/News/Releases/Release/Article/4499305/department-of-war-publishes-second-release-of-unidentified-anomalous-phenomena/`
Official manifest endpoint: `https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv`
Manifest retrieval used for this snapshot: `https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv`
Retrieval note: official War.gov CSV endpoint

## Scope

This pass normalizes the War.gov UFO Release 01 manifest subset into repo-local research tables. It records the manifest metadata fields, official asset URLs, DVIDS IDs, and exact local filename coverage against `research/ufo-file-manifest.csv`.

The live WAR.GOV feed is now a combined tranche index. This run filters the current feed by release date, so the output remains tranche-specific while still using the official source of record.

## Outputs

- `research/war-gov-ufo-release-01-manifest-normalized.csv`
- `research/war-gov-ufo-release-01-asset-coverage.csv`
- `research/war-gov-ufo-release-01-dow-documents.csv`
- `research/war-gov-ufo-release-01-metadata-summary.csv`
- `research/war-gov-ufo-release-01-metadata-notes.md`
- `research/war-gov-ufo-release-01-delta.csv`

## Manifest Counts

| Type | Rows |
| ---- | ---- |
| AUD  | 1    |
| IMG  | 14   |
| PDF  | 116  |
| VID  | 27   |

| Agency              | Rows |
| ------------------- | ---- |
| Department of State | 7    |
| Department of War   | 79   |
| FBI                 | 57   |
| NASA                | 15   |

Department of War family breakdown:

| Family                  | Rows |
| ----------------------- | ---- |
| air force report        | 1    |
| email correspondence    | 3    |
| historical archive file | 4    |
| launch summary          | 1    |
| mission report          | 30   |
| other                   | 7    |
| public-release video    | 27   |
| range fouler            | 6    |

## Local Asset Coverage

The manifest has `142` rows with a linked asset URL and `130` unique linked asset URLs. Exact basename comparison against the local UFO manifest finds `98` unique linked assets present locally and `32` without an exact local filename match.

This is exact filename coverage only. It does not prove a file was not downloaded under a renamed basename, and it does not evaluate DVIDS-hosted MP4 video downloads because those are tracked separately in the release-index sweep.

## Tranche Delta

Release 02 is additive against the current live feed. It introduces a new tranche of records with no exact record-id or DVIDS-video-id overlap against Release 01 in the current combined feed snapshot.

- `existing_asset_url`: `81`
- `existing_record_id`: `77`

## Initial Takeaways

- The live feed now contains both tranches: `158` Release 01 rows and `64` Release 02 rows, `222` total records.
- Release 02 broadens the corpus with more Department of War video records, plus NASA audio, DOE imagery/correspondence, CIA historical reporting, ODNI narrative material, and a new Sandia/PANTEX lane.
- The new material is mostly additive evidence breadth, not a change in claim ceiling. The new tranche gives more report families to cross-check, but it still requires deeper source review before any stronger interpretation.
- The most immediately interesting Release 02 rows are the PANTEX imagery, Sandia Base correspondence, CIA USSR report, ODNI USPER narrative, Apollo 12 audio, and the modern PR050-PR099 video cluster.

## Selected Report Rows

| Record | Type | Incident date | Location | Pairing fields |
| ------ | ---- | ------------- | -------- | -------------- |

## Next Work

Use the normalized manifest as the upstream metadata layer for tranche synthesis. The next focused pass should compare the new Release 02 Department of War document rows against local extracted text, DVIDS page identities, exact local file coverage, and the existing evidence ladder before promoting any case.
