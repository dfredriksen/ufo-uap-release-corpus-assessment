# Scientific Assessment of the UFO/UAP Release Corpus

Owner: Dan Fredriksen
Draft created: 2026-05-14
Source files: official public UFO/UAP release files, not redistributed in this repository
Report status: public release version, consistency checked; modern operational subset reviewed in depth, broader historical/image subsets covered by targeted triage

## Abstract

This report evaluates an assembled corpus of `170` UFO/UAP-related files totaling approximately `4.24 GB`: `91` PDFs, `41` MP4 videos, `34` JPG images, and `4` PNG images. The corpus includes modern DoW/DoD mission reports and range-fouler records, public DoD video releases, recent briefing material, historical FBI/archive PDFs, NASA transcript and image material, State Department cables, and FBI photo sets.

The material with highest probative value is the modern operational subset: official mission reports, range-fouler forms, and public DoD video releases. These records support a finding of credible unresolved operational observations. They do not, on the evidence reviewed here, establish non-human technology, recovered material, biological claims, a single unified phenomenon, or independently reconstructed extraordinary physics.

The principal evidence lanes are hard report/video pairings or strong report-content/video reconciliations, especially `D38/PR36/DOD_111689030.mp4`, `D33/PR34/DOD_111689011.mp4`, `D25/PR28/DOD_111688954.mp4`, `D27/PR29/DOD_111688964.mp4`, `D23/PR27/DOD_111688825.mp4`, and `D35/PR35/DOD_111689022`. Important document-only source-request targets include `D58`, `D28`, `D74`, `D75`, `D44/D57`, `D8`, and `D54`; within that set, `D58` and `D28` preserve the densest operational context. The main regional pattern is the Persian Gulf / Strait of Hormuz 2020 cluster, where `D61` provides the most informative behavior row and `D65` the densest single mission record.

The principal scientific limitation is the absence, in most public videos and redacted reports, of raw telemetry, sensor field of view, slant range, platform motion, gimbal pointing, exact coordinates, and frame-level metadata. Reported speeds, altitudes, object shapes, and maneuvers therefore remain, in many cases, source-reported claims rather than independently reconstructable physical findings.

## Scope

The full source folder was inventoried. Review depth varied by source family. Modern DoW/DoD operational records and public DoD videos received the most detailed treatment because they preserve the most probative fields: event times, mission context, sensor context, object descriptions, reported behavior, negative controls, and official release metadata.

Historical FBI/archive PDFs, NASA transcript and image material, State Department cables, and FBI photo sets were assessed through targeted source-family triage. They were not exhaustively OCR-reviewed, photogrammetrically measured, or interpreted at the same depth as the modern operational subset. These materials should be treated as lower-priority context unless future extraction promotes specific records into the main evidence ladder.

Accordingly, the report's main findings concern the modern operational subset and public media releases, not every historical page or image in the broader folder.

Primary scope artifacts:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-manifest.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-report-coverage-audit.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-map.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-analysis-thread.md`

## Materials and Methods

The review followed a conservative source-first protocol:

1. Inventory all source files without moving, renaming, or altering the originals.
2. Identify duplicate media and duplicate PDFs where exact same-size candidates were present.
3. Extract embedded PDF text where available.
4. Use OCR only on derived copies or page renders when embedded text was unavailable.
5. Cross-check local filenames, PDF text, War.gov source files, and DVIDS public release metadata.
6. Build video contact sheets and targeted visual passes for selected high-value public MP4s.
7. Separate source-reported claims from locally observed public-media behavior.
8. Rank evidence by provenance, source context, report/video linkage, visual support, and caveats.
9. Apply targeted group-level triage to NASA/DOS, FBI photo, and historical/archive material where local extraction or high-resolution review was limited by disk/read constraints.
10. Generate and validate publication figures from the manifest, coverage map, evidence ladder, source-request table, and transparent keyword scans.
11. Prepare and archive publication-stage review packets and returned outputs: one ChatGPT Pro packet for editorial polish without strengthening unsupported claims, and one Claude packet for methodological and evidentiary critique before public revision.

The video analysis was intentionally bounded. Local visual review can support statements about image-plane features, compact returns, relative contrast, phase sequence, apparent image-plane turns, and visible release-description alignment. It cannot establish true object speed, altitude, range, physical trajectory, or acceleration without sensor geometry and platform data.

Methods artifacts:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-duplicate-candidates.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-targeted-duplicate-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dedupe-summary.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-evidence-ladder.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-nasa-dos-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/figure-validation.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/generate_publication_figures.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/review-packets/chatgpt-pro-touchup-packet.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/review-packets/chatgpt-pro-polished-paper.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/review-packets/claude-review-packet.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/review-packets/claude-review-output.md`

