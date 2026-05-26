# PR44 Overlay Label Persistence

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: `DOW-UAP-PR44` / `DOD_111689115.mp4`
Status: local-media overlay exploitation pass

## Purpose

This note records the first manual exploitation result from the measurement-overlay lane.

It uses the local-media scan output from:

```powershell
python scripts/build_ufo_overlay_measurement_audit.py --scan-local-video --record-id DOW-UAP-PR44 --sample-step-seconds 1 --output research/ufo-overlay-measurement-pr44-local-scan.csv --summary-output research/ufo-overlay-measurement-pr44-local-scan.md
```

The generated source crops are stored under `research/ufo-derived/overlay-measurement-audit/` and remain excluded from Git.

## Result

Manual review of the PR44 scan crops found a persistent measurement-like label beside the reticle/track box:

- `230s` to `233s`: `11M`-like label, medium manual-read confidence.
- `234s` to `249s`: `10M`-like label, high manual-read confidence.
- The label stays to the right of the reticle/track box across adjacent one-second samples.
- The label is visible across at least `20` consecutive one-second samples in this review window.

Supporting table:

- `research/ufo-overlay-measurement-pr44-label-persistence.csv`

High-rate transition follow-up:

- `research/ufo-overlay-measurement-pr44-transition-pass.md`
- `research/ufo-overlay-measurement-pr44-transition-pass.csv`
- `research/ufo-overlay-measurement-pr44-motion-compare.md`
- `research/ufo-overlay-measurement-pr44-motion-compare.csv`
- `research/ufo-overlay-measurement-pr44-full-label-survey.md`
- `research/ufo-overlay-measurement-pr44-label-value-intervals.csv`

## Interpretation

This is stronger than a single-frame observation. The label is persistent across adjacent frames and changes from `11M` to `10M` before stabilizing.

The high-rate transition pass localizes the change: the 5 Hz pass brackets it between `233.200s` / frame `6996` and `233.400s` / frame `7002`; the frame-by-frame compare places the visible change between frame `7000` and frame `7001`.

The full-label survey extends the manually reviewed sequence. The standard reticle-associated meter-like label is visible from about `204s` to `266s`, with a descending sequence: `12M`, `11M`, `10M`, then a short `9M`-like final interval.

It still does not establish physical object size, range, or distance.

Current unresolved semantics:

- object-size estimate
- slant-range or range-like readout
- track-box, gate, or measurement-window dimension
- reticle/display parameter
- zoom or sensor-state annotation
- OCR/manual-read ambiguity

The safest current phrasing is:

> PR44 contains a persistent meter-like reticle/track-box label, manually read as `11M` from about 230-233s and `10M` from about 234-249s. The label is telemetry-like, but its display semantics are not resolved from the public MP4 alone.

## Method Limitations

The local-media scan is intentionally broad. It detected a textlike overlay cluster in every sampled PR44 second because the reticle/overlay itself is visible throughout the clip. That makes it useful for crop generation, but not sufficient as a classifier.

Manual review remains required to decide whether a crop contains a meaningful measurement-like label.

## Next Actions

1. Search for equivalent labels in other local MP4s and PR051 once the official asset is acquired.
2. Compare against control clips with reticle/track-box overlays but no claimed measurement labels.
3. Do not use the label as physical size or range until display documentation or raw telemetry resolves the semantics.
