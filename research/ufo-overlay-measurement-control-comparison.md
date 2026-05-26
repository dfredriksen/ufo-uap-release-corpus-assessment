# Overlay Measurement Control Comparison

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: measurement-overlay control comparison after PR44 full-label survey
Status: direct local-media control scans complete for six comparison clips

## Purpose

This note compares PR44's sustained meter-like reticle/track-box label sequence against existing reticle, glare, sensor-display, and apparent-size control cases.

The PR44 finding is now:

> PR44 contains a sustained meter-like reticle/track-box display annotation from about `204s` to `266s`, manually read as `12M -> 11M -> 10M -> 9M`. The label is telemetry-like and display-state-associated, but its physical semantics are unresolved.

The control question is narrower:

> Do other reviewed reticle/track-box/glare clips show the same kind of meter-like display label?

## Direct Survey Result

The direct one-second local-media control survey found no PR44-like reticle-associated meter-label candidates in the six selected control clips.

Supporting table:

- `research/ufo-overlay-measurement-control-comparison.csv`

Direct survey outputs:

| Case | Samples | PR44-like meter label found? | Survey output |
|---|---:|---|---|
| `PR31` / `DOD_111688970.mp4` | 6 | no | `research/ufo-overlay-measurement-control-pr31-label-survey.csv` |
| `PR32` / `DOD_111688997.mp4` | 7 | no | `research/ufo-overlay-measurement-control-pr32-label-survey.csv` |
| `PR33` / `DOD_111689005.mp4` | 6 | no | `research/ufo-overlay-measurement-control-pr33-label-survey.csv` |
| `PR34` / `DOD_111689011.mp4` | 178 | no | `research/ufo-overlay-measurement-control-pr34-label-survey.csv` |
| `PR36` / `DOD_111689030.mp4` | 138 | no | `research/ufo-overlay-measurement-control-pr36-label-survey.csv` |
| `PR45` / `DOD_111689123.mp4` | 59 | no | `research/ufo-overlay-measurement-control-pr45-label-survey.csv` |

Each interval table has one continuous no-label interval for the clip:

- `research/ufo-overlay-measurement-control-pr31-label-survey-intervals.csv`
- `research/ufo-overlay-measurement-control-pr32-label-survey-intervals.csv`
- `research/ufo-overlay-measurement-control-pr33-label-survey-intervals.csv`
- `research/ufo-overlay-measurement-control-pr34-label-survey-intervals.csv`
- `research/ufo-overlay-measurement-control-pr36-label-survey-intervals.csv`
- `research/ufo-overlay-measurement-control-pr45-label-survey-intervals.csv`

## Interpretation

PR44 remains unusual within the current committed review evidence because it has:

- a sustained meter-like label interval
- a descending visible value sequence
- frame-localized value change
- reticle/track-box association rather than object-centroid following

The control set prevents overclaiming in both directions:

- glare and halo controls show release artifacts can be visually strong without being object evidence
- reticle controls show symbology alone is not evidence of measurement semantics
- PR45 shows apparent-size and reticle-lock confounds can coexist without a PR44-like meter-label finding
- none of the six selected controls reproduced PR44's sustained `12M -> 11M -> 10M -> 9M` style sequence

## Important Limitation

The control survey uses the same PR44-oriented crop and reticle/label detector. That is useful for testing whether PR44's specific geometry recurs in comparable clips, but it can miss labels outside that crop geometry, in different colors, or with different symbology. The result is therefore a bounded negative control:

> The selected controls do not show a PR44-like meter-label sequence under the current survey geometry; this does not prove that no other telemetry labels exist elsewhere in the corpus.

## Next Actions

1. Keep these six clips as bounded negative controls in `research/ufo-overlay-measurement-classification.csv`.
2. Add non-PR44 crop presets if additional clips show meter-like labels in different display locations.
3. Keep PR44's `12M -> 11M -> 10M -> 9M` sequence and PR051's `5M` / `5m-style` label as telemetry-like but physically unresolved until display documentation or raw telemetry appears.
