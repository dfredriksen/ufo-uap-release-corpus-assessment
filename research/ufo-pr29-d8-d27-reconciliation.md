# UFO PR29 / D8 / D27 Reconciliation

Owner: Dan Fredriksen
Created: 2026-05-10
Scope: `DOD_111688964.mp4`, DVIDS `DOW-UAP-PR29`, local/War.gov `DoW-UAP-D8`, and local/War.gov `DoW-UAP-D27`
Status: Reconciled as a report-label discrepancy, pending any official correction

## Bottom Line

`DOD_111688964.mp4` is hard-linked to DVIDS release `DOW-UAP-PR29`, United Arab Emirates, June 2024. The DVIDS page states that the accompanying mission report is `DoW-UAP-D8`, but that report label conflicts with the official War.gov/local `D8` file, which describes a separate 2025 two-object case. The D8 filename/title says Djibouti, but its visible grid `35SQT3423692957` decodes to the Eastern Mediterranean, so D8 has its own title/grid location mismatch.

The official War.gov/local file named `dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf` contains the report language that matches the PR29 page: one over-water UAP, vertical pole/bar or possible water reflection, about 140 knots, and event timing around `070457ZJUN24`.

Working conclusion: treat `DOD_111688964.mp4` as a hard `PR29` video identity, treat the written-report content match as `D27`, and treat the DVIDS `DoW-UAP-D8` accompanying-report label as an unresolved release-index or report-label discrepancy.

Follow-on source review: `research/ufo-d27-source-review.md`

That review confirms D27 as the report-content match while adding two provenance constraints: D27's filename/title says October 2023 while the report body is June 2024, and the event serial is printed as `060457ZJUN2024-CENTCOM` while the initial contact/acquisition fields are `070457:00ZJUN24`.

## Evidence Table

| Item | Source | Key observations | Reconciliation meaning |
|---|---|---|---|
| `DOD_111688964.mp4` | DVIDS `DOW-UAP-PR29` | DVIDS lists filename `DOD_111688964`, length `00:00:21`, location `AE`, and describes a 21-second IR clip from 2024. | Hard video-to-release identity. |
| DVIDS accompanying report label | DVIDS `DOW-UAP-PR29` | DVIDS says the accompanying mission report is `DoW-UAP-D8` and summarizes an object with a vertical pole/bar, possibly a water reflection. | Conflicts with official/local `D8`; do not use local `D8` text for this video. |
| `dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf` | War.gov/local PDF | Contains the UAE over-water pole/bar/reflection language, `070457:00ZJUN24` initial contact, event serial `060457ZJUN2024-CENTCOM`, and 140-knot velocity. | Best written-report content match to PR29. |
| `dow-uap-d8-mission-report-djibouti-2025.pdf` | War.gov/local PDF | Describes two round white-hot UAPs moving south at about 240 NM/hour near grid `35SQT3423692957`; source review decodes that grid to approximately `34.2514N, 29.5437E`. | Separate 2025 case with its own title/grid mismatch; not the PR29 content. |

## Local File Checks

| Local source file | Size | SHA256 |
|---|---:|---|
| `I:\My Drive\UFO\dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf` | `689226` bytes | `86275421F64583566FCC32B7422C5D991B35DD7D3700E01D3FCF24B279FFF243` |
| `I:\My Drive\UFO\dow-uap-d8-mission-report-djibouti-2025.pdf` | `29154` bytes | `0A8548A845C3B45F90EE512BDFD8EAC1AF073072228E7E4D24E779D12025886C` |

## Caveats

- The DVIDS page lists date taken `06.01.2024`; the D27 report content has initial contact `070457:00ZJUN24`. This is a metadata/date discrepancy, not a content mismatch.
- The local/War.gov D27 filename says `united-arab-emirates-october-2023`, but the extracted event timing in the report is June 2024. Treat filename dates cautiously across this release set.
- The local/War.gov D8 filename/title says Djibouti, 2025, but the visible MGRS grid decodes to approximately `34.2514N, 29.5437E` in the Eastern Mediterranean. This strengthens the conclusion that D8 is not the PR29/D27 UAE pole/bar case, while also adding a separate D8 source-label caveat.
- PowerShell `HEAD` requests to War.gov returned `403 Forbidden`, but the PDF URLs were accessible through normal document retrieval and were also present locally under `I:\My Drive\UFO`.

## Sources

- DVIDS `DOW-UAP-PR29`: `https://www.dvidshub.net/video/1006074/dow-uap-pr29-unresolved-uap-report-united-arab-emirates-june-2024`
- War.gov `DoW-UAP-D27` PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf`
- War.gov `DoW-UAP-D8` PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d8-mission-report-djibouti-2025.pdf`

