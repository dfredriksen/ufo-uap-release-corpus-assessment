# D25 Source Review

Owner: Dan Fredriksen
Created: 2026-05-12
Source file: `source-files-not-included/dow-uap-d25-mission-report-greece-january-2024.pdf`
Official URL: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d25-mission-report-greece-january-2024.pdf`
Related DVIDS release: `https://www.dvidshub.net/video/1006073/dow-uap-pr28-unresolved-uap-report-greece-january-2024`
Status: source review complete; PR28 report-content match with D7 label caveat

## Bottom Line

`D25` is the written-report content match for DVIDS `DOW-UAP-PR28` / local `DOD_111688954.mp4`. It preserves a Greece / January 2024 ISR mission context, target pod `AN/DAS-4`, UAP signature `SWIR WHT`, event time `250509:00ZJAN24`, event serial `250509ZJAN2024-CENTCOM 001`, and a distinctive report description: a round/diamond-shaped UAP with a straight non-maneuverable tail or probe, visible only on SWIR, observed for about two minutes.

The DVIDS page labels the accompanying mission report as `DoW-UAP-D7`, but the public DVIDS description matches D25 and conflicts with the official/local D7 Arabian Gulf balloon-like/TFLIR report. Treat `DOD_111688954.mp4` as hard PR28 media, D25 as the written-report content match, and DVIDS's `D7` label as an unresolved source-index discrepancy.

The main limit is kinematic. The public report gives approximate `434 KNOTS`, estimated FL200 altitude, and westward trajectory, but the kinetic-velocity field itself is blank and the public MP4 lacks source FOV, range, platform/gimbal motion, and telemetry. Do not treat the public release as an independent validation of speed, size, range, or physical shape.

## Source Metadata

| Field | Value |
|---|---|
| PDF filename | `dow-uap-d25-mission-report-greece-january-2024.pdf` |
| PDF title/subject metadata | `DOW-UAP-D25, Mission Report, Greece, January 2024` |
| Pages | `7` |
| Creation date | `2026-04-03 07:12:44 PDT` |
| Modification date | `2026-05-07 13:38:38 PDT` |
| File size | `680054` bytes |
| Declassification marker | Declassified by MG Richard A. Harrison on `24 October 2025` |
| Report marker | `Misrep undefined-9629373` |
| Release marker | `USCENTCOM MDR 25-0100 thru 25-0103 / JS-250710-TM8S`; approved for release to AARO |

Generated page renders:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D25/d25-page-5.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D25/d25-page-6.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D25/d25-page-7.png`

## Mission Context

| Field | Preserved value |
|---|---|
| COCOM / operations center | `USCENTCOM`; `603rd` |
| MAJCOM / originator | `AFSOC`; `33 SOS` |
| Mission type | ISR |
| Tasking order / ATO mission number | `24-024`; `4055` |
| Takeoff | `250109:00ZJAN24`, LGLR |
| Landing / shutdown | `252149:00ZJAN24` / `252159:00ZJAN24`, LGLR |
| Total mission time | `20 hours 40 minutes` |
| On-station window | `250635:00ZJAN24` to `251504:00ZJAN24` |
| Total time on station | `8 hours 29 minutes` |
| Primary sensor | `FMV` |
| Sensors available | `BLASPHEMY` |
| Target pod | `AN/DAS-4` |
| Additional avionics | `AH/GMESH/SANTA FE` |
| Data link | `LINK 16` |
| Weather | Clear |

The UAP event occurred before the ISR on-station time listed later in the report narrative, while the platform was in transit.

## UAP Fields

| Field | Preserved value |
|---|---|
| Initial contact DTG | `250509:00ZJAN24` |
| Event type | `UAP Incident` |
| Event serial | `250509ZJAN2024-CENTCOM 001` |
| DoD acquisition date | `250509:00ZJAN24` |
| Maneuverability observation | `NONE` |
| Response to observer actions | `NONE` |
| Friendly aircraft location | Redacted `35SQT67` lane |
| Friendly aircraft altitude/depth | `FL250` |
| Friendly aircraft trajectory | `162` |
| Friendly aircraft speed | `176 KTS` |
| Observer assessment | `Benign` |
| Observation interrogation | `NO` |
| Third-party observers/reporters | `NONE` |
| UAP physical state | `Solid` |
| UAP propulsion means | `UNK` |
| UAP under intelligent control | `UNK` |
| UAP signatures | `SWIR WHT` |
| Advanced capabilities/materials | `NO` |
| Effects on persons/equipment | `NO` / `NONE` |
| Objects/material recovered | `NO` |
| Observer engagement | `NONE` |
| First coordinate | Redacted `35SQT44` lane; radius `20`; first accuracy `Estimated` |
| Last coordinate | Redacted `35SPT63` lane; radius `20`; last accuracy `Estimated` |
| Kinetic altitude | `FL200`, estimated |
| Kinetic velocity field | Blank in structured field; gentext reports approximate `434 KNOTS` |
| Kinetic trajectory | `W`, estimated |
| Anomalous characteristics/behaviors | Maintained steady flight path, increased/decreased altitude profile, did not change trajectory |

## Description And Video Alignment

The D25 text reports a round diamond shape with a straight, non-maneuverable tail, and the gentext describes a diamond-shaped UAP with a non-maneuvering probe at the bottom. It says the UAP only appeared on the SWIR camera and the event lasted about two minutes, ending at `0511Z`.

DVIDS `PR28` describes the public video as a multi-sensor clip that starts split EO/SWIR, shifts to full-screen SWIR, loses the subject when switching to visible spectrum, and does not reacquire it in the later SWIR black-hot segment. That is a close content match to D25.

Prior local PR28 phase review already found:

- `DOD_111688954.mp4` is the hard DVIDS PR28 media file.
- The full-screen SWIR interval from `10.0s-55.9s` had `86/92` high-or-medium detections.
- The `57.0s-65.5s` SWIR black-hot non-reacquisition interval had `0/18` high-or-medium detections.
- The public MP4 supports the SWIR-only sequence, but not independent speed, range, size, altitude, or physical-shape claims.

## Analytic Treatment

- Confidence is high for D25 as the PR28 written-report content match.
- Confidence is high for event time, event serial, SWIR signature, mission context, and negative controls as report text.
- Confidence is high for public-video support of the SWIR visibility sequence, because PR28 and the local phase review align with the report.
- Confidence is medium for the exact shape/tail/probe description. It is preserved in the report and visually consistent with PR28's trailing-mass description, but not resolved as physical morphology.
- Confidence is low for physical kinematics. Approximate `434 KNOTS`, FL200, and westward trajectory remain report-derived without public source telemetry.

## Follow-Up

1. Keep D25 / PR28 as a high-priority hard media-plus-report-content lane.
2. Preserve the DVIDS `D7` label discrepancy and do not use local/War.gov D7 as the PR28 written report.
3. Do not run physical kinematics from the public MP4 alone. Require FOV/zoom state, slant range, platform/gimbal motion, and raw telemetry before revisiting `434 KNOTS`.
4. Use D25 as the baseline SWIR-only comparator when reviewing D33/D35 and other Greece/Eastern Mediterranean cases.

## Sources

- War.gov D25 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d25-mission-report-greece-january-2024.pdf`
- DVIDS PR28: `https://www.dvidshub.net/video/1006073/dow-uap-pr28-unresolved-uap-report-greece-january-2024`
