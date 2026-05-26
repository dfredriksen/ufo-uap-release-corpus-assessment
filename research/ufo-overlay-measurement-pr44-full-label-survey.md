# PR44 Full Overlay Label Survey

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: `DOW-UAP-PR44` / `DOD_111689115.mp4`
Status: full-clip one-second overlay-label survey

## Purpose

This pass searches the full PR44 public MP4 for reticle-associated meter-like labels, not just the previously known `230-249s` window.

It answers three questions:

1. Does the label occur elsewhere in PR44?
2. Is the label continuous or intermittent?
3. Does the label value change in a way that supports display-state analysis?

## Command

```powershell
python scripts/ufo_pr44_overlay_label_survey.py
```

Outputs:

- `research/ufo-overlay-measurement-pr44-label-survey.csv`
- `research/ufo-overlay-measurement-pr44-label-survey-intervals.csv`
- ignored contact sheets under `research/ufo-derived/overlay-measurement-audit/DOD_111689115-label-survey/`

Manual value intervals:

- `research/ufo-overlay-measurement-pr44-label-value-intervals.csv`

## Detector Result

The one-second detector produced `312` survey rows.

Detected reticle-associated label-candidate interval:

- `204s-264s`: `61` one-second samples.

Non-detected intervals:

- `0s-203s`
- `265s-311s`

The detector is useful as a crop/triage tool, not as the final authority. Manual review found a short `9M`-like interval at `265s-266s` that the detector missed because the label is near the crop edge.

## Manual Value Sequence

Manual contact-sheet review supports this bounded sequence:

| Interval | Label | Confidence | Notes |
|---|---|---|---|
| `202s-203s` | ambiguous edge display value | low | Large/edge display geometry; do not use for value-sequence claims. |
| `204s-206s` | `12M` | high | First stable standard reticle-associated label interval. |
| `207s-233s` | `11M` | high | Stable label interval before transition. |
| `234s-264s` | `10M` | high | Stable label interval after transition. |
| `265s-266s` | `9M` | medium | Short final interval near crop edge. |

The earlier frame-level transition pass refines one boundary:

- Last reviewed `11M` frame: frame `7000`, `233.333s`.
- First reviewed `10M` frame: frame `7001`, `233.367s`.

## Interpretation

The full survey strengthens the display-annotation interpretation.

The PR44 label is not a one-off OCR artifact. It appears as a sustained reticle/track-box-associated value sequence:

> `12M -> 11M -> 10M -> 9M`

That sequence behaves like an updating display value tied to the reticle/track-box state. The public MP4 still does not reveal whether the value represents object size, range, gate size, zoom/display state, or another sensor/display parameter.

The strongest current bounded claim is:

> PR44 contains a sustained meter-like reticle/track-box display annotation from about `204s` to `266s`, manually read as a descending `12M`, `11M`, `10M`, and `9M` sequence. The label is telemetry-like and display-state-associated, but its physical semantics are unresolved.

## Claim Boundary

Allowed:

- PR44 has a persistent meter-like display annotation.
- The annotation changes value over time.
- The annotation is associated with the reticle/track-box, not simply with the moving object centroid.
- The value sequence should drive source requests for display documentation, raw metadata, and telemetry.

Not allowed:

- The object is physically `12m`, `11m`, `10m`, or `9m` wide.
- The object is physically `12m`, `11m`, `10m`, or `9m` distant.
- The public MP4 proves physical closure, range, size, speed, or acceleration from this label alone.

## Next Actions

1. Retain the completed direct overlay-label control scans for PR31, PR32, PR33, PR34, PR36, and PR45 as bounded negative controls under the current survey geometry.
2. Acquire PR051 and run the same full-label survey against its `5m`-style annotation.
3. Request sensor/display documentation that defines the meter-like label.
4. If display documentation appears, revisit whether the sequence can support range, gate-size, or object-size hypotheses.

Current control-comparison scaffold:

- `research/ufo-overlay-measurement-control-comparison.md`
- `research/ufo-overlay-measurement-control-comparison.csv`
