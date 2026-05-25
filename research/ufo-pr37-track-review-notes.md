# PR37 Bottom-To-Top Track Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689044.mp4`
Release identity: `DOW-UAP-PR37`
DVIDS URL: `https://www.dvidshub.net/video/1006087/dow-uap-pr37-unresolved-uap-report-middle-east-2020`

## Scope

DVIDS identifies `DOD_111689044.mp4` as `DOW-UAP-PR37`, Middle East, 2020. The page says CENTCOM submitted about nine seconds of infrared sensor video from a U.S. military platform, and that the reporter did not provide an oral or written description.

DVIDS describes the visual event at `00:06-00:08`: an area of contrast enters from the lower-left part of the sensor field, follows a generally bottom-to-top path, and exits near the upper-left part of the field.

This remains a standalone public-release video review. It does not create a local `D` report pairing.

## Method

Script:

- `scripts/ufo_pr37_track_review.py`

Outputs:

- `research/ufo-video-pr37-track-review-dod111689044.csv`
- `research/ufo-video-pr37-track-review-summary.csv`
- `research/ufo-video-pr37-track-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr37-track-review/DOD_111689044/*`

The script samples the full local file at `10 fps`, suppresses colored symbology and black redaction regions, and extracts compact bright components in a left-side search lane. The lane is only used to rank ambiguous bright components in the DVIDS-described event window.

The measured component is an image-processing proxy for the visible area of contrast. It is not a physical object-size, range, speed, or trajectory estimate.

## Results

The source MP4 is `1920x1080`, `30 fps`, `294` frames, and `9.800s`.

Ten-fps full-clip review:

| Review quality | Count |
|---|---:|
| High | `15` |
| Low | `3` |
| None | `81` |
| High or medium | `15` |

DVIDS event-window review, `6.0s-8.0s`:

| Review quality | Count |
|---|---:|
| High | `15` |
| Low | `3` |
| None | `3` |
| High or medium | `15` |

Supported interval: `6.4s-7.8s`.

Supported image-plane track:

| Metric | Value |
|---|---:|
| Supported rows | `15` |
| Net displacement | `896.143 px` |
| Path length | `896.327 px` |
| Horizontal delta | `+118.300 px` |
| Vertical delta | `-888.300 px` |
| Upward displacement | `888.300 px` |
| Path-average rate | `640.233 px/s` |
| Median step rate | `667.636 px/s` |
| Linearity | `1.000` |

Supported component metrics:

| Metric | Median |
|---|---:|
| Distance from event lane | `17.3 px` |
| Component area | `199.0 px` |
| Bbox width | `12.0 px` |
| Bbox height | `22.0 px` |
| Brightness delta | `76.0 luma` |
| Max positive contrast | `87.0 luma` |

## Interpretation

PR37 strongly supports the narrow DVIDS visual description at image-plane level. The public MP4 contains a bright, compact-to-elongated contrast streak in the left side of the field from `6.4s-7.8s`, and the supported centers move almost monotonically upward through the event window.

The stronger conclusion is visual, not physical. The public MP4 does not establish range, altitude, true speed, physical trajectory, platform motion, object size, or object identity. The boat/vessel context visible in the rest of the clip remains scene context, not a report pairing.

PR37 should be treated as:

- Hard public-release identity: `DOD_111689044.mp4` = `DOW-UAP-PR37`.
- Strong standalone visual support for the DVIDS bottom-to-top left-side contrast event.
- No local `D` report pairing.
- No physical size, range, speed, altitude, trajectory, or object-identity conclusion without source telemetry and sensor context.

## Next Work

PR37 is now reviewed enough for standalone-release completeness. Later passes reviewed `PR39` and `PR46`; the prior index-only standalone target list is now complete.

