# UFO Telemetry Explanation Screening

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: using recovered telemetry-like data to screen explanations
Status: explanation viability matrix

## Purpose

This note answers what can be done with the telemetry-like data collected so far. It does not attempt a full physical reconstruction. It uses the recovered report fields, overlay candidates, image-plane tracks, coordinate decodes, and range-fouler fields to decide whether explanation families can be practically ruled out or should remain viable within current public-data tolerances.

The governing standard is conservative:

- Rule out only when the public evidence directly contradicts an explanation inside the available tolerance.
- Preserve when missing range, FOV, platform state, gimbal pointing, raw sensor data, or source-index uncertainty leaves the explanation physically or procedurally viable.
- Escalate to source request when the public data names the missing telemetry that would decide the case.

## Practical Tolerance Rules

| Data class | Practical tolerance | Can rule out | Must preserve |
|---|---|---|---|
| Report-derived speed | Treat as an estimate unless the report gives calibrated source data. | Explanations requiring a speed grossly outside the reported field and no plausible report-error path. | Aircraft/drone/platform-relative interpretations unless FOV/range/platform state proves otherwise. |
| Image-plane motion | Treat pixel rates and turns as screen-space only. | Single-frame dust/glare explanations if the feature persists across many accepted frames and phases. | Sensor pan, gimbal stabilization, platform motion, tracker re-lock, and physical target motion. |
| Meter-like overlay labels | Treat `5m`, `10M`, or `10m` as unresolved display annotations unless semantics are proven. | Pure "no overlay/readout exists" claims when the label is visible and persistent. | Meter readout, range gate, track-box parameter, generic annotation, and OCR artifact. |
| Coordinate decodes | Treat full readable grids as approximate geospatial anchors; preserve source-title conflicts. | Locations contradicted by a full decoded grid, unless official correction appears. | Title/grid mismatch, redaction, transcription, and partial-grid uncertainty. |
| Range-fouler geometry fields | Treat slant range, ground range, HAT, and sensor angle as report fields with OCR/form caveats. | Explanations requiring no sensor/range context where the form directly preserves it. | Conventional aircraft, drone, EW/range activity, and unresolved sensor event. |
| Multi-contact counts | Treat counts as report or visual candidates unless track identity is known. | Single-object-only explanations if independent tracks are confirmed by raw data. | Multiple objects, split tracks, glints, clutter, and duplicate/title inflation. |
| Altered public clips | Treat as controls unless raw originals are separately available. | Kinematic claims based on replay speed, sharpening, thresholding, or edits. | Provenance/control use and source-request value. |

## Explanation Families

| Explanation family | Current status across stack | Why |
|---|---|---|
| Public evidence proves extraordinary performance | Practically ruled out | No case has public raw telemetry, FOV/zoom state, slant-range time series, platform motion, and gimbal pointing sufficient to validate speed, acceleration, or true turn geometry. |
| Public evidence proves non-human origin | Practically ruled out | The recovered telemetry-like data does not establish origin or technology. |
| Conventional aircraft or drones | Preserved as viable in many cases | Speeds, strobes, radar lock, target-pod tracks, and over-water/operational contexts remain compatible without raw track data. |
| Sensor, compression, glare, reticle, or overlay artifacts | Preserved as viable for many video cases | Controls and altered clips show the artifact floor is material; image-plane tracks alone cannot eliminate display or processing effects. |
| Birds, balloons, or environmental clutter | Preserved selectively | Some cases have report fields or controls compatible with these lanes; stronger sensor-context cases may weaken but not eliminate them without raw data. |
| Unresolved operational observation | Preserved and supported | Multiple official records preserve structured unresolved observations, report/video pairings, and source-request paths. |
| Source-index or metadata error | Preserved and supported | `D25/D7`, `D27/D8`, `D54/D31`, and `D56-D58` metadata collisions show label errors are real. |

## Case-Level Screening

