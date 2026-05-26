# Overlay Measurement PR059 Label Survey

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: `DOW-UAP-PR059` / `DOD_111719809.mp4`
Status: positive measurement-like overlay candidate; physical interpretation not promoted

## Purpose

PR059 was one of the five P1 residual overlay targets because its release metadata names field-of-view, reticle, and zoom context. After local acquisition outside Git, the P1 quicklook and OCR probe elevated PR059 from a metadata-only residual to a visible frame-level overlay candidate.

The narrow finding is:

> PR059 contains a persistent cyan/green track-box or target-adjacent label with an `M`/`m`-style suffix visible across a long interval of the public MP4.

This is a display-annotation finding only. The public MP4 does not define whether the suffix represents range, object size, gate size, zoom/display state, or another sensor parameter.

## Source And Method

Source media:

- Record ID: `DOW-UAP-PR059`
- Source video: `DOD_111719809.mp4`
- Source URL: `https://d34w7g4gy10iej.cloudfront.net/video/2605/DOD_111719809/DOD_111719809.mp4`
- DVIDS page: `https://www.dvidshub.net/video/1007727/dow-uap-pr059-nag-uap-1-jun-20`
- SHA-256: `11698020b966a3b38178f9ab66272f49d4400feb178fb269229009fbb08b3365`

Generated local-review artifacts:

- `research/ufo-overlay-measurement-p1-source-acquisition.csv`
- `research/ufo-overlay-measurement-p1-quicklook-samples.csv`
- `research/ufo-overlay-measurement-p1-ocr-probe.csv`
- `research/ufo-overlay-measurement-pr059-label-survey-samples.csv`
- `research/ufo-overlay-measurement-pr059-label-intervals.csv`

Ignored derived contact sheets were generated under:

- `research/ufo-derived/overlay-measurement-audit/p1-quicklook/PR059/`
- `research/ufo-derived/overlay-measurement-audit/DOD_111719809-pr059-label-survey/`

## Findings

| Interval | Manual read | Association | Confidence | Note |
|---|---|---|---|---|
| `0-21s` | none promoted | reticle/display only | high | No confirmed target-associated meter-suffix label before the track box becomes clear. |
| `22-37s` | `36M/36m-style` | large track-box edge | high | Full box appears with label at the right edge beginning around `23s`. |
| `38-41s` | `33M-style -> 10M-style -> 13M/10M-like` | changing track-box/target marker state | medium | The display changes from full box to corner brackets. |
| `42-95s` | `<4M/4M/5M-like` | target-adjacent label | medium | Label remains adjacent to the bright target. |
| `96-191s` | `2M/22M/23M-like` | target-adjacent label | medium | Label persists through brightening/saturation. |
| `192-277s` | `2M/3M/5M-like` | target-adjacent label | low | Label remains visible but exact values are more compression-limited. |
| `278-291s` | none promoted | reticle/display only | medium | Target/label association is not reliably visible after the late transition. |

## Interpretation Boundary

PR059 strengthens the measurement-overlay lane because it is a third positive public-video example, after PR44 and PR051, where a visible label with an `M`/`m`-style suffix is associated with reticle/track/target display state.

It does not support any of these claims from public pixels alone:

- the label is object size
- the label is slant range
- the label is speed, acceleration, or flight performance
- the changing label values are physical kinematics
- the public MP4 is sufficient for independent physical reconstruction

The correct classification is `unresolved_display_annotation` with `physical_claim_status=not_promoted`.
