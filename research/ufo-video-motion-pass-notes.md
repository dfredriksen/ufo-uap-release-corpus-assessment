# UFO Video Motion-Pass Notes

Owner: Dan Fredriksen
Created: 2026-05-09
Source folder: `I:\My Drive\UFO`
Derived artifacts: `research/ufo-derived/video-motion-pass`
Status: Motion review of the three strongest videos

## Method

The strongest three videos from the second-pass crop review were processed into one-frame-per-second center crops and segmented contact sheets:

- `DOD_111689115.mp4`
- `DOD_111689090.mp4`
- `DOD_111688964.mp4`

Generated files:

- `research/ufo-video-motion-pass-index.csv`
- `research/ufo-video-motion-segment-sheet-index.csv`
- `research/ufo-video-object-position-dod111689115.csv`
- `research/ufo-video-object-position-dod111689115-ranges.csv`
- `research/ufo-video-source-overlay-dod111689115.csv`
- `research/ufo-video-ffmpeg-metadata-dod111689115.txt`
- `research/ufo-video-point-count-dod111689090.csv`
- `research/ufo-video-point-count-dod111689090-strong.csv`
- `research/ufo-video-point-count-dod111689090-ranges.csv`
- `research/ufo-video-point-count-dod111689090-segment-summary.csv`
- `research/ufo-video-high-rate-review-dod111689090.csv`
- `research/ufo-video-ffmpeg-metadata-dod111689090.txt`
- `research/ufo-video-high-rate-review-dod111688964.csv`
- `research/ufo-video-high-rate-notes-dod111688964.md`
- `research/ufo-video-object-position-dod111688964-fps5.csv`
- `research/ufo-video-manual-track-dod111688964.csv`
- `research/ufo-video-full-frame-stills-dod111688964.csv`
- `research/ufo-video-ffmpeg-metadata-dod111688964.txt`
- `research/ufo-derived/video-motion-pass/one-fps-center-crops/*/*.jpg`
- `research/ufo-derived/video-motion-pass/segment-sheets/*.jpg`
- `research/ufo-derived/video-motion-pass/overlay-crops/DOD_111689115/*.png`
- `research/ufo-derived/video-motion-pass/overlay-crops/DOD_111689115/*_ocr.txt`
- `research/ufo-derived/video-motion-pass/source-overlay/DOD_111689115/*`

No source files in `I:\My Drive\UFO` were modified.

## Top Result

`DOD_111689115.mp4` is now the strongest media candidate in the corpus reviewed so far. It starts with over-water vessel context and later shows persistent small bright point returns near the reticle, including boxed/range-like annotation behavior in later segments. This makes it the best evidence-lane match to the 2020 range-fouler cluster, especially the reports that describe over-water IR/radar/target-pod observations.

This is still not a hard report-to-video match. The derived frames reviewed so far do not expose a readable date-time group, report number, platform identifier, or coordinates.

Later update: after the DVIDS release-index pass, `DOD_111689030.mp4` became the hard report-video anchor for `DoW-UAP-D38`. `DOD_111689115.mp4` remains the strongest local visual clip, but should be treated as `DOW-UAP-PR44`, not as a specific local `D44` report match.

Further update: the 2026-05-10 PR44 standalone dense pass sampled `DOD_111689115.mp4` from `154.0s-243.0s` at `5 fps`. It found `446` seeded dense marks across the strongest compact-return interval, including `320` local compact-bright refinements and `126` seed-only/interpolated marks. This strengthens PR44 as standalone visual evidence while preserving the no-D-report-pairing caveat.

Follow-on update: the PR44 primary validation and late-phase review added `204/255` high-or-medium visual-quality rows in the `154.0s-204.8s` primary interval, plus `26/51` conservative compact-return detections in the `244s-294s` late review. The loss/exit interval `291s-294s` had `0/4` conservative compact-return detections.

## Per-Video Observations

| File | Motion-pass observation | Updated assessment |
|---|---|---|
| `DOD_111689115.mp4` | The first minute is mostly vessel/context. Segments `s120-179`, `s180-239`, and `s240-299` show stronger persistent point-return behavior, including small bright point(s), track/box symbology, and range-like annotation. | Strongest range-fouler media candidate. Medium-high correlation at the evidence-lane level, not at the specific-report level. |
| `DOD_111689090.mp4` | Long low-texture sensor sequence with one persistent bright point, intermittent weak secondary specks, and late vessel/scene context. | Downgraded after point-count and high-rate review. Not a clean `d56` or `d58` match without external linkage. |
| `DOD_111688964.mp4` | Short 21.8-second over-water sequence with a persistent bright object/point and repeated nearby track-box symbology. | Strengthened after high-rate review. Clean short over-water track candidate, but still lacks report-link metadata. |

