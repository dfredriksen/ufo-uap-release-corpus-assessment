# PR38 Star-Like Contrast Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689051.mp4`
Release identity: `DOW-UAP-PR38`
DVIDS URL: `https://www.dvidshub.net/video/1006088/dow-uap-pr38-unresolved-uap-report-middle-east-2013`

## Scope

DVIDS identifies `DOD_111689051.mp4` as `DOW-UAP-PR38`, Middle East, 2013. The page says the reporter provided no oral or written description, so this remains a standalone public-release video review.

DVIDS describes an area of contrast resembling an eight-pointed star with alternating-length arms. The time-coded description says the sensor zooms in at `00:10`, the star-like area moves within the field of view with a visible trail from `00:11-00:29`, leaves the field at the bottom right around `00:30`, then after an apparent cut generally remains in view from `00:35-01:44` before exiting from the top-left quarter.

This review tests whether the public MP4 supports that visual description at image-plane level. It does not test object identity, physical size, range, speed, altitude, trajectory, sensor geometry, or whether the starburst pattern is an optical/sensor effect.

## Method

Script:

- `scripts/ufo_pr38_startrail_review.py`

Outputs:

- `research/ufo-video-pr38-startrail-review-dod111689051.csv`
- `research/ufo-video-pr38-startrail-review-summary.csv`
- `research/ufo-video-pr38-startrail-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr38-startrail-review/DOD_111689051/*`

The script samples the full clip at `1 fps`. It searches the central sensor field for dark local-contrast components, suppresses fixed redaction blocks and persistent sensor symbology, groups nearby components into a target candidate, and records a `star_like_proxy` when the candidate has a broad, low-fill bounding box consistent with the dark starburst shape.

This is a visual audit of the star-like contrast feature. The detector is intentionally conservative around the earliest pre-zoom rows, the bottom-right exit/cut gap, and rows where the target overlaps fixed overlays.

## Results

The source MP4 is `1920x1080`, `30 fps`, `3193` frames, and `106.433s`.

One-fps full review:

| Review quality | Count |
|---|---:|
| High | `77` |
| Medium | `13` |
| Low | `9` |
| None | `8` |
| High or medium | `90` |

Supported intervals:

- `3.0s-5.0s`; `7.0s-10.0s`; `12.0s-21.0s`; `23.0s-29.0s`; `35.0s-54.0s`; `60.0s-101.0s`; `103.0s-106.0s`.

Supported rows by DVIDS phase:

| Phase | Supported rows |
|---|---:|
| Initial star-like contrast | `6` |
| Zoom-in event | `1` |
| Star-like movement with trail | `17` |
| Bottom-right exit and cut gap | `0` |
| Post-cut in-field star-like contrast | `63` |
| Top-left exit | `3` |

Selected target-group summary:

| Metric | Median | Note |
|---|---:|---|
| Component area | `4379.5 px` | Mean `3716.500`, stdev `2020.365`, CV `0.544`. |
| Dark contrast delta | `99.0 luma` | Local median luma minus selected dark group luma proxy. |
| Distance from central reticle | `294.735 px` | Mean `330.617`, stdev `174.996`. |
| Edge margin inside central ROI | `286.635 px` | Mean `268.788`, stdev `121.734`. |
| Bounding-box width | `163.0 px` | Mean `158.889`, stdev `80.661`. |
| Bounding-box height | `122.0 px` | Mean `118.733`, stdev `59.810`. |

Image-plane target-center path for supported star-like rows:

| Metric | Value |
|---|---:|
| Supported star-like rows | `90` |
| Supported span | `3.0s-106.0s` |
| Net displacement | `640.039 px` |
| Path length | `14984.312 px` |
| Path-average rate | `145.479 px/s` |
| Median one-second step rate | `51.219 px/s` |

The path values are image-plane measurements across sensor motion and an apparent cut. They should not be interpreted as physical target motion.

## Interpretation

PR38 strongly supports the DVIDS visual description at image-plane level. The public MP4 contains a prominent dark, star-like contrast feature with a broad low-fill shape, and that feature is recoverable across most of the movement/trail interval and the long post-cut in-field interval.

The bottom-right exit/cut-gap phase is intentionally not counted as high/medium support in this automated pass. The visible target is at the edge or absent around that transition, and nearby overlays make those rows unsuitable for robust target-center measurement. This does not weaken the release identity; it only limits the local quantitative claim for that short phase.

PR38 should be treated as:

- Hard public-release identity: `DOD_111689051.mp4` = `DOW-UAP-PR38`.
- Strong standalone visual support for DVIDS's star-like contrast / trail / post-cut in-field description.
- No local `D` report pairing.
- No physical size, range, speed, altitude, trajectory, object identity, or sensor-effect conclusion without source telemetry and sensor context.

## Next Work

PR38 is now reviewed enough for the standalone-release matrix. Later passes reviewed `PR40`, `PR26`, `PR39`, `PR46`, and other previously less-complete lanes.