## Evidence Standard

Four practical evidence tiers were used:

| Tier | Meaning | Examples |
|---|---|---|
| Tier 1 | Hard report/video pairings or strong report-content/video lanes with bounded visual analysis | `D38/PR36`, `D33/PR34`, `D25/PR28`, `D27/PR29`, `D23/PR27`, `D35/PR35` |
| Tier 2 | High-value document-only reports with strong operational context but no hard public video pairing | `D58`, `D28`, `D74`, `D75`, `D44/D57`, `D8`, `D54` |
| Tier 3 | Standalone public videos with useful local visual analysis but no written-report pairing | `PR44`, `PR47`, `PR45` |
| Tier 4 | Pattern, narrative, or lower-provenance lanes | Persian Gulf / Strait 2020 cluster, Western U.S. slide deck |

The ranking measures analytic utility, not strangeness. A case ranks higher when it preserves source identity, exact time, location, sensor context, report/video linkage, object behavior, negative controls, and a concrete source-request path. It ranks lower when the available record is redacted, unpaired, metadata-conflicted, reporter-derived only, visually ambiguous, or conventionally confounded.

## Figures

The figures were generated from repository artifacts using `scripts/generate_publication_figures.py`. Validation checks are recorded in `figures/figure-validation.md`.

![Figure 1. Corpus Media Composition](figures/fig1-corpus-media-composition.svg)

Figure 1 shows the `170` source files by media type: `91` PDFs, `41` MP4 videos, `34` JPG images, and `4` PNG images.

![Figure 2. File-Level Coverage Status](figures/fig2-file-coverage-status.svg)

Figure 2 reports review coverage. No manifest row remains inventory-only; the largest bucket is targeted review for broader NASA/DOS, FBI photo, and historical/archive material.

![Figure 3. Evidence Ladder Ranking](figures/fig3-evidence-ladder-ranking.svg)

Figure 3 plots the `18` ranked evidence-ladder rows. The ranking measures analytic utility and source quality, not strangeness.

![Figure 4. Source-Request Priorities](figures/fig4-source-request-priorities.svg)

Figure 4 lists the top raw-data/source-request priorities. The first two priorities, `D58` and `D28`, are document-only cases with dense operational context but insufficient public data for physical reconstruction.

![Figure 5. Common Themes in Ranked Evidence Rows](figures/fig5-evidence-ladder-theme-frequency.svg)

Figure 5 presents a controlled keyword-frequency visualization across the `18` ranked evidence-ladder rows. It is illustrative only; it should not be read as a real-world prevalence estimate.

## Principal Findings

### Finding 1: The corpus supports unresolved operational reporting

Official U.S. records in the release contain multiple structured reports of unresolved aerial or sensor observations in operational contexts. The most informative records include mission timing, supported unit, sensor type, aircraft/platform context, observation fields, weather or mission-effect fields, and explicit UAP/range-fouler language.

