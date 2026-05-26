# PR44 Overlay Motion Compare

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: `DOW-UAP-PR44` / `DOD_111689115.mp4`, frames `6996-7002`
Status: frame-by-frame overlay/object motion comparison

## Purpose

This pass tests whether the PR44 meter-like label behaves more like an object-following value, a reticle/track-box annotation, or a static display element across the `11M` to `10M` transition.

It compares:

- cyan reticle/track-box component position
- cyan meter-like label component position
- bright object/return candidate position

## Command

```powershell
python scripts/ufo_pr44_overlay_motion_compare.py --start-frame 6996 --end-frame 7002
```

Outputs:

- `research/ufo-overlay-measurement-pr44-motion-compare.csv`
- ignored annotated crops under `research/ufo-derived/overlay-measurement-audit/DOD_111689115-motion-compare/`
- ignored contact sheet `research/ufo-derived/overlay-measurement-audit/DOD_111689115-motion-compare/pr44_overlay_motion_compare_contact_sheet.jpg`

## Result

Frame-by-frame review found:

- The reticle/track-box center is effectively stable: about `952.5-952.7 px`, `529.6-529.8 px`.
- The label stays immediately to the right of the reticle/track-box.
- The label's offset from the reticle is stable while the label reads `11M`: about `+91 px`, `+20 px`.
- The label changes from `11M` to `10M` between frame `7000` and frame `7001`.
- The first manually reviewed `10M` frame is frame `7001`, at `233.367s`.
- The bright object/return candidate moves down-left relative to the reticle across the same interval.

Supporting table:

- `research/ufo-overlay-measurement-pr44-motion-compare.csv`

## Interpretation

This behavior weighs against the label being a simple static burnt-in text element, because its value changes during a short frame interval.

It also weighs against the label directly following the object centroid, because the bright object candidate moves down-left while the reticle/label complex stays nearly fixed in screen coordinates.

The strongest current interpretation is:

> The PR44 `11M` / `10M` label is tied to the reticle/track-box display state rather than to the bright object centroid alone. It remains a telemetry-like display annotation with unresolved semantics.

This still does not establish object size, range, or distance. It narrows the ambiguity from "single-frame possible OCR artifact" to "persistent reticle/track-box-associated display annotation with a frame-localized value change."

## Remaining Ambiguities

- The label may be a range-like or meter-like display value.
- The label may be a track-box, gate, or measurement-window parameter.
- The label may update from a sensor/display state change rather than object state.
- The public MP4 lacks display documentation, raw metadata, FOV/zoom state, slant range, platform state, and gimbal state.

## Next Actions

1. Use the full-label survey to compare the broader `12M -> 11M -> 10M -> 9M` sequence against object/reticle motion.
2. Run the same motion-compare workflow on PR051 after acquiring `DOD_111719715`.
3. Compare PR44 against control clips that have reticle/track-box overlays but no claimed measurement labels.
4. Request display documentation or raw telemetry before interpreting the meter-like values physically.
