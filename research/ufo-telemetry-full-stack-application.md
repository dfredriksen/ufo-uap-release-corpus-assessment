# UFO Telemetry Recovery Full-Stack Application

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: applying telemetry recovery methods to the full current evidence stack
Status: application pass

## Purpose

This note applies the telemetry recovery methods to the current evidence stack, rather than merely listing the methods. It covers:

- Tier 1 hard report/video or strong report/video lanes
- Tier 2 document-only source-request lanes
- Tier 3 standalone video lanes
- Tier 4 pattern and narrative lanes
- control and caveat cases
- Release 02 video and non-video tranche material

The output is a bounded telemetry audit. It records what can be extracted, what scenario families remain plausible, and what missing source data would be required for physical reconstruction.

The explanation-screening pass that uses these outputs to rule out or preserve explanation families is `research/ufo-telemetry-explanation-screening.md`.

## Overall Result

The full stack yields useful derived telemetry, but not raw telemetry.

Strongest recoverable classes:

- report-derived speeds, altitudes, times, headings, object counts, and coordinates
- decoded coordinates and regional geometry
- image-plane tracks, pixel rates, path lengths, and apparent heading changes
- explicit overlay/readout candidates such as the `10M` / `10m`-like `PR44` label
- source-request targets for radar, target-pod video, EW logs, gimbal state, platform motion, and unredacted grids

Not recoverable from the public stack alone:

- validated physical speed
- validated object size
- validated acceleration
- raw slant-range time series
- platform/gimbal state by frame
- object origin or technology

## Method Coverage

| Method | Applied to full stack? | Highest-yield cases | Result |
|---|---:|---|---|
| Overlay OCR and label persistence | Yes | `PR44`; external `5m` frame example | One repo-local `10M` / `10m`-like label candidate; semantics unresolved. |
| Source-resolution crop stabilization | Yes, where prior crops exist | `PR44`, `PR29`, `PR34`, `PR38` | Supports overlay and object-lane review; does not resolve physical telemetry. |
| Manual image-plane tracking | Yes | `D38/PR36`, `D33/PR34`, `D27/PR29`, `PR44`, `D23/PR27` | Produces pixel tracks, acceptance counts, path lengths, and apparent motion proxies. |
| FOV/range scenario sweeps | Yes, for best cases | `D33/PR34`, `D27/PR29`, `D38/PR36` | Tests compatibility with report speeds; cannot select true range or FOV. |
| Report-field extraction | Yes | `D25`, `D27`, `D33`, `D35`, `D54`, `D8`, `D61`, `D65`, `D74`, `D75`, `D58` | Highest-yield public telemetry source; values remain report-derived. |
| Coordinate decoding | Yes | `D54`, `D8`, `D65`, `D75`, `D61` | Produces approximate geospatial anchors and exposes title/grid mismatches. |
| Phase alignment | Yes | `D25/PR28`, `D33/PR34`, `D35/PR35`, `D38/PR36`, `PR44` | Supports release identity and useful intervals. |
| Apparent-size and contrast-area analysis | Yes | `PR45`, `PR47`, `PR41`, `PR44`, `PR49` | Produces visual proxies only; no physical size. |
| Multi-contact counting | Yes | `PR47`, `PR42`, `D56`, `D58`, `D65`, `PR050`, `PR079`, `PR098` | Useful for scenario filtering, weak for physical identity. |
| Sensor-context exploitation | Yes | `D58`, `D28`, `D61`, `D65`, `D74`, `D75`, Release 02 operational clips | Produces source-request priorities and conventional-confound maps. |
| Range-fouler geometry extraction | Yes | `D44`, `D57`, `D58` | Extracts slant/ground range fields and sensor angles where present, but not enough for formal reconstruction. |
| Control-lane calibration | Yes | `PR21/D14`, `PR31-PR33/D32`, `D10`, `D18`, NASA Release 02 audio, altered Release 02 videos | Defines artifact floor and prevents overclaiming. |
| Provenance reconciliation | Yes | `D25/D7`, `D27/D8`, `D54/D31`, `D56-D58`, Release 02 duplicates | Prevents false telemetry extraction from wrong pairings. |
| Historical structured OCR | Yes, targeted | Historical FBI/archive, `D017`, CIA/DOE context | Produces context fields, not calibrated telemetry. |
| Blinded/synthetic validation | Not yet fully executed | All video pipelines | Listed as next methodological hardening; not complete as an applied validation run. |

## Tier 1 Application

