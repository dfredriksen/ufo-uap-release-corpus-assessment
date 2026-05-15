# UFO FBI Photo Set Gap Triage

Owner: Dan Fredriksen
Created: 2026-05-14
Scope: `33` local manifest rows assigned to `fbi_photo_set`
Status: targeted source and visual-provenance triage complete; not a photogrammetric analysis

## Sources And Method

Primary official source base:

- War.gov PURSUE portal: `https://www.war.gov/UFO/`
- Official media URL pattern: `https://www.war.gov/medialink/ufo/release_1/<record>`
- Official records checked directly through browser-accessible media or screenshots: `fbi-photo-a1.png`, `fbi-photo-a5.png`, `fbi-photo-b5.pdf`, `fbi-photo-b6.pdf`, and `fbi-photo-b7.pdf`
- Official-record CSV text was cross-checked through an indexed copy of the War.gov release CSV because direct local CSV retrieval returned HTTP `403`: `https://gist.github.com/ahmetcadirci25/e4edb7d30109fdb8ff14b73dc75f67bc`

Local-source limitations:

- Local Drive-backed image reads remain unreliable under current disk pressure. `Get-FileHash` and PIL image reads returned no-space errors, and the .NET image loader crashed while reading the image set.
- This pass therefore avoids pixel-level measurement, contrast tuning, geometric measurement, or photogrammetry.
- The pass is limited to official provenance, release structure, official narrative descriptions, and direct visual checks of representative official media.

## Source Structure

The local folder has `33` FBI photo-set rows, but those correspond to `32` official records:

- `FBI Photo A1` through `FBI Photo A8`: eight official image files, all published as PNGs on War.gov. The local copies for `A5` through `A8` are JPGs, so the local extension differs from the official source URL.
- `FBI Photo B1` through `FBI Photo B24`: twenty-four official PDF records, each presenting a single redacted still. The local folder contains extracted JPGs for the B-series and also retains `fbi-photo-b6.pdf`, making `B6` appear twice locally.

Machine-readable index:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-record-index.csv`

## Common Provenance Pattern

The A-series records are FBI submissions to AARO consisting of still images derived from a U.S. government system. The official metadata does not provide the event location or specific date beyond `Late 2025`. Each file is a redacted single still, no accompanying mission report was provided, and the operator was unable to positively identify the object.

The B-series records are FBI submissions to AARO consisting of still images derived from a U.S. military system in 2025, with location generalized to the western United States. The original imagery was redacted, no accompanying mission report was provided, and the operator was unable to positively identify the object. The B-series images display an embedded `12/31/99` timestamp in representative frames, but the official metadata states that the image date is incorrect because the system date/time was not set.

## Visual Triage Findings

A-series:

- The A-series consists of monochrome reticle stills with one small object near or at the reticle.
- `A2`, `A3`, and `A6` are the cleanest centered circular-object examples.
- `A1`, `A4`, and `A8` place a small dark irregular object below/right of the reticle center.
- `A5` places a dark circular object in the lower/right quadrant over a speckled background.
- `A7` differs from the rest because the object is light-colored with a bright highlight rather than dark.
- Because the A-series lacks location, platform, sensor, calibration, range, and mission context, it is weaker than the modern DoW/DoD mission-report/video lanes.

B-series:

- The B-series has more context than the A-series because it is tied to a U.S. military system and generalized western U.S. location, but it is still a single-frame, redacted, no-mission-report set.
- `B1` through `B4` and `B8` through `B12` mostly show a single small dark circular object near the central reticle, often against an indistinct mountain/cloud background.
- `B5` is important as a control-like frame because the official description says no distinct object is clearly visible in the central frame; the direct screenshot check is consistent with that.
- `B6` and `B7` are the most visually diagnostic B-series records. `B6` shows a structured dark object near the top of the reticle plus a smaller dot below/right. `B7` shows a similar dark upper-right object that the official description says is consistent in appearance with a helicopter, plus a smaller dot below the reticle.
- `B13` through `B18` and `B20` through `B22` are mainly one-to-two-object stills around a simplified or central reticle. They add recurrence within the photo set, but no kinematics.
- `B19`, `B23`, and `B24` are single-object stills with tiny dark features at or near the reticle.

## Scientific Weight

The FBI photo set is useful as an image-corpus gap closer, but it should not materially alter the final scientific report's ranking.

Reasons:

1. The records are largely single stills, not raw videos or image sequences with telemetry.
2. The files lack platform state, range, sensor field-of-view, exposure settings, calibration data, atmospheric context, and pre/post frames.
3. Heavy redaction removes potentially decisive context.
4. The B-series embedded image timestamp is explicitly unreliable.
5. At least one of the most visually structured cases, `B7`, has an official conventional-appearance cue: a dark object consistent with a helicopter.
6. The official narrative descriptions are informational only and do not present an analytic conclusion about the objects' nature.

## Corpus Impact

This pass promotes the FBI photo set from inventory-only to targeted review.

Initial takeaway:

- The FBI photos broaden the corpus into static imagery, but they do not provide stronger evidence than the modern DoW/DoD operational records.
- The best interpretation is unresolved low-context imagery, not independent evidence for anomalous propulsion, non-human technology, or extraordinary kinematics.
- `B5`, `B6`, and `B7` should be retained as the most useful internal controls/examples for any later image appendix: `B5` because no distinct central object is visible, `B6` because it is visually structured, and `B7` because it supplies a likely conventional aircraft comparison.

Recommended report treatment:

Add a short appendix note stating that the FBI photo records were reviewed at source/provenance level and remain low-weight single-still evidence. They should not be placed above D38/PR36, D33/PR34, D25/PR28, D27/PR29, D58, D28, D61, or D65.
