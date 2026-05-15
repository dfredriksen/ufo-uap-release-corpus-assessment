# D74 Source Review

Owner: Dan Fredriksen
Created: 2026-05-12
Source file: `source-files-not-included/dow-uap-d74-mission-report-syria-november-2023.pdf`
Official URL: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d74-mission-report-syria-november-2023.pdf`
Status: source review complete; document-only case

## Bottom Line

`D74` is one of the stronger structured mission-report records because the public release preserves the UAP event time, event serial, mission context, estimated speed, relative altitude language, duration, and negative controls. It reports one probable UAP in Syria on `2023-11-09` at `092153:00ZNOV23`, shaped in the event narrative like a bouncy ball, coming from the south near co-altitude, dropping altitude, passing the aircraft safely, and maintaining an estimated `424KN` for about seven minutes before becoming out of range.

The important limit is that D74 is still document-only. The released record does not provide raw video, frame stills, FOV, range, platform telemetry, exact coordinates, or a public PR/DVIDS video pairing. Treat the `424KN` value and shape language as report-derived, not independently measured from public imagery.

## Source Metadata

| Field | Value |
|---|---|
| PDF filename | `dow-uap-d74-mission-report-syria-november-2023.pdf` |
| PDF title/subject metadata | `DoW-UAP-D42` |
| Report body identity | D74 by filename/release label; MISREP `9381202` |
| Pages | `10` |
| Recommendation/declassification marker | Recommended by MG Brandon R. Tegtmeier on `2 June 2025` |
| Classification/caveat in released body | `SECRET//NOFORN` |
| COCOM / operations center | `USCENTCOM`; `609th` |
| Operation | `INHERENT RESOLVE` |
| Domain / mission type | Air / ISR |
| Service tasked | Air Force |

The embedded PDF title/subject says `DoW-UAP-D42`, which conflicts with the D74 filename/release identity. Treat this as a source metadata mismatch, not as a reason to relabel the record.

## Mission Context

| Field | Preserved value |
|---|---|
| Takeoff | `090217Z` in narrative |
| Handover | `090229Z` in narrative |
| ISR 2 on station | `090431:00ZNOV23` to `090554:00ZNOV23` |
| ISR 2 tasking | Dynamic target development at redacted `37S FU` coordinate lane |
| ISR 3 on station | `090805:00ZNOV23` to `091933:00ZNOV23` |
| ISR 3 tasking | Dynamic target development at redacted `38S MB` coordinate lane |
| UAP observation | `092153:00ZNOV23` |
| Later mission markers | Handback at `092254Z`; landed at `092319Z` |
| Primary sensor in ISR sections | `FMV` |
| Other collection context | Narrative says FMV/SIGINT collection occurred during tasking |
| Weather | `CLEAR WX` |

One timing caveat is worth preserving: the narrative says the platform returned to base at `1933Z`, while the UAP gentext says the event occurred while returning to base at `2153Z`, followed by handback at `2254Z` and landing at `2319Z`. The UAP event time is internally repeated and should remain the anchor; the RTB wording should be treated as mission-phase context.

## UAP Fields

| Field | Preserved value |
|---|---|
| Initial contact DTG | `092153:00ZNOV23` |
| Event type | `UAP Incident` |
| Event serial | `092153ZNOV2023-CENTCOM` |
| DoD acquisition date | `092153:00ZNOV23` |
| Maneuverability observation | `NONE` |
| Response to observer actions | `NO` |
| Friendly aircraft location | Redacted `37S ET` coordinate lane |
| Friendly aircraft trajectory | `SOUTHEAST` |
| Observer assessment | `Benign` |
| Observation interrogation | `NO` |
| Third-party observers/reporters | `NONE` |
| UAP physical state | `Solid` |
| Propulsion means | `UNK` |
| Under intelligent control | `NO` |
| Advanced capabilities/materials field | Marked yes, with the explanation tied to estimated `424KN` travel for at least seven minutes |
| RF frequency / duration | `NONE` / `N/A` |
| Effects on persons | `NO` |
| Objects/material recovered | `NO` |
| Effects on equipment | `NONE` |
| Observer engagement | `NO` |
| First coordinate | Redacted `37D ST` coordinate lane |
| Last coordinate | Redacted `37S FT` coordinate lane |
| First / last seen radius | `5` / `10` |
| Kinetic altitude | `170`, estimated; public unit/context unclear |
| Kinetic velocity | `424KN`, estimated |
| Kinetic trajectory | Blank |
| Anomalous characteristics/behaviors | `N/A` |
| UAP description field | Visible structured description is mostly redacted after `SHOWED AS` |

## Narrative Finding

The free-text UAP narrative is more useful than D75's because it is mostly readable. It reports a probable UAP shaped like a bouncy ball, coming from the south near co-altitude, dropping altitude, passing the aircraft safely, maintaining about `424KN`, then becoming out of range after roughly seven minutes. It also states there were no emissions, no threat assessment to aircraft or public safety, and no effects on the aircrew.

The structured description field is still redacted, so the shape claim should be cited to the gentext narrative, not to preserved image evidence.

Generated page renders:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D74/d74-page-08.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D74/d74-page-09.png`

## Analytic Treatment

- Confidence is high for event identity, time, event serial, COCOM/operation context, and the negative controls.
- Confidence is medium for the shape, pass geometry, and duration because they are preserved in a report narrative but not in public imagery.
- Confidence is low for independent physical kinematics. `424KN` is an estimated report value without public range, FOV, telemetry, or video.
- No local or public PR/DVIDS video pairing has been found that names D74, `092153ZNOV2023-CENTCOM`, `424KN`, or the bouncy-ball description.
- Do not expand `HC` in `prob HC UAP` without a source; use the conservative wording "probable UAP."

## Follow-Up

1. Keep D74 in the high-priority document-only lane.
2. Search only for official source metadata that names D74, MISREP `9381202`, `092153ZNOV2023-CENTCOM`, `424KN`, or the redacted Syria coordinate lanes.
3. If source video appears, prioritize the seven-minute window beginning around `092153Z` and require platform/FOV/range data before using the `424KN` value analytically.
4. Compare D74 against D75 as a later USCENTCOM mission-report pair: D74 has readable narrative detail; D75 has more redacted narrative but useful Gulf of Aden structured fields.

## Sources

- War.gov D74 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d74-mission-report-syria-november-2023.pdf`
