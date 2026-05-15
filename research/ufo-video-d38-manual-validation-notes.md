# UFO D38 Manual Validation Notes: DOD_111689030

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `source-files-not-included/DOD_111689030.mp4`
Status: Manual validation of `50s-87s` anchor interval

## Purpose

The 2026-05-10 quantitative pass identified `50s-87s` as the strongest local audit-track interval for the hard `DOD_111689030` / `DoW-UAP-D38` report-video pair. This manual validation pass reviewed raw one-fps crops and zoomed candidate patches for that interval.

## Generated Artifacts

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_manual_review_assets.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-manual-review-assets.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111689030.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/manual-validation/DOD_111689030/raw-onefps/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/manual-validation/DOD_111689030/candidate-patches-onefps/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/manual-validation/DOD_111689030/sheets/*`

No source files in `source-files-not-included` were modified.

## Method

The review script exported:

- raw one-fps center crops from `50s` through `87s`
- zoomed candidate patches centered on the detector-derived coordinate
- contact sheets for both raw context and zoomed review

The manual track table accepts or qualifies each detector-centered coordinate after visual review. This is not blind automated detection, but it is also not a pixel-perfect independent hand-click track. It is a conservative manual acceptance pass over the detector-centered audit coordinates.

## Result

Manual validation accepted all 38 one-second samples from `50s` through `87s` as containing a visible compact bright object/contrast candidate.

Quality split:

- high: 31 samples
- medium: 7 samples
- rejected: 0 samples

Phase split:

- `50s-75s`, primary sustained DVIDS in-FOV interval: 26 accepted samples, 22 high and 4 medium.
- `76s-87s`, post-zoom sustained interval: 12 accepted samples, 9 high and 3 medium.

## Interpretation

The manual review strengthens the D38 anchor. The `50s-87s` interval is not just a detector artifact: the raw crops and zoom patches show a visible compact bright object/contrast candidate at each one-second sample.

The track is still not final kinematics. The candidate moves relative to the reticle and sensor field, but the video contains water texture, overlay elements, redactions, and zoom/contrast changes. The manual table should be used as a validated audit track, not as final speed/trajectory evidence.

## Caveats

Medium-quality points were accepted but flagged where the candidate is close to overlay/redaction edges, zoomed water texture, or partial field context.

The review does not establish object origin. It strengthens the report-video correlation and gives a defensible interval for later manual kinematic work.
