# UFO Forensic Telemetry Technique Matrix

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: public-release corpus only
Status: technique list for derived telemetry and scenario generation

## Purpose

This matrix lists the forensic techniques that can extract additional telemetry-like values or scenario constraints from the released evidence. It is designed to be used with:

- `research/ufo-telemetry-evidence-inventory.md`
- `research/ufo-telemetry-recovery-methods.md`
- `research/ufo-telemetry-full-stack-application.md`
- `research/ufo-telemetry-explanation-screening.md`

The goal is not to convert public MP4s into raw mission telemetry. The goal is to recover bounded measurements, test scenario compatibility, and identify the exact source data required to resolve each ambiguity.

## Technique Matrix

| Rank | Technique | What it can extract | Best current evidence | Scenario configurations it can test | Required caveat |
|---:|---|---|---|---|---|
| 1 | Overlay OCR and label persistence | Meter-like labels, range-like labels, track-box annotations, stable display-layer cues | `PR44` / `DOD_111689115.mp4` `10M` / `10m`; external `5m` frame example | Meter readout; range gate; track-box parameter; generic annotation; OCR artifact | Label semantics are not self-proving. Require multi-frame persistence and source-resolution crops before treating the label as measurement data. |
| 2 | Source-resolution crop stabilization | Clearer text, reticle state, track-box edges, zoom/field transitions | `PR44`, `PR29`, `PR34`, `PR38` | Stable sensor overlay; compression ghost; redaction/overlay collision; frame-scaling artifact | Do not read single-frame text or geometry from compressed crops without adjacent-frame checks. |
| 3 | Manual image-plane tracking | Pixel coordinates, path length, pixel rates, apparent heading changes | `D33/PR34`, `D38/PR36`, `D27/PR29`, `PR44` | Object motion; sensor pan; gimbal stabilization; platform motion; tracker correction | Image-plane tracks are not physical trajectories without FOV, range, platform motion, and pointing metadata. |
| 4 | FOV and slant-range sensitivity sweeps | Implied speed/range scenarios under assumed HFOV and range | `D33/PR34` geometry pass; `D27/PR29` geometry pass | Report speed true at near/wide FOV; report speed true at far/narrow FOV; sensor motion dominating pixel motion | The sweep tests compatibility, not truth. It cannot select the correct FOV or range from the public MP4 alone. |
| 5 | Report-field extraction and normalization | Times, speeds, altitudes, headings, object counts, coordinates, sensor names | `D25`, `D27`, `D33`, `D35`, `D54`, `D8`, `D65`, `D74`, `D75` | Report estimate; platform-relative field; target field; OCR or metadata noise | Treat values as report-derived unless independently paired with source telemetry or calibrated imagery. |
| 6 | Coordinate decoding and geodesic checks | Lat/lon from MGRS or DMS coordinates; regional clustering; approximate distances if endpoints exist | `D54`, `D8`, `D65`, `D75`, `D61` | Correct grid; partial grid; title/grid mismatch; transcription or OCR error | A target coordinate alone does not yield slant range or altitude. |
| 7 | Phase alignment against official release descriptions | Useful intervals, loss/reacquisition boundaries, modality switches, zoom phases | `D25/PR28`, `D33/PR34`, `D35/PR35`, `D38/PR36`, `PR44` | Public video supports report phase; video is only title-level related; mismatch or source-index error | Phase agreement supports release identity and timing, not physical performance by itself. |
| 8 | Apparent-size and contrast-area measurement | Contrast-area changes, apparent growth/shrinkage, centroid stability, exit timing | `PR45`, `PR47`, `PR41`, `PR44`, `PR49` | Real closure; zoom change; focus/exposure change; threshold artifact; reticle overlap | Apparent size is a visual proxy, not physical size. |
| 9 | Multi-contact counting and track continuity | Number of visible compact returns, candidate persistence, track splitting | `PR47`, `PR42`, `D56`, `D58`, `D65` | Multiple objects; one object split by detector; glints; water/cloud clutter; track reinitialization | Count compatibility is weaker than report/video pairing and cannot establish object identity alone. |
| 10 | Sensor-context exploitation | Missing telemetry targets, radar/target-pod/EW source requests, conventional-confound mapping | `D58`, `D28`, `D61`, `D65`, `D74`, `D75` | Conventional aircraft; drone; EW platform; sensor artifact; unresolved UAP | Useful for prioritization, not direct public reconstruction. |
| 11 | Range-fouler geometry extraction | Slant range, ground range, sensor depression angle, HAT, contact count | `D44`, `D57`, `D58` | Actual range geometry; OCR noise; form-field mismatch; platform-relative interpretation | Current one-page forms are enough for triage, not formal reconstruction. |
| 12 | Control-lane false-positive calibration | Reticle artifacts, glare/halo behavior, cloud/water false positives, detector acceptance floor | `PR21/D14`, `PR31-PR33/D32`, `D10`, `D18`, `D35/PR35` | True compact return; benign aircraft; glare; cloud; water texture; reticle selection | Any detector or manual rule that fails controls should not be used for telemetry inference. |
| 13 | Provenance and label reconciliation | Correct report/video identity, source-index conflicts, duplicate handling | `D25/D7`, `D27/D8`, `D54/D31`, `D56-D58` metadata-title noise | Official label error; local filename mismatch; duplicate; unrelated same-number case | Wrong pairing invalidates downstream telemetry scenarios. |
| 14 | Historical structured-field OCR | Legacy speed, size, direction, weather, sound, altitude language | `38_143685...`, `342_hs1...`, `341_110677...` | Witness estimate; institutional summary; OCR artifact; later archival grouping | Historical fields are useful context, not calibrated telemetry. |
| 15 | Synthetic and blinded validation | Reviewer agreement, threshold sensitivity, false-positive/false-negative behavior | Any manual or automated video-review pipeline | Robust detector; overfit detector; reviewer expectation bias; compression sensitivity | Validation supports method reliability, not case truth. |