This supports a significant but bounded finding: the corpus preserves unresolved operational reporting. It does not establish non-human technology. The public record repeatedly withholds or redacts the data needed to test physical-performance claims.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-priority-incidents.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-modern-event-timeline.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-evidence-ladder.md`

### Finding 2: Hard report/video pairings exist

The source set is not merely a collection of disconnected reports and videos. Several public MP4s can be tied to official release pages and, in some cases, to stated accompanying reports.

The clearest anchor is `D38/PR36/DOD_111689030.mp4`. DVIDS explicitly pairs the public video with `DoW-UAP-D38`, and local visual review supports compact point-return behavior during the useful interval. D38 therefore serves as the report's calibration case.

Additional high-value public lanes include:

- `D33/PR34/DOD_111689011.mp4`: Greece ocean-surface maneuver lane. Manual tracking supports multiple sharp apparent image-plane heading changes, including `>=60` degree image-plane heading changes in the reviewed track, while true physical 90-degree turns and `80 MPH` remain report-derived.
- `D25/PR28/DOD_111688954.mp4`: Greece SWIR-only lane. The public video supports the SWIR acquisition/loss sequence, while `434 KNOTS`, size, altitude, and detailed shape remain report-derived.
- `D27/PR29/DOD_111688964.mp4`: UAE over-water unusual morphology lane. The public video aligns with the pole/bar or possible-reflection description, but the pole/bar may be a water reflection and the `140 KNOTS` value remains report-derived.
- `D23/PR27/DOD_111688825.mp4`: long hard-paired visual sequence. Manual validation supports repeated compact-return candidates, especially in the late loss/reacquisition interval: `144/181` reviewed late-interval frames were validated as compact-return candidates versus `31/146` in the earlier comparison interval. The public video does not identify which D23 UAP row it depicts.
- `D35/PR35/DOD_111689022`: Greece ocean-surface control/comparison lane. The public clip supports the broad sequence, while clouds, shoreline, terrain, and the report's `NONE` maneuverability field limit its anomaly value.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-manual-track-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr28-d25-phase-review-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-visual-alignment.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-pr35-phase-review-notes.md`

### Finding 3: Public videos do not independently establish physical kinematics

The reviewed videos generally do not contain the sensor metadata required for physical reconstruction. Public video review can detect or validate image-plane behavior, phase alignment, compact-return candidates, contrast persistence, or formation-like visual structure. It cannot independently convert those observations into real-world speed, altitude, range, acceleration, or physical turn geometry.

`D33/PR34` illustrates the boundary. Local manual tracking supports multiple sharp apparent image-plane heading changes, including `>=60` degree image-plane changes, and geometry scenarios do not falsify the report's `80 MPH` value. The same analysis also shows that actual FOV/zoom, slant range, platform motion, gimbal pointing, and telemetry are required before those image-plane turns can be treated as real physical maneuvers.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility.md`

### Finding 4: Several source-index conflicts are real

The corpus contains official-source label and metadata conflicts. These conflicts must be preserved rather than smoothed over.

Key examples:

- DVIDS `PR29` says the accompanying report is `DoW-UAP-D8`, but local/War.gov `D8` is a separate Djibouti 2025 / Eastern Mediterranean-grid document-only case. The written-report content summarized by PR29 matches local/War.gov `D27`.
- DVIDS `PR28` says the accompanying report is `DoW-UAP-D7`, but local/War.gov `D7` is an Arabian Gulf 2020 balloon-like/TFLIR case. The written-report content summarized by PR28 matches local/War.gov `D25`.
- War.gov/local PDFs for `D56`, `D57`, and `D58` carry PDF metadata title/subject values resembling `DoW-UAP-D33`, `DoW-UAP-D34`, and `DoW-UAP-D35`, but those labels conflict with already-reviewed Greece lanes. These are best treated as metadata noise unless an official correction appears.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d8-d27-reconciliation.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr28-d25-d7-reconciliation.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-official-metadata-check.md`

### Finding 5: D58 is the highest-value document-only source-request target

`D58` is the leading unresolved document-only case in the range-fouler lane. It preserves radar lock, target-pod video, KINGPIN-directed identification, two IR-significant contacts, red blinking strobes, closest range `16.9 NM`, and noise-jamming language.

Those details are operationally important, but they also leave substantial conventional explanation space. Red blinking strobes, radar/target-pod context, jamming indications, and directed identification can fit military aircraft, drones, or electronic-warfare platforms. D58 should therefore be treated as a high-priority source-request case, not as a public proof-of-anomaly case.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d58-evidence-packet.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d58-evidence-constraints.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-cluster-packet.md`