## Correlation Implications

The motion pass strengthens the video pool. Later DVIDS release metadata changed the report-pairing layer, but not the core evidentiary conclusion:

- The strongest current thesis remains "official records and media contain unresolved over-water sensor events," not a stronger claim about origin.
- The best hard media-to-document linkage is now `DOD_111689030.mp4` to `DoW-UAP-D38`, established externally by DVIDS and locally supported by the 2026-05-10 quantitative pass.
- The remaining unpaired clips should still be handled by evidence lane: over-water point tracks line up with the `d44`, `d57`, and related range-fouler cluster; the `d56`/`d58` multi-contact lane remains weaker after high-rate review.
- `DOD_111689115.mp4` should receive the next detailed review because it has the clearest combination of maritime context, persistent point return, and sensor annotation behavior.
- `DOD_111688964.mp4` is now the cleaner short visual track candidate after full-clip 5 fps review.
- `DOD_111689090.mp4` should remain in the media pool but should not anchor the `d56` or `d58` interpretation unless external package metadata links it to one of those reports.

## Object-Position Pass: `DOD_111689115.mp4`

A first conservative compact-blob table was generated from the one-frame-per-second center crops. The detector looks for small balanced-white bright components and suppresses the cyan/red overlay colors. This makes it useful for a first pass, but it is not a substitute for manual track marking.

Important caveat: the detector also captures bright vessel structure in the opening context segment. Those detections are separated as `vessel/context` in the range table.

High-value grouped detections:

| Frame range | Approx seconds | Detections | Interpretation |
|---|---:|---:|---|
| `7-27` | `6-26` | 21 | Vessel/context, not target evidence. |
| `124-153` | `123-152` | 26 across three nearby groups | Intermittent post-vessel point returns. |
| `155-238` | `154-237` | 84 | Primary post-vessel point-return interval. |
| `240-244` | `239-243` | 5 | Continuation near the boxed/range-annotated segment. |
| `252-285` | `251-284` | 22 across several groups | Late intermittent point returns. |

This supports the visual assessment that `DOD_111689115.mp4` is not just a single isolated frame artifact. At one-frame-per-second sampling, compact bright returns recur for a sustained post-vessel interval, with the strongest interval running from about second 154 through second 243.

## PR44 Dense Quantitative Pass: `DOD_111689115.mp4`

A seeded dense audit was added for the strongest PR44 interval, `154.0s-243.0s`, at `5 fps`.

Generated files:

- `scripts/ufo_pr44_standalone_quant_pass.py`
- `research/ufo-pr44-standalone-quant-notes.md`
- `research/ufo-video-pr44-dense-track-dod111689115.csv`
- `research/ufo-video-pr44-dense-track-summary.csv`
- `research/ufo-video-pr44-dense-track-assets.csv`
- `research/ufo-derived/video-motion-pass/pr44-standalone/DOD_111689115/*`

The dense pass produced `446` rows across `89.0s`, with `155 high`, `154 medium`, and `137 low` confidence. The full interval has path length `3651.620 px`, path-average rate `41.029 px/s`, median step rate `36.418 px/s`, and p95 step rate `83.860 px/s`.

The reticle-cycling segment, `205.0s-243.0s`, is the cleaner portion: `82 high`, `100 medium`, and `9 low` rows. The earlier `154.0s-204.8s` segment contains more low-confidence and seed-only marks, so it is the better target for hand validation.

Interpretation: `DOD_111689115.mp4` is now stronger as a standalone sustained point-return clip, but still not a hard local `D` report match. The public MP4 does not expose speed, range, altitude, FOV, platform motion, target coordinates, or a hard event timestamp.

## PR44 Primary Validation And Late Phase Review

Dedicated note: `research/ufo-pr44-primary-validation-late-phase-notes.md`

Generated files:

- `scripts/ufo_pr44_primary_visual_validation.py`
- `scripts/ufo_pr44_late_phase_review.py`
- `research/ufo-video-pr44-primary-visual-validation-dod111689115.csv`
- `research/ufo-video-pr44-primary-visual-validation-summary.csv`
- `research/ufo-video-pr44-late-phase-review-dod111689115.csv`
- `research/ufo-video-pr44-late-phase-review-summary.csv`
- `research/ufo-derived/video-motion-pass/pr44-primary-validation/DOD_111689115/*`
- `research/ufo-derived/video-motion-pass/pr44-late-phase-review/DOD_111689115/*`

The primary validation reviewed `154.0s-204.8s` and classified `121` high, `83` medium, and `51` low visual-quality rows. This raises the supported subset from the dense pass's `127/255` high-or-medium rows to `204/255` validation rows. Remaining lows cluster around `181s-199s`, where reticle/overlay graphics and dark-field texture make the target difficult to separate.

