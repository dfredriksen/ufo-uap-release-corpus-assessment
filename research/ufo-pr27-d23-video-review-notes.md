# PR27 / D23 Video Review

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `I:\My Drive\UFO\DOD_111688825.mp4`
Release identity: `DOW-UAP-PR27`
Accompanying report: `DoW-UAP-D23`

## Scope

DVIDS identifies `DOD_111688825` as `DOW-UAP-PR27`, United Arab Emirates, October 2023, and states that the accompanying mission report is `DoW-UAP-D23`. This removes the earlier "no DVIDS filename hit" caveat for this local MP4.

Official/local `D23` contains two UAP report lines from the same mission: one at `240241:00ZOCT23` with estimated kinetic velocity `320 MPH`, and one at `240322:00ZOCT23` with estimated kinetic velocity `440 MPH`. The public MP4 does not expose enough visible timestamp, platform, range, or coordinate metadata to independently assign the video sequence to one line versus the other. Treat the hard pairing as PR27-to-D23, not as a solved physical kinematic reconstruction.

## Method

Script:

- `scripts/ufo_pr27_d23_video_review.py`

Outputs:

- `research/ufo-video-pr27-d23-review-dod111688825.csv`
- `research/ufo-video-pr27-d23-review-summary.csv`
- `research/ufo-video-pr27-d23-review-assets.csv`
- `research/ufo-derived/video-motion-pass/pr27-d23-review/DOD_111688825/*`

The script samples the DVIDS-described content interval from `116.0s` through `297.0s` at one frame per second. It suppresses colored overlays and line-like graphics, searches for compact bright or dark local contrast components in the main sensor view, and scores candidates against the DVIDS phase narrative: right-side acquisition, pan-to-center, zoom, generally centered track, and erratic sensor-motion/reacquisition.

This is a visual audit, not a final hand-clicked track.

## Source Checks

| Local source file | Size | SHA256 |
|---|---:|---|
| `I:\My Drive\UFO\DOD_111688825.mp4` | `155885289` bytes | `3C510FE34677A0784C656105B9653CE3039D83DE46F929F1EE6D6FB820CE3B8C` |
| `I:\My Drive\UFO\dow-uap-d23-mission-report-united-arab-emirates-october-2023.pdf` | `1324277` bytes | `EA1CD5296143F378DB533066B524C32C1ECFBFD43D74EC6BE7D832C20FA271BB` |

## Results

The source MP4 is `1920x1080`, `30 fps`, `8920` frames, and `297.333s`.

One-fps review:

| Review quality | Count |
|---|---:|
| High | 98 |
| Medium | 60 |
| Low | 24 |
| High or medium | 158 |

Supported intervals:

`130.0s-132.0s`; `134.0s-178.0s`; `181.0s-184.0s`; `186.0s-212.0s`; `214.0s-227.0s`; `230.0s`; `234.0s-297.0s`

Supported rows by DVIDS phase:

| DVIDS phase | Supported rows |
|---|---:|
| Sensor pans to center | 3 |
| Field-of-view narrows | 1 |
| Generally centered track | 69 |
| Erratic sensor motion and reacquisition | 85 |

The script did not support the initial `116s-123s` right-side acquisition phase. Those rows remained low-confidence, so the local visual audit should not claim it independently validates the earliest distinguishable moment. The stronger support begins around `130s` and continues through the zoom, generally-centered, and reacquisition phases.

Supported track metrics:

| Metric | Value |
|---|---:|
| Supported high-or-medium rows | `158` |
| Supported span | `130.0s-297.0s`, with gaps |
| Net displacement | `6.801 px` |
| Path length | `18267.318 px` |
| Path-average image-plane rate | `109.385 px/s` |
| Median one-second step rate | `69.909 px/s` |

The path length and step rate are dominated by sensor motion, reacquisition, and candidate relocking. They should not be interpreted as physical target speed.

## Interpretation

PR27/D23 is now a hard report-video pairing:

- Hard public-release identity: `DOD_111688825.mp4` = `DOW-UAP-PR27`.
- DVIDS-stated accompanying report: `DoW-UAP-D23`.
- Local video support: high-or-medium compact contrast support in `158/182` one-fps samples from the public content interval, strongest after the zoom/centered phase begins.
- Report content: `D23` contains two UAP lines with estimated velocities of `320 MPH` and `440 MPH`, both with unknown altitude/trajectory fields and limited redacted coordinates.

The case is analytically useful because it adds another hard report-video lane in the UAE October 2023 set. It is still bounded: the public MP4 does not provide enough metadata to validate either reported speed, distinguish the two `D23` UAP lines, recover range/altitude, or produce physical kinematics.

## Sources

- DVIDS `DOW-UAP-PR27`: `https://www.dvidshub.net/video/1006067/dow-uap-pr27-unresolved-uap-report-united-arab-emirates-october-2023`
- War.gov `DoW-UAP-D23` PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d23-mission-report-united-arab-emirates-october-2023.pdf`

