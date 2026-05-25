# PR23 / D18 Diagonal Review Notes

Created: 2026-05-11

Source video: `DOD_111688809.mp4`

DVIDS release: `DOW-UAP-PR23`

DVIDS URL: `https://www.dvidshub.net/video/1006062/dow-uap-pr23-unresolved-uap-report-iraq-december-2022`

Accompanying report stated by DVIDS: `DoW-UAP-D18`

War.gov D18 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d18-mission-report-iraq-december-2022.pdf`

## Scope

This pass reviews the short PR23 public MP4 against DVIDS's diagonal bottom-left-to-top-right visual description and the D18 mission-report lane.

DVIDS identifies the public release as Iraq, December 2022, filename `DOD_111688809`, length `00:00:10`, and states that the accompanying mission report is `DoW-UAP-D18`.

The D18 PDF records an initial UAP contact at `011620:00ZDEC22`, one UAP sighted, and a description of one possible `UAP/UAV` flying west to east. The report says the observer did not follow the UAP and continued the tasked mission. Public altitude, depth, velocity, and trajectory fields are not populated.

## Method

Script: `scripts/ufo_pr23_d18_diagonal_review.py`

Tracked outputs:

- `research/ufo-video-pr23-d18-diagonal-review-dod111688809.csv`
- `research/ufo-video-pr23-d18-diagonal-review-summary.csv`
- `research/ufo-video-pr23-d18-diagonal-review-assets.csv`

Ignored visual artifacts:

- `research/ufo-derived/video-motion-pass/pr23-d18-diagonal-review/DOD_111688809/*`

The script samples the public MP4 every half second. It builds a median background from the first seven seconds, masks colored symbology and known redaction regions, and searches for compact residuals near a diagonal proxy line from lower-left to upper-right. The event phase is constrained by DVIDS's description that the area of contrast leaves near the upper-right around six seconds.

This is an image-plane residual-alignment proxy, not a validated object tracker.

## Results

Video metadata from OpenCV:

- Resolution: `1920x1080`
- FPS: `30.0`
- Frames: `322`
- Duration: `10.733s`

Half-second results:

- Sampled rows: `22`
- Medium-confidence rows: `3`
- Low-confidence rows: `19`
- High-or-medium supported rows: `3`
- Supported interval: `4.5s-5.5s`

Selected residual candidate:

- Median candidate score: `679.117`
- Median component area: `112.0 px`
- Median contrast delta: `110.0` luma
- Median distance from diagonal proxy line: `29.509 px`
- Median distance from the linearized six-second proxy point: `70.271 px`
- Median line-projection fraction: `0.796`
- Median center: `x=1271.205 px`, `y=224.580 px`

Image-plane path summary:

- Supported rows: `3`
- Interval: `4.5s-5.5s`
- Net displacement: `3.025 px`
- Path length: `3.317 px`
- Path rate: `3.317 px/s`
- X shift: `-1.556 px`
- Y shift: `+2.594 px`

The path metrics are deliberately low-weight. The selected feature barely moves across the supported rows, and the urban scene contains strong building, road, compression, redaction, and platform-motion confounds.

## Interpretation

PR23 is a hard DVIDS report-video pair to `DoW-UAP-D18`. The local public-video pass recovers only weak-to-moderate support for the narrow visual description: a diagonal-lane residual aligns with the upper-right/exit phase around `4.5s-5.5s`.

The pass does not recover a clean bottom-left-to-top-right moving object track. It also does not validate D18's west-to-east movement language, physical speed, range, altitude, trajectory, UAP/UAV identity, or whether the selected residual is the reported object rather than an urban-scene artifact.

## Current Judgment

Treat `DOD_111688809.mp4` as a hard `PR23` / `D18` report-video pair with weak-to-moderate visual-description support and a strong ambiguity caveat. D18 is especially useful as a control case because the official report itself frames the object as possible `UAP/UAV` and says it was not followed.

