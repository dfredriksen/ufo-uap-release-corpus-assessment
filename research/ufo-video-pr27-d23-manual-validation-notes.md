# UFO PR27 / D23 Manual Validation Notes

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: category validation for active `DOD_111688825.mp4` / `DOW-UAP-PR27` / `DoW-UAP-D23` phase-track rows
Status: validation layer complete; no kinematics

## Bottom Line

The PR27/D23 manual-validation layer confirms that the public MP4 contains repeated compact-return candidates, but it also materially narrows the claim.

The strongest support is not the full `134.0s-297.0s` active interval. The useful support concentrates in the later DVIDS loss/reacquisition phase, where `144/181` sampled rows validated as compact-return candidates. The earlier zoom/centered-track phase is heavily contaminated by reticle/overlay and water-texture artifacts; only `31/146` rows validated as compact-return candidates there.

This strengthens PR27/D23 as a long hard-paired visual-sequence case, but it remains unsuitable for public physical speed, range, or trajectory claims.

## Validation Method

The validation pass reviewed the active interval from `134.0s-297.0s` using the phase-track rows generated from `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr27_d23_phase_review.py`.

Each row was assigned one category:

| Category | Meaning |
|---|---|
| `true_compact_return_candidate` | compact hot point, separated from frame edge and colored overlay |
| `reticle_overlay_artifact` | candidate near or intersecting colored reticle/overlay graphics |
| `shoreline_terrain_artifact` | early candidate in shoreline/terrain transition area |
| `water_texture_artifact` | candidate geometry, luminance, or clutter consistent with water/sensor texture |
| `frame_edge_artifact` | candidate adjacent to frame edge or black border |
| `uncertain` / `uncertain_no_candidate` | not enough visual support for validation |

## Counts

| Category | Count |
|---|---:|
| True compact-return candidate | `175` |
| Reticle/overlay artifact | `88` |
| Frame-edge artifact | `27` |
| Water-texture artifact | `23` |
| Uncertain | `10` |
| Shoreline/terrain artifact | `3` |
| Uncertain/no candidate | `1` |
| Total reviewed | `327` |

By phase:

| Phase | True compact-return candidates | Main caveat |
|---|---:|---|
| Zoom and centered track, `134.0s-206.5s` | `31/146` | `86` reticle/overlay artifacts and `23` water-texture artifacts |
| Sensor-motion loss and reacquisition, `207.0s-297.0s` | `144/181` | `27` frame-edge artifacts and `8` uncertain rows |

## Validated Compact-Return Segments

The validation pass found `18` compact-return candidate segments using a maximum `1.0s` gap rule. These are visual-support runs only, not physical tracks.

Longest segments:

| Segment | Window | Samples | Interpretation |
|---|---:|---:|---|
| `PR27-C16` | `235.00s-266.00s` | `62` | strongest validated compact-return run |
| `PR27-C17` | `269.50s-284.50s` | `31` | late validated run after brief interruption |
| `PR27-C18` | `287.50s-297.00s` | `20` | final validated run through the end of the public file |
| `PR27-C15` | `215.50s-228.00s` | `23` | earlier loss/reacquisition support |

## Judgment

PR27/D23 should remain promoted as a hard-paired visual-sequence case, with a refined evidentiary statement:

- Good support: repeated compact-return candidates after the zoom/center transition, especially `207.0s-297.0s`.
- Weak support: continuous centered tracking from `134.0s-206.5s`; many marks are reticle/overlay or water-texture artifacts.
- Not supported: public validation of D23's estimated `320 MPH` or `440 MPH` values.
- Not resolved: which D23 UAP line is depicted by the MP4.

## Generated Artifacts

| Artifact | Path |
|---|---|
| Script | `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr27_d23_manual_validation.py` |
| Validation CSV | `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-dod111688825.csv` |
| Summary CSV | `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-summary.csv` |
| Segment CSV | `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-compact-return-segments.csv` |
| Asset index | `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-assets.csv` |
| Contact sheets and patches | `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-manual-validation/DOD_111688825/` |

## Next Step

PR27/D23 is now sufficiently reviewed for corpus ranking. The next better corpus action is source reconciliation, especially the `PR26/D12` date/location/report mismatch, before spending more time on standalone clips.