| Case | Telemetry basis | Explanations practically ruled out | Explanations preserved as viable | Deciding data needed |
|---|---|---|---|---|
| `D38/PR36` | Hard report/video pairing, validated compact-return interval, 38 accepted one-second points. | No-object-in-video; purely unrelated video. | Physical target, sensor pan/stabilization, track-update artifact, conventional distant object. | Raw video metadata, FOV, range, platform state, gimbal pointing. |
| `D33/PR34` | `80 MPH` report field, manual image-plane track, 7 apparent turn events, FOV/range scenarios. | Claim that public clip has no structured image-plane maneuver behavior. | True physical turns, sensor slew, gimbal stabilization, platform motion, tracker correction. | Source FOV/range/platform/gimbal telemetry and target coordinates. |
| `D25/PR28` | `434 KNOTS`, `FL200`, SWIR-only report lane, dense SWIR support. | Visible-spectrum-only explanation for the report lane; local `D7` as the matching report text. | Aircraft/drone/other heat source, SWIR artifact, report-estimate error, source-index label error. | Original multi-sensor file, FOV/range, platform telemetry, corrected report label. |
| `D27/PR29` | `140 KNOTS`, `AN/DAS-1`, dense object/track-box relation, vertical-feature flags. | Claim that PR29 has no visual support for the D27 pole/bar/reflection description. | Physical appendage, water reflection, track-box/display artifact, conventional target. | Raw sensor video, range/FOV, water-surface geometry, platform and gimbal data. |
| `D23/PR27` | 327 active rows; 175 compact-return candidates; artifact classes recorded. | Treating every candidate as reticle/texture artifact. | Compact target, reticle artifact, water texture, frame-edge artifact, candidate-rule bias. | Blinded re-review, control clip, raw source metadata. |
| `D35/PR35` | `30 MPH`, `NONE` maneuverability field, phase support with cloud/shore/terrain confounds. | High-anomaly maneuver claim for this case. | Conventional object, cloud/shore/terrain confound, weak UAP report. | Better object-level track and source geometry. |
| `PR44` | `10M` / `10m`-like overlay label, sustained compact-return track, dense and late reviews. | Claim that there is no telemetry-like overlay/readout candidate. | Meter readout, range gate, track-box parameter, generic annotation, OCR artifact, physical target, overlay-driven artifact. | Source-resolution frames, label persistence, overlay documentation, raw sensor file. |
| `PR47` | Three-component groups in 349/598 rows. | Single isolated-frame artifact. | Three objects, one object split by detection, glints/reflections, background clutter. | Raw video, independent tracks, range/FOV, platform state. |
| `PR45` | Apparent central contrast growth and exit-adjacent motion. | Physical-size claim from public clip alone. | Closure, zoom/contrast change, thresholding, reticle interaction. | Zoom/FOV state, range, source image processing settings. |
| `PR38` | Star-like contrast support across 90 rows and path proxy. | Claim that the DVIDS visual description is unsupported. | Physical target, optical/sensor effect, post-cut discontinuity, display artifact. | Raw sensor context and optical/display metadata. |
| `D44/D57` | Slant/ground range, HAT, sensor angle, one-contact IR geometry fields. | No-range-geometry explanation. | Conventional aircraft/drone, platform-relative motion, OCR noise, unresolved range-fouler. | Clear source forms, raw IR video, platform geometry, range-time series. |
| `D58` | Radar lock, target-pod video, two contacts, `16.9 NM`, red strobes, noise jamming. | Pure image-only artifact; no operational sensor context. | Military aircraft, drones, EW/training platform, unresolved two-contact event. | Radar tracks, target-pod video, EW logs, KINGPIN comms, unredacted coordinates. |
| `D8` | `240NM/HOUR`, two round white-hot UAPs, decoded `35SQT3423692957`. | Djibouti location as the only viable geospatial interpretation. | Eastern Mediterranean grid, title/grid mismatch, report-estimate error, separate D8 from PR29/D27. | Official correction, unredacted report, source imagery. |
| `D54` | DMS coordinate, `24,989FT MSL`, `168KTS`, triangular/metallic report. | Non-Aegean location if the coordinate is accepted as accurate. | Sparse report estimate, metadata `D31` mismatch, no-media uncertainty. | Full date, platform, sensor, and media linkage. |
| `D61/D65` | Formation/duration fields, three FMV observations, full D65 grid. | Claim that there is no regional reporting-density pattern. | Conventional regional activity, repeated sensor observations, weather/cloud effects, unresolved UAP reports. | Raw FMV, DGS exploitation notes, unredacted grids, weather imagery. |
| Release 02 altered clips | Explicit digital alteration and replay notes. | Use as raw kinematic evidence. | Control/provenance use; source-request pointers if raw originals exist. | Unaltered originals and metadata. |
| `ODNI-UAP-D001` | Senior-USIC narrative, FLIR/NVG/naked-eye account, Release 01 still linkage. | Public kinematic proof from the narrative alone. | Credible witness narrative, memory/reporting error, still-image corroboration, missing sensor metadata. | Raw FLIR/NVG imagery, platform data, timestamped sensor logs. |
| NASA Release 02 audio | Fireflies, particles, hardware/dye-pack context. | Spaceflight audio as modern UAP kinematics. | Internal visual effects, ice/condensation, mission hardware, environment. | Not a telemetry target for this corpus. |

## Tolerance-Based Conclusions

The public telemetry-like data can practically rule out:

- extraordinary-performance conclusions from public video alone
- non-human-origin conclusions from the current telemetry set
- using altered Release 02 clips for kinematic reconstruction
- treating PR44 as local `D44`, or using PR44 as a D44/D57/D58 match
- treating source labels as infallible where source-index conflicts are already documented
- treating D35 as a strong maneuver case

The public telemetry-like data preserves as viable:

- unresolved operational observations in official records
- conventional aircraft, drone, EW, range, or sensor-context explanations for the strongest document-only cases
- image-plane maneuver behavior without physical-turn validation
- meter-like overlay semantics as an unresolved high-value question
- regional reporting-density patterns that do not yet imply one phenomenon or performance class
- Release 02 as a broadened source/control family, not a claim upgrade

## Practical Uses For The Collected Telemetry

The recovered telemetry-like data is useful for:

1. Source-request prioritization, especially `D58`, `D28`, `D44/D57`, `D33/PR34`, `D27/PR29`, and `PR44`.
2. Plausibility testing under FOV/range assumptions.
3. Rejecting overclaims that require raw telemetry the public release does not contain.
4. Separating source-index errors from event facts.
5. Designing targeted follow-up extraction work around overlay persistence, frame crops, and control clips.
6. Ranking cases by what missing data would actually decide the explanation.

## Decision Standard For Future Promotion

Promote an explanation from "viable" to "favored" only when at least one of these appears:

- raw sensor video with frame-level metadata
- range-time series or radar tracks
- platform state and gimbal pointing
- known FOV/zoom state
- unredacted coordinates with timestamps
- documented overlay semantics for labels like `5m`, `10M`, or `10m`
- control tests showing the detector or manual rule rejects benign cases at an acceptable false-positive rate

Until then, the defensible conclusion is:

> The telemetry-like data can eliminate several overclaims and some metadata confusions, but it mostly preserves multiple conventional and unresolved explanations rather than selecting a single physical explanation.