| Case | Methods applied | Extracted telemetry-like output | Remaining scenarios | Current telemetry status |
|---|---|---|---|---|
| `D38/PR36/DOD_111689030.mp4` | Pairing, phase alignment, manual validation, image-plane tracking | Hard report/video anchor; validated compact-return interval around `50-87s`; `38` accepted one-second points. | Physical object motion; panning sensor; track update; camera state change. | Best calibration anchor, not a physical reconstruction. |
| `D33/PR34/DOD_111689011.mp4` | Report fields, manual image-plane tracking, FOV/range sweep | Report-derived `80 MPH`; `111` samples; `97` accepted marks; `7` apparent heading-change events; `118.84 px/s` path-average. | True turns; sensor slew; gimbal stabilization; platform motion; tracker correction. | Strongest image-plane maneuver benchmark; speed remains report-derived. |
| `D25/PR28/DOD_111688954.mp4` | Report fields, phase alignment, SWIR-track review | Report-derived `434 KNOTS`, `FL200`, SWIR-only field; dense SWIR interval with `217` high-or-medium rows. | True speed; platform-relative field; SWIR artifact; source-index mismatch with `D7`. | Strong SWIR sequence support, no public speed validation. |
| `D27/PR29/DOD_111688964.mp4` | Report fields, visual alignment, dense marking, geometry scenarios | Report-derived `140 KNOTS`; `101` dense samples; `40` track-box relation samples; `95` vertical-feature flags. | Physical pole/bar; water reflection; track-box artifact; source-index mismatch with `D8`. | Strong visual/report-content match, no independent kinematics. |
| `D23/PR27/DOD_111688825.mp4` | Manual validation, phase review, control classification | `327` active rows; `175` true compact-return candidates; `144/181` late-interval accepted rows. | Compact return; reticle artifact; water texture; frame-edge artifact; candidate definition drift. | Strong manual-validation comparator, not tied to exact D23 UAP line. |
| `D35/PR35/DOD_111689022` | Report fields, phase alignment, control comparison | Report-derived `30 MPH`; sequence supports ocean-surface/toward-land lane. | Object motion; cloud/shore/terrain confound; weak object-level track. | Paired control/comparison case; low kinematic value. |

## Tier 2 Application

| Case | Methods applied | Extracted telemetry-like output | Remaining scenarios | Current telemetry status |
|---|---|---|---|---|
| `D58` | Report fields, sensor-context exploitation, source-request mapping | `10/27/20 01:12:21Z`; `26000`; `060/20`; two contacts; `16.9 NM`; radar lock; target-pod video; noise jamming. | Military aircraft; drone; EW platform; unresolved two-contact sensor event. | Best source-request target; not public kinematics. |
| `D28` | Report fields, source-context exploitation | AGM-176 phase; MX-20/MX-25 IR lens-flare language; event timing around weapon release and impact. | Munition/sensor artifact; conventional object; unresolved sensor event. | High-value request target for raw imagery and weapon timeline. |
| `D74` | Report fields | `092153:00ZNOV23`; estimated `424KN`; seven-minute near-co-altitude narrative. | Estimated speed; relative geometry; narrative summary without raw sensor data. | Strong readable report, document-only. |
| `D75` | Report fields, coordinate-lane extraction | `140517:00ZJUL24`; FMV primary sensor; `38P MT` lane; low altitude; `NW` trajectory; faster-than-platform statement. | Redacted absolute speed; platform-relative movement; straight path vs sensor geometry. | Useful structured fields, no shape or absolute speed. |
| `D44/D57` | Range-fouler geometry extraction | D44: `4.06 NM`, `4.78 KM`, `-50 deg`, `19,073 HAT`; D57: about `6.1? NM`, `8.81 KM`, `-39 deg`, `23,819 HAT`. | OCR noise; platform-relative interpretation; conventional aircraft/drone; no paired video. | Best document-only geometry pair, still not formal reconstruction. |
| `D8` | Report fields, coordinate decoding, provenance reconciliation | `1653Z`; two round white-hot UAPs; `240NM/HOUR`; `35SQT3423692957` -> Eastern Mediterranean approximate coordinate. | True grid vs title mismatch; report estimate; separate from PR29/D27. | Quantitative document-only case with label/location caveat. |
| `D54` | Report fields, coordinate decoding | `1319Z`; `363453N 0255943E`; `24,989FT MSL`; `168KTS`; triangular/metallic description. | Sparse report value; metadata mismatch with `D31`; no media. | Useful Aegean document-only coordinate/speed row. |

## Tier 3 Application

