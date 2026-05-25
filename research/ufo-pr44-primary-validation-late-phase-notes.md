# PR44 Primary Validation And Late Phase Review

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `I:\My Drive\UFO\DOD_111689115.mp4`
Release identity: `DOW-UAP-PR44`

## Scope

This is a follow-on to `research/ufo-pr44-standalone-quant-notes.md`.

It does two things:

- Validates the weaker `154.0s-204.8s` primary-interval rows from the dense seeded audit.
- Reviews `244s-294s` qualitatively against the DVIDS reticle-cycling, zoom-out, and loss/exit narrative.

This remains a standalone PR44 video analysis. It does not create a local `D44`, `D57`, or `D58` report pairing.

## Primary Visual Validation

Script:

- `scripts/ufo_pr44_primary_visual_validation.py`

Outputs:

- `research/ufo-video-pr44-primary-visual-validation-dod111689115.csv`
- `research/ufo-video-pr44-primary-visual-validation-summary.csv`
- `research/ufo-video-pr44-primary-visual-validation-assets.csv`
- `research/ufo-derived/video-motion-pass/pr44-primary-validation/DOD_111689115/*`

The validation pass reviewed all `255` dense rows from `154.0s-204.8s`. It preserved the dense mark, searched a larger local window for a compact low-saturation bright candidate, and generated annotated sheets that show the dense mark versus the validation mark.

| Result | Count |
|---|---:|
| High visual quality | 121 |
| Medium visual quality | 83 |
| Low visual quality | 51 |
| High or medium total | 204 |

Status split:

| Validation status | Count |
|---|---:|
| Confirmed dense mark | 163 |
| Confirmed near dense mark | 39 |
| Recentered visual candidate | 2 |
| Weak visual candidate | 15 |
| Unconfirmed seed or dense mark | 36 |

The previous dense audit had only `127/255` high-or-medium rows in this primary interval. The validation pass raises the visually supported subset to `204/255`, while keeping `51` rows low.

The remaining low rows are concentrated around `181s-199s`, especially `192s-198s`, where the apparent target is close to reticle/overlay graphics and dark-field texture. Those rows should stay conservative rather than be used as independent tracking evidence.

Image-plane rates remain similar to the dense pass:

| Track | Samples | Time range | Path length | Path-average rate | Median step rate | P95 step rate |
|---|---:|---|---:|---:|---:|---:|
| All primary validation rows | 255 | `154.0s-204.8s` | `1918.801 px` | `37.772 px/s` | `33.459 px/s` | `81.002 px/s` |
| High/medium validation rows only | 204 | `154.4s-204.8s` | `1716.456 px` | `34.057 px/s` | `33.634 px/s` | `81.056 px/s` |

## Late Phase Review

Script:

- `scripts/ufo_pr44_late_phase_review.py`

Outputs:

- `research/ufo-video-pr44-late-phase-review-dod111689115.csv`
- `research/ufo-video-pr44-late-phase-review-summary.csv`
- `research/ufo-video-pr44-late-phase-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr44-late-phase-review/DOD_111689115/*`

The late-phase review sampled `244s-294s` at one frame per second using the existing conservative one-fps compact-return table as a seed source.

| Phase | Samples | Conservative compact-return detections |
|---|---:|---:|
| Reticle-cycling tail, `244s-263s` | 20 | 8 |
| Zoom-out continued-track interval, `264s-290s` | 27 | 18 |
| Loss/exit interval, `291s-294s` | 4 | 0 |
| Total | 51 | 26 |

Seed confidence split:

| Seed confidence | Count |
|---|---:|
| High | 21 |
| Medium | 1 |
| Low | 4 |
| None | 25 |

This supports the DVIDS phase narrative at a qualitative level: after the dense `154s-243s` track, compact returns become intermittent, continue through much of the zoom-out interval, and are not conservatively detected in the `291s-294s` loss/exit window.

It does not support a continuous late-phase dense track. The late marks should be treated as intermittent visual support for tracking/loss behavior, not as a kinematic sequence.

## Updated PR44 Judgment

`DOD_111689115.mp4` is now strong as a standalone PR44 video case:

- The `154.0s-243.0s` dense seeded audit supports sustained compact-return behavior.
- The follow-on validation confirms most of the weaker primary interval: `204/255` rows are high or medium visual quality.
- The `244s-294s` qualitative review supports the DVIDS zoom-out and loss/exit narrative at scene level.

The caveats remain decisive:

- No DVIDS-stated written report accompanies PR44.
- No source currently links this clip to local `D44`, `D57`, or `D58`.
- No public MP4 data provides speed, range, altitude, platform motion, FOV, target coordinates, or a hard event timestamp.
- Physical kinematics remain unavailable from this release alone.

## Next Work

PR44 is now reasonably complete as a standalone public-release video review. Remaining PR44 work would be marginal: hand-clicking the ambiguous `181s-199s` rows or reviewing the earlier intermittent `123s-153s` pre-primary returns.

The better next corpus target is a new standalone clip with distinct evidentiary value, especially PR45 (`DOD_111689123.mp4`) or PR47 (`DOD_111689142.mp4`).

