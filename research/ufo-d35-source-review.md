# D35 Source Review

Owner: Dan Fredriksen
Created: 2026-05-13
Source file: `source-files-not-included/dow-uap-d35-mission-report-greece-october-2023.pdf`
Official URL: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d35-mission-report-greece-october-2023.pdf`
Related DVIDS release: `https://www.dvidshub.net/video/1006082/dow-uap-pr35-unresolved-uap-report-greece-october-2023`
Status: source review complete; hard PR35 report-video pairing

## Bottom Line

`D35` is a hard report-video pairing, but it is a weaker anomaly/kinematics case than `D33`. DVIDS `DOW-UAP-PR35` identifies filename `DOD_111689022` and states that the accompanying report is `DoW-UAP-D35`. The local video file `DOD_111689022-1920x1080-9000k.mp4` matches the DVIDS filename stem and duration, and all three local copies hash identically.

The source report says a seemingly circular UAP was spotted just above the ocean surface while the observer was RTB, flew toward land, and was lost from feed at the same minute. It preserves an estimated velocity of `30 MPH`, but lists `NONE` for maneuverability observations. The public clip supports the DVIDS phase sequence, not an independent physical-speed, altitude, range, or trajectory claim.

## Source Metadata

| Field | Value |
|---|---|
| PDF filename | `dow-uap-d35-mission-report-greece-october-2023.pdf` |
| PDF title/subject metadata | `DOW-UAP-D35, Mission Report, Greece, October 2023` |
| Pages | `7` |
| Creation date | `2026-01-26 08:28:30 PST` |
| Modification date | `2026-05-07 13:41:25 PDT` |
| File size | `1415369` bytes |
| Embedded files | `0` |
| Report marker | `Misrep 9337873` |
| Declassification marker | Declassified by MG Richard A. Harrison on `22 January 2026` |
| Release marker | `USCENTCOM MDR 26-0019`; approved for release to AARO |

Generated page renders:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D35/d35-page-5.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D35/d35-page-6.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D35/d35-page-7.png`

## Mission Context

| Field | Preserved value |
|---|---|
| COCOM / operations center | `USCENTCOM`; `603rd` |
| MAJCOM / originator | `AFSOC`; `33 SOS` |
| Mission type | ISR |
| Domain / service tasked | Air / Air Force |
| Takeoff | `281504:00ZOCT23`, LGLR |
| Landing / shutdown | `291105:00ZOCT23` / `291115:00ZOCT23`, LGLR |
| Total mission time | `20 hours 1 minute` |
| On-station window | `282018:00ZOCT23` to `290542:00ZOCT23` |
| Total time on station | `9 hours 24 minutes` |
| Primary sensor | `FMV` |
| Sensors available | `G-MESH` |
| Target pod | `AN/DAS-4` |
| Additional avionics | `AH/GMESH` |
| Data link | `LINK 16` |
| Tasking | Planned target development / AREC |
| Weather | Clear |

The UAP event occurred at `0811Z`, after the report's `0542Z` off-station/RTB marker. Treat the event as an RTB observation, consistent with the UAP gentext.

## UAP Fields

| Field | Preserved value |
|---|---|
| Initial contact DTG | `290811:00ZOCT23` |
| DoD acquisition date | `290811:00ZOCT23` |
| Event type | `UAP Incident` |
| Event serial | `-` |
| Maneuverability observation | `NONE` |
| Response to observer actions | `NONE` |
| Friendly aircraft location | Redacted `35SMV3...` lane |
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
| First coordinate | Redacted `35SMV3...` lane; first seen radius `5`; first accuracy `Estimated` |
| Last coordinate | Redacted `35SMV3...` lane; last seen radius `5`; last accuracy `Estimated` |
| Kinetic velocity | `30 MPH`, estimated |
| Kinetic altitude/depth/trajectory | Blank in public fields |
| UAP reaction to observation/interrogation/engagement | `UNK` |

## Description And Video Alignment

The D35 gentext reports that at `0811Z`, while RTB, the observer spotted a UAP flying just above the surface of the ocean water. The UAP flew just above the ocean toward land, and at `0811Z` the observer lost the UAP from the feed. The description field says the object was seemingly circular and too small to make out details.

DVIDS `PR35` provides the hard public media pairing:

- Release: `DOW-UAP-PR35`, Greece, October 2023.
- Video filename: `DOD_111689022`.
- Length: `00:00:24`.
- DVIDS says the accompanying report is `DoW-UAP-D35`.
- DVIDS describes a 24-second infrared clip in which the sensor zooms near `00:02`, tracks an area of contrast over ocean from roughly `00:03-00:19`, and loses the contrast as the background transitions to land near `00:20`.

Local PR35/D35 work already found:

- The local suffixed video file matches the DVIDS filename stem and release duration.
- The three local `DOD_111689022-1920x1080-9000k` copies are exact SHA-256 duplicates.
- The phase review supports the DVIDS zoom/ocean/land-transition sequence.
- Automated detections are visually confounded by clouds, shoreline, and high-contrast land/terrain features, especially after the land-transition phase begins.

DVIDS lists `Date Taken: 10.01.2023` and VIRIN `231002-D-D0360-7307`; those public metadata fields should not override the report's internal event DTG `290811:00ZOCT23`.

## Analytic Treatment

- Confidence is high for the PR35/D35 report-video pairing.
- Confidence is high for the report-derived event time, `30 MPH` estimated velocity field, near-ocean-surface / toward-land description, and negative controls.
- Confidence is medium that the public clip shows the described ocean-to-land/loss sequence.
- Confidence is low for physical kinematics. Public material does not preserve FOV, slant range, platform/gimbal motion, size, exact target coordinates, or raw telemetry.
- D35 should be used as a release/report completeness and comparison case, not as a strong maneuver case.

## Follow-Up

1. Keep D35 / PR35 paired with the Greece cluster, but below D33 / PR34 for anomaly strength and motion analysis.
2. Treat `30 MPH` as an estimated report field, not independently validated public-video kinematics.
3. Preserve D35 as a useful comparison case: same broad Greece/ocean-surface lane as D33, but with `NONE` maneuverability observations and a shorter, more visually confounded public clip.
4. If source telemetry appears, prioritize FOV/zoom state, slant range, platform/gimbal motion, and unredacted coordinates before revisiting speed or trajectory.

## Sources

- War.gov D35 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d35-mission-report-greece-october-2023.pdf`
- DVIDS PR35: `https://www.dvidshub.net/video/1006082/dow-uap-pr35-unresolved-uap-report-greece-october-2023`
