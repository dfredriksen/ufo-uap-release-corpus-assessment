# UFO PR29 / D27 Dense Marking Notes

Owner: Dan Fredriksen
Created: 2026-05-10
Scope: Dense review of `DOD_111688964.mp4` from `1.0s` through `21.0s`
Status: Dense audit track, not final kinematics

## Bottom Line

The dense pass strengthens `DOD_111688964.mp4` as the PR29 visual lane and the local/War.gov `D27` report-content match. Across 101 samples at 5 fps, the object/contrast feature remains trackable in 97 medium-or-high confidence samples, with only 4 low-confidence samples.

The pass also strengthens the visual-summary alignment to the D27 language: the object repeatedly shows a short downward/vertical bright feature in zoom patches, and it interacts with colored track-box symbology in 40 of 101 samples. This supports the "vertical pole/bar or possible reflection" description at the video-review level.

It still does not prove the report's 140-knot speed, altitude, exact event timing, or whether the vertical feature is a physical object feature versus a reflection or sensor/video artifact.

## Method

The script `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr29_dense_marking_pass.py` sampled the source video at 5 fps from `1.0s` through `21.0s`. It used the existing one-second manual track as control points, interpolated between those marks, and then refined each intermediate sample using a local bright-feature search around the predicted point.

This is a dense audit track. It is more rigorous than the earlier one-second hand table, but it is not a final hand-click kinematic measurement.

Generated artifacts:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-track-dod111688964.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-track-dod111688964-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-marking-assets-dod111688964.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111688964/annotated-crops/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111688964/object-zoom-patches/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111688964/sheets/*`

No source files under `source-files-not-included` were modified.

## Results

| Metric | Result |
|---|---:|
| Dense samples | `101` |
| High-confidence samples | `62` |
| Medium-confidence samples | `35` |
| Low-confidence samples | `4` |
| Non-`no` vertical-feature flags | `95` |
| Colored track-box relation: inside/intersects/near | `40` |
| Manual-control mean delta | `13.53 px` |
| Manual-control max delta | `32.76 px` |

Object position in the 960x540 center crop spans approximately:

- `x`: `77.2` to `801.1`
- `y`: `94.6` to `500.9`
- start of dense interval: `77.2, 94.6`
- end of dense interval: `469.4, 275.0`

This large image-plane displacement is why the clip is useful as a visual anchor. It is not enough by itself to infer real-world speed without platform motion, slant range, sensor geometry, and timing context.

## Low-Confidence Samples

| Approx second | Reason for caution |
|---:|---|
| `8.4` | Object/contrast feature is faint against water texture. |
| `8.6` | Object/contrast feature is faint and local refinement is less stable. |
| `10.4` | Object is near/intersecting orange track symbology. |
| `10.6` | Object is low in the field and partly confused with nearby symbology/background. |

## Interpretation

The dense pass supports three limited claims:

1. The clip contains a persistent bright object/contrast feature over water-like texture.
2. The feature repeatedly aligns with, enters, or is bracketed by colored sensor track-box symbology.
3. A downward/vertical bright feature is visible often enough that the D27/PR29 pole-bar/reflection description is visually plausible.

The dense pass does not support stronger claims about anomalous performance, origin, or physical structure.

## Next Step

Completed next step: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility.md`

That note keeps the `140 knots` value report-derived. The dense track gives image-plane motion, but speed validation still requires platform motion, slant range, sensor field of view, and frame-level telemetry or equivalent geometry.
