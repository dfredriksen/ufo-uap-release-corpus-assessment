# PR44 Overlay Label Transition Pass

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: `DOW-UAP-PR44` / `DOD_111689115.mp4`
Status: high-rate local-media transition pass

## Purpose

This pass narrows the PR44 meter-like overlay transition from the one-second persistence review.

The previous one-second pass found:

- `11M`-like label from about `230-233s`
- `10M`-like label from about `234-249s`

This pass samples the transition window at `5 Hz`.

## Command

```powershell
python scripts/ufo_pr44_overlay_transition_pass.py --start-second 232 --end-second 235 --sample-rate-hz 5
```

Outputs:

- `research/ufo-overlay-measurement-pr44-transition-pass.csv`
- ignored crops under `research/ufo-derived/overlay-measurement-audit/DOD_111689115-transition/`
- ignored contact sheet `research/ufo-derived/overlay-measurement-audit/DOD_111689115-transition/pr44_overlay_transition_contact_sheet.jpg`

## Result

Manual review of the generated high-rate contact sheet found:

- Last `11M` sample in the 5 Hz pass: `233.200s`, frame `6996`.
- First `10M` sample in the 5 Hz pass: `233.400s`, frame `7002`.
- A follow-on frame-by-frame compare localized the visible change further: last manually reviewed `11M` frame `7000`, first manually reviewed `10M` frame `7001`.

Supporting table:

- `research/ufo-overlay-measurement-pr44-transition-pass.csv`
- `research/ufo-overlay-measurement-pr44-motion-compare.csv`

## Interpretation

The label transition is temporally localized and appears display-native in the public MP4 crop sequence, but the semantics remain unresolved.

The transition could represent:

- object-size estimate update
- range-like display update
- reticle/track-box gate update
- zoom or sensor-state update
- operator/display processing update
- compression or display-read ambiguity

Current bounded phrasing:

> In PR44, the meter-like label beside the reticle/track box changes from `11M` to `10M` between frames `7000` and `7001` of the public MP4, around `233.333-233.367s`. The public material shows label persistence and transition timing, but not the display semantics needed to treat the label as physical object size or range.

## Next Actions

1. If needed, rerun at frame-by-frame cadence from frame `6996` to frame `7002`.
2. Compare reticle-box position, object position, and label position across the transition.
3. Search other local MP4s for equivalent reticle/label behavior.
4. Acquire PR051 and run the same transition/persistence workflow on the `5m`-style annotation.
