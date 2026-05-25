# PR44 Standalone Quantitative Pass

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `I:\My Drive\UFO\DOD_111689115.mp4`
Release identity: `DOW-UAP-PR44`

## Scope

This pass treats `DOD_111689115.mp4` as a standalone public-release video, not as a specific local `D` report match.

DVIDS identifies the clip as `DOW-UAP-PR44`, Middle East, 2020. The DVIDS page also states that the reporter did not provide an oral or written description, so this should not be called local `DoW-UAP-D44`, `D57`, or `D58` without another source link.

## DVIDS Phase Anchor

DVIDS's public phase narrative gives the usable timing frame:

| Time range | DVIDS-described content | Treatment here |
|---|---|---|
| `00:00-00:30` | No UAP-related content. | Excluded. |
| `00:31-03:24` | Sensor focuses on and tracks an area of contrast in the center of the field of view. | Broad tracking context. |
| `03:25-04:23` | Multiple reticles indicate tracking through changing field of view. | Reticle-cycling context. |
| `04:24-04:50` | Sensor zooms out and continues tracking. | Follow-on qualitative review completed. |
| `04:50-04:54` | Sensor stops tracking as the object exits the field of view. | Follow-on qualitative review completed. |
| `04:55-05:11` | No UAP-related content. | Excluded. |

The dense pass below focuses on the strongest local one-fps seed interval, `154.0s-243.0s`, which straddles the end of DVIDS's `00:31-03:24` tracking interval and most of the `03:25-04:23` reticle-cycling interval.

## Method

Script:

- `scripts/ufo_pr44_standalone_quant_pass.py`

Inputs:

- `research/ufo-video-object-position-dod111689115.csv`
- `I:\My Drive\UFO\DOD_111689115.mp4`

Outputs:

- `research/ufo-video-pr44-dense-track-dod111689115.csv`
- `research/ufo-video-pr44-dense-track-summary.csv`
- `research/ufo-video-pr44-dense-track-assets.csv`
- `research/ufo-derived/video-motion-pass/pr44-standalone/DOD_111689115/*`

The script sampled `154.0s-243.0s` at `5 fps`, using the prior one-fps compact-return marks as seeds. For each dense sample, it interpolated the expected seed position and attempted local compact-bright refinement inside the center crop. Rows therefore fall into two classes:

| Marking basis | Count |
|---|---:|
| Interpolated one-fps seed plus local compact-bright refinement | 320 |
| Interpolated one-fps seed only; local compact-bright refinement failed | 126 |

This is a seeded dense audit, not an independent hand-clicked track.

## Results

The dense table contains `446` samples across `89.0s`.

| Track | Samples | Time range | Net displacement | Net rate | Path length | Path-average rate | Median step rate | P95 step rate |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Primary plus reticle | 446 | `154.0s-243.0s` | `256.427 px` | `2.881 px/s` | `3651.620 px` | `41.029 px/s` | `36.418 px/s` | `83.860 px/s` |
| Primary interval | 255 | `154.0s-204.8s` | `231.282 px` | `4.553 px/s` | `1962.457 px` | `38.631 px/s` | `33.923 px/s` | `81.174 px/s` |
| Reticle-cycling interval | 191 | `205.0s-243.0s` | `147.368 px` | `3.878 px/s` | `1683.310 px` | `44.298 px/s` | `41.638 px/s` | `83.860 px/s` |

Confidence distribution:

| Interval | High | Medium | Low |
|---|---:|---:|---:|
| Primary `154.0s-204.8s` | 73 | 54 | 128 |
| Reticle-cycling `205.0s-243.0s` | 82 | 100 | 9 |
| Total | 155 | 154 | 137 |

Overlay relation:

| Relation to colored overlay | Count |
|---|---:|
| Separate from colored overlay | 382 |
| Near colored overlay | 58 |
| Intersects colored overlay | 6 |

The late `239.0s-243.0s` contact sheet keeps a visible compact bright return near the tracking graphics. The object is close enough to reticle/overlay symbology that the rows should be treated as image-plane visual marks, not as validated telemetry.

## Interpretation

This pass strengthens `DOD_111689115.mp4` as the best standalone visual clip in the local set. It shows a sustained compact point-return track across the strongest `154s-243s` interval, with continued visibility through the reticle-cycling phase.

It does not create a report pairing. It does not provide speed, range, altitude, platform motion, field of view, target coordinates, or a date-time group. Physical kinematics remain unavailable from the public MP4 alone.

The correct treatment is:

- Hard public-release identity: `DOD_111689115.mp4` = `DOW-UAP-PR44`.
- Strong standalone video evidence: sustained compact return and sensor-tracking behavior.
- No hard local `D` report pairing.
- No independent real-world speed or maneuver conclusion.

## Follow-On Validation

Dedicated note: `research/ufo-pr44-primary-validation-late-phase-notes.md`

The follow-on pass added:

- `scripts/ufo_pr44_primary_visual_validation.py`
- `scripts/ufo_pr44_late_phase_review.py`
- `research/ufo-video-pr44-primary-visual-validation-dod111689115.csv`
- `research/ufo-video-pr44-late-phase-review-dod111689115.csv`
- Derived artifacts under `research/ufo-derived/video-motion-pass/pr44-primary-validation/DOD_111689115/*`
- Derived artifacts under `research/ufo-derived/video-motion-pass/pr44-late-phase-review/DOD_111689115/*`

The primary validation reviewed `154.0s-204.8s` and raised the high-or-medium visual subset from `127/255` dense rows to `204/255` validation rows. The remaining `51` low rows are concentrated around `181s-199s`, where the target is hard to separate from reticle/overlay graphics and dark-field texture.

The late-phase review sampled `244s-294s` at one frame per second. It found `26/51` conservative compact-return detections: `8/20` in the reticle-cycling tail, `18/27` in the zoom-out continued-track interval, and `0/4` in the loss/exit interval.

## Next Work

PR44 is now reasonably complete as a standalone public-release video review. Remaining PR44 work would be marginal: hand-clicking the ambiguous `181s-199s` rows or reviewing the earlier intermittent `123s-153s` pre-primary returns. The better next corpus target is a new standalone clip with distinct evidentiary value, especially PR45 (`DOD_111689123.mp4`) or PR47 (`DOD_111689142.mp4`).

