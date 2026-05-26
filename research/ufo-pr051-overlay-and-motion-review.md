# PR051 Overlay And Motion Review

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: `DOW-UAP-PR051`, `DOD_111719715`, Release 02
Status: source MP4 acquired outside repo; initial overlay-label survey complete

## Source Identity

| Field | Value |
|---|---|
| Public identifier | `DOW-UAP-PR051` |
| DVIDS video ID | `1007707` |
| DVIDS filename | `DOD_111719715` |
| DVIDS title | `DOW-UAP-PR051, "Syrian UAP instant acceleration"` |
| Official page | `https://www.dvidshub.net/video/1007707/dow-uap-pr051-syrian-uap-instant-acceleration` |
| War.gov anchor | `https://www.war.gov/UFO/#DOW-UAP-PR051-Syrian-UAP-instant-acceleration` |
| Release | Release 02 |
| Current repo source status | Public MP4 acquired outside the repo at `source-files-not-included/DOD_111719715.mp4`; source media is not redistributed. |
| Source acquisition row | `research/ufo-overlay-measurement-pr051-source-acquisition.csv` |
| SHA-256 | `034759DFC01CB87C718968F3012A57D89ACAE7BAED3A52D60041A59098DF2007` |

## Why This Case Matters

PR051 is one of the most important Release 02 video cases because it combines:

- an official title that frames the case as instant acceleration
- an explicit DVIDS provenance caveat that the public media was digitally altered before upload
- repeated public-MP4 frames showing a `5M` / `5m-style` reticle annotation near the object/track
- an apparent motion event that could be affected by sensor tracking, replay speed, thresholding, and enhancement

That combination makes PR051 analytically valuable, but also dangerous for overclaiming.

## Frame Observation

The user-provided `DOW-UAP-PR051.jpg` frame and the acquired public MP4 show:

- a bright compact object or return near the central reticle
- a visible north marker
- a reticle/track-box region
- a repeated `5M` / `5m-style` label close to the object/reticle
- multiple black redaction boxes
- low-resolution, compressed public-release imagery

The `5M` / `5m-style` label is an explicit measurement-like annotation candidate. It is not yet a validated physical object-size measurement.

## Initial Public-MP4 Overlay Survey

Survey note:

- `research/ufo-overlay-measurement-pr051-label-survey.md`
- `research/ufo-overlay-measurement-pr051-label-survey.csv`

The public MP4 contains repeated `5M` / `5m-style` visibility in the least-altered original excerpt at `007s`, `011s`, and `012s`, and again in the exit replay around `271s`, `275s`, and `276s`.

The later reticle-lock / zoomed segment around `249s-257s` shows a different display state with a large box and meter-like suffix values manually read as `31M-like`, `30M-like`, `13M-like`, and lower-confidence `6M-like` / `9M-like` candidates.

This makes PR051 a positive overlay-semantics case. It does not make PR051 a physical-performance case.

## Measurement Ambiguity

The `5M` / `5m-style` label could plausibly represent:

- object-size estimate
- range or slant-range readout
- track-box, gate, or measurement-window dimension
- reticle, zoom-state, or operator-display parameter
- enhancement/replay artifact
- annotation introduced before public upload
- OCR or visual misread caused by compression and frame scaling

The working conclusion is therefore:

> PR051 preserves a high-value measurement-like overlay candidate, but the public frame alone does not establish that the object is physically five meters wide or distant.

## Required Analysis Sequence

Run the PR051 analysis in this order:

1. Maintain the official MP4 outside the publish set with source URL, access date, byte size, SHA-256 hash, and expected local path.
2. Identify which intervals are original-resolution, replayed, slowed, thresholded, inverted, zoomed, sharpened, or otherwise altered.
3. Extract frame-accurate crops around the reticle/object/`5M` / `5m-style` label from the least-altered interval first.
4. Check whether the `5M` / `5m-style` label persists across adjacent frames.
5. Check whether the label moves with the object, reticle, track box, sensor frame, or post-production overlay.
6. Classify the later reticle-lock labels separately from the original-excerpt `5M` / `5m-style` label.
7. Compare label behavior against PR44's `10M` / `10m` candidate.
8. Compare against control clips with obvious reticle, range-gate, glare, threshold, and replay artifacts.
9. Only then run image-plane motion tracking on the original interval.
10. Keep all motion claims image-plane-only unless source FOV/zoom state, range, platform motion, gimbal state, and raw telemetry become available.

## Initial Claim Boundaries

Allowed claims now:

- PR051 is a high-priority overlay-exploitation target.
- The public MP4 contains repeated `5M` / `5m-style` measurement-like annotation visibility.
- The later reticle-lock interval contains separate meter-like suffix values in a different display state.
- The semantics of that annotation are unresolved.
- PR051 should not be used as clean kinematic evidence until original and altered intervals are separated.

Disallowed claims now:

- The object is definitively five meters in size.
- The `5M` / `5m-style` label is definitively a slant range or object-width readout.
- The clip proves instant acceleration or extraordinary performance.
- The public altered/replayed segments can support physical acceleration reconstruction.

## Needed Source Records

Highest-value requests:

- original, unaltered sensor video
- frame-level metadata
- FOV and zoom state
- slant range or range-time series
- platform position, speed, attitude, and heading
- gimbal pointing and stabilization state
- track-box or reticle display documentation
- uploader/editor chain of custody for altered public segments

## Working Disposition

PR051 should be promoted from a generic Release 02 provenance/control row into a targeted positive overlay-measurement review lane.

It should not yet be promoted into the ranked hard-evidence ladder above report/video pairings such as D38/PR36 or D33/PR34, because the public record currently lacks a local D-report pairing and because the released video is explicitly alteration-qualified.
