# UFO PR27 / D23 Phase Review Notes

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: bounded phase review of `DOD_111688825.mp4` / `DOW-UAP-PR27` / `DoW-UAP-D23`
Status: DVIDS visual sequence supported; kinematics not validated

## Bottom Line

`DOD_111688825.mp4` is a hard DVIDS report-video pairing for `DOW-UAP-PR27` and `DoW-UAP-D23`. The phase review supports the public DVIDS sequence from acquisition/zoom into a centered tracking interval and then sensor-motion-driven loss/reacquisition.

The public MP4 does not independently validate the D23 report's estimated `320 MPH` or `440 MPH` values. It also does not identify which of D23's two UAP lines the video depicts. Treat velocity, altitude, location coordinates, and event-line assignment as report-derived unless source telemetry appears.

## Inputs

| Field | Value |
|---|---|
| Local video | `I:\My Drive\UFO\DOD_111688825.mp4` |
| Release identity | `DOW-UAP-PR27` |
| Written report | `DoW-UAP-D23` |
| Video metadata | `1920x1080`, `30.0 fps`, `8920` frames, `297.33s` |
| DVIDS phase anchors | no-content lead-in; contrast at `01:56`; pan at `02:04`; zoom at `02:14`; centered track through `03:26`; loss/reacquisition through `04:57` |

## D23 Report Context

D23 contains two UAP line records during the mission:

| UAP line | Initial contact | Reported velocity | Reported signature | Other report fields |
|---|---:|---:|---|---|
| UAP 1 | `240241:00ZOCT23` | `320 MPH` estimated | `THERMAL SHOWED COLD` | solid physical state; no maneuverability observed; observer assessment benign; no engagement; no effects on persons; no reported intelligent control |
| UAP 2 | `240322:00ZOCT23` | `440 MPH` estimated | `UNK` | solid physical state; no maneuverability observed; observer assessment benign; no engagement; no effects on persons; no reported intelligent control |

The DVIDS page states the accompanying mission report mentions a UAP observed during the mission, but the public release does not cleanly assign the MP4 to UAP line 1 or UAP line 2.

## Phase Results

| Phase | Window | Samples | Result |
|---|---:|---:|---|
| No-content / scene context lead-in | `0.0-115.5s` | `29` | All sampled marks classified low. These are shoreline, terrain, edge, or scene-context features rather than UAP support. |
| Initial right-side contrast | `116.0-123.5s` | `16` | `0/16` high-or-medium after tightening the ROI. This avoids shoreline false positives but means the first public "becomes distinguishable" moment is not independently confirmed by the detector. |
| Pan to center | `124.0-133.5s` | `20` | `10/20` high-or-medium, but several marks remain close to shoreline/scene features. Treat as phase alignment, not clean track data. |
| Zoom and centered track | `134.0-206.5s` | `146` | `101/146` high-or-medium. This is the useful object-level interval, though `89` rows are near or intersecting colored overlay/reticle graphics. |
| Sensor-motion loss and reacquisition | `207.0-297.0s` | `181` | `180/181` high-or-medium candidate marks. The public video preserves repeated compact-return candidates during the DVIDS loss/reacquisition phase, but sensor motion and water texture prevent physical trajectory claims. |

## Interpretation

The strongest visual support begins after the zoom/center transition. From roughly `134s` onward, the public MP4 repeatedly presents a compact contrast candidate near the sensor's focus area. The late interval also preserves frequent candidate returns, consistent with DVIDS's statement that sensor motion repeatedly loses and reacquires the area of contrast.

The phase review is not a clean kinematic track. The detector can be misled by shoreline detail before the zoom, colored reticle/overlay graphics near the center, and water/scene texture during sensor motion. The CSV should therefore be used as phase evidence and a manual-review index, not as physical speed, range, or maneuver proof.

## Manual Validation Addendum

Dedicated note: `research/ufo-video-pr27-d23-manual-validation-notes.md`

The follow-on validation layer reviewed `327` active rows from `134.0s-297.0s` and classified each row by visual category. It found `175` true compact-return candidates, `88` reticle/overlay artifacts, `27` frame-edge artifacts, `23` water-texture artifacts, `3` shoreline/terrain artifacts, `10` uncertain rows, and `1` no-candidate row.

The validation narrows the result: the late `207.0s-297.0s` loss/reacquisition phase is stronger (`144/181` validated compact-return candidates) than the `134.0s-206.5s` zoom/centered-track phase (`31/146` validated compact-return candidates). Treat the centered-track interval as heavily caveated by reticle and water texture.

## Generated Artifacts

| Artifact | Path |
|---|---|
| Script | `scripts/ufo_pr27_d23_phase_review.py` |
| Metadata | `research/ufo-video-dod_111688825-metadata.txt` |
| Phase track CSV | `research/ufo-video-dod_111688825-phase-track.csv` |
| Phase summary CSV | `research/ufo-video-dod_111688825-phase-summary.csv` |
| Asset index | `research/ufo-video-pr27-d23-phase-review-assets.csv` |
| Contact sheets and patches | `research/ufo-derived/video-hard-pair-phase-review/DOD_111688825/` |
| Manual validation table | `research/ufo-video-pr27-d23-manual-validation-dod111688825.csv` |
| Manual validation summary | `research/ufo-video-pr27-d23-manual-validation-summary.csv` |
| Manual validation assets | `research/ufo-video-pr27-d23-manual-validation-assets.csv` |

## Next Step

If PR27/D23 is developed further, the next useful work is a manual validation pass on `134.0s-297.0s`, separating true compact-return candidates from reticle and water-texture artifacts. Do not run physical kinematics unless FOV/zoom state, slant range, platform motion, target coordinates, or original telemetry become available.

