# UFO Telemetry Recovery Methods

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: public-release corpus only; derived telemetry candidates, not raw mission telemetry
Status: methods memo

## Bottom Line

The public corpus does not let us recover raw telemetry in the strict sense. The released PDFs and MP4s usually omit the exact sensor state, platform motion, gimbal pointing, range-time series, and frame-level metadata needed for a full 3D reconstruction.

What the corpus does support is a limited set of derived outputs:

- report-derived numeric fields such as speed, altitude, time, coordinates, direction, and object count
- decoded coordinates and approximate geodesic distances
- image-plane motion, turn geometry, and angular-rate scenarios
- apparent-size or contrast-area proxies
- report/video pairing and phase alignment
- source-request prioritization for the missing raw data

Direct meter-based object-size recovery is currently low-yield. The corpus more often preserves meters as narrative range or motion cues, not as verified object dimensions. The strongest explicit meter-like cue found so far is a historical archive narrative describing a rapid whip-off after reaching about `2,000 meters`; that is useful for context, but it is not a direct object-size measurement.

## Recoverability Matrix

| Telemetry class | Recoverable from public release alone? | Examples | Current status |
|---|---|---|---|
| Raw mission telemetry | No | Frame-level sensor metadata, gimbal pointing, range-time series, platform state | Missing from the public corpus |
| Report-derived telemetry | Yes | Speed, altitude, time, direction, object count, coordinate strings | Common and already usable |
| Geometry-derived telemetry | Yes, in bounded form | Pixel rates, implied slant ranges, turn radii, coordinate distances | Useful but assumption-sensitive |
| Apparent-size telemetry | Yes, as proxy data | Contrast-area change, distinctiveness change, exit timing | Useful for visual audit, not physical size |
| Reference-scale telemetry | Rarely | Known-size object in-frame, trustworthy meter-based reference, or paired measured target | Low-yield in current corpus |
| Operational-context telemetry | Sometimes | Radar lock, target-pod, EW/jamming, sensor mode, mission phase | Valuable for source requests, not full reconstruction |

## Evidence Inventory

The extracted cases, numeric values, and ambiguity classes are tracked in `research/ufo-telemetry-evidence-inventory.md`.

The practical forensic technique list is tracked in `research/ufo-forensic-telemetry-techniques.md`.

The full evidence-stack application pass is tracked in `research/ufo-telemetry-full-stack-application.md`.

The explanation-screening pass is tracked in `research/ufo-telemetry-explanation-screening.md`.

## Ambiguity Rules

Use these same-outcome classes when deciding whether a value is telemetry, a proxy, or just a sensor artifact:

- `5m`, `10M`, or `10m` can mean a meter readout, a range gate, a track-box parameter, a generic sensor annotation, or an OCR artifact.
- A sharp image-plane turn can reflect object motion, sensor pan, gimbal stabilization, platform motion, or a track-update correction.
- A visible size increase can reflect closure, zoom changes, focus/exposure changes, thresholding, or reticle overlap.
- Multiple apparent contacts can be multiple objects, one object split by detection logic, glints, or clutter.
- A speed field can be a report estimate, a platform-relative closure value, or a pixel-motion scenario under assumed FOV and range.
- A coordinate can be exact, analytically decoded, or a source-label mismatch that must be preserved rather than merged.

## What Can Be Recovered Now

| Recovery type | What it yields | Typical inputs | Current strength |
|---|---|---|---|
| Report-field extraction | Speed, altitude, time, direction, coordinates, object count, shape words, range words | OCR, embedded PDF text, release metadata | High |
| Coordinate decoding | Lat/lon from MGRS or partial grids; approximate distances between known points | MGRS strings, partial grids, platform/target coordinates | High |
| Overlay readout capture | Meter-labeled track boxes, range labels, sensor readouts, or other explicit on-frame annotations | Readable overlays, adjacent frames, OCR, release packaging | Rare but high value |
| Report/video pairing | Which MP4 corresponds to which report; phase alignment by DTG and content | DVIDS pages, local report text, release filenames | High |
| Image-plane geometry | Pixel rates, apparent heading changes, angular-rate scenarios, FOV sensitivity | Manual track data, frame rates, crop geometry | High to medium |
| Apparent size proxies | Contrast-area change, distinctiveness change, exit timing | Segmented frames, reticle-aware review, local controls | Medium |
| Sensor-context inference | Which missing data would resolve a case and which source requests matter most | Narrative text, report fields, radar/target-pod references | Medium to high |
| Historical archive extraction | Legacy dates, sizes, directions, speed estimates, weather, witness remarks | OCR on archive PDFs and incident summaries | Medium |
| Control-lane calibration | False-positive floor, artifact behavior, method sanity checks | Conventional clips and benign controls | Medium |
| Direct object-size scaling | Approximate physical size if a reliable reference dimension exists | Known reference object, range, FOV, platform geometry | Low in current corpus |

