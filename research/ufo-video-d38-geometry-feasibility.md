# UFO D38 Motion-Geometry Feasibility

Owner: Dan Fredriksen
Created: 2026-05-10
Scope: `DOD_111689030.mp4`, DVIDS `PR36`, local/War.gov `DoW-UAP-D38`, and the validated `50s-87s` interval
Status: Geometry feasibility, not real-world speed estimate

## Bottom Line

The D38 dense pass provides a strong image-plane track, but it still cannot recover real-world speed or trajectory without sensor geometry. The missing pieces are sensor field of view or zoom state, slant range, platform motion, gimbal pointing, and frame-level telemetry.

This is especially important because the validated interval crosses the DVIDS `01:16` zoom/narrow-field event. The `50s-75s` primary interval and the `76s-87s` post-zoom interval should be analyzed separately unless the zoom/FOV change is known.

## Report And Release Context

DVIDS `PR36` identifies `DOD_111689030.mp4` and states that the accompanying Range Fouler report is `DoW-UAP-D38`. The DVIDS page describes a two-minute, 17-second IR video and says the report described a solid white object making erratic movements above water.

The local D38 report text says the crew temporarily lost and reacquired the object, followed it as it appeared to make erratic movements above the water, obtained `4x` zoom, and then lost the object due to poor track placement.

Unlike PR29/D27, D38 does not give a clean target-speed value to test. The geometry question here is whether the image-plane motion can be converted into real-world motion. With the current public MP4, it cannot.

## Image-Plane Motion

| Track | Duration | Net rate | Path-average rate | Median step rate |
|---|---:|---:|---:|---:|
| Dense full validated interval, `50s-87s` | `37.0s` | `3.0 px/s` | `85.0 px/s` | `54.3 px/s` |
| Dense primary interval, `50s-75s` | `25.0s` | `8.7 px/s` | `72.4 px/s` | `48.3 px/s` |
| Dense post-zoom interval, `76s-87s` | `11.0s` | `9.5 px/s` | `97.1 px/s` | `81.6 px/s` |
| Manual full validated interval, `50s-87s` | `37.0s` | `3.0 px/s` | `80.4 px/s` | `52.9 px/s` |
| Manual primary interval, `50s-75s` | `25.0s` | `8.7 px/s` | `67.7 px/s` | `42.0 px/s` |
| Manual post-zoom interval, `76s-87s` | `11.0s` | `9.6 px/s` | `92.6 px/s` | `81.0 px/s` |

The full-interval net rate is not a useful speed proxy because the object's path curls back through the frame and the interval crosses a zoom change. The phase-specific median step rates are better audit measures, but they are still image-plane rates.

## Scenario Examples

The scenario table asks what real-world speed would be implied under assumed full-frame horizontal FOV and slant range values. These are illustrative only.

Using the dense median step rate:

| Phase | Pixel rate | Assumed HFOV | 5 nm | 10 nm | 20 nm |
|---|---:|---:|---:|---:|---:|
| Primary `50s-75s` | `48.3 px/s` | `4 deg` | `31.6 kt` | `63.2 kt` | `126.3 kt` |
| Post-zoom `76s-87s` | `81.6 px/s` | `4 deg` | `53.4 kt` | `106.8 kt` | `213.7 kt` |

Changing assumed FOV or range changes the implied speed proportionally. That sensitivity is why the public MP4 alone is insufficient for a real-world speed estimate.

Full tables:

- `research/ufo-video-d38-geometry-feasibility-summary.csv`
- `research/ufo-video-d38-geometry-feasibility-scenarios.csv`

## What Would Be Needed

To convert the dense D38 track into a real-world motion estimate, we would need at least one credible geometry path:

- Sensor FOV or zoom state by frame, especially across `01:16`.
- Slant range or range-to-target.
- Platform position, altitude, attitude, and velocity.
- Gimbal pointing, stabilization mode, and sensor-line-of-sight data.
- Original mission-system file or telemetry-bearing export, not only the public MP4 transcode.
- Unredacted target coordinates with timing precise enough to compare against video frames.

## Assessment

The dense D38 track is strong evidence for report-video correlation and phase alignment. It is not enough for real-world speed or trajectory reconstruction.

D38 should remain the corpus gold-standard anchor, but its kinematic claims should stay limited to image-plane motion unless source telemetry appears.