| Case | Methods applied | Extracted telemetry-like output | Remaining scenarios | Current telemetry status |
|---|---|---|---|---|
| `PR44/DOD_111689115.mp4` | Overlay OCR, dense track, phase alignment, late review | `10M` / `10m`-like label; `446` dense rows; `41.029 px/s` path-average; sustained compact-return interval. | Meter readout; range gate; track-box parameter; object return; overlay artifact. | Highest-value overlay target and strongest standalone visual clip. |
| `PR47/DOD_111689142.mp4` | Multi-contact counting and formation review | Three-component groups in `349/598` rows; high-or-medium support in `466/598` rows. | Three objects; split detection; glints; background clutter. | Strong formation comparator, no physical separation or speed. |
| `PR45/DOD_111689123.mp4` | Apparent-size and exit review | Central contrast growth and lower-right exit-adjacent motion. | Closure; zoom/contrast change; reticle/track-box confound. | Apparent-size proxy only. |
| `PR38/DOD_111689051.mp4` | Contrast-shape review, image-plane path proxy | `90` supported star-like rows; `14984.312 px` path length; `145.479 px/s` path-average. | Star-like target; sensor/optical effect; cut-gap artifact. | Visual-description benchmark, not physical telemetry. |
| `PR41`, `PR48`, `PR49`, `PR37`, `PR39`, `PR40`, `PR43`, `PR46` | Standalone visual audits | Compact contrast, centered-track, two-area, top-third, loop, or morphology support depending on clip. | Real target; sensor artifact; compression; terrain/cloud texture. | Standalone visual context only unless a report pairing appears. |

## Tier 4 And Pattern Application

| Case family | Methods applied | Extracted telemetry-like output | Remaining scenarios | Current telemetry status |
|---|---|---|---|---|
| Persian Gulf / Strait `D60-D65` | Report fields, timeline, coordinate decoding, pattern analysis | D61: `271527:00ZAUG20`, formation, `NE-NW`, two-minute track; D65: three FMV observations and full grid `39RUN6234236874`. | Repeated separate reports; repeated conventional activity; sparse UAP observations; sensor/weather limits. | Reporting-density pattern, not performance proof. |
| Western U.S. slide/narrative lane | Narrative extraction, provenance review | Four witness-summary clusters and linked Release 02 ODNI narrative/photo context. | Witness narrative; briefing synthesis; still-image provenance; no raw telemetry. | Narrative/context lane, not kinematic evidence. |
| Historical FBI/archive and `D017` | Structured OCR and historical context review | Dates, colors, directions, institutional concern, green-fireball classifications, sensitive-installation context. | Witness estimate; archive summary; OCR noise; historical reporting bias. | Historical context only. |
| NASA Release 02 audio controls | Control-lane review | Fireflies, light flashes, particles, mission hardware, dye-pack context. | Spaceflight environment; hardware/ice/condensation; internal visual effects. | Control/caveat material. |
| CIA/DOE Release 02 context | Historical/provenance review | CIA USSR luminous-object narrative; DOE Pantex image/provenance packet; DOE correspondence context. | Historical narrative; image provenance; no motion record. | Context/provenance only. |

## Control And Caveat Application

| Control family | Recovery method applied | What it constrains |
|---|---|---|
| `PR21/D14` probable aircraft | Control-lane calibration | Shows that release identity and visual track do not imply anomaly. |
| `PR31-PR33/D32` glare/halo set | Artifact-floor calibration | Constrains reticle, halo, glare, and compression false positives. |
| `D10` possible birds/dust | Conventional explanation control | Constrains bird/dust lanes and degraded FMV confidence. |
| `D18` UAP/UAV ambiguity | Conventional-platform ambiguity | Keeps UAP/UAV ambiguity from being overpromoted. |
| Release 02 altered clips `PR051-PR056` and `PR072` | Provenance/control review | Prevents digitally altered clips from entering kinematic reconstruction. |
| Release 02 duplicate pair `PR057a/PR057b` | Provenance reconciliation | Prevents duplicate assets from inflating pattern density. |

## Release 02 Application