The late phase review sampled `244s-294s` at one frame per second. It found `8/20` compact-return detections in the reticle-cycling tail, `18/27` in the zoom-out continued-track interval, and `0/4` in the loss/exit interval.

Interpretation: PR44 now has enough local review to treat it as the strongest standalone visual clip, but it still has no written-report pairing and no physical kinematic basis.

## Overlay OCR Pass: `DOD_111689115.mp4`

The boxed/range-annotated frames around `238-244` were cropped, enlarged, contrast-adjusted, and passed through Tesseract. Manual review of the zoomed crop confirms a visible `10M`/`10m`-like label beside the tracking box. OCR recovered only weak fragments, including one `10m` read.

No date-time group, coordinates, platform identifier, report number, or other hard-link metadata was recovered from this crop pass.

A second source-resolution pass used full MP4 frames from seconds `238-244`, then cropped and enlarged the overlay region. It produced the same substantive result: the `10M`/`10m`-like label is visible, but no hard-link metadata was recovered.

## Source MP4 Metadata: `DOD_111689115.mp4`

FFmpeg container metadata for the source MP4 shows:

- `creation_time`: `2026-05-08T01:20:45.000000Z`
- video codec: H.264, 1920x1080, 30 fps
- encoder: `Elemental H.264`
- duration: 5 minutes 12 seconds

This is useful file/transcode metadata, but it should not be treated as the incident date. It does not expose location, mission, platform, report number, or event date.

## Point-Count Pass: `DOD_111689090.mp4`

A strict bright-point post-process was generated for `DOD_111689090.mp4` to test the `d56` three-contact lane and `d58` two-contact lane. Across 293 one-frame-per-second samples:

| Strong bright-point count | Frames |
|---:|---:|
| 0 | 78 |
| 1 | 211 |
| 2 | 4 |
| 3+ | 0 |

This weakens a direct `d56` visual match because `d56` describes three possible small air contacts, while no sampled frame shows three clean compact bright points under the strict rule. It remains count-compatible with `d58` only in a limited sense: four sampled frames show two strong bright-point candidates, but the derived frames do not expose the radar-lock, strobe, jamming, or report-ID metadata described in `d58`.

Higher-rate review around the two-candidate moments weakens the multi-contact interpretation. The `106-110` second window is mostly one persistent bright point with a weak intermittent secondary speck. The `234-237` and `249-252` second windows mix the persistent bright point with dark elongated vessel/scene features, not clean compact bright-point contacts.

Current media assessment: `DOD_111689090.mp4` remains useful background material for the range-fouler media pool, but it should be treated as a single-point/context clip unless release-package metadata links it to `d56` or `d58`.

## High-Rate Review: `DOD_111688964.mp4`

The full 21.8-second clip was extracted at 5 fps. This strengthens `DOD_111688964.mp4` as a short over-water track candidate. The bright object persists through the useful sequence, moves relative to the reticle/camera field, and appears near changing track-box symbology.

This clip is now stronger than `DOD_111689090.mp4` as a visual media anchor. It is still weaker than `DOD_111689115.mp4` as a report-correlation candidate because it is short and lacks readable metadata, but visually it is cleaner than the noisy multi-contact candidate.

An automated bright-blob table was generated but is not reliable enough for final tracking because the water background creates many bright highlights. Use it as a preliminary audit artifact only.

A selected-frame manual track was added for `DOD_111688964.mp4`. It supports the visual interpretation that one persistent object moves substantially relative to the reticle and is repeatedly bracketed or overlapped by track-box symbology. This strengthens the clip as a short over-water sensor-track candidate, while preserving the caveat that no report-link metadata is visible.

Full-frame stills were extracted for the strongest track-box moments. They preserve wider sensor context but still do not expose a date-time group, coordinates, platform identifier, or report number.

Later DVIDS lookup identified `DOD_111688964.mp4` as `DOW-UAP-PR29` / `DoW-UAP-D8`, but the local `d8` PDF/text appears to describe a different Djibouti 2025 event. Treat the DVIDS release identity as hard and the local `D8` reconciliation as unresolved.

## Next Best Work

1. Manually validate the `DOD_111689030.mp4` / `D38` audit track, especially the `50-87s` interval.
2. Resolve the local `D8` mismatch for `DOD_111688964.mp4`.
3. Review PR38 (`DOD_111689051.mp4`) as the next distinct standalone visual target. PR47 (`DOD_111689142.mp4`) now has a full formation pass; see `research/ufo-pr47-formation-visual-notes.md`.
4. Optionally hand-click the remaining ambiguous PR44 `181s-199s` rows or the earlier `123s-153s` pre-primary intermittent returns.
5. Continue using DVIDS release metadata before assigning any MP4 to a specific local `D` report.