## Ranked Methods

### Overlay readout and sensor-annotation extraction

What it can recover:

- explicit on-frame measurement artifacts such as meter-labeled track boxes, range labels, or sensor readouts
- potential scale or range anchors when the label is tied to a stable sensor overlay
- OCR-able labels that can be compared across adjacent frames or source-resolution crops

Best current cases:

- `DOD_111689115.mp4` with the visible `10M` / `10m`-like overlay label beside the track box
- user-provided external frame examples with a readable `5m`-like label adjacent to the target reticle
- any other clip where the label stays attached to the same track box or range gate across multiple frames

Usefulness:

- Very high when readable and stable

Why it matters:

- This is closer to direct measurement than pixel-rate geometry because the annotation itself can encode a measured quantity or sensor range cue.
- If the label semantics can be established, it can seed better distance, scale, or sensor-state inference.

Main caveat:

- The label still needs interpretation.
- `5m` or `10M/10m` could be a meter readout, a track-box parameter, a range gate, or a display-layer annotation rather than object size.
- The label should only be treated as measurement data if adjacent frames, overlay behavior, and release context show it is a persistent sensor annotation rather than an OCR hallucination or editorial artifact.

### 1. Structured report-field extraction and normalization

What it can recover:

- times, dates, speeds, altitudes, directions, object counts, colors, and shape words
- report-derived range or distance language
- occasional meter-based narrative cues

Best current cases:

- `D25`, `D27`, `D33`, `D54`, `D61`, `D65`, `D74`, `D75`, `D8`, `D58`
- historical archive summaries such as `38_143685_box7_incident_summaries_101-172.pdf` and `341_110677_numerical_file_5-2500.pdf`

Usefulness:

- High

Why it matters:

- This is the most direct way to recover numeric information already present in the public corpus.
- It yields report-derived quantities immediately, without needing image reconstruction.
- It is the right first pass before any geometric inference.

Main caveat:

- The output is still report-derived unless the public release also contains sensor metadata or paired imagery that independently supports the number.

### 2. Coordinate decoding and geodesic reconstruction

What it can recover:

- approximate latitude/longitude from MGRS or coordinate strings
- approximate distance between the aircraft and the observed activity if both endpoints are present
- a better geographic cluster map than the raw text alone

Best current cases:

- `D54` with `363453N 0255943E`
- `D61` and `D65` with partial `39R...` grids
- `D8` with `35SQT3423692957`
- `D75` with MGRS-style coordinates
- `D28` where coordinate fragments help confirm the Iraq / Ayn al Asad lane

Usefulness:

- High

Why it matters:

- This is the cleanest path from report text to something like geometry.
- If both the platform and target coordinates are known, it can support a slant-range estimate.

Main caveat:

- A target coordinate alone does not give slant range.
- Partial grids and redaction limit precision.

### 3. Report/video pairing and phase alignment

What it can recover:

- which video belongs to which report
- whether the report description matches the public clip at a coarse visual level
- where the useful intervals, zoom changes, or feed-loss boundaries occur

Best current cases:

- `D38/PR36`
- `D33/PR34`
- `D25/PR28`
- `D27/PR29`
- `D23/PR27`
- `D35/PR35`

Usefulness:

- High

Why it matters:

- This is the foundation for any later geometry work.
- Without a correct pairing, any subsequent pixel-rate or FOV analysis is at risk of being attached to the wrong case.

Main caveat:

- Pairing does not itself establish physical kinematics.

### 4. Image-plane tracking with FOV sensitivity sweeps

What it can recover:

- pixel rates
- apparent heading changes
- turn-radius scenarios under assumed speed
- implied slant-range scenarios under assumed FOV

Best current cases:

- `D33/PR34`
- `D38/PR36`
- `D27/PR29`
- `PR44`

Usefulness:

- High to medium

Why it matters:

- This is the strongest route to derived telemetry-like numbers from public video alone.
- It can show whether a report speed is plausible under some FOV/range assumptions.

Main caveat:

- It produces scenarios, not validated real-world motion, unless actual sensor geometry is known.
- It is especially sensitive to zoom changes, platform motion, and gimbal stabilization.

### 5. Apparent-size and contrast-area proxy analysis

What it can recover:

- changes in visible contrast area
- apparent growth or shrinkage across a clip
- relation to reticle overlap, lock boxes, and zoom changes

Best current cases:

- `PR45`
- `PR47`
- `PR41`
- `PR44`
- `PR49`

Usefulness:

- Medium

Why it matters:

- This is useful when the public clip is too degraded for a clean object contour but still has a repeatable target lane.
- It can separate "more visible" from "physically larger" if the caveats are kept intact.

