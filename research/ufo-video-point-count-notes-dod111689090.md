# UFO Video Point-Count Notes: DOD_111689090

Owner: Dan Fredriksen
Created: 2026-05-09
Source folder: `I:\My Drive\UFO`
Source video: `DOD_111689090.mp4`
Status: Multi-contact screening pass

## Method

This pass used the existing one-frame-per-second center crops for `DOD_111689090.mp4` and produced a raw compact-point detector table plus a stricter post-processed table.

Generated files:

- `research/ufo-video-point-count-dod111689090.csv`
- `research/ufo-video-point-count-dod111689090-strong.csv`
- `research/ufo-video-point-count-dod111689090-ranges.csv`
- `research/ufo-video-point-count-dod111689090-segment-summary.csv`
- `research/ufo-video-high-rate-review-dod111689090.csv`
- `research/ufo-video-ffmpeg-metadata-dod111689090.txt`
- `research/ufo-derived/video-motion-pass/high-rate/DOD_111689090/*`

The raw table is intentionally sensitive. The strong table removes margin/overlay-adjacent hits, requires stronger local contrast, and merges nearby split components so a two-lobed bright return is not counted as two separate contacts.

## Point-Count Result

Strict bright-point count across 293 sampled frames:

| Strong bright-point count | Frames |
|---:|---:|
| 0 | 78 |
| 1 | 211 |
| 2 | 4 |
| 3+ | 0 |

Segment summary:

| Segment | Frames with 1+ strong bright point | Frames with 2+ strong bright points | Max count | Note |
|---|---:|---:|---:|---|
| `s000-059` | 50 / 60 | 0 | 1 | Mostly one recurring bright point. |
| `s060-119` | 50 / 60 | 2 | 2 | Mostly one bright point, with isolated two-candidate frames. |
| `s120-179` | 48 / 60 | 0 | 1 | Mostly one recurring bright point. |
| `s180-239` | 50 / 60 | 1 | 2 | Mostly one bright point, with isolated two-candidate frames. |
| `s240-292` | 17 / 53 | 1 | 2 | Late sequence includes vessel/scene context and intermittent candidates. |

The dominant machine-counted pattern is one persistent bright point, usually near the left/lower-left portion of the reticle area in the center crop. Two-bright-candidate frames occur only at frames `108`, `109`, `236`, and `251`.

## Visual Caveats

The video is noisy and compression-heavy. Some late frames also show dark elongated scene objects or vessel-like features. Those were not included in the strict bright-point table because they are not clean compact bright point returns. They may be relevant as scene context, but they should not be counted as UAP contacts without manual full-motion review.

The strict table therefore answers a narrow question: how often does the one-frame-per-second center crop show multiple clean compact bright point returns?

## Comparison To `d56` And `d58`

`d56` reports three possible unidentified small air contacts, with an initial contact followed by two additional contacts after the first was reacquired. The `DOD_111689090.mp4` strong bright-point table does not show any sampled frames with three clean compact bright points. That weakens a direct `d56` visual match.

`d58` reports two contacts in the group and target-pod video showing two IR-significant contacts, along with radar lock, red blinking strobes, and noise-jamming language. `DOD_111689090.mp4` is count-compatible with `d58` only in a limited sense: it has four isolated sampled frames with two strong bright-point candidates. It does not show, in the derived frames reviewed so far, readable metadata, radar-lock evidence, strobe/jamming context, or a report identifier.

Current assessment: `DOD_111689090.mp4` remains a useful multi-contact candidate at the evidence-lane level, but it is weaker than `DOD_111689115.mp4` as a media anchor. It should not be treated as a direct `d56` or `d58` match without release-package linkage or readable overlay metadata.

## Higher-Rate Review

Three windows were extracted at 5 fps around the strict two-bright-candidate moments:

| Window | Reason | Visual result |
|---|---|---|
| `w106-110` | Covers two-candidate frames `108-109`. | Mostly one persistent bright point left/lower-left of the reticle. A faint secondary speck appears intermittently, but it is weak and does not create a robust two-contact sequence. |
| `w234-237` | Covers two-candidate frame `236`. | Persistent bright point remains visible. A dark elongated object/feature moves near the upper field and reads more like scene/vessel context than a clean compact bright point return. |
| `w249-252` | Covers two-candidate frame `251`. | Persistent bright point plus dark elongated objects/features in the upper field, followed by display/contrast changes. This is not a clean two-bright-contact sequence. |

The higher-rate review downgrades `DOD_111689090.mp4` as a multi-contact anchor. It is better described as a persistent single bright-point clip with intermittent weak secondary specks and later vessel/scene context.

Updated assessment: `DOD_111689090.mp4` should remain in the range-fouler media pool, but it should not be used as the primary visual support for either `d56` or `d58`.

## Source MP4 Metadata

FFmpeg container metadata for the source MP4 shows:

- `creation_time`: `2026-05-08T01:05:25.000000Z`
- video codec: H.264, 1920x1080, 30.30 fps
- encoder: `Elemental H.264`
- duration: 4 minutes 53.17 seconds

This appears to be file/transcode metadata rather than incident metadata. It does not expose location, mission, platform, report number, or event date.

## Next Best Work

1. If needed, add a separate dark-object/context detector for the late vessel-like frames, keeping it separate from bright-point contact counts.
2. Search release packaging or filenames outside the MP4 itself for any explicit pairing between `DOD_111689090.mp4` and a `dow-uap-d*` report.
3. Move the next media effort to `DOD_111688964.mp4`, which is short enough for higher-rate frame review.

