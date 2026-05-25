# UFO PR28 / D25 Video Review Notes

Owner: Dan Fredriksen
Created: 2026-05-10
Source video: `I:\My Drive\UFO\DOD_111688954.mp4`
Release identity: `DOW-UAP-PR28`
DVIDS-stated report label: `DoW-UAP-D7`
Best written-report content lane: `DoW-UAP-D25`
Status: One-fps full-clip pass and five-fps SWIR-track pass complete

## Bottom Line

The PR28 visual pass supports the DVIDS-described sequence at image-plane level: a compact bright return is recoverable through the SWIR tracking interval and then is not supported after the modality-switch/loss sequence.

The review strengthens `DOD_111688954.mp4` as a high-priority `PR28` visual case, but it does not validate the D25 report-derived `434 knots`, range, altitude, object identity, or sensor geometry.

## Generated Files

- `scripts/ufo_pr28_d25_visual_review.py`: repeatable PR28/D25 visual-review script.
- `research/ufo-video-pr28-d25-review-dod111688954.csv`: one-fps full-clip review table.
- `research/ufo-video-pr28-d25-review-dense.csv`: five-fps SWIR-track review table from `10.0s-56.0s`.
- `research/ufo-video-pr28-d25-review-summary.csv`: summary metrics.
- `research/ufo-video-pr28-d25-review-assets.csv`: generated artifact index.
- `research/ufo-derived/video-motion-pass/pr28-d25-review/DOD_111688954/*`: ignored annotated frames, patches, and contact sheets.

## Method

The script samples the source MP4 in two passes:

- Full clip at `1 fps`, covering `0.0s-66.0s`.
- Dense SWIR-track interval at `5 fps`, covering `10.0s-56.0s`.

It uses DVIDS phase anchors:

- `00:00-00:03`: split-view startup.
- `00:04-00:09`: split-view initial contrast.
- `00:10-00:54`: full-screen SWIR track.
- `00:55`: late SWIR teardrop view.
- `00:56`: visible-spectrum loss.
- `00:57-01:05`: SWIR black-hot non-reacquisition.

The detector searches for compact bright contrast components after suppressing colored overlay and line artifacts. It ranks candidates by local brightness contrast, compactness, distance from a phase-specific expected lane, and relation to colored overlays. The dense pass uses contiguous-segment dynamic tracking so post-loss frames cannot pull the supported SWIR segment onto later noise.

## Results

Source metadata:

- FPS: `30.0`
- Frames: `1980`
- Duration: `66.000s`

Full one-fps pass:

- Samples: `67`
- Supported high-or-medium rows: `47`
- Quality split: `37 high`, `10 medium`, `16 low`, `4 none`
- Supported interval: `9.0s-55.0s`
- Supported phase split: `45` rows in full-screen SWIR track, `1` row in late SWIR teardrop view, `1` row in split-view initial contrast
- Image-plane track summary: `9.0s-55.0s`; net displacement `305.317 px`; path `2984.705 px`; path-rate proxy `64.885 px/s`; median one-second step rate `43.073 px/s`

Dense five-fps pass:

- Samples: `231`
- Supported high-or-medium rows: `217`
- Quality split: `185 high`, `32 medium`, `14 low`
- Supported intervals: `10.0s-10.4s`; `11.0s-11.4s`; `12.8s-17.2s`; `17.8s-25.0s`; `25.8s-55.8s`
- Supported phase split: `212` rows in full-screen SWIR track and `5` rows in late SWIR teardrop view
- Image-plane track summary: `10.0s-55.8s`; net displacement `146.452 px`; path `3304.070 px`; path-rate proxy `72.141 px/s`; median 0.2-second step rate `45.768 px/s`

Shared supported-row medians:

- Component area: `162.5 px`
- Contrast delta: `81.0` luma
- Distance from phase-specific expected lane: `106.49 px`
- Distance from central reticle: `120.75 px`

## Interpretation

The strongest local support is the dense SWIR interval from `25.8s-55.8s`, where the detector consistently follows the compact bright return through the lead-up to the DVIDS `00:55` teardrop/trailing-mass description.

The early `10s-25s` interval is still useful but more cloud-confounded, with several gaps and larger jumps. Treat it as phase support, not as a clean physical trajectory.

Rows at `56.0s` and after are intentionally classified as low or none even when the detector finds bright specks, because DVIDS describes the subject as lost at the visible-spectrum switch and not reacquired after the SWIR black-hot switch. This supports the described loss/non-reacquisition sequence without turning later noise into a target track.

## Current Judgment

`DOD_111688954.mp4` is now a reviewed PR28 visual case:

- High confidence for DVIDS release identity.
- High confidence that the public MP4 contains a compact bright SWIR return during the PR28 tracking interval.
- High confidence that local/War.gov `D25` is the matching written-report content lane.
- Low confidence for the DVIDS `D7` label, which remains an unresolved official-source discrepancy.
- No independent validation of the report-derived `434 knots` or physical geometry from the public MP4 alone.

