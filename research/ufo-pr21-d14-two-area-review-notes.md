# PR21 / D14 Two-Area Review Notes

Created: 2026-05-11

Source video: `DOD_111688762.mp4`

DVIDS release: `DOW-UAP-PR21`

DVIDS URL: `https://www.dvidshub.net/video/1006059/dow-uap-pr21-unresolved-uap-report-iraq-may-2022`

Accompanying report stated by DVIDS: `DoW-UAP-D14`

War.gov D14 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d14-mission-report-iraq-may-2022.pdf`

## Scope

This pass reviews the short PR21 public MP4 against DVIDS's central two-area visual description and the D14 report lane.

DVIDS says the public release consists of ten seconds of infrared footage from a U.S. military platform. It states that the accompanying report is D14 and says the video depicts two areas of contrast moving together near the center of the field of view throughout runtime.

## D14 Reconciliation Caveat

DVIDS also summarizes D14 as describing the UAP as a probable `SU-27/35`. The local/War.gov D14 PDF text needs a more careful treatment:

- The D14 mission narrative has a separate observation line at `0011Z` for one probable `SU-27/35` landing near Al Asad Airfield.
- The D14 UAP section separately lists initial contact at `300117:00ZMAY22`, says one possible small UAP was observed, and describes it as flying north to northeast while the screener could not get a positive ID.

Current treatment: use DVIDS as the hard PR21/D14 report-video pairing source, but do not treat the public MP4 as validating `SU-27/35` identity. Keep the D14 probable-aircraft observation and D14 UAP line separated unless an official correction or fuller context resolves the relationship.

## Method

Script: `scripts/ufo_pr21_d14_two_area_review.py`

Tracked outputs:

- `research/ufo-video-pr21-d14-two-area-review-dod111688762.csv`
- `research/ufo-video-pr21-d14-two-area-review-summary.csv`
- `research/ufo-video-pr21-d14-two-area-review-assets.csv`

Ignored visual artifacts:

- `research/ufo-derived/video-motion-pass/pr21-d14-two-area-review/DOD_111688762/*`

The script samples the public MP4 at one frame per second and searches a central ROI for compact bright/dark contrast components. It selects a two-area proxy only when two compact candidates have plausible separation and remain near the central field. This is a conservative visual-alignment proxy, not a validated object tracker.

## Results

Video metadata from OpenCV:

- Resolution: `1920x1080`
- FPS: `30.0`
- Frames: `308`
- Duration: `10.267s`

One-fps results:

- Sampled rows: `11`
- High-confidence rows: `4`
- Medium-confidence rows: `5`
- Low-confidence rows: `2`
- High-or-medium supported rows: `9`
- Supported interval: `0.0s-8.0s`

Supported two-area proxy:

- Median pair score: `409.350`
- Median pair separation: `106.072 px`
- Median pair-center distance from reticle: `170.538 px`
- Median pair center: `x=1067.032 px`, `y=504.011 px`

The supported pair-center path summary is intentionally low evidentiary weight: net `147.083 px`, path `1532.912 px`, path rate `191.614 px/s` across `0.0s-8.0s`. The selected pair is a detection proxy in a textured terrain scene, not a physical track.

## Interpretation

PR21 has moderate image-plane support for DVIDS's narrow visual description: the public MP4 repeatedly contains two compact contrast candidates near the center field. The support is not as clean as PR19 because terrain texture and central overlays can create plausible false candidates, so this should be treated as visual-description alignment rather than object-level proof.

The public MP4 does not validate the D14 `SU-27/35` observation, the D14 UAP north-to-northeast movement language, physical speed, range, altitude, trajectory, object identity, or whether the two image-plane contrast areas correspond to one aircraft, two aircraft, sensor/terrain effects, or another source.

## Current Judgment

Treat `DOD_111688762.mp4` as a hard `PR21` / `D14` report-video pair with moderate central two-area visual support. Keep the D14 report-text caveat visible: D14 contains both a separate probable `SU-27/35` observation line and a UAP line with no positive ID.

