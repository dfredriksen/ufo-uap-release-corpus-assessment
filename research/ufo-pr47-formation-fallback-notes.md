# PR47 Formation Fallback Review

Owner: Dan Fredriksen
Created: 2026-05-13
Source files: official public UFO/UAP release files, not redistributed in this repository
Status: superseded by full PR47 pass

Supersession note: this fallback review was superseded on 2026-05-13 by `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr47-formation-visual-notes.md`, after local disk space recovered enough to open and process the full MP4.

## Scope

This pass reviews `DOD_111689142.mp4`, identified in the local correlation matrix as DVIDS `DOW-UAP-PR47`, INDOPACOM, 2023.

PR47 is a standalone visual lane, not a hard-paired local `DoW-UAP-D*` report case. The analytic question is whether the public material supports the DVIDS/local description of three distinct contrast areas maintaining fixed relative positions.

## Disk/Access Blocker

The full Drive-backed MP4 could not be opened during this turn because the local filesystem reported zero free bytes and raw reads from the Drive file failed with `No space left on device`. OpenCV also could not open the MP4. Because of that, this review uses only the eight already-extracted full-frame JPGs from the earlier second-pass frame set:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0000.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0012.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0030.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0048.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0065.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0083.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0101.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/DOD_111689142/t0115.jpg`

Generated fallback files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr47_formation_visual_pass.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-fallback-frame-review-dod111689142.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-fallback-frame-summary.csv`

No source files under `source-files-not-included` were modified.

## Fallback Results

Across the eight existing frames:

| Confidence | Frames |
|---|---:|
| high | 5 |
| medium | 1 |
| low | 1 |
| none | 1 |

Six of eight sampled frames have at least partial formation support, and five have three-component high-confidence support. The three-component frames span `12s`, `30s`, `48s`, `65s`, and `115s`.

The compact three-component rows have consistent spacing at the scale visible in the fallback frames:

- `t0012`: max pair distance `49.664 px`
- `t0030`: max pair distance `61.493 px`
- `t0048`: max pair distance `42.348 px`
- `t0065`: max pair distance `60.842 px`
- `t0115`: max pair distance `48.235 px`

The fallback pass also preserves a movement trend: the cluster is high in the crop at `12s-65s`, is not conservatively recovered at `83s`, appears partially at `101s`, and is detected again as a three-component group lower in the field at `115s`.

## Interpretation

Within the limits of the already-extracted frames, PR47 has stronger standalone formation evidence than PR45. The public frames support a tight group of bright contrast areas with similar relative spacing across multiple separated samples.

This is not a physical formation-kinematics result. The fallback pass is sparse, frame-only, and reticle/overlay-confounded. It does not recover range, FOV, platform motion, zoom state, target coordinates, altitude, size, speed, or a hard `D` report pairing.

## Next Step

Free local disk space, then rerun `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr47_formation_visual_pass.py` against the full MP4 at `5 fps`. That full pass should generate dense per-frame rows and annotated formation sheets before PR47 is promoted above a fallback finding.
