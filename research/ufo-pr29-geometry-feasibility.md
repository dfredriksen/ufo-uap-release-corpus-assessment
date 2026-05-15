# UFO PR29 / D27 Speed-Geometry Feasibility

Owner: Dan Fredriksen
Created: 2026-05-10
Scope: `DOD_111688964.mp4`, DVIDS `PR29`, local/War.gov `D27`, and the reported `140 knots` value
Status: Feasibility analysis, not speed validation

## Bottom Line

The dense video track can measure image-plane motion, but it cannot independently validate the `140 knots` value in the D27 report. The missing pieces are slant range, sensor field of view or zoom state, platform motion, sensor pointing/stabilization data, and target geolocation.

The video does not falsify `140 knots`. It shows image motion that could correspond to `140 knots` under many plausible FOV/range combinations. But the same pixel motion can imply very different real-world speeds if the object is near/far, if the sensor is zoomed/narrow/wide, or if platform and gimbal motion dominate the image-plane displacement.

## Report Values

The local/War.gov `D27` report text gives these relevant values:

- UAP maneuverability observation: straight flight just over water at `140 knots`.
- Kinetic velocity: `140 knots`, marked estimated.
- Friendly aircraft altitude: `23,999 ft`.
- Friendly aircraft speed: `163 knots`.
- UAP date of DoD acquisition: `070457:00ZJUN24`.
- Description: glowing hot spherical object with a vertical cylindrical pole/bar attached to the bottom, possibly a reflection from the object in water.

These values are report-derived. The reviewed MP4 does not expose enough visible overlay or metadata to independently recover them.

## Video-Derived Measurements

The dense review and one-second control track agree at the rough image-plane level.

| Track | Samples | Duration | Net displacement | Net rate | Path-average rate | Median step rate |
|---|---:|---:|---:|---:|---:|---:|
| Dense 5 fps audit track | `101` | `20.0s` | `431.7 px` | `21.6 px/s` | `159.2 px/s` | `124.4 px/s` |
| Manual 1 fps control track | `21` | `20.0s` | `383.3 px` | `19.2 px/s` | `135.6 px/s` | `122.8 px/s` |

The net rate is the simplest start-to-end image-plane rate. The path-average and step-rate figures are much larger because the object moves around the frame and the sensor/track symbology changes. Those larger values should not be treated as real-world target velocity.

## Geometry Formula

For a rough angular-rate estimate:

`angular_rate_rad_s = pixel_rate_px_s * (horizontal_FOV_rad / 1920)`

For a target speed assumption:

`slant_range_m = target_speed_m_s / angular_rate_rad_s`

This assumes the full 1920-pixel source width corresponds to the stated horizontal FOV and that all image-plane motion is target angular motion. Those assumptions are not established for this clip.

`140 knots` is approximately `72.0 m/s`.

## Scenario Results

The table below asks: if the image motion represented `140 knots`, what slant range would be implied under different assumed full-frame horizontal FOV values?

| Track / rate basis | Pixel rate | 1 deg HFOV | 2 deg HFOV | 4 deg HFOV | 8 deg HFOV | 10 deg HFOV |
|---|---:|---:|---:|---:|---:|---:|
| Dense net rate | `21.6 px/s` | `198.2 nm` | `99.1 nm` | `49.5 nm` | `24.8 nm` | `19.8 nm` |
| Dense median step rate | `124.4 px/s` | `34.4 nm` | `17.2 nm` | `8.6 nm` | `4.3 nm` | `3.4 nm` |
| Manual net rate | `19.2 px/s` | `223.2 nm` | `111.6 nm` | `55.8 nm` | `27.9 nm` | `22.3 nm` |
| Manual median step rate | `122.8 px/s` | `34.8 nm` | `17.4 nm` | `8.7 nm` | `4.4 nm` | `3.5 nm` |

This is the core reason the speed cannot be resolved from the MP4 alone. A narrow FOV or use of net displacement pushes the implied range outward. A wider FOV or use of local step motion pushes the implied range inward. Without actual sensor FOV and range, both families of answers are just scenarios.

Full scenario table: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility-scenarios.csv`

## What Would Be Needed To Test `140 Knots`

To validate or challenge the report speed, at least one of these evidence paths is needed:

- Sensor metadata with FOV or zoom state for the PR29 clip.
- Slant range or range-to-target from the platform/sensor system.
- Platform position, altitude, velocity, attitude, and gimbal pointing by frame.
- Unredacted or precise first/last target coordinates with reliable timestamps.
- A stabilized line-of-sight reconstruction against known sea-surface/background geometry.
- Any original mission-system file with frame-level telemetry rather than the public MP4 transcode.

## Assessment

The current evidence supports this statement:

`DOD_111688964.mp4` visually supports the PR29/D27 object-description lane and provides a strong image-plane track, but it does not independently verify the D27 report's `140 knots` estimate.

The speed claim should remain report-derived unless better geometry or source telemetry appears.
