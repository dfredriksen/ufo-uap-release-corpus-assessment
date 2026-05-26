# UFO Telemetry Evidence Inventory

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: public-release corpus only; explicit telemetry-bearing or telemetry-like evidence
Status: repo-local extraction inventory

## Purpose

This note logs the cases where the released corpus preserves telemetry-bearing values or telemetry-like evidence that can be extracted without claiming raw mission telemetry.

It separates:

- direct report-derived numeric fields
- coordinate and grid-derived fields
- explicit overlay or sensor-annotation labels
- image-plane measurement proxies
- ambiguity classes that can explain the same visual outcome

The inventory is deliberately conservative. Many of these values are report-derived or image-plane-derived, not independently validated physical telemetry.

## Overlay And Sensor-Annotation Evidence

The measurement-overlay exploitation lane is indexed in `research/ufo-overlay-measurement-audit.csv` and summarized in `research/ufo-overlay-measurement-audit.md`. That audit is the controlling table for explicit labels, metadata-derived scan targets, and optional local-media crop candidates. The classification/source-request control table is `research/ufo-overlay-measurement-classification.csv`, with source requests in `research/ufo-overlay-measurement-source-requests.csv`. Direct PR44-style control comparison for PR31, PR32, PR33, PR34, PR36, and PR45 is tracked in `research/ufo-overlay-measurement-control-comparison.md`; those six control scans found no PR44-like reticle-associated meter-label candidates under the current survey geometry.

| Case | Extracted evidence | Telemetry class | Ambiguity configurations | Best next technique |
|---|---|---|---|---|
| `DOD_111689115.mp4` / `PR44` | Persistent meter-like label beside the reticle/track box: full-label survey manually reads a descending `12M -> 11M -> 10M -> 9M` sequence from about `204-266s`; frame-by-frame pass localizes the `11M` to `10M` transition between frame `7000` and frame `7001`; label/reticle remain nearly fixed while the bright object candidate moves down-left; direct PR44-style control scans of PR31, PR32, PR33, PR34, PR36, and PR45 found no matching meter-label candidates; later dense pass found `446` rows across `89.0s`, `155 high`, `154 medium`, `137 low`, `41.029 px/s` path-average, and `3651.620 px` path length. | Explicit overlay readout plus image-plane track and bounded negative controls. | Meter readout; range gate; track-box parameter; reticle/display-state annotation; OCR/manual-read artifact. | Extend the search only after adding crop presets for non-PR44 geometry and compare PR051 once acquired. |
| `DOD_111719715` / `PR051` | Public MP4 acquired outside the repo and hashed as `034759DFC01CB87C718968F3012A57D89ACAE7BAED3A52D60041A59098DF2007`; interval survey finds repeated `5M` / `5m-style` visibility in the original excerpt at `007s`, `011s`, and `012s`, and again in the exit replay around `271s`, `275s`, and `276s`; later reticle-lock segment shows separate `31M-like`, `30M-like`, `13M-like`, and lower-confidence `6M-like` / `9M-like` candidates. Official DVIDS title frames the clip as instant acceleration, but the public page says the media was digitally altered before upload and describes the key exit as sensor tracking stopping. | Explicit overlay/readout candidate plus provenance-control case. | Object-size estimate; range or slant-range readout; track-box/gate parameter; reticle/zoom annotation; enhancement/replay artifact; public-upload alteration artifact. | Keep as a positive overlay-semantics case and source-request target; do not promote to physical kinematics without display documentation, raw video, FOV/zoom state, range, platform state, and chain-of-custody records. |

Note: the PR051 source MP4 is locally retained outside the publish set and is not redistributed in the repo. The source-acquisition row is tracked in `research/ufo-overlay-measurement-pr051-source-acquisition.csv`.

## Direct Report-Derived Numeric Fields

