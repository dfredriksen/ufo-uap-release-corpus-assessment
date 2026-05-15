# UFO Video Anchor Notes: DOD_111689030 / DoW-UAP-D38

Owner: Dan Fredriksen
Created: 2026-05-09
Updated: 2026-05-10
Source files: official public UFO/UAP release files, not redistributed in this repository
Source video: `DOD_111689030.mp4`
Status: Quantitative anchor pass complete

## Why This Matters

`DOD_111689030.mp4` is the best hard correlation anchor in the local corpus. DVIDS identifies the video as `DOW-UAP-PR36`, Middle East, May 2020, and states that the accompanying Range Fouler report is `DoW-UAP-D38`.

The local `DoW-UAP-D38` text independently describes a single solid white object making erratic movements above water during ISR/IR observation, with temporary loss, reacquisition, zoom, and eventual track loss. DVIDS describes the same broad sequence: brief entry, panning/contrast/zoom cycling, re-entry, extended in-field observation, zoom, reticle attempt, modality switch, and loss of track.

## Generated Artifacts

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_anchor_video_pass.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_manual_review_assets.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-extraction-index.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-timeline.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-manual-review-assets.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-manual-validation-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-marking-notes.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility.md`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-ffmpeg-metadata-dod111689030.txt`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111689030.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-track-dod111689030.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-track-dod111689030-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-marking-assets-dod111689030.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility-scenarios.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030-ranges.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030-fps5.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030-fps5-ranges.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/one-fps-center-crops/DOD_111689030/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/high-rate/DOD_111689030/fps5-center-crops/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/segment-sheets/DOD_111689030/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/manual-validation/DOD_111689030/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111689030/*`

No source files in `source-files-not-included` were modified.

## Source Metadata

OpenCV and FFprobe both read the MP4 successfully:

- resolution: `1920x1080`
- frame rate: `30 fps`
- frame count: `4121`
- duration: `137.366667 seconds`
- video codec: H.264

## Method

The script extracted:

- 138 one-frame-per-second center-crop samples.
- 687 five-frame-per-second center-crop samples.
- One-fps contact sheets for whole-clip visual review.
- Five-fps contact sheets for detector-active and main review windows.
- CSV tables for compact bright-candidate detections.

The detector suppresses colored overlays and looks for compact low-saturation bright components. It is an audit detector, not a final object tracker. Detector boxes are useful for finding candidate intervals but should not be treated as proof that every boxed component is the UAP.

## Main Result

The strongest quantitative anchor interval is `50s` through `87s`.

From `50s` through `75s`, which sits inside DVIDS's `00:20-01:15` generally-in-field interval:

- one-fps table: 26 samples, 24 strong and 2 medium detections
- five-fps table: 126 samples, 116 strong, 8 medium, 2 weak

From `76s` through `87s`, immediately after the DVIDS `01:16` zoom/narrow-field event:

- one-fps table: 12 samples, all strong detections
- five-fps table: 56 samples, 54 strong, 2 weak

This gives a defensible local quantitative anchor for the D38/PR36 video, especially when paired with the DVIDS release metadata and local D38 report text.

## Manual Validation

A manual review pass was completed for the `50s-87s` interval using raw one-fps crops and zoomed candidate patches.

Result:

- 38 one-second samples reviewed.
- 38 accepted as visible compact bright object/contrast candidates.
- 31 high-quality accepted points.
- 7 medium-quality accepted points.
- 0 rejected points.

The manual track file is `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111689030.csv`.

This is a manually accepted detector-centered track, not a pixel-perfect independent hand-click track. It is strong enough to treat `50s-87s` as a validated audit interval for the D38 anchor, but later kinematic work should still re-mark the object manually at higher temporal density.

## Dense Marking Pass

A 2026-05-10 dense pass sampled the validated `50s-87s` interval at 5 fps. It produced 186 samples: 148 high-confidence, 33 medium-confidence, and 5 low-confidence marks.

Phase split:

- `50.0s-75.0s`, primary sustained DVIDS in-FOV interval: 126 samples; 106 high, 17 medium, 3 low.
- `75.2s-75.8s`, zoom-transition lead-in: 4 samples; 2 medium, 2 low.
- `76.0s-87.0s`, post-zoom sustained interval: 56 samples; 42 high, 14 medium, 0 low.

The dense marks stayed very close to the one-second manual controls, with a mean control delta of `1.0 px` and max control delta of `3.17 px`.

Dedicated note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-marking-notes.md`

## Geometry Feasibility

The D38 dense track is strong image-plane evidence, but it does not recover real-world speed or trajectory. The missing geometry remains sensor FOV/zoom state, slant range, platform motion, gimbal pointing, and frame-level telemetry.

The `50s-75s` and `76s-87s` intervals should be treated separately for geometry because the DVIDS `01:16` zoom/narrow-field event falls between them.

Dedicated note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility.md`

## Phase Assessment

The extracted frames align with the DVIDS sequence:

- `0-4s`: initial maritime/over-water subject matter.
- `5s`: brief entry marker, but cluttered and low confidence locally.
- `6-18s`: sensor panning, contrast, and zoom changes.
- `19-24s`: reported re-entry interval; locally low-confidence at one-fps review.
- `25-49s`: intermittent pre-track candidates; not strong enough for quantitative anchor.
- `50-75s`: strongest sustained object/contrast interval.
- `76-87s`: post-zoom sustained interval, strong detector continuity but more water-texture caveat.
- `91-108s`: secondary detector-active interval, less stable for position tracking.
- `110-121s`: further zoom / texture-dominated interval.
- `127-134s`: blue/cyan reticle-style symbology appears; lock is not established.
- `135-137s`: modality switch / loss endpoint.

See `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-timeline.csv` for the structured phase table.

## Caveats

The detector often finds the brightest compact component, and in textured water scenes that can include wave highlights or compression artifacts. The `50-87s` window is the strongest because the candidate persists across both one-fps and five-fps sampling and visually aligns with the DVIDS-described extended observation and zoom point.

The later `91-137s` detections are useful for aligning the DVIDS zoom, reticle, and loss-of-track phases, but they are weaker for object-position claims because the field is more texture-dominated and candidate boxes jump more.

## Updated Judgment

Confidence is high that `DOD_111689030.mp4` is the video paired with `DoW-UAP-D38`.

Confidence is high that the local extraction supports the DVIDS-described timeline.

Confidence is high that the accepted one-fps coordinates and the new 5 fps dense marks represent the visible object/contrast candidate throughout `50-87s`. They should be treated as validated audit tracks, not final kinematics.
