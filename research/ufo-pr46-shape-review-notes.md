# PR46 Shape Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689133.mp4`
Release identity: `DOW-UAP-PR46`
DVIDS URL: `https://www.dvidshub.net/video/1006106/dow-uap-pr46-unresolved-uap-report-indopacom-2024`

## Scope

DVIDS identifies `DOD_111689133.mp4` as `DOW-UAP-PR46`, INDOPACOM, 2024. The page describes an approximately nine-second infrared video from a U.S. military platform and says the reporter did not provide an oral or written description.

DVIDS's visual description is morphology-focused rather than track-focused: the contrast area is visible for the whole video, its general body is football-shaped, and it has three radial projections: one vertical and two angled downward at roughly `45 deg` relative to the body.

This remains a standalone public-release video review. It does not create a local `D` report pairing.

## Method

Script:

- `scripts/ufo_pr46_shape_review.py`

Outputs:

- `research/ufo-video-pr46-shape-review-dod111689133.csv`
- `research/ufo-video-pr46-shape-review-summary.csv`
- `research/ufo-video-pr46-shape-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr46-shape-review/DOD_111689133/*`

The script samples the full local file at `2 fps`, suppresses colored overlays and thin reticle/line artifacts where possible, then searches the persistent central target region for a grouped high-contrast morphology proxy. The grouped proxy measures the visible elongated/football-like body and projection-like detached or merged lobes.

This is an image-processing proxy for the DVIDS visual morphology. It is not a literal object-size, object-count, aircraft-identification, range, speed, altitude, or trajectory estimate. Reticle overlap cuts through the target region throughout the clip, so the component count is useful as a repeatable segmentation diagnostic, not as a physical count of projections.

## Results

The source MP4 is `1920x1080`, `30 fps`, `296` frames, and `9.867s`.

Two-fps full-clip morphology review:

| Review quality | Count |
|---|---:|
| High | `20` |
| Medium | `0` |
| Low | `0` |
| None | `0` |
| High or medium | `20` |

Supported interval: `0.0s-9.5s`.

Supported morphology metrics:

| Metric | Median |
|---|---:|
| Aggregate target-region area | `1741.0 px` |
| Oriented aspect ratio | `1.575` |
| Component count | `13.0` |
| Projection-proxy count, capped diagnostic | `3.0` |
| Max absolute contrast | `176.0 luma` |
| Center x | `991.614 px` |
| Center y | `520.157 px` |

## Interpretation

PR46 supports the narrow DVIDS visual description at image-plane level. The target-region contrast group is visible in every two-fps sample across the full public clip, and the local patch sheet shows the same persistent elongated/football-like body with projection-like lobes despite reticle overlap.

PR46 should be treated as:

- Hard public-release identity: `DOD_111689133.mp4` = `DOW-UAP-PR46`.
- Strong standalone visual support for the DVIDS full-duration morphology description.
- No local `D` report pairing.
- No aircraft, drone, balloon, UAP-object identity, physical size, range, speed, altitude, trajectory, or platform-motion conclusion without source telemetry and sensor context.

## Next Work

PR46 is now reviewed enough for standalone-release completeness. The standalone release-index lanes that were previously index-only have focused reviews; remaining work should shift to source-label reconciliation, unmatched local `D` reports, and physical-telemetry limitations rather than another standalone completeness pass.