| Case | Extracted evidence | Telemetry class | Ambiguity configurations | Best next technique |
|---|---|---|---|---|
| `D25` / `PR28` / `DOD_111688954.mp4` | `434 KNOTS`; estimated `FL200`; westward trajectory; SWIR-only round/diamond lane. | Report-derived speed and altitude fields. | Report-estimated speed; platform-relative speed; geometry scenario under assumed FOV/range; source-summary wording. | Pair the report fields with the SWIR phase review and preserve them as report-derived unless source telemetry appears. |
| `D27` / `PR29` / `DOD_111688964.mp4` | `140 KNOTS`; `23,999 FT`; `070457:00ZJUN24`; `AN/DAS-1`; pole/bar or possible water-reflection description. | Report-derived speed, altitude, and sensor-context fields. | True object speed; platform-relative speed; reflection drift; observer estimate; display/annotation artifact. | Compare the narrative fields with the dense visual alignment and water-reflection controls. |
| `D33` / `PR34` / `DOD_111689011.mp4` | `80 MPH`; `0035Z-0038Z`; multiple sharp apparent image-plane heading changes. | Report-derived speed plus image-plane motion proxy. | Physical turn; sensor slew; gimbal stabilization; platform motion; track-update artifact. | Use the manual track and FOV sensitivity sweep only as a bounded scenario test. |
| `D35` / `PR35` / `DOD_111689022` | `30 MPH`; `290811:00ZOCT23`; `NONE` maneuverability observations. | Report-derived speed and maneuverability field. | Report estimate; closure relative to platform; sensor-state effect; sequence-only support. | Keep the public clip as release/report alignment, not a kinematic reconstruction. |
| `D54` | `363453N 0255943E` -> approx `36.58138889N, 25.99527778E`; `24,989FT MSL`; `168KTS`; `1319Z`. | Coordinate-derived location plus report-derived altitude/speed. | Exact geolocation vs analytic decode; report estimate vs physical speed; metadata mismatch with the `D31` title. | Preserve the coordinate decode and treat the altitude/speed as report text. |
| `D8` | `35SQT3423692957` -> approx `34.2514N, 29.5437E`; `240NM/HOUR`; `1653Z`; two round white-hot UAPs moving south. | Grid-derived location plus report-derived speed. | Exact grid decode vs source-label mismatch; report estimate vs physical speed; separate case vs PR29/D27. | Keep the title/location mismatch intact and do not merge with PR29/D27. |
| `D65` | Observation 3: `39RUN6234236874` -> approx `29.253233N, 49.583281E`; `115 KIAS`; `FL191`; heading `331M`. | Coordinate-derived location plus report-derived airspeed/altitude/heading. | Separate objects vs repeated observations; partial grids vs full grid; FMV observation vs geospatial anchor. | Preserve the full grid and request unredacted grids for the first two observations if needed. |
| `D74` | `092153:00ZNOV23`; estimated `424KN`; seven-minute near-co-altitude pass. | Report-derived kinematic field. | Estimated report speed; relative geometry vs physical speed; narrative summary vs raw sensor data. | Keep it in the document-only narrative lane until source video or telemetry appears. |
| `D61` | `271527:00ZAUG20`; formation of unknown flying objects; `NE-NW` along the coast; about two minutes of tracking before PID loss in cloud cover. | Report-derived movement and duration fields. | Birds; small aircraft or drones; shoreline/cloud contrast; weather-driven track loss. | Pair the report text with weather imagery and any raw FMV before treating the motion as physical trajectory. |
| `D75` | `140517:00ZJUL24`; low altitude; `NW` trajectory; faster than observing platform; FMV primary sensor. | Report-derived timeline and movement fields. | Redacted speed vs relative-speed statement; straight path vs platform motion; narrative vs raw sensor track. | Search only for official media that names `D75` or `140517ZJUL24`. |

## Geometry And Range-Fouler Evidence

| Case | Extracted evidence | Telemetry class | Ambiguity configurations | Best next technique |
|---|---|---|---|---|
| `D44` | `10/15/20 14:18:39Z`; one contact; round cold object in IR; `19,073 HAT`; sensor `-50 deg`; slant range `4.06 NM`; ground range `4.78 KM`; abrupt directional changes. | Report-derived range geometry. | Actual geometry; OCR noise; platform angle vs object motion; conventional aircraft/drone activity. | Rebuild the geometry worksheet only if clearer source images or raw forms become available. |
| `D57` | `09/04/20 21:09Z-21:17Z`; one contact; round cold object in IR; `23,819 HAT`; `168/277`; sensor `-39 deg`; slant range about `6.1? NM`; ground range `8.81 KM`; abrupt directional changes. | Report-derived range geometry. | Actual geometry; OCR uncertainty on slant range; conventional aircraft/drone activity; platform-relative motion. | Keep D44 and D57 paired as a geometry-only comparison lane. |
| `D56` | Three possible unidentified small air contacts; negative ES, radar track, and IFF track; cloud loss then reacquisition. | Multi-contact ambiguity lane. | Three separate objects; one object with track splits; sensor artifacts; benign traffic in a cloud-interrupted scene. | Use raw FMV, weather imagery, and track files before any stronger interpretation. |
| `D58` | `10/27/20 01:12:21Z`; `26000`; `060/20`; two contacts; `16.9 NM`; `2X RED BLINKING STROBES`; noise jamming; radar lock; target-pod video. | Operational sensor-context telemetry proxy. | Conventional military aircraft; drone activity; EW or training platform; two contacts influenced by sensor geometry. | Request target-pod video, radar logs, EW logs, KINGPIN comms, and platform state. |

## Image-Plane Measurement Evidence

