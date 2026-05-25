# PR40 Top-Third Small Thermal Signature Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111689082.mp4`
Release identity: `DOW-UAP-PR40`
DVIDS URL: `https://www.dvidshub.net/video/1006093/dow-uap-pr40-unresolved-uap-report-middle-east-2020`

## Scope

DVIDS identifies `DOD_111689082.mp4` as `DOW-UAP-PR40`, Middle East, 2020. The page describes a 63-second infrared-sensor clip in which an area of contrast brightens, the reporter pauses playback and adds a white circle/arrow annotation for a small thermal signature, and then playback resumes while the sensor pans with contrast and zoom cycling.

This review tests whether the public MP4 supports that visual description at image-plane level. It does not test object identity, physical size, range, speed, altitude, trajectory, or whether the later compact contrast candidates all represent the same object.

## Source Handling

The local Google Drive path existed at `I:\My Drive\UFO\DOD_111689082.mp4`, but OpenCV could not decode that cloud-backed file during this pass and `ffprobe` returned a local cache-space error. To keep the analysis repeatable, the script falls back to an exact DVIDS source copy stored under ignored derived media:

- `research/ufo-derived/video-motion-pass/pr40-top-third-review/source/DOD_111689082.mp4`

That fallback copy is not tracked in Git. It matches the release-index size for `DOD_111689082.mp4`: `29,392,078` bytes.

## Method

Script:

- `scripts/ufo_pr40_top_third_review.py`

Outputs:

- `research/ufo-video-pr40-top-third-review-dod111689082.csv`
- `research/ufo-video-pr40-top-third-review-summary.csv`
- `research/ufo-video-pr40-top-third-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr40-top-third-review/DOD_111689082/*`

The script samples the full clip at `1 fps`. It uses three phase lanes:

- `00:00-00:09`: compact local-contrast candidates near the later annotation area.
- `00:10-00:14`: annotation-guided crop inside the reporter's circled area, capped at medium support because the image is paused and overlaid.
- `00:15-01:03`: compact bright-or-dark local-contrast candidates in the unobscured top-third lane, with fixed redaction blocks, cyan/green symbology, and local black/white contamination suppressed.

The post-resume detections are candidate-level evidence. They are useful for checking the DVIDS top-third visual description, but the detector does not prove all selected candidates are the same physical object.

## Results

The source MP4 used by the script is `1920x1080`, `30 fps`, `1896` frames, and `63.200s`.

One-fps full review:

| Review quality | Count |
|---|---:|
| High | `10` |
| Medium | `21` |
| Low | `22` |
| None | `11` |
| High or medium | `31` |

Supported intervals:

- Overall high-or-medium: `0.0s`; `3.0s`; `5.0s-15.0s`; `17.0s-22.0s`; `31.0s`; `36.0s`; `38.0s-40.0s`; `48.0s-50.0s`; `52.0s`; `54.0s`; `60.0s-61.0s`.
- Annotation-guided: `10.0s-14.0s`.
- Post-resume top-third candidates: `15.0s`; `17.0s-22.0s`; `31.0s`; `36.0s`; `38.0s-40.0s`; `48.0s-50.0s`; `52.0s`; `54.0s`; `60.0s-61.0s`.

Supported rows by DVIDS phase:

| Phase | Supported rows |
|---|---:|
| Initial brightening | `7` |
| Reporter annotation pause | `5` |
| Post-annotation top-third tracking | `19` |

Selected candidate summary:

| Metric | Median | Note |
|---|---:|---|
| Component area | `54.0 px` | Mean `55.484`, stdev `31.280`, CV `0.564`. |
| Absolute contrast delta | `34.0 luma` | Local contrast against median background. |
| Distance from central reticle | `251.22 px` | Mean `298.368`, stdev `160.188`. |
| Distance from annotation focus | `186.56 px` | Mean `194.183`, stdev `141.745`. |
| Post-resume candidate y | `377.0 px` | Top-third proxy threshold was `500.0 px`. |

The post-resume compact-candidate path has `19` supported rows from `15.0s-61.0s`, net displacement `211.035 px`, path length `2670.876 px`, path-rate proxy `58.063 px/s`, and median one-second step rate `39.140 px/s`.

Those path values are for selected visual candidates only. They should not be interpreted as a continuous physical object track.

## Interpretation

PR40 supports the DVIDS visual description in a narrower way than PR48, PR49, or PR38. The release identity is hard, the reporter annotation is visible and measurable, and compact contrast candidates recur in the upper display lane after playback resumes.

The support is intermittent and texture-confounded. Several post-resume rows are low or none because cloud/terrain texture, contrast cycling, and zoom changes make the small target hard to distinguish. The later candidate path should therefore be treated as a top-third compact-contrast audit, not a solved target track.

PR40 should be treated as:

- Hard public-release identity: `DOD_111689082.mp4` = `DOW-UAP-PR40`.
- Moderate standalone visual support for the DVIDS small-thermal-signature / top-third tracking description.
- No local `D` report pairing.
- No physical size, range, speed, altitude, trajectory, object identity, or continuous-object conclusion without source telemetry and sensor context.

## Next Work

PR40 is now reviewed enough for the standalone-release matrix. Later passes reviewed the previously index-only lanes including `PR26`, `PR37`, `PR39`, `PR46`, and the `PR31-PR33` / `D32` control set.

