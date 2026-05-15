# UFO PR29 / D27 Visual Alignment

Owner: Dan Fredriksen
Created: 2026-05-10
Scope: `DOD_111688964.mp4` visual review against DVIDS `PR29` and local/War.gov `D27`
Status: Visual-summary alignment, not full kinematic validation

## Bottom Line

The existing high-rate frame review supports using `DOD_111688964.mp4` as the visual lane for DVIDS `PR29` and the local/War.gov `D27` report-content match.

The support is bounded: the clip shows one persistent bright object/contrast feature over a water-like background, with repeated sensor track-box interaction and intermittent short downward/vertical smear. That is consistent with the PR29/D27 description of an over-water object with a vertical pole/bar or possible reflection, but the frames do not independently prove the D27 report's speed, altitude, exact event time, platform, or reflection interpretation.

## Review Inputs

- Source video: `source-files-not-included/DOD_111688964.mp4`
- Existing high-rate sheets: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/high-rate/DOD_111688964/fps5-s000-059-sheet.jpg` and `fps5-s060-109-sheet.jpg`
- Existing manual one-second track: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111688964.csv`
- Existing full-frame still index: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-full-frame-stills-dod111688964.csv`
- Reconciliation note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d8-d27-reconciliation.md`
- Dense marking note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-dense-marking-notes.md`

## Visual Findings

The manual track has 21 selected one-second samples across the 21.8-second clip. Of those samples, 18 are marked high confidence and 3 are marked medium confidence for object visibility.

The object is visible against water-like texture for essentially the full useful sequence. It moves substantially relative to the reticle and appears near, inside, or intersected by track-box symbology at multiple points.

## Dense Marking Pass

A 2026-05-10 dense pass sampled `1.0s` through `21.0s` at 5 fps, producing 101 dense samples. It found 62 high-confidence, 35 medium-confidence, and 4 low-confidence marks. The dense marks span approximately `x=77.2-801.1` and `y=94.6-500.9` in the 960x540 center crop.

The dense pass also found 40 samples where the marked feature was inside, intersecting, or near colored track-box symbology. The vertical-feature flag was `yes` or `possible` in 95 samples, which is consistent with the PR29/D27 pole-bar/reflection description but should not be treated as proof of a rigid physical appendage.

Dedicated note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-dense-marking-notes.md`

Key alignment frames:

| Approx second | Frame | Visual relation | Alignment value |
|---:|---:|---|---|
| `4` | `21` | Object visible with a short downward smear. | Supports the PR29/D27 vertical-trailing-feature description at a visual-summary level. |
| `10` | `51` | Orange tracking box around object near lower field. | Supports that the sensor/video treats the contrast feature as a tracked target. |
| `13` | `66` | Green track box overlays object near reticle. | Strong local alignment between visible object and symbology. |
| `14` | `71` | Object visible on or near the green box edge. | Continued track-box/object association. |
| `19` | `96` | Orange tracking box around object left of reticle. | Reacquisition/track-box association later in the clip. |
| `20` | `101` | Orange tracking box inside green reticle box; object partly obscured. | Consistent with DVIDS's generally centered sensor-field description. |
| `21` | `106` | Green track-box edge intersects object. | End-of-clip association persists, with reduced visibility. |

## What This Does Not Establish

- It does not prove the object was moving at 140 knots.
- It does not prove the friendly aircraft altitude, speed, location, or event DTG.
- It does not distinguish a physical object from a reflection.
- It does not resolve why DVIDS labels the accompanying report `D8` while the matching report text is in local/War.gov `D27`.

## Working Assessment

`DOD_111688964.mp4` should remain a high-priority, hard `PR29` visual item. For report-text correlation, the strongest written lane is local/War.gov `D27`, with the `D8` label discrepancy documented separately.