### Finding 6: D28 is the clearest weapons-context document-only case

`D28` is important because the report body places the event in an Iraq / Ayn Al Asad / Operation Inherent Resolve context and describes a UAP during an AGM-176 weapons-employment sequence, with MX-20/MX-25 IR lens-flare language. The report is operationally narrow and warrants a targeted source request.

The file's title/filename indicates East China Sea, but the body metadata is consistently USCENTCOM / Iraq-context. A release-index search found no hard public PR/video pairing for D28 or its unique anchors. The case remains document-only and cannot support public physical reconstruction without raw imagery and weapon timeline data.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-release-index-search.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-evidence-packet.md`

### Finding 7: Persian Gulf / Strait 2020 is a reporting-density pattern, not a performance lane

The core Persian Gulf / Strait of Hormuz 2020 cluster is `D60-D65`. `D4` and `D5` are adjacent but should not be treated as core Gulf/Strait rows because their readable full MGRS grids decode outside the Gulf/Strait lane despite Arabian Gulf filenames.

Inside the core `D60-D65` cluster:

- `D61` is the most informative behavior row. It reports a formation of unknown flying objects moving `NE-NW` along the coast, tracked for about two minutes before PID was lost in cloud cover.
- `D65` is the densest mission. It records three FMV UAP observations on `2020-07-16`, including one full observed-activity grid, `39RUN6234236874`, decoded locally to approximately `29.253233N, 49.583281E`.

This lane supports a regional reporting-density finding. It does not support object-level physical performance claims because the rows are sparse, redacted, and unpaired to public raw video or telemetry.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-persian-gulf-2020-timeline.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d61-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d65-source-review.md`

### Finding 8: The corpus contains its own controls

The corpus is not limited to high-anomaly claims. It includes control and caveat records that point toward mundane or ambiguous explanations:

- possible birds and dust-limited FMV collection
- probable aircraft
- possible UAP/UAV ambiguity
- glare and halo artifacts
- balloon-like wind-traveling objects
- public videos with no written reporter description
- conventionally confounded military-platform signatures

These controls have analytic value. They show that the release includes unresolved, ambiguous, and likely mundane lanes, reducing the risk that the evidence ladder is driven only by selection of anomalous-sounding cases.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-evidence-ladder.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-priority-incidents.md`

### Finding 9: Historical and static-image material adds breadth, not stronger physical evidence

The targeted NASA/DOS, FBI-photo, and historical/archive passes broaden the corpus but do not alter the evidence hierarchy.

NASA records add useful historical spaceflight context, especially Apollo 12, Gemini 7, Apollo 17, and Skylab material. Their highest-value lanes remain bounded by particles, booster or panel context, spacecraft debris/fragments, satellites, light-flash controls, and lack of calibration for independent object claims.

The FBI photo set covers `32` official records represented by `33` local files because `B6` appears both as a PDF and an extracted JPG. The A-series is low-context single still imagery with no location or mission report. The B-series has more context, but remains single-frame, redacted, and without reliable embedded image time. `B5` is a useful control-like frame with no distinct central object, while `B7` supplies an explicit conventional-appearance cue because the visible object is consistent with a helicopter.