| Release 02 family | Methods applied | Extracted telemetry-like output | Remaining scenarios | Current telemetry status |
|---|---|---|---|---|
| `PR050` | Multi-contact counting, phase/context triage | Title/page-level over-water formation lane with four contrast areas plus a fifth entering from top-left. | Formation; multiple ordinary contacts; sensor/background artifacts; no report pairing. | Standalone pattern comparator only. |
| `PR051-PR056` | Provenance review, control-lane calibration | Alteration status, replay modes, thresholding/sharpening notes, cloud-limited or mode-change context. | True motion; edit-induced apparent motion; threshold artifact; replay-speed artifact. | Control material; do not use for kinematic reconstruction. |
| `PR057a/PR057b` | Provenance reconciliation | Explicit duplicate relationship and alternate titles for one underlying asset. | Duplicate inflation; title-based overcounting; one-event/two-row confusion. | Deduplication control, not telemetry. |
| `PR065-PR071` | Sensor-context triage | USCG Tyndall TIC TAC IR-hot, USO/submarine, fifth-generation aircraft, F/A-18 FLIR, Eglin aircrew, Lake Huron comparator lanes. | Operational UAP; conventional aircraft; shootdown/kinetic comparator; no local report link. | Source-request candidates, no public telemetry extraction yet. |
| `PR072-PR079` | Provenance review, multi-contact triage | Administrative revision, Columbus multi-UAP, two-part tracking set, three-fast-moving-UAPs lane. | Digitally altered device clip; multiple objects; duplicate-like family; title-level speed language. | Standalone triage; no hard local pairing. |
| `PR091`, `PR093`, `PR095`, `PR098` | Regional pattern comparison, provenance reconciliation | Persian Gulf / Gulf of Arabia contrast and formation family; `PR093` and `PR095` same-title non-duplicate clarification. | Regional pattern; repeated assets; distinct assets with same title; no raw kinematics. | Pattern comparator only. |
| Remaining Release 02 video rows | Release-index hygiene | Confirmed as part of 51-row DVIDS video tranche. | Unreviewed telemetry details at frame level; title-only patterns; no local report pairing. | No promotion until case-level frame review or source linkage appears. |
| `ODNI-UAP-D001` | Narrative extraction, provenance linkage | FLIR/NVG/naked-eye narrative, orb split, swarm, and Release 01 imagery linkage. | First-hand narrative; still-image corroboration; missing raw sensor metadata. | Strong narrative/provenance lane, no public kinematics. |
| `DOE-UAP-D001` | Image/provenance review | Pantex radar-tower image and enhanced object imagery. | Small object image; enhancement artifact; missing motion sequence. | Image provenance lane, not telemetry. |
| `DOW-UAP-D017`, `CIA-UAP-D001`, `DOE-UAP-D002-D003` | Historical/context OCR | Sandia green-fireball history, USSR luminous-object narrative, Los Alamos/scientific context. | Historical narrative; archive summary; context only. | Historical context, not telemetry reconstruction. |
| `NASA-UAP-D008-D014` | Control-lane review | Spaceflight light flashes, particles, fireflies, hardware/dye-pack context. | Internal visual effects; ice/condensation; mission hardware; environmental particles. | Control/caveat set. |

## Extracted Scenario Outputs

These are the strongest scenario outputs after applying the methods:

| Scenario output | Evidence basis | Status |
|---|---|---|
| `PR44` overlay scenario | `10M` / `10m`-like label plus sustained compact-return track | High-priority follow-up; label semantics unresolved. |
| `D33/PR34` 80 MPH compatibility scenarios | Manual track plus FOV/range sweep | Does not falsify report speed under some assumptions; does not validate speed. |
| `D27/PR29` 140-knot scenarios | Dense track plus report speed | Compatible under multiple FOV/range configurations; speed remains report-derived. |
| `D44/D57` range-geometry comparison | Slant range, ground range, HAT, sensor angle fields | Geometry-rich document pair; OCR/source clarity limits formal reconstruction. |
| `D58` multi-sensor request scenario | Radar lock, target-pod video, EW/noise-jamming, closest range | Best path to true telemetry if raw records are released. |
| Release 02 pattern comparison | 51 video rows, 13 non-video rows, altered/duplicate/control handling | Broadens source landscape; no new hard local report pairing. |

## Missing Data Required For Physical Reconstruction

For nearly every high-value case, the same missing data controls the claim ceiling:

- original sensor video or mission-system file
- frame-level metadata
- FOV and zoom state
- slant range or range-time series
- platform position, speed, attitude, and heading
- gimbal pointing and stabilization state
- radar track history and track quality
- EW receiver details for jamming claims
- unredacted coordinates and timestamps
- official correction of source-index mismatches where applicable

## Completion Judgment

The telemetry recovery methods have now been applied across the full evidence stack at the publication-note level.

The result does not produce new proof of extraordinary performance. It produces a defensible derived-telemetry map:

- which values are extractable now
- which cases support only scenario testing
- which ambiguity families remain live
- which raw source records would be needed to promote a case

Coverage check:

- Tier 1 hard report/video lanes: applied.
- Tier 2 document-only lanes: applied.
- Tier 3 standalone video lanes: applied.
- Tier 4 pattern and narrative lanes: applied.
- Control/caveat cases: applied.
- Release 02 video and non-video tranche families: applied.
