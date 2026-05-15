# D33 Source Review

Owner: Dan Fredriksen
Created: 2026-05-12
Source file: `source-files-not-included/dow-uap-d33-mission-report-greece-october-2023.pdf`
Official URL: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d33-mission-report-greece-october-2023.pdf`
Related DVIDS release: `https://www.dvidshub.net/video/1006080/dow-uap-pr34-unresolved-uap-report-greece-october-2023`
Status: source review complete; hard PR34 report-video pairing

## Bottom Line

`D33` is one of the strongest hard report-video cases in the current set. DVIDS `DOW-UAP-PR34` identifies local video `DOD_111689011`, and the DVIDS report summary matches the local/War.gov D33 report: a seemingly circular UAP just above the ocean surface, making multiple sharp 90-degree turns at an estimated `80 MPH`, then being lost from the feed.

The source review confirms D33 should stay high priority, but it should remain bounded. The public video and local manual track support multiple sharp apparent image-plane heading changes; they do not independently prove true real-world 90-degree turns, exact speed, range, altitude, or size without FOV, slant range, platform/gimbal motion, and telemetry.

## Source Metadata

| Field | Value |
|---|---|
| PDF filename | `dow-uap-d33-mission-report-greece-october-2023.pdf` |
| PDF title/subject metadata | `DOW-UAP-D33, Mission Report, Greece, October 2023` |
| Pages | `7` |
| Creation date | `2026-05-04 08:31:19 PDT` |
| Modification date | `2026-05-07 13:40:50 PDT` |
| File size | `897434` bytes |
| Report marker | `Misrep 9329374` |
| Declassification marker | Declassified by MG Richard A. Harrison on `22 January 2026` |
| Release marker | `USCENTCOM MDR 26-0019`; approved for release to AARO |

Generated page renders:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D33/d33-page-5.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D33/d33-page-6.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D33/d33-page-7.png`

## Mission Context

| Field | Preserved value |
|---|---|
| COCOM / operations center | `USCENTCOM`; `603rd` |
| MAJCOM / originator | `AFSOC`; `33 SOS` |
| Mission type | ISR |
| Domain / service tasked | Air / Air Force |
| Takeoff | `262339:00ZOCT23`, LGLR |
| Landing / shutdown | `271309:00ZOCT23` / `271319:00ZOCT23`, OJMS |
| Total mission time | `13 hours 30 minutes` |
| On-station window | `270342:00/01ZOCT23` to `271011:00/01ZOCT23` |
| Total time on station | `6 hours 29 minutes` |
| Primary sensor | `FMV` |
| Sensors available | `G-MESH` |
| Target pod | `AN/DAS-4` |
| Additional avionics | `AWGMESH` |
| Data link | `LINK 16` |
| Tasking | Planned target development |
| Weather | Clear |

The UAP event occurred at `0035Z`, before the later on-station tasking window in the report.

## UAP Fields

| Field | Preserved value |
|---|---|
| Initial contact DTG | `270035:12ZOCT23` |
| DoD acquisition date | `270035:00ZOCT23` |
| Event type | `UAP Incident` |
| Event serial | `-` |
| Maneuverability observation | Sharp 90-degree turns |
| Response to observer actions | `NONE` |
| Friendly aircraft location | Redacted `35SKD5...` lane |
| Friendly aircraft trajectory | `SW` |
| Observer assessment | `Benign` |
| UAP physical state | `Solid` |
| Propulsion means | `UNK` |
| Under intelligent control | `NO` |
| UAP signatures | `NONE` |
| Advanced capabilities/materials | `UNK` |
| RF frequency / duration | `UNK` / `UNK` |
| Effects on persons/equipment | `NO` / `NONE` |
| Objects/material recovered | `NO` |
| Observer engagement | `NO` |
| First coordinate | Redacted `35S KD 95...5...` lane; first seen radius `5`; first accuracy `Estimated` |
| Last coordinate | Redacted `35SKD9...` lane; last seen radius `5`; last accuracy `Estimated` |
| Kinetic velocity | `80 MPH`, estimated |
| Kinetic altitude/depth/trajectory | Blank in public fields |
| UAP reaction to observation/interrogation/engagement | `UNK` |

## Description And Video Alignment

The D33 gentext reports that at `0035Z`, while en route to target, the observer spotted a UAP flying just above the ocean surface. It took multiple 90-degree turns at an estimated `80 MPH`, and at `0038Z` the observer lost the UAP from the feed. The description field says the object was seemingly circular and too small to make out details.

DVIDS `PR34` provides the hard public media pairing:

- Release: `DOW-UAP-PR34`, Greece, October 2023.
- Video filename: `DOD_111689011`.
- Length: `00:02:57`.
- DVIDS says the accompanying report is `DoW-UAP-D33`.
- DVIDS video description includes entry from the lower-left field, back-and-forth horizontal motion, generally centered tracking, blue-reticle designation, contrast filter use, loss against background, and post-lock zoom/contrast cycling.

Prior local PR34/D33 work already found:

- Phase review supports the first-minute visual sequence, but later reticle/filter intervals are artifact-prone for automated tracking.
- Manual review from `4.0s-59.0s` retained `97` accepted marks, interpolated `14` bounded dropouts, and identified seven smoothed image-plane heading changes of at least `60 deg`.
- Geometry feasibility scenarios do not falsify the report's `80 MPH` value, but cannot validate it without FOV/range/platform telemetry.

## Analytic Treatment

- Confidence is high for the report-video pairing.
- Confidence is high for the reported event time, approximate feed-loss time, `80 MPH` report value, over-water/surface-proximate lane, and negative controls as report text.
- Confidence is medium-high that the public MP4 contains multiple sharp apparent image-plane heading changes during the useful early interval.
- Confidence is low for physical kinematics. Public material does not preserve FOV, slant range, target size, platform/gimbal motion, or raw telemetry.
- Do not convert image-plane heading changes into real-world 90-degree turns without source geometry.

## Follow-Up

1. Keep D33 / PR34 as the strongest Greece ocean-surface hard-paired case.
2. Preserve D33 as a public image-plane maneuver-support case, not a solved physical-turn or speed case.
3. Use D33 as the comparison baseline before source-reviewing D35, the paired Greece ocean-surface toward-land case.
4. If source telemetry appears, prioritize FOV/zoom state, slant range, platform/gimbal motion, and exact target coordinates before revisiting `80 MPH` or true turn geometry.

## Sources

- War.gov D33 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d33-mission-report-greece-october-2023.pdf`
- DVIDS PR34: `https://www.dvidshub.net/video/1006080/dow-uap-pr34-unresolved-uap-report-greece-october-2023`
