# PR31-PR33 / D32 Glare-Halo Control Review Notes

Created: 2026-05-11

Source videos:

- `DOD_111688970.mp4` / `DOW-UAP-PR31`
- `DOD_111688997.mp4` / `DOW-UAP-PR32`
- `DOD_111689005.mp4` / `DOW-UAP-PR33`

DVIDS URLs:

- `https://www.dvidshub.net/video/1006076/dow-uap-pr31-unresolved-uap-report-syria-october-2024`
- `https://www.dvidshub.net/video/1006078/dow-uap-pr32-unresolved-uap-report-syria-october-2024`
- `https://www.dvidshub.net/video/1006079/dow-uap-pr33-unresolved-uap-report-syria-october-2024`

Accompanying report stated by DVIDS: `DoW-UAP-D32`

War.gov D32 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d32-mission-report_-syria-october-2024.pdf`

## Scope

This pass reviews the three short Syria / October 2024 public videos that DVIDS links to `DoW-UAP-D32`.

DVIDS says each clip came from full-motion video aboard a U.S. military platform. The three visual descriptions are all glare/overlay oriented:

- `PR31`: a small, indistinct multi-colored area moves right-to-left across the top edge within the first second.
- `PR32`: an irregular white/red half-oval glare/halo-like area appears near the top edge from about `2s-4s`.
- `PR33`: two semi-transparent irregular orange areas overlay the background for less than two seconds each.

The D32 PDF records an initial UAP contact at `201559:00ZOCT24`. Its report text describes a misshapen uneven ball of white light, multiple light/glare events from unknown origin, one light/glare crossing the FMV camera at `1559Z`, `1602Z`, and `1644Z`, and a light/glare halo effect at the top of the FMV feed at `1609Z` and `1620Z`. The report also says the aircrew assessed the event as benign, with no mission impact or change, no intelligent control, no advanced capabilities/materials, and no effects on persons or recovered material.

## Method

Script: `scripts/ufo_pr31_pr33_d32_glare_review.py`

Tracked outputs:

- `research/ufo-video-pr31-pr33-d32-glare-review.csv`
- `research/ufo-video-pr31-pr33-d32-glare-review-summary.csv`
- `research/ufo-video-pr31-pr33-d32-glare-review-assets.csv`

Ignored visual artifacts:

- `research/ufo-derived/video-motion-pass/pr31-pr33-d32-glare-review/*`

The script samples each clip at `5 fps`. It does not try to build a conventional object track. Instead, it measures the artifact lane that DVIDS and D32 actually describe:

- top-edge warm-color area for `PR31`;
- broad top-band residual area for `PR32`;
- saturated orange overlay area for `PR33`.

All rows marked high or medium are artifact-support rows, not UAP-object support rows.

## Results

`PR31` / `DOD_111688970.mp4`:

- Resolution: `1920x1080`
- FPS: `30.0`
- Frames: `154`
- Duration: `5.133s`
- Sampled rows: `26`
- Medium rows: `2`
- Low rows: `24`
- Supported intervals: `0.6s-0.6s`; `1.0s-1.0s`
- Median top-edge warm-color area across supported rows: `198.5 px`

`PR32` / `DOD_111688997.mp4`:

- Resolution: `1920x1080`
- FPS: `30.0`
- Frames: `198`
- Duration: `6.600s`
- Sampled rows: `34`
- Medium rows: `6`
- Low rows: `28`
- Supported intervals: `2.0s-2.6s`; `3.2s-3.2s`; `4.0s-4.0s`
- Median broad top-edge residual component area: `10160.5 px`
- Median broad top-edge residual component width: `347.5 px`

`PR33` / `DOD_111689005.mp4`:

- Resolution: `1920x1080`
- FPS: `30.0`
- Frames: `151`
- Duration: `5.033s`
- Sampled rows: `26`
- High rows: `14`
- Low rows: `12`
- Supported interval: `0.0s-2.6s`
- Median saturated orange overlay area: `36764.0 px`
- Median largest orange overlay component area: `36784.0 px`

## Interpretation

This review supports treating `PR31`, `PR32`, and `PR33` as a D32 glare/halo/overlay control set.

The visual support is strongest for `PR33`, where the orange overlay is large and obvious. `PR31` is a tiny first-second warm-color top-edge artifact. `PR32` is weaker as an independent computer-vision result because camera motion and top-edge scene structure contribute to the broad residuals, but the detected residuals line up with DVIDS's `2s-4s` top-edge halo phase.

None of the three clips should be treated as a physical object track. The public videos do not validate speed, range, altitude, trajectory, object identity, or intelligent control. The released D32 report itself points in the opposite direction: benign light/glare/halo control context.

## Current Judgment

Mark the `PR31-PR33` / `D32` lane reviewed as a hard DVIDS report-video set and a control case. It is useful for false-positive handling and release/report completeness, not as positive unresolved-object evidence.