Main caveat:

- Apparent size is not physical size.
- Closure, zoom, and contrast settings can all drive the measurement.

### 6. Multi-sensor and operational-context exploitation

What it can recover:

- which missing records would actually resolve the case
- whether radar, target-pod, or EW references indicate a genuine source-request path
- how strong the conventional-confound space remains

Best current cases:

- `D58`
- `D28`
- `D61`
- `D65`
- `D74`
- `D75`

Usefulness:

- Medium to high for prioritization
- Low for direct telemetry recovery from the public release itself

Why it matters:

- This is the best way to turn narrative clues into a concrete source-request queue.
- It often yields the most useful next step even when it does not produce final numbers.

Main caveat:

- The public release usually names the missing data, but does not include it.

### 7. Historical-archive OCR of structured incident summaries

What it can recover:

- date, location, size, shape, color, speed, direction, sound, exhaust, and weather fields
- early UFO-report prose that is rich enough to rank by evidence family

Best current cases:

- `38_143685_box7_incident_summaries_101-172.pdf`
- `342_hs1-416511228_box186_319.1-flying-discs-1949.pdf`
- `341_110677_numerical_file_5-2500.pdf`

Usefulness:

- Medium

Why it matters:

- These files are more likely than the modern redacted reports to preserve explicit field structure.
- They broaden the historical record and sometimes surface concrete speed or altitude language.

Main caveat:

- They are still witness or institutional narrative records, not calibrated sensor telemetry.

### 8. Control-lane comparison and artifact-floor estimation

What it can recover:

- the false-positive floor for compact-return detection
- the effect of compression, reticles, glare, clouds, water, and track boxes
- whether a method is too permissive to trust

Best current cases:

- control clips and benign-looking lanes such as `D10`, `D32`, `D7`, `D18`, `PR21/D14`

Usefulness:

- Medium

Why it matters:

- This is a method-validation tool, not a telemetry-recovery tool.
- It is essential before trusting any pixel-based measure.

Main caveat:

- A method that cannot reject conventional controls is not useful for telemetry inference.

### 9. Provenance and label reconciliation

What it can recover:

- the correct report/video linkage
- the correct case family
- a clean distinction between live release assets and local files

Best current cases:

- `D25` versus `D7`
- `D27` versus `D8`
- `D54` versus `D31`
- `D56`, `D57`, and `D58` metadata noise

Usefulness:

- High as a safeguard

Why it matters:

- Wrong pairing breaks every later calculation.
- This method does not recover telemetry directly, but it prevents false recovery.

### 10. Direct meter-based object-size scaling from known references

What it can recover:

- approximate physical size if the report gives a trustworthy reference object or a known dimension in the same frame
- approximate distance if object size is known and the image scale is stable

Best current cases:

- No strong current public case
- Weak historical narrative cues only, such as the archive mention of a whip-off after reaching about `2,000 meters`

Usefulness:

- Low in the current corpus

Why it matters:

- This is the method closest to the user's example, but the present corpus rarely gives a reliable object dimension in meters.
- Most meter-bearing phrases in the corpus are range or motion language, not direct object dimensions.

Practical evaluation rule:

- Treat this method as a future-opportunity method, not a current cornerstone.
- Promote it only if a release page, report, or video overlay supplies a trustworthy measured reference dimension or a clearly annotated target size in meters.

Main caveat:

- It is easy to overinterpret if the reference dimension is itself uncertain.

## How To Evaluate These Methods

The methods above should be tested in a validation order, not all at once.

1. Run a conventional control clip through the same detector and review pipeline.
2. Measure reviewer agreement on compact-return candidates and track continuity.
3. Sweep FOV and zoom assumptions to see how unstable the derived ranges are.
4. Compare report-derived numeric fields against decoded coordinates and time windows.
5. Only then promote a method into the main evidence ladder.

Recommended validation experiments:

- blinded manual review of a conventional aircraft clip processed with the same pipeline
- inter-rater agreement on a small sample of compact-return candidates
- sensitivity analysis for FOV, zoom, and pixel-threshold choices
- synthetic injection tests against compression, reticles, glare, water, and clouds
- archived-snapshot capture for live release pages before they are cited as evidence

## Conclusion

The public corpus supports derived telemetry, not raw telemetry.

The best near-term recovery paths are:

1. report-field extraction and normalization
2. coordinate decoding and geodesic reconstruction
3. report/video pairing and phase alignment
4. image-plane geometry with explicit FOV sensitivity
5. provenance and label reconciliation

Meter-based object-size recovery is possible in principle, but it is currently low-yield in this corpus. The strongest practical outcome is a disciplined set of bounded estimates and source-request targets, not a full physical reconstruction from the public release alone.
