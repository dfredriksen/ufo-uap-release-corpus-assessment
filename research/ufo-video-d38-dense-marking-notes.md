# UFO D38 Dense Marking Notes: DOD_111689030

Owner: Dan Fredriksen
Created: 2026-05-10
Scope: Dense review of the validated `50s-87s` D38 anchor interval
Status: Dense audit track, not final kinematics

## Bottom Line

The dense pass upgrades `DOD_111689030.mp4` / `DoW-UAP-D38` from a one-second manually validated audit interval to a 5 fps dense audit interval.

Across `50.0s-87.0s`, the pass produced 186 samples: 148 high confidence, 33 medium confidence, and 5 low confidence. The dense marks stay extremely close to the existing one-second accepted control points: mean control delta `1.0 px`, max control delta `3.17 px`.

This makes D38 the best current methodological anchor in the corpus. It has the cleanest report-video pairing, the clearest DVIDS phase alignment, and the strongest validated dense interval.

## Method

The script `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_dense_marking_pass.py` sampled the source video at 5 fps from `50.0s` through `87.0s`.

It used the manually accepted one-second D38 track as control points, interpolated between those points, and refined each dense sample with a local bright-feature search around the predicted full-frame coordinate.

Generated artifacts:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_dense_marking_pass.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-track-dod111689030.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-track-dod111689030-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-marking-assets-dod111689030.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111689030/*`

No source files under `source-files-not-included` were modified.

## Results

| Metric | Result |
|---|---:|
| Dense samples | `186` |
| High-confidence samples | `148` |
| Medium-confidence samples | `33` |
| Low-confidence samples | `5` |
| Manual-control mean delta | `1.0 px` |
| Manual-control max delta | `3.17 px` |
| Colored overlay intersects | `16` |
| Colored overlay near | `65` |
| Separate from colored overlay | `105` |

Phase split:

| Phase | Samples | Confidence split |
|---|---:|---|
| `50.0s-75.0s`, primary sustained DVIDS in-FOV interval | `126` | `106 high`, `17 medium`, `3 low` |
| `75.2s-75.8s`, zoom-transition lead-in | `4` | `2 medium`, `2 low` |
| `76.0s-87.0s`, post-zoom sustained interval | `56` | `42 high`, `14 medium`, `0 low` |

The five low-confidence samples occur at `50.2s`, `51.4s`, `51.6s`, `75.6s`, and `75.8s`. They are low because the object is close to colored overlay/redaction edges or the zoom-transition lead-in.

## DVIDS Phase Alignment

The dense interval maps cleanly onto the DVIDS PR36 description:

- `50.0s-75.0s`: inside the DVIDS `00:20-01:15` period where the area of contrast remains generally within the sensor field of view.
- `75.2s-75.8s`: transition immediately before the DVIDS `01:16` narrowing of field of view.
- `76.0s-87.0s`: immediately after the DVIDS `01:16` zoom/narrow-field event.

This does not cover the later `01:56` further zoom or `02:10-02:17` reticle/loss sequence. Those later segments remain phase-alignment evidence, but not the strongest position-track interval.

## Interpretation

The dense pass supports these bounded claims:

1. The D38 `50s-87s` interval contains a persistent bright object/contrast candidate.
2. The candidate remains trackable at 5 fps across both the primary in-FOV and immediate post-zoom intervals.
3. The dense marks validate the existing one-second audit track rather than contradicting it.
4. The `76s-87s` post-zoom interval remains usable, but should not be merged with `50s-75s` for geometry without accounting for the zoom/FOV change.

The dense pass does not establish object origin or real-world speed.
