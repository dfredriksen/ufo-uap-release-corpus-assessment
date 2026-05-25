# PR48 Centered Track Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689167.mp4`
Release identity: `DOW-UAP-PR48`
DVIDS URL: `https://www.dvidshub.net/video/1006110/dow-uap-pr48-unresolved-uap-report-indopacom-2024`

## Scope

DVIDS identifies `DOD_111689167.mp4` as `DOW-UAP-PR48`, INDOPACOM, 2024. The page says the submitted material is one minute and 39 seconds of infrared sensor footage from a U.S. military platform, and that the reporter provided no oral or written description.

The DVIDS video description is broad: across `00:00-01:39`, the sensor tracks an area of contrast and keeps it generally near the center of the frame.

This remains a standalone public-release video review. DVIDS does not state an accompanying local `D` report pairing.

## Method

Script:

- `scripts/ufo_pr48_centered_track_review.py`

Outputs:

- `research/ufo-video-pr48-centered-track-review-dod111689167.csv`
- `research/ufo-video-pr48-centered-track-review-summary.csv`
- `research/ufo-video-pr48-centered-track-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr48-track-review/DOD_111689167/*`

The script samples the full clip at `1 fps`. It searches the central sensor field for compact bright local-contrast components, suppresses magenta/cyan overlay graphics, removes line artifacts, and penalizes candidates adjacent to dark wind-turbine/structure masks or close to the central ROI boundary.

This is a visual audit of center-field compact bright contrast. It is not a physical target tracker. The clip contains offshore wind turbines and water texture, so image-plane measurements are sensor/scene dependent.

## Results

The source MP4 is `1920x1080`, `30 fps`, `2981` frames, and `99.367s`.

One-fps full review:

| Review quality | Count |
|---|---:|
| High | `88` |
| Medium | `12` |
| High or medium | `100` |

Supported interval:

- `0.0s-99.0s`

Supported rows by local scene phase:

| Phase | Supported rows |
|---|---:|
| Initial centered track | `18` |
| Open-water centered track | `24` |
| Wind-farm crossing | `34` |
| Late centered track | `24` |

Compact bright component summary:

| Metric | Median | Note |
|---|---:|---|
| Component area | `71.0 px` | Mean `79.640`, stdev `30.948`, CV `0.389`. |
| Contrast delta | `135.0 luma` | Mean `133.200`, stdev `22.719`, CV `0.171`. |
| Distance from central reticle | `158.365 px` | Mean `178.721`, stdev `103.885`. |
| Edge margin inside central ROI | `281.535 px` | The selected candidate is usually well inside the central search region. |
| Nearest dark structure | `97.935 px` | `70` supported rows are separate from the wind-turbine/dark-structure mask. |

Dark-structure relation counts among supported rows:

| Relation | Count |
|---|---:|
| Separate from dark structure | `70` |
| Near dark structure | `20` |
| Adjacent to dark structure | `10` |

Image-plane path metrics for the selected center-field candidate:

| Metric | Value |
|---|---:|
| Supported rows | `100` |
| Supported span | `0.0s-99.0s` |
| Net displacement | `116.302 px` |
| Path length | `6240.009 px` |
| Path-average rate | `63.030 px/s` |
| Median one-second step rate | `55.261 px/s` |

## Interpretation

PR48 strongly supports the broad DVIDS visual description at image-plane level. A compact bright contrast candidate is recoverable in every one-second sample, and it remains generally in the central sensor field while the scene moves across open water and through an offshore wind-turbine field.

The strongest conservative claim is visual: the public MP4 contains a persistent compact bright area of contrast kept near center by the sensor. The public release does not provide range, FOV/zoom, platform motion, target coordinates, or telemetry, so the review does not validate physical speed, altitude, range, object identity, or trajectory.

PR48 should be treated as:

- Hard public-release identity: `DOD_111689167.mp4` = `DOW-UAP-PR48`.
- Strong standalone visual support for DVIDS's centered tracked-area description.
- No local `D` report pairing.
- No physical kinematic conclusion without source telemetry.

## Next Work

PR48 is now reviewed enough for the standalone-release matrix. Later passes reviewed `PR49`, `PR38`, `PR40`, `PR37`, `PR39`, and `PR46`; the prior index-only standalone target list is now complete.