The historical/archive PDFs confirm long-running official, military, FBI, diplomatic, and public interest in unusual aerial reports from World War II through the present. The highest-priority future OCR candidates are the `342` flying-discs file and the two `38_143685` incident-summary files, because they are most likely to preserve structured event fields. At current public-triage depth, however, they do not outrank the modern operational report/video lanes.

Primary support:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-nasa-dos-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-record-index.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-record-index.csv`

## Evidence Ranking Summary

| Rank | Case | Evidence class | Use in this report |
|---:|---|---|---|
| 1 | `D38/PR36/DOD_111689030.mp4` | Hard report/video pair | Calibration anchor |
| 2 | `D33/PR34/DOD_111689011.mp4` | Hard pair plus manual track | Image-plane maneuver benchmark |
| 3 | `D25/PR28/DOD_111688954.mp4` | Hard release identity plus corrected report-content match | SWIR-only anomaly lane |
| 4 | `D27/PR29/DOD_111688964.mp4` | Hard release identity plus corrected report-content match | Unusual morphology / possible-reflection lane |
| 5 | `D23/PR27/DOD_111688825.mp4` | Hard report/video pair | Long compact-return sequence |
| 6 | `D35/PR35/DOD_111689022` | Hard report/video pair | Greece comparison/control lane |
| 7 | `D58` | High-value document-only | Radar/target-pod/jamming source-request target |
| 8 | `D28` | High-value document-only | Weapons-context sensor-event source-request target |
| 9 | `D74` | Document-only narrative | Best later readable narrative report |
| 10 | `D75` | Document-only structured fields | Gulf of Aden structured row with redacted description |
| 11 | `D44/D57` | Document-only geometry pair | Gulf of Aden IR range-fouler comparison |
| 12 | `D8` | Document-only short quantitative row | Djibouti-title / Eastern Mediterranean-grid mismatch |
| 13 | `D54` | Document-only short quantitative row | Aegean/Eastern Mediterranean sparse shape/speed/altitude row |
| 14 | `PR44/DOD_111689115.mp4` | Standalone video | Compact-return standalone benchmark |
| 15 | `PR47/DOD_111689142.mp4` | Standalone video | Formation-like standalone benchmark |
| 16 | `PR45/DOD_111689123.mp4` | Standalone video | Central-contrast growth lane |
| 17 | `D60-D65` cluster | Pattern lane | Persian Gulf / Strait 2020 reporting-density pattern |
| 18 | `western_us_event_slides_5.08.2026.pdf` | Briefing/witness narrative | Lower-provenance narrative context |

## Interpretation

The corpus is best interpreted as a set of distinct reporting lanes rather than evidence for one phenomenon or one physical mechanism:

- operational mission reports with UAP fields
- range-fouler debriefs with sensor and mission context
- public videos with limited release metadata
- standalone public videos with no written reporter description
- source-index discrepancies between public pages, PDFs, and local filenames
- narrative and briefing artifacts
- targeted-reviewed historical, NASA/DOS, and static-image collections with lower scientific weight

Object descriptions vary widely: compact point returns, circular objects, diamond/probe descriptions, triangular/metallic descriptions, pole/bar or possible-reflection descriptions, cold IR objects, white-hot UAPs, formation language, balloon-like objects, glare/halo artifacts, and witness-narrative kite/orb descriptions. That variability argues against treating the corpus as one unified phenomenon at this stage.

The most defensible scientific claim is therefore deliberately narrow:

> The source set contains multiple official operational records and public media items documenting reported unresolved aerial or sensor observations. The leading cases justify source requests for raw data and release-index corrections. The public record does not justify a conclusion of non-human technology or independently reconstructed anomalous physics.

## Limitations

The following limitations are decisive:

1. Public videos lack the raw metadata needed for physical kinematics.
2. Reported speeds, shapes, altitudes, and behaviors are frequently source-reported rather than independently verified.
3. Many documents are redacted, OCR-noisy, or internally inconsistent.
4. Several public release labels conflict with local/War.gov report content.
5. Some apparently unusual visual features have plausible sensor, reflection, shoreline, cloud, water-texture, reticle, or compression explanations.
6. The historical FBI/NASA/DOS/image subsets have targeted triage coverage, but not exhaustive OCR, photogrammetry, or event-level reconstruction; they should not be used for stronger conclusions than their source quality supports.
7. Unresolved status is not evidence of extraordinary origin by itself.
8. The publicly released DVIDS video subset is a non-random selection from a larger operational archive. The frequency of any feature in the public-video subset should not be read as its frequency in the underlying operational corpus.
9. Public DVIDS clips are lossy-compressed and contain reticle, track-box, zoom, chroma, and luma artifacts. Apparent compact-return persistence, contrast growth, or formation-like structure must be evaluated against a codec-artifact floor before being treated as object behavior.

## Source Request Priorities

The next scientific step is acquisition of raw source data, not stronger interpretation of compressed public clips.

Priority requests:

| Priority | Case | Requested material |
|---:|---|---|
| 1 | `D58` | Target-pod video, radar tracks, EW/noise-jamming logs, KINGPIN communications, platform identity, unredacted location/bullseye context |
| 2 | `D28` | Raw MX-20/MX-25 imagery, weapon-release and impact timestamps, FOV, range, sensor pointing, platform state |
| 3 | `D38` | Original video, FOV/zoom state, slant range, gimbal pointing, platform motion, track file |
| 4 | `D33` | Original video, telemetry, FOV/zoom, slant range, platform/gimbal motion, target coordinates |
| 5 | `D25` | Raw SWIR/video data, sensor metadata, release-label correction for PR28/D25/D7 |
| 6 | `D27` | Raw PR29 video/sensor data, reflection-control evidence, release-label correction for PR29/D27/D8 |
| 7 | `D61/D65` | Raw FMV, DGS-1 notes, unredacted grids, platform/sensor metadata, identification follow-up |
| 8 | `D44/D57` | Clearer range-fouler forms, raw IR video, sensor geometry, platform metadata |

## Conclusion

As a source set, the release is scientifically useful because it contains repeated official operational reports and public media releases involving unresolved aerial or sensor observations. The leading cases are not proof of exotic technology; they are high-value records that preserve enough operational context to justify formal follow-up requests for raw sensor data, telemetry, and source-index corrections.

The current evidence supports a bounded conclusion:

> There are credible unresolved observations in the corpus. The released evidence is insufficient to determine origin or extraordinary physical performance.

The appropriate path forward is to preserve the evidence ladder, pursue raw data for the top source-request cases, and avoid converting redacted reports or compressed public videos into stronger claims than they can support.

## Supporting Artifacts

Core synthesis:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-evidence-ladder.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-priority-incidents.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-modern-event-timeline.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-report-coverage-audit.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-report-consistency-check.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-goal-completion-audit.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/figure-validation.md`

Case packets and source reviews:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d58-evidence-packet.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-evidence-packet.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d74-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d75-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d61-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d65-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d25-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d27-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d33-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d35-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d8-source-review.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d54-source-review.md`

Video and geometry reviews:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-manual-track-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr28-d25-phase-review-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-visual-alignment.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr44-standalone-quant-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr47-formation-visual-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr45-standalone-visual-notes.md`

Source-index reconciliation:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d8-d27-reconciliation.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr28-d25-d7-reconciliation.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-official-metadata-check.md`

Broader corpus triage:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-nasa-dos-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-record-index.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-gap-triage.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-record-index.csv`

Publication figures:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/fig1-corpus-media-composition.svg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/fig2-file-coverage-status.svg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/fig3-evidence-ladder-ranking.svg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/fig4-source-request-priorities.svg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/fig5-evidence-ladder-theme-frequency.svg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/theme-frequency.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/figures/source-request-priorities.csv`
