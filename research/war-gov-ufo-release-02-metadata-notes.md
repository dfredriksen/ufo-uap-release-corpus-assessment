# War.gov UFO Release 02 Metadata Notes

Owner: Dan Fredriksen
Created: 2026-05-23
Official UFO page: `https://www.war.gov/UFO/`
Official release 01 page: `https://www.war.gov/News/Releases/Release/Article/4480582/department-of-war-releases-unidentified-anomalous-phenomena-files-in-historic-t/`
Official release 02 page: `https://www.war.gov/News/Releases/Release/Article/4499305/department-of-war-publishes-second-release-of-unidentified-anomalous-phenomena/`
Official manifest endpoint: `https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv`
Manifest retrieval used for this snapshot: `https://www.war.gov/Portals/1/Interactive/2026/UFO/uap-data.csv`
Retrieval note: official War.gov CSV endpoint

## Scope

This pass normalizes the War.gov UFO Release 02 manifest subset into repo-local research tables. It records the manifest metadata fields, official asset URLs, DVIDS IDs, and exact local filename coverage against `research/ufo-file-manifest.csv`.

The live WAR.GOV feed is now a combined tranche index. This run filters the current feed by release date, so the output remains tranche-specific while still using the official source of record.

## Outputs

- `research/war-gov-ufo-release-02-manifest-normalized.csv`
- `research/war-gov-ufo-release-02-asset-coverage.csv`
- `research/war-gov-ufo-release-02-dow-documents.csv`
- `research/war-gov-ufo-release-02-metadata-summary.csv`
- `research/war-gov-ufo-release-02-metadata-notes.md`
- `research/war-gov-ufo-release-02-delta.csv`

## Manifest Counts

| Type | Rows |
| ---- | ---- |
| AUD  | 7    |
| PDF  | 6    |
| VID  | 51   |

| Agency                                          | Rows |
| ----------------------------------------------- | ---- |
| Central Intelligence Agency                     | 1    |
| Department of Energy                            | 3    |
| Department of War                               | 52   |
| NASA                                            | 7    |
| Office of the Director of National Intelligence | 1    |

Department of War family breakdown:

| Family | Rows |
| ------ | ---- |
| other  | 1    |
| video  | 51   |

## Local Asset Coverage

The manifest has `6` rows with a linked asset URL and `6` unique linked asset URLs. Exact basename comparison against the local UFO manifest finds `0` unique linked assets present locally and `6` without an exact local filename match.

This is exact filename coverage only. It does not prove a file was not downloaded under a renamed basename, and it does not evaluate DVIDS-hosted MP4 video downloads because those are tracked separately in the release-index sweep.

## Tranche Delta

Release 02 is additive against the current live feed. It introduces a new tranche of records with no exact record-id or DVIDS-video-id overlap against Release 01 in the current combined feed snapshot.

- `new`: `64`

## Initial Takeaways

- The live feed now contains both tranches: `158` Release 01 rows and `64` Release 02 rows, `222` total records.
- Release 02 broadens the corpus with more Department of War video records, plus NASA audio, DOE imagery/correspondence, CIA historical reporting, ODNI narrative material, and a new Sandia/PANTEX lane.
- The new material is mostly additive evidence breadth, not a change in claim ceiling. The new tranche gives more report families to cross-check, but it still requires deeper source review before any stronger interpretation.
- The most immediately interesting Release 02 rows are the PANTEX imagery, Sandia Base correspondence, CIA USSR report, ODNI USPER narrative, Apollo 12 audio, and the modern PR050-PR099 video cluster.

## Selected Report Rows

| Record        | Type | Incident date | Location                   | Pairing fields                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------- | ---- | ------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CIA-UAP-D001  | PDF  | 12/20/73      | USSR                       | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOE-UAP-D001  | PDF  |               |                            | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOW-UAP-D017  | PDF  | 1948-1950     | New Mexico                 | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOW-UAP-PR050 | VID  | 2022          | CENTCOM                    | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOW-UAP-PR051 | VID  | 2021          | CENTCOM                    | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOW-UAP-PR065 | VID  | 2024          | Southeastern United States | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOW-UAP-PR071 | VID  | 2023          | NORTHCOM                   | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOW-UAP-PR075 | VID  | 2021          | East China Sea             | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| DOW-UAP-PR098 | VID  |               | CENTCOM                    | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| NASA-UAP-D008 | AUD  | 1969          | Texas                      | video=-; pdf=-                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ODNI-UAP-D001 | PDF  | 2025          | Western United States      | video=-; pdf=FBI Photo A001 | FBI Photo A002 | FBI Photo A003 | FBI Photo A004 | FBI Photo A005 | FBI Photo A006 | FBI Photo A007 | FBI Photo A008 | FBI Photo B001 | FBI Photo B002 | FBI Photo B003 | FBI Photo B004 | FBI Photo B005 | FBI Photo B006 | FBI Photo B007 | FBI Photo B008 | FBI Photo B009 | FBI Photo B010 | FBI Photo B011 | FBI Photo B012 | FBI Photo B013 | FBI Photo B014 | FBI Photo B015 | FBI Photo B016 | FBI Photo B017 | FBI Photo B018 | FBI Photo B019 | FBI Photo B020 | FBI Photo B021 | FBI Photo B022 | FBI Photo B023 | FBI Photo B024 | USPER Statement about UAP Sighting |

## Next Work

Use the normalized manifest as the upstream metadata layer for tranche synthesis. The next focused pass should compare the new Release 02 Department of War document rows against local extracted text, DVIDS page identities, exact local file coverage, and the existing evidence ladder before promoting any case.
