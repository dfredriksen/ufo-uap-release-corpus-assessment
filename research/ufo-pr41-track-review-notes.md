# PR41 Track Review

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `I:\My Drive\UFO\DOD_111689083.mp4`
Release identity: `DOW-UAP-PR41`

## Scope

DVIDS identifies `DOD_111689083` as `DOW-UAP-PR41`, Middle East, 2020. The public page describes one minute and 34 seconds of infrared footage from a U.S. military platform and says the reporter did not provide an oral or written description.

DVIDS describes an area of contrast entering the sensor field of view from the bottom third of the left side at `00:01`, followed by the sensor panning from left to right while tracking the area of contrast and keeping it generally centered from `00:02-01:34`.

This remains a standalone public-release video review. It does not create a local `D` report pairing.

## Method

Script:

- `scripts/ufo_pr41_track_review.py`

Outputs:

- `research/ufo-video-pr41-track-review-dod111689083.csv`
- `research/ufo-video-pr41-track-review-summary.csv`
- `research/ufo-video-pr41-track-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr41-track-review/DOD_111689083/*`

The script samples the full `94.533s` source video at `1 fps`. It suppresses cyan/green sensor overlays, detects compact bright or dark local contrast candidates in the main sensor view, then uses a dynamic smoothness pass to select one candidate path through the terrain/cloud background.

This is a visual audit of compact image-plane contrast. It is not a clean physical tracker. PR41 has a textured terrain/cloud background with many compact specks, so the result should be treated as intermittent support rather than a frame-perfect target solution.

## Results

The source MP4 is `1920x1080`, `30 fps`, `2836` frames, and `94.533s`.

Full one-fps review:

| Review quality | Count |
|---|---:|
| High | 55 |
| Medium | 6 |
| Low | 34 |
| High or medium | 61 |

Supported high-or-medium intervals:

- `2.0s`
- `20.0s-36.0s`
- `39.0s-40.0s`
- `42.0s-50.0s`
- `60.0s-78.0s`
- `81.0s`
- `83.0s-94.0s`

The startup/entry interval is weak in the local automated pass. The first single supported row appears at `2.0s`, and the first sustained supported run starts at `20.0s`.

Supported target-center image-plane track:

| Metric | Value |
|---|---:|
| Supported high/medium rows | `61` |
| Supported span | `2.0s-94.0s`, intermittent |
| Net displacement | `129.752 px` |
| Path length | `2631.144 px` |
| Path-average rate | `28.599 px/s` |
| Median step rate | `32.212 px/s` |

Compact contrast-component summary:

| Metric | Median | Note |
|---|---:|---|
| Component area | `56.0 px` | Mean `66.770`, stdev `46.068`, CV `0.690`. |
| Contrast delta | `82.0 luma` | Mean `84.959`, stdev `23.080`, CV `0.272`. |
| Distance from central reticle | `252.38 px` | The tracked contrast candidate is generally in the sensor field, not locked to the reticle center. |
| One-second supported step | `39.498 px` | Image-plane step between supported rows. |

All `61` supported rows were bright-polarity candidates. All `95` sampled rows were separate from colored overlay by the script's overlay-distance rule.

## Interpretation

The local PR41 pass supports the broad DVIDS description at image-plane level: the clip contains a compact bright area of contrast that is repeatedly recoverable while the sensor pans and keeps the area within the field of view.

The support is materially weaker than PR44, PR45, and PR47. The detector does not cleanly validate the `00:01` entry moment, and the textured background creates intermittent gaps and possible terrain-speck confounds. The best supported claim is a standalone visual one: PR41 contains intermittent compact bright contrast candidates compatible with DVIDS's tracked-area description.

PR41 should be treated as:

- Hard public-release identity: `DOD_111689083.mp4` = `DOW-UAP-PR41`.
- Moderate standalone support for a compact bright tracked contrast area across multiple intervals.
- No hard local `D` report pairing.
- No independent physical speed, range, altitude, platform-motion, or target-coordinate conclusion.

## Next Work

The PR29 `D8`/`D27` reconciliation and the `DOD_111688825.mp4` PR27/D23 lookup have both been completed in follow-on passes. Remaining higher-value work is now either denser independent hand marking for a hard anchor such as D38/PR36, or a release-index completeness sweep for any remaining local MP4s not yet tied to DVIDS/War.gov pages.

