# PR49 Two-Area Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689168.mp4`
Release identity: `DOW-UAP-PR49`
DVIDS URL: `https://www.dvidshub.net/video/1006111/dow-uap-pr49-unresolved-uap-report-department-army-2026`

## Scope

DVIDS identifies `DOD_111689168.mp4` as `DOW-UAP-PR49`, Department of the Army, 2026. The page says the reporter provided no oral or written description, so this remains a standalone public-release video review.

The DVIDS description splits the clip into five visual phases:

- `00:00-00:08`: sensor tracks an initial area of interest.
- `00:09-00:16`: sensor pans right-to-left to track two areas of contrast while narrowing field of view.
- `00:17-01:03`: sensor widens field of view and keeps the areas generally centered.
- `01:04-01:08`: field of view rapidly cycles, making the areas appear to change size.
- `01:09-01:48`: sensor tracks the areas of contrast while intermittently cycling contrast settings.

This review tests whether the public MP4 supports that visual two-area description at image-plane level. It does not test object identity, number of independent objects, physical size, range, speed, altitude, or sensor geometry.

## Method

Script:

- `scripts/ufo_pr49_two_area_review.py`

Outputs:

- `research/ufo-video-pr49-two-area-review-dod111689168.csv`
- `research/ufo-video-pr49-two-area-review-summary.csv`
- `research/ufo-video-pr49-two-area-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr49-two-area-review/DOD_111689168/*`

The script samples the full clip at `1 fps`. It searches the central sensor field for compact bright local-contrast groups, suppresses fixed overlay/redaction/symbology, groups nearby bright components into one target candidate, and records a `two_area_proxy` when the candidate has either multiple components or a merged two-lobed bright group.

Because the late target often overlaps the central reticle, the script has a reticle-adjacent fallback pass. Rows from that fallback are capped at medium quality because target and overlay cannot be cleanly separated.

## Results

The source MP4 is `1920x1080`, `30 fps`, `3276` frames, and `109.200s`.

One-fps full review:

| Review quality | Count |
|---|---:|
| High | `54` |
| Medium | `44` |
| Low | `7` |
| None | `5` |
| High or medium | `98` |

Supported intervals:

- High-or-medium supported rows: `0.0s`; `2.0s-3.0s`; `5.0s-16.0s`; `18.0s-34.0s`; `37.0s-43.0s`; `45.0s-53.0s`; `55.0s`; `57.0s-63.0s`; `65.0s-91.0s`; `94.0s-97.0s`; `99.0s-109.0s`.
- Two-area proxy supported rows: `9.0s-16.0s`; `18.0s-27.0s`; `29.0s-34.0s`; `39.0s-43.0s`; `46.0s-53.0s`; `55.0s`; `57.0s-63.0s`; `65.0s-73.0s`; `75.0s-83.0s`; `88.0s-91.0s`; `94.0s-97.0s`; `99.0s-105.0s`; `107.0s-109.0s`.

Supported rows by DVIDS phase:

| Phase | High/medium rows | Two-area proxy rows |
|---|---:|---:|
| Initial area of interest | `7` | `0` |
| Two-area acquisition and zoom-in | `8` | `8` |
| Zoomed-out two-area tracking | `41` | `37` |
| Rapid zoom cycling | `4` | `4` |
| Late two-area tracking | `38` | `32` |

Selected target-group summary:

| Metric | Median | Note |
|---|---:|---|
| Component area | `216.5 px` | Mean `246.827`, stdev `136.938`, CV `0.555`. |
| Contrast delta | `236.0 luma` | Mean `225.327`, stdev `36.655`, CV `0.163`. |
| Distance from central reticle | `86.085 px` | Mean `120.331`, stdev `144.437`. |
| Max component separation | `22.61 px` | Median two-area proxy component/group separation. |

Two-area proxy track:

| Metric | Value |
|---|---:|
| Supported two-area proxy rows | `81` |
| Supported span | `9.0s-109.0s` |
| Net displacement | `341.127 px` |
| Path length | `3720.333 px` |
| Path-average rate | `37.203 px/s` |
| Median one-second step rate | `14.619 px/s` |

Detection modes among the `98` supported rows:

| Mode | Count |
|---|---:|
| Overlay-suppressed | `68` |
| Reticle-adjacent fallback | `30` |

## Interpretation

PR49 strongly supports the DVIDS visual description at image-plane level. After the initial single-area interval, the public MP4 repeatedly shows a paired bright contrast group through zoom-in, zoom-out, rapid zoom cycling, and late contrast-cycling phases.

The strongest conservative claim is visual: the public MP4 contains two close bright contrast areas that the sensor keeps near the center for most of the described two-area interval. The reticle-overlap and contrast-cycling portions are real caveats, which is why some rows are medium, low, or none.

PR49 should be treated as:

- Hard public-release identity: `DOD_111689168.mp4` = `DOW-UAP-PR49`.
- Strong standalone visual support for DVIDS's two-area contrast description.
- No local `D` report pairing.
- No physical size, range, speed, altitude, object-count, or trajectory conclusion without source telemetry.

## Next Work

PR49 is now reviewed enough for the standalone-release matrix. Later standalone passes reviewed `PR38`, `PR40`, `PR37`, `PR39`, and `PR46`; the prior index-only standalone target list is now complete.