## Scenario Families

Use these scenario families when a technique produces more than one possible interpretation:

| Evidence type | Scenario family A | Scenario family B | Scenario family C | Scenario family D |
|---|---|---|---|---|
| Meter-like overlay label | Actual meter/range readout | Track-box or range-gate parameter | Generic display annotation | OCR or compression artifact |
| Pixel motion | Physical object motion | Sensor pan or gimbal motion | Platform motion | Tracker correction or interpolation artifact |
| Apparent turn | True heading change | Panning/stabilized frame geometry | Track-box re-lock | Detection jump between features |
| Apparent growth | Physical closure | Zoom/FOV change | Exposure/focus/contrast change | Reticle or compression interaction |
| Multiple contacts | Multiple physical objects | One object split by detection | Glints/reflections | Background clutter |
| Report speed | Target speed estimate | Platform-relative closure | Operator narrative estimate | OCR/source-summary error |
| Coordinate field | Exact event grid | Partial/redacted grid | Title/grid mismatch | Transcription/OCR error |
| Radar/EW narrative | Conventional military platform | Drone or range activity | EW/training artifact | Unresolved sensor event |

## Recommended Work Order

1. Confirm source identity and report/video pairing.
2. Extract report fields, coordinates, and visible overlay labels.
3. Stabilize and crop the highest-value frame regions.
4. Test label persistence and OCR across adjacent frames.
5. Build image-plane tracks only after phase alignment is stable.
6. Run FOV/range sensitivity sweeps as scenario tests.
7. Compare against control lanes and false-positive behavior.
8. Promote only bounded claims into the evidence ladder.
9. Convert unresolved ambiguity into source requests for raw telemetry.

## Current Priority Targets

| Priority | Target | Why |
|---:|---|---|
| 1 | `PR44` / `DOD_111689115.mp4` overlay region | Best current meter-like overlay candidate and strongest standalone compact-return clip. |
| 2 | `D58` | Best operational source-request case: radar lock, target-pod video, EW/noise-jamming, closest range, and two contacts. |
| 3 | `D33/PR34` | Best image-plane maneuver benchmark with an existing geometry sweep. |
| 4 | `D27/PR29` | Best track-box/object alignment case with a speed-report scenario. |
| 5 | `D44/D57` | Best document-only range-geometry pair, pending clearer forms or raw data. |

## Bottom Line

The highest-value forensic path is overlay extraction plus scenario testing, not a single-frame interpretation. A label like `5m` or `10m` is worth pursuing because it may encode measurement context, but it should be promoted only after persistence, semantics, and source-resolution checks survive control comparisons.
