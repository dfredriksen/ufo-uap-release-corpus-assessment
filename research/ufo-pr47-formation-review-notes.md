# PR47 Formation Review

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `I:\My Drive\UFO\DOD_111689142.mp4`
Release identity: `DOW-UAP-PR47`

## Scope

DVIDS identifies `DOD_111689142` as `DOW-UAP-PR47`, INDOPACOM, 2023. The public description says the video is one minute and 59 seconds of infrared footage from a U.S. military platform, and that the reporter did not provide an oral or written description.

DVIDS describes the visible content as three distinct areas of contrast that remain generally centered and appear to maintain fixed position and orientation relative to one another. This review tests that description against the local MP4 at image-plane level.

This remains a standalone public-release video review. It does not create a local `D` report pairing and should not be folded into `D58` or other multi-contact reports without a source link.

## Method

Script:

- `scripts/ufo_pr47_formation_review.py`

Outputs:

- `research/ufo-video-pr47-formation-review-dod111689142.csv`
- `research/ufo-video-pr47-formation-review-summary.csv`
- `research/ufo-video-pr47-formation-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr47-formation-review/DOD_111689142/*`

The script samples the full `119.667s` source video at `1 fps`. It searches a central sensor-view ROI for compact low-saturation bright clusters while suppressing colored reticle overlays, then models the bright component as three visual subclusters using k-means on the component pixels.

This is not a physical formation model. The three-subcluster centers are a repeatable image-processing proxy for the three bright visual areas.

## Results

The review produced `120` one-fps rows.

| Review quality | Count |
|---|---:|
| High | 107 |
| Medium | 3 |
| Low | 10 |
| High or medium | 110 |

All `110` high-or-medium rows were modeled as three visual subclusters. The low rows are mostly the startup interval `0s-8s`, where the target is weak, small, or reticle-adjacent, plus one later weak/overlay-adjacent row at `113s`.

The supported track spans `9.0s-119.0s`.

| Metric | Value |
|---|---:|
| Supported high/medium rows | 110 |
| Formation-center net displacement | `92.635 px` |
| Formation-center path length | `8963.384 px` |
| Formation-center path-average rate | `81.485 px/s` |
| Formation-center median step rate | `62.585 px/s` |

Three-subcluster geometry summary for supported rows:

| Metric | Median | Note |
|---|---:|---|
| Left-right spacing | `47.162 px` | Scale-dependent image-plane width; mean `41.240`, stdev `15.367`, CV `0.373`. |
| Left-middle / middle-right ratio | `1.059` | Scale-normalized spacing ratio; mean `1.115`, stdev `0.296`, CV `0.265`. |
| Formation angle | `1.149 deg` | Image-plane left-to-right axis; broad outliers due thresholding, reticle proximity, and changing apparent shape. |
| Middle offset from left-right axis | `6.675 px` | Proxy for how far the middle subcluster sits off the left-right line. |

Overlay relation:

| Relation to colored overlay | Count |
|---|---:|
| Separate from colored overlay | 58 |
| Near colored overlay | 59 |
| Intersects colored overlay | 3 |

## Interpretation

The local PR47 review supports the DVIDS visual description at image-plane level. From about `9s` through the end of the clip, the public MP4 repeatedly shows a compact bright three-lobed/three-contrast-area cluster near the sensor reticle. The three-subcluster proxy is present in `110/120` one-fps samples and in all high-or-medium supported samples.

The pass does not prove that the three visual areas are three independent objects. It also does not establish physical spacing, speed, range, altitude, platform motion, or target coordinates. Pixel motion is dominated by sensor tracking, reticle-relative motion, and possible zoom/field-of-view behavior.

PR47 should be treated as:

- Hard public-release identity: `DOD_111689142.mp4` = `DOW-UAP-PR47`.
- Strong standalone video evidence for a persistent three-area visual formation.
- No hard local `D` report pairing.
- No independent physical kinematic conclusion.

## Next Work

The next best standalone target is PR45 (`DOD_111689123.mp4`), because it is a different visual lane: apparent size increase/exit-frame behavior rather than PR44's point return or PR47's three-area formation.

