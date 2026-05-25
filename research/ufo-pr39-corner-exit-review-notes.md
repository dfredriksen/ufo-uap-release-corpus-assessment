# PR39 Lower-Right Corner Exit Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689057.mp4`
Release identity: `DOW-UAP-PR39`
DVIDS URL: `https://www.dvidshub.net/video/1006089/dow-uap-pr39-unresolved-uap-report-middle-east-2020`

## Scope

DVIDS identifies `DOD_111689057.mp4` as `DOW-UAP-PR39`, Middle East, 2020. The page says CENTCOM submitted five seconds of infrared sensor video from a U.S. military platform, and that the reporter did not provide an oral or written description.

DVIDS describes the visual event at `00:03-00:05`: a faint area of contrast enters from the lower half of the right edge, proceeds right-to-left across the corner of the frame, and exits near the center of the bottom edge.

This remains a standalone public-release video review. It does not create a local `D` report pairing.

## Method

Script:

- `scripts/ufo_pr39_corner_exit_review.py`

Outputs:

- `research/ufo-video-pr39-corner-exit-review-dod111689057.csv`
- `research/ufo-video-pr39-corner-exit-review-summary.csv`
- `research/ufo-video-pr39-corner-exit-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr39-corner-exit-review/DOD_111689057/*`

The script samples the full local file at `10 fps`, suppresses colored overlays and black redaction regions, and searches the lower-right/lower-center water lane for compact local contrast components. The expected lane is used only to rank ambiguous lower-corner residuals during the DVIDS-described event window.

The measured component is an image-processing proxy for the faint visible contrast area. It is not a physical object-size, speed, range, altitude, or trajectory estimate.

## Results

The source MP4 is `1920x1080`, `30 fps`, `175` frames, and `5.833s`.

Ten-fps full-clip review:

| Review quality | Count |
|---|---:|
| High | `8` |
| Medium | `2` |
| Low | `4` |
| None | `46` |
| High or medium | `10` |

DVIDS event-window review, `3.0s-5.0s`:

| Review quality | Count |
|---|---:|
| High | `8` |
| Medium | `2` |
| Low | `4` |
| None | `7` |
| High or medium | `10` |

Supported interval: `3.6s-4.5s`.

Supported image-plane track:

| Metric | Value |
|---|---:|
| Supported rows | `10` |
| Net displacement | `508.769 px` |
| Path length | `509.041 px` |
| Horizontal delta | `-487.400 px` |
| Vertical delta | `+145.900 px` |
| Path-average rate | `565.601 px/s` |
| Median step rate | `627.458 px/s` |
| Linearity | `0.999` |

Supported component metrics:

| Metric | Median |
|---|---:|
| Distance from event lane | `12.435 px` |
| Component area | `62.0 px` |
| Bbox width | `12.5 px` |
| Bbox height | `7.5 px` |
| Max absolute contrast | `16.0 luma` |
| Mean signed contrast | `10.364 luma` |

## Interpretation

PR39 supports the narrow DVIDS visual description at image-plane level, but the target is faint. The public MP4 contains a compact lower-water contrast component from `3.6s-4.5s` that moves leftward and downward toward the bottom-center exit lane.

The early `3.0s-3.3s` rows are low-confidence edge/entry residuals, and the `4.6s-5.0s` rows are not counted as supported because the detector begins selecting a separate shoreline/edge component after the visible lower-water candidate exits or becomes too weak.

PR39 should be treated as:

- Hard public-release identity: `DOD_111689057.mp4` = `DOW-UAP-PR39`.
- Moderate-to-strong standalone visual support for the DVIDS lower-right corner / bottom-edge exit description.
- No local `D` report pairing.
- No physical size, range, speed, altitude, trajectory, platform-motion, or object-identity conclusion without source telemetry and sensor context.

## Next Work

PR39 is now reviewed enough for standalone-release completeness. A later pass reviewed `PR46`, so the prior index-only standalone target list is now complete.

