# PR45 Size And Exit Review

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `I:\My Drive\UFO\DOD_111689123.mp4`
Release identity: `DOW-UAP-PR45`

## Scope

DVIDS identifies `DOD_111689123` as `DOW-UAP-PR45`, Middle East, 2020. The public page describes `58s` of infrared footage from a U.S. military platform and says the reporter did not provide an oral or written description.

DVIDS breaks the clip into five visual phases: initial reticle-lock acquisition, increasing target distinctiveness before zoom, a field-of-view narrowing at about `31s`, post-zoom apparent size/distinctiveness increase through `56s`, and lower-right exit at `57s-58s`. The page also cautions that apparent size increase is likely at least partly attributable to platform closure.

This remains a standalone public-release video review. It does not create a local `D` report pairing.

## Method

Script:

- `scripts/ufo_pr45_size_exit_review.py`

Outputs:

- `research/ufo-video-pr45-size-exit-review-dod111689123.csv`
- `research/ufo-video-pr45-size-exit-review-exit-window.csv`
- `research/ufo-video-pr45-size-exit-review-summary.csv`
- `research/ufo-video-pr45-size-exit-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr45-size-exit-review/DOD_111689123/*`

The script samples the full `58.767s` source video at `1 fps`, then samples the `54.0s` through end interval at `5 fps`. It suppresses colored overlays and line-like reticle/lock-box graphics, then scores the remaining local contrast component near the expected PR45 target lane.

The measured component is an image-processing proxy for the visible area of contrast. It is not a physical size estimate, and it should not be treated as target range, closure rate, or true dimensions.

## Results

The source MP4 is `1920x1080`, `30 fps`, `1763` frames, and `58.767s`.

Full-clip one-fps review:

| Review quality | Count |
|---|---:|
| High | 48 |
| Medium | 2 |
| Low | 9 |
| High or medium | 50 |

Dense exit-window review, `54.0s` through the end of the clip:

| Review quality | Count |
|---|---:|
| High | 16 |
| Medium | 3 |
| Low | 5 |
| High or medium | 19 |

The dense exit pass supports a visible contrast component from `54.0s-58.2s`. The final `58.4s-58.6s` rows are classified low because the target is mostly out of frame or the detector is seeing lock-box/edge residuals rather than a clean target component.

Supported target-center image-plane track:

| Metric | Value |
|---|---:|
| Supported full-clip rows | 50 |
| Supported interval | `3.0s-58.0s` |
| Net displacement | `258.344 px` |
| Path length | `874.028 px` |
| Path-average rate | `15.891 px/s` |
| Median step rate | `9.552 px/s` |

Contrast-component size proxy:

| Metric | Value |
|---|---:|
| Median component area | `175.5 px` |
| Median bbox width | `20.0 px` |
| Median bbox height | `19.5 px` |
| Median brightness delta | `137.0 luma` |
| Post-zoom component-area ratio, about `32s` to `56s` | `2.836x` |
| Full supported component-area ratio, about `4s` to `56s` | `1.912x` |
| Pre-zoom component-area ratio, about `4s` to `30s` | `0.674x` |

The detector does not independently support a monotonic pre-zoom size increase. The stronger local support is for the post-zoom interval, where the contrast component grows and becomes more visually distinct before leaving the center and exiting lower right.

Overlay relation for the one-fps full-clip pass:

| Relation to colored overlay | Count |
|---|---:|
| Separate from colored overlay | 8 |
| Near colored overlay | 46 |
| Intersects colored overlay | 5 |

The high overlay proximity is important: much of PR45 places the target inside or immediately beside reticle and lock-box symbology. The automated table is useful for repeatable review, but it should be treated as a visual audit, not a clean independent tracker.

## Interpretation

The local PR45 review supports the DVIDS visual sequence at image-plane level:

- A target-like contrast component becomes usable near the reticle after the initial acquisition seconds.
- The post-zoom interval shows a clear increase in measured contrast-component area and visible distinctiveness.
- The final seconds show lower-right departure from the center, with dense support through `58.2s` and low-confidence residuals by `58.4s-58.6s`.

This does not prove physical target growth. It also does not establish speed, range, altitude, platform motion, field of view, target coordinates, or object nature. DVIDS/AARO's closure caveat should remain attached to any discussion of apparent size increase.

PR45 should be treated as:

- Hard public-release identity: `DOD_111689123.mp4` = `DOW-UAP-PR45`.
- Strong standalone visual support for post-zoom apparent size/distinctiveness increase and lower-right exit.
- No hard local `D` report pairing.
- No independent physical size, speed, or range conclusion.

## Next Work

The next standalone hard-identity video target is PR41 (`DOD_111689083.mp4`), because PR41 remains less reviewed than PR44, PR45, and PR47. If report reconciliation is higher priority than standalone video review, the unresolved PR29 `D8` label versus local/War.gov `D27` text mismatch remains the best document-side target.

