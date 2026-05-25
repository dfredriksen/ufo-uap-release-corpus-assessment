# PR26 / D12 Elongated Contrast Review

Owner: Dan Fredriksen
Created: 2026-05-11
Source video: `I:\My Drive\UFO\DOD_111688816.mp4`
Release identity: `DOW-UAP-PR26`
Report identity: `DoW-UAP-D12`
DVIDS URL: `https://www.dvidshub.net/video/1006063/dow-uap-pr26-unresolved-uap-report-united-arab-emirates-october-2023`
War.gov D12 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d12-mission-report-iraq-may-2022.pdf`

## Scope

DVIDS identifies `DOD_111688816.mp4` as `DOW-UAP-PR26` and states that the accompanying mission report is `DoW-UAP-D12`. The DVIDS page says the submitted material consisted of a still image derived from a U.S. military system in 2022, with the original reporter digitally adding a red line around an area of interest before submitting it to AARO. DVIDS describes an elongated area of contrast in the top-left quarter whose intensity increases from top-left to bottom-right.

The official D12 PDF contains the same core movement language summarized by DVIDS: one UAP was observed at `2043Z` flying north to northeast and followed as long as possible; the screener could not positively identify it. The PDF title and internal timing are Iraq / May 2022, while the DVIDS PR26 page title is United Arab Emirates / October 2023. That date/location mismatch should remain explicit.

This review tests whether the public MP4 supports the visible elongated-contrast description. It does not validate the report's north-to-northeast movement, object identity, range, altitude, speed, or sensor geometry.

## Source Handling

The local Google Drive path existed at `I:\My Drive\UFO\DOD_111688816.mp4`, but OpenCV could not decode that cloud-backed file during this pass and `ffprobe` returned a local cache-space error. The script therefore falls back to an exact DVIDS source copy stored under ignored derived media:

- `research/ufo-derived/video-motion-pass/pr26-d12-image-review/source/DOD_111688816.mp4`

That fallback copy is not tracked in Git. It matches the release-index size for `DOD_111688816.mp4`: `27,493,716` bytes.

## Method

Script:

- `scripts/ufo_pr26_d12_image_review.py`

Outputs:

- `research/ufo-video-pr26-d12-image-review-dod111688816.csv`
- `research/ufo-video-pr26-d12-image-review-summary.csv`
- `research/ufo-video-pr26-d12-image-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr26-d12-image-review/DOD_111688816/*`

The script samples the full clip at `1 fps`. It searches the left/top-left sensor field for compact bright local-contrast components, suppresses fixed redaction blocks and cyan/green symbology, and records whether the selected candidate falls in the DVIDS-described left-quarter lane and has an elongation proxy.

The MP4 is not a physical-trajectory product. Sensor motion, contrast changes, and the fact that DVIDS frames this as submitted imagery mean the output should be treated as a visual-support audit, not as a motion solution.

## Results

The source MP4 used by the script is `1920x1080`, `30 fps`, `1295` frames, and `43.167s`.

One-fps full review:

| Review quality | Count |
|---|---:|
| High | `26` |
| Medium | `1` |
| Low | `1` |
| None | `16` |
| High or medium | `27` |

Supported intervals:

- `0.0s-16.0s`
- `20.0s-29.0s`

Supported rows by local review phase:

| Phase | Supported rows |
|---|---:|
| Primary visible left-field contrast | `17` |
| Intermittent left-field contrast | `10` |

Selected candidate summary:

| Metric | Median | Note |
|---|---:|---|
| Component area | `166.0 px` | Mean `168.074`, stdev `24.749`, CV `0.147`. |
| Contrast delta | `98.0 luma` | Candidate max luma minus local median. |
| Aspect ratio | `1.267` | Bounding-box elongation proxy; mean `1.271`. |
| Distance from central reticle | `560.86 px` | The target-bearing region is left of the reticle. |
| Target center x | `406.4 px` | Median selected x-position. |
| Target center y | `460.6 px` | Median selected y-position. |

The supported candidate path has `27` rows from `0.0s-29.0s`, net displacement `130.593 px`, path length `1351.590 px`, path-rate proxy `46.607 px/s`, and median one-second step rate `40.013 px/s`.

Those path values are image-plane measurements across sensor motion and should not be interpreted as physical north-to-northeast target motion.

## Interpretation

PR26 now has strong image-plane support for the narrow DVIDS visual claim: the public MP4 contains a compact, bright, elongated area of contrast in the left/top-left field for the first supported interval and recurring support through `29s`.

The clip does not solve the D12 report. It supports that the public release shows the relevant left-field contrast feature, and the D12 PDF confirms the report's one-UAP north-to-northeast language, but the public MP4 does not validate the direction, altitude, velocity, range, or object identity. The DVIDS title/date/location and D12 PDF title/date/location mismatch also remains unresolved.

PR26 should be treated as:

- Hard public-release/report identity: `DOD_111688816.mp4` = `DOW-UAP-PR26` / `DoW-UAP-D12`.
- Strong visual support for the DVIDS elongated left-field contrast description.
- Report-text support for one UAP moving north to northeast, but no physical movement validation from the public MP4.
- A date/location caveat: DVIDS PR26 title says UAE / October 2023, while the D12 PDF is Iraq / May 2022.

## Next Work

PR26 is now reviewed enough for the report-paired completeness matrix. As of the later PR19, PR21, PR22, PR23, and PR31-PR33 passes, this early report-paired group is reviewed; the `D32` lane is now treated as a glare/halo control set.

