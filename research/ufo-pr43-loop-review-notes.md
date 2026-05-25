# PR43 Loop-Aware Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689759.mp4`
Release identity: `DOW-UAP-PR43`
DVIDS URL: `https://www.dvidshub.net/video/1006159/dow-uap-pr43-unresolved-uap-report-africa-2025`

## Scope

DVIDS identifies `DOD_111689759.mp4` as `DOW-UAP-PR43`, Africa, 2025. The page says AFRICOM submitted two seconds of infrared sensor video from a U.S. military platform, with no oral or written reporter description.

DVIDS describes `00:00-00:02` as a small, barely distinguishable area of contrast moving from the left side of the sensor field of view to the right side and exiting from the bottom-right quarter. The page also says the public video is looped for viewing.

This remains a standalone public-release video review. It does not create a local `D` report pairing.

## Method

Script:

- `scripts/ufo_pr43_loop_review.py`

Outputs:

- `research/ufo-video-pr43-loop-review-dod111689759.csv`
- `research/ufo-video-pr43-loop-review-loop-summary.csv`
- `research/ufo-video-pr43-loop-review-summary.csv`
- `research/ufo-video-pr43-loop-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr43-loop-review/DOD_111689759/*`

The script first detects loop/reset boundaries by adjacent-frame difference peaks. It then samples the local looped file at `10 fps`, normalizes each row to a loop-relative `cycle_second`, and runs a compensated frame-difference pass for compact residuals near a DVIDS-shaped left-to-right/downward exit lane.

This is not a clean object tracker. The public clip is short, looped, and terrain-confounded, and the described area of contrast is barely distinguishable. The review therefore uses `medium` only for lane-compatible compact residuals and assigns no high-confidence rows.

## Results

The source MP4 is `1920x1080`, `29.970 fps`, `352` frames, and `11.745s`.

Loop detection:

| Loop index | Start | End | Duration |
|---:|---:|---:|---:|
| `0` | `0.000s` | `2.936s` | `2.936s` |
| `1` | `2.936s` | `5.873s` | `2.936s` |
| `2` | `5.873s` | `8.809s` | `2.936s` |
| `3` | `8.809s` | `11.612s` | `2.803s` |
| `4` | `11.612s` | `11.745s` | `0.133s` |

The local file is therefore a repeated viewing loop, not an independent `11.745s` observation. The stable reset-to-reset period is about `2.936s`; the DVIDS-stated observation remains the `00:00-00:02` segment inside each loop.

Ten-fps loop-aware review:

| Review quality | Count |
|---|---:|
| Medium | `5` |
| Low | `16` |
| None | `97` |

Primary-observation rows, defined as `cycle_second <= 2.0`, produced `5` medium rows, `3` low rows, and `74` none rows across the repeated loops. Cycle-normalized medium support clusters at `1.8s-1.9s`, near the lower-right exit portion of the DVIDS-described lane.

Cycle-normalized supported residual metrics:

| Metric | Value |
|---|---:|
| Supported cycle bins | `2` |
| Supported cycle interval | `1.8s-1.9s` |
| Median distance from expected lane | `44.620 px` |
| Median max residual | `41.564 luma` |
| Cycle-bin net displacement | `47.247 px` |

## Interpretation

PR43 is best treated as a hard public-release identity with weak standalone visual support. The loop structure is clear and reproducible, and the compensated review finds a small cluster of lane-compatible residuals near the expected lower-right exit phase. It does not recover a robust left-side-to-exit target track.

The visual result is weaker than PR41, PR44, PR45, and PR47. PR43 can support the conservative claim that the local file is the DVIDS PR43 looped Africa 2025 clip and that a faint residual appears near the described exit lane. It should not be used for object identity, speed, range, altitude, physical trajectory, or independent report matching.

PR43 should be treated as:

- Hard public-release identity: `DOD_111689759.mp4` = `DOW-UAP-PR43`.
- Looped viewing file with about `2.936s` reset-to-reset cycles and only a DVIDS-stated `2s` underlying observation.
- Weak, terrain-confounded image-plane support for the described barely distinguishable contrast area near the exit phase.
- No local `D` report pairing and no physical kinematic conclusion.

## Next Work

PR43 is now reviewed enough for index completeness. The next higher-value work is another unreviewed standalone release with a longer, less loop-confounded visual sequence, or a denser manual review of an already strong anchor if the goal shifts from completeness to physical-claim stress testing.

