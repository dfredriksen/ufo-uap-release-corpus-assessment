# UFO Video High-Rate Notes: DOD_111688964

Owner: Dan Fredriksen
Created: 2026-05-09
Source files: official public UFO/UAP release files, not redistributed in this repository
Source video: `DOD_111688964.mp4`
Status: Full-clip high-rate review

## Method

The full 21.8-second clip was extracted at 5 fps using center crops. This produced 109 derived frames and two contact sheets.

Generated files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-high-rate-review-dod111688964.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111688964-fps5.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111688964.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-full-frame-stills-dod111688964.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-ffmpeg-metadata-dod111688964.txt`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/high-rate/DOD_111688964/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/full-frame-stills/DOD_111688964/*`

No source files in `source-files-not-included` were modified.

## Visual Result

`DOD_111688964.mp4` is strengthened by the high-rate review. The clip shows a persistent bright object over a water-like background for essentially the full useful sequence. The object moves relative to the reticle/camera field, and sensor symbology repeatedly appears around or near it.

The visual evidence is stronger than `DOD_111689090.mp4` because the object is not just an intermittent faint speck. It remains visible through the high-rate sheets and appears in relation to changing track-box symbology.

## Caveats

The clip is short. It does not expose readable date-time, coordinates, platform, or report ID in the derived sheets reviewed so far.

An automated bright-blob position table was generated, but it is not reliable enough to use as the primary track table because the water background contains many bright wave highlights. Treat `ufo-video-object-position-dod111688964-fps5.csv` as a preliminary audit artifact, not a final object track.

## Manual Track

A conservative manual track was added using 21 selected frames at roughly one-second intervals from the 5 fps center-crop sequence. Coordinates are approximate and use the 960x540 center-crop frame, with `(480,270)` as the reticle-center reference.

The selected-frame track shows the object moving substantially relative to the reticle:

- At about `1.0s`, the object is near the upper-left edge of the center crop.
- By `3.0s`, it is near the upper-right.
- Between about `5.0s` and `9.0s`, it remains right/lower-right of the reticle while the track box shifts.
- Around `10.0s`, orange tracking symbology appears around the object near the lower field.
- Around `13.0s`, the object is inside or immediately adjacent to the green track box near the reticle.
- From about `16.0s` to `19.0s`, the object is left/lower-left of the reticle and orange tracking symbology again appears around it.

This supports the visual interpretation that the clip contains one persistent object being tracked/reacquired by sensor symbology, not just random water highlights.

## Full-Frame Stills

Full-frame stills were extracted for six moments where the object is close to or overlapped by tracking symbology:

| Approx second | Selected frame | Reason |
|---:|---:|---|
| `10.0` | `51` | Orange tracking box around object near lower field. |
| `13.0` | `66` | Green track box overlays object near reticle. |
| `14.0` | `71` | Object sits on/near box edge. |
| `19.0` | `96` | Orange tracking box around object left of reticle. |
| `20.0` | `101` | Orange tracking box inside green reticle box. |
| `21.0` | `106` | Object near track-box edge. |

The full-frame stills preserve wider sensor context but do not reveal date-time, coordinates, platform, report number, or other hard-link metadata.

## Correlation Assessment

Current best lane: official `DOW-UAP-PR29` media, with the written-report content matching local/War.gov `DoW-UAP-D27` and the DVIDS `DoW-UAP-D8` label remaining a source discrepancy.

DVIDS identifies `DOD_111688964.mp4` as `DOW-UAP-PR29`, United Arab Emirates, June 2024, and states that the accompanying mission report is `DoW-UAP-D8`. DVIDS describes the video as a 21-second infrared clip and summarizes the report as an object with a vertical pole/bar attached to the bottom, with the observer noting that it may instead be a reflection from an object in water.

This supersedes the earlier evidence-lane-only guess that the clip might belong with local `d38`, `d44`, or `d57` single-object range-fouler reports. It is a hard external release identity for the MP4. The cleanest written-report reconciliation is now local/War.gov `D27`, not local/War.gov `D8`.

## Packaging Link Check

A targeted external lookup found the DVIDS pairing above. A local/War.gov search finds that `dow-uap-d8-mission-report-djibouti-2025.pdf` describes two round white-hot UAPs moving south near Djibouti in 2025. That does not match the DVIDS `PR29` / UAE June 2024 description.

Local/War.gov `dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf` does match the DVIDS `PR29` written-report summary: one over-water object with vertical pole/bar or possible reflection language, about 140 knots, with initial contact at `070457:00ZJUN24`.

Treat DVIDS as authoritative for the MP4 identity, treat `D27` as the written-report content match, and keep the DVIDS `D8` accompanying-report label as an official-source discrepancy unless corrected.

Dedicated reconciliation note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d8-d27-reconciliation.md`

Dedicated visual alignment note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-visual-alignment.md`

Dedicated dense marking note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-dense-marking-notes.md`

## Dense Marking Pass

A 2026-05-10 dense pass sampled `1.0s` through `21.0s` at 5 fps and generated 101 object/track-box review rows. It found 62 high-confidence, 35 medium-confidence, and 4 low-confidence marks.

The dense pass strengthens the visual-summary alignment to PR29/D27: the object remains trackable through almost the full reviewed interval, shows repeated short downward/vertical bright structure in zoom patches, and is inside/intersecting/near colored track-box symbology in 40 samples.

Generated files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr29_dense_marking_pass.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-track-dod111688964.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-track-dod111688964-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-marking-assets-dod111688964.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111688964/*`

This is still an audit track, not a final speed/trajectory product.

## Source MP4 Metadata

FFmpeg container metadata for the source MP4 shows:

- `creation_time`: `2026-05-08T00:20:50.000000Z`
- video codec: H.264, 1920x1080, 30 fps
- encoder: `Elemental H.264`
- duration: 21.8 seconds

This appears to be file/transcode metadata rather than incident metadata.

## Next Best Work

1. Watch for any official correction to the PR29 `D8` label.
2. Keep `DOD_111689030.mp4` / `D38` as the hard report-video anchor; treat `DOD_111688964.mp4` / `PR29` / `D27` as the strongest second visual-report lane, with label caveat.
3. If more PR29 source material appears, look specifically for telemetry, FOV/zoom state, slant range, or platform/gimbal data. The current speed-geometry note keeps `140 knots` report-derived.