| Case | Extracted evidence | Telemetry class | Ambiguity configurations | Best next technique |
|---|---|---|---|---|
| `D38` / `PR36` / `DOD_111689030.mp4` | Hard report-video anchor; 50-87s anchor; `38` accepted one-second points in the validated interval; local validation supports compact point-return behavior. | Image-plane measurement proxy with hard report/video pairing. | Compact return vs track update; panning sensor vs target motion; camera state change. | Preserve the DVIDS-linked anchor and compare future clips against this calibration case. |
| `D33` / `PR34` / `DOD_111689011.mp4` | `111` samples; `97` accepted; `14` interpolated; `7` turn events; `6536.08 px` path length; `118.84 px/s` path-average. | Image-plane heading-change proxy. | Object turn vs sensor slew; gimbal stabilization; platform motion; interpolation artifact. | Use the manual track as the benchmark for image-plane maneuver analysis. |
| `D25` / `PR28` / `DOD_111688954.mp4` | `67` one-fps samples; `47` supported rows; `231` dense samples; `217` high-or-medium dense rows; `64.885 px/s` one-fps path-rate proxy; `72.141 px/s` dense path-rate proxy. | Image-plane sequence support with SWIR-lane context. | SWIR return vs black-hot loss; cloud confound; track continuity vs sensor mode change. | Keep the SWIR acquisition/loss sequence separate from any physical-speed claim. |
| `D27` / `PR29` / `DOD_111688964.mp4` | `101` dense samples; `62` high, `35` medium, `4` low; `40` samples inside/intersecting/near track-box symbology; `95` vertical-feature flags. | Image-plane object-alignment proxy. | Physical appendage vs reflection; track-box following object vs operator cue; target vs water glare. | Use dense marking plus water-reflection controls. |
| `D23` / `PR27` / `DOD_111688825.mp4` | `327` active rows; `175` true compact-return candidates; `144/181` validated compact-return candidates in the late interval; `31/146` in the earlier centered-track interval. | Manual-validation acceptance counts. | Candidate definition drift; reticle/texture contamination; late-loss interval vs centered-track interval. | Run blinded review and a control clip through the same pipeline. |
| `PR38` / `DOD_111689051.mp4` | `90` supported star-like rows; `14984.312 px` path length; `145.479 px/s` path-average; median `51.219 px/s`; supported across most of the movement/trail interval. | Image-plane contrast-shape proxy. | Star-like contrast vs sensor effect; cut-gap vs target absence; reticle or overlay confound. | Keep it as a visual-description benchmark, not a physical-object reconstruction. |
| `PR44` / `DOD_111689115.mp4` | `446` rows across `89.0s`; `320` local compact-bright refinements; `126` seed-only rows; `41.029 px/s` path-average; `58` near-overlay rows; `6` intersect-overlay rows. | Sustained compact-return track proxy. | Object return vs reticle-following artifact; closure vs zoom change; overlay interaction vs target motion. | Use temporal OCR, zoom-state review, and control lanes to isolate the stable return. |

## Ambiguity Rules

The same visual outcome can arise from several telemetry configurations. Keep these rules in mind when reviewing clips:

- A `5m`, `10M`, or `10m` label can be a meter readout, a range gate, a track-box parameter, a generic sensor annotation, or an OCR artifact.
- A sharp image-plane turn can be an object maneuver, sensor pan, gimbal stabilization, platform motion, or a track-update correction.
- A visible size increase can be real closure, a zoom change, focus/exposure change, a thresholding artifact, or a reticle overlap effect.
- Multiple apparent contacts can be multiple objects, one object split by detection logic, glints on the same object, or clutter from sensor noise.
- A reported speed can be a report estimate, a platform-relative closure value, or a scenario derived from pixel motion under assumed FOV and range.
- A coordinate can be an exact report grid, an analytically decoded approximation, or a grid/title mismatch that must be preserved rather than merged.

## Techniques For Further Extrapolation

Best current techniques for squeezing more telemetry-like value out of the public material:

1. Multi-frame OCR on overlay regions, with label persistence checks across adjacent frames.
2. Crop stabilization and source-resolution re-extraction before reading a label or reticle annotation.
3. Manual track reconstruction for image-plane motion, followed by FOV sensitivity sweeps.
4. Coordinate decoding from MGRS or partial grids, then geodesic reconstruction against mission context.
5. Control-lane comparison against birds, glare, clouds, shoreline texture, and other benign targets.
6. Phase alignment between DVIDS timing descriptions and local frame sequences.
7. Archived-snapshot capture of live release pages before citing them as evidence.
8. Source requests for raw radar, target-pod video, EW logs, gimbal state, platform motion, and unredacted grids.

## Working Conclusion

The current corpus yields derived telemetry, not raw telemetry.

The strongest practical outputs are:

- bounded numeric extraction
- explicit label capture
- coordinate decoding
- image-plane measurement proxies
- source-request targets that identify the missing raw data

The telemetry value is real, but the public release still does not let us collapse these cases into a full physical reconstruction.
