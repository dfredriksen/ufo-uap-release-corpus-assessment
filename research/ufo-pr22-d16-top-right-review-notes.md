# PR22 / D16 Top-Right Review Notes

Created: 2026-05-11

Source video: `DOD_111688775.mp4`

DVIDS release: `DOW-UAP-PR22`

DVIDS URL: `https://www.dvidshub.net/video/1006060/dow-uap-pr22-unresolved-uap-report-syria-july-2022`

Accompanying report stated by DVIDS: `DoW-UAP-D16`

War.gov D16 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d16-mission-report-syria-july-2022.pdf`

## Scope

This pass reviews the short PR22 public MP4 against DVIDS's upper-field visual description and the D16 report lane.

DVIDS says the release is `14` seconds of footage from split infrared and electro-optical sensors aboard a U.S. military platform. It states that the accompanying report is D16 and describes the video as showing an object near the five-second mark moving right-to-left across the top-right quarter of the sensor field.

The D16 PDF reports an initial UAP contact at `310239:00ZJUL22`, says the event occurred in less than a minute, and describes movement from north to south. It does not provide usable public altitude, depth, velocity, or trajectory fields for the UAP.

## Method

Script: `scripts/ufo_pr22_d16_top_right_review.py`

Tracked outputs:

- `research/ufo-video-pr22-d16-top-right-review-dod111688775.csv`
- `research/ufo-video-pr22-d16-top-right-review-summary.csv`
- `research/ufo-video-pr22-d16-top-right-review-assets.csv`

Ignored visual artifacts:

- `research/ufo-derived/video-motion-pass/pr22-d16-top-right-review/DOD_111688775/*`

The script samples the public MP4 at one frame per second. Because the public file is a split IR/EO display, the script uses the strongest recoverable IR upper-field lane near the DVIDS event window and searches for a dark elongated contrast component. It masks colored symbology and fixed redaction blocks where possible.

This is an image-plane visual-alignment proxy, not a validated object tracker.

## Results

Video metadata from OpenCV:

- Resolution: `1920x1080`
- FPS: `30.0`
- Frames: `426`
- Duration: `14.200s`

One-fps results:

- Sampled rows: `15`
- High-confidence rows: `8`
- Low-confidence rows: `1`
- None rows: `6`
- High-or-medium supported rows: `8`
- Supported interval: `1.0s-8.0s`

Selected dark elongated candidate:

- Median candidate score: `1560.728`
- Median component area: `520.0 px`
- Median dark contrast delta: `147.0` luma
- Median aspect ratio: `2.111`
- Median center: `x=390.607 px`, `y=344.669 px`

Image-plane path summary:

- Supported rows: `8`
- Interval: `1.0s-8.0s`
- Net displacement: `40.164 px`
- Path length: `41.342 px`
- Path rate: `5.906 px/s`
- X shift: `+31.386 px`
- Y shift: `+25.061 px`

The positive x-shift is important. In raw image coordinates, the selected feature does not independently validate DVIDS's right-to-left wording. That may reflect split-screen geometry, sensor/platform motion, or the detector selecting an associated dark terrain/contrast feature instead of the reported object.

## Interpretation

PR22 has strong image-plane support for the presence of a dark elongated upper-field contrast feature during the DVIDS event window. It is also a hard DVIDS report-video pairing to `DoW-UAP-D16`.

The public MP4 does not validate the D16 north-to-south movement language, DVIDS's right-to-left direction wording, physical speed, range, altitude, trajectory, object identity, or whether the selected dark feature is the reported UAP rather than a terrain/sensor/overlay-confounded contrast feature.

## Current Judgment

Treat `DOD_111688775.mp4` as a hard `PR22` / `D16` report-video pair with strong but directionally ambiguous upper-field visual support. The case is useful for release/report completeness and visual-description alignment, but not for physical kinematics.

