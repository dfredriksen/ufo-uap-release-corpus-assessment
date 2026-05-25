# UFO PR28 / D25 Phase Review Notes

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: bounded phase review of `DOD_111688954.mp4` / `DOW-UAP-PR28`, using local/War.gov `D25` as the working written-report content match
Status: phase sequence confirmed; kinematics not validated

## Bottom Line

The local `DOD_111688954.mp4` phase review supports DVIDS's PR28 visual sequence and strengthens the working `D25` content match, while preserving the official-source label discrepancy that DVIDS calls the accompanying report `D7`.

The public MP4 supports a narrower, defensible claim: a compact SWIR contrast is persistently trackable through the full-screen SWIR portion and then is not robustly reacquired after the visible-spectrum switch. It does not independently validate the report's `434 knots`, range, object size, altitude, or the detailed physical shape/tail/probe description.

## Inputs

| Field | Value |
|---|---|
| Local video | `I:\My Drive\UFO\DOD_111688954.mp4` |
| Release identity | `DOW-UAP-PR28` |
| DVIDS report label | `DoW-UAP-D7` |
| Working report-content match | `DoW-UAP-D25` |
| Video metadata | `1920x1080`, `30.0 fps`, `1980` frames, `66.0s` |
| Sampling | `2 fps` through `65.5s`, aligned to DVIDS time-coded phase descriptions |

## Phase Results

| Phase | Window | Samples | Result |
|---|---:|---:|---|
| Split EO/SWIR context | `0.0-3.9s` | `8` | `7/8` high-or-medium detections, but this interval includes split-screen and display-context artifacts. |
| Split-screen right-frame contrast | `4.0-9.9s` | `12` | `11/12` high-or-medium detections, consistent with the DVIDS `00:04` right-frame contrast note. |
| Full-screen SWIR track | `10.0-55.9s` | `92` | `86/92` high-or-medium detections and no no-candidate rows. This is the useful object-level interval. |
| Visible-spectrum loss | `56.0-56.9s` | `2` | One low-confidence candidate and one no-candidate row; supports loss at the visible-spectrum switch rather than continued visual track. |
| SWIR black-hot non-reacquisition | `57.0-65.5s` | `18` | `0/18` high-or-medium detections. Low marks are edge, cloud, or overlay artifacts, consistent with non-reacquisition. |

## Interpretation

The strongest supported interval is `10.0s-55.5s`. Across that segment, the candidate stays visible as a compact bright contrast in SWIR and remains generally within the sensor presentation. The detector occasionally marks nearby overlays, cloud texture, or reticle-adjacent features, so the CSV is best treated as a phase-support and visual-reference table rather than a clean kinematic track.

The loss sequence is the most important validation point. At `56s`, the display changes to visible spectrum and the compact SWIR contrast is no longer robustly present. From `57s-65.5s`, the black-hot SWIR segment has no high-or-medium reacquisition marks. This matches the DVIDS narrative sequence.

The phase pass does not resolve the `D7`/`D25` source-index discrepancy. It does, however, align with the Greece / SWIR-only lane found in `D25`, not the separate Arabian Gulf balloon-like/TFLIR report found in local/War.gov `D7`.

## Generated Artifacts

| Artifact | Path |
|---|---|
| Script | `scripts/ufo_pr28_d25_phase_review.py` |
| Metadata | `research/ufo-video-dod_111688954-metadata.txt` |
| Phase track CSV | `research/ufo-video-dod_111688954-phase-track.csv` |
| Phase summary CSV | `research/ufo-video-dod_111688954-phase-summary.csv` |
| Asset index | `research/ufo-video-pr28-d25-phase-review-assets.csv` |
| Contact sheets and patches | `research/ufo-derived/video-hard-pair-phase-review/DOD_111688954/` |

## Next Step

Do not attempt physical speed or trajectory analysis from this clip unless FOV/zoom state, slant range, platform motion, gimbal pointing, target coordinates, or original telemetry become available. The useful next action is corpus-level: reconcile the remaining PR/D-label mismatches and promote only hard report-video pairs into any top-level findings.

