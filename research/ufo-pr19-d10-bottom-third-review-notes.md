# PR19 / D10 Bottom-Third Review Notes

Created: 2026-05-11

Source video: `DOD_111688723.mp4`

DVIDS release: `DOW-UAP-PR19`

DVIDS URL: `https://www.dvidshub.net/video/1006056/dow-uap-pr19-unresolved-uap-report-middle-east-may-2022`

Accompanying report stated by DVIDS: `DoW-UAP-D10`

War.gov D10 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d10-mission-report-middle-east-may-2022.pdf`

## Scope

This pass reviews the short PR19 public MP4 against the DVIDS visual description and D10 report lane.

DVIDS says the public release consists of five seconds of infrared footage from a U.S. military platform and states that D10 described the depicted object as a possible missile moving across the field of view. DVIDS also says D10 described four other objects not depicted in the video as possible birds.

The local D10 extracted-text triage is consistent with that framing: it reports five UAP observations, with the first at `1514Z` having the visual-recognition profile of a possible missile and the remaining four fitting closer to possible birds. It also notes dust hindered most full-motion-video ground collection.

## Method

Script: `scripts/ufo_pr19_d10_bottom_third_review.py`

Tracked outputs:

- `research/ufo-video-pr19-d10-bottom-third-review-dod111688723.csv`
- `research/ufo-video-pr19-d10-bottom-third-review-summary.csv`
- `research/ufo-video-pr19-d10-bottom-third-review-assets.csv`

Ignored visual artifacts:

- `research/ufo-derived/video-motion-pass/pr19-d10-bottom-third-review/DOD_111688723/*`

The script reviews all decoded frames, not just one-frame-per-second samples. It searches a lower-display ROI for a dark, horizontally elongated component matching the DVIDS bottom-third left-to-right description. It suppresses weak candidates unless they meet the narrow PR19 streak profile.

## Results

Video metadata from OpenCV:

- Resolution: `1920x1080`
- FPS: `30.0`
- Frames: `162`
- Duration: `5.400s`

Dense-frame results:

- Reviewed frames: `162`
- High-confidence frames: `5`
- Medium-confidence frames: `0`
- None: `157`
- Supported interval: `2.500s-2.633s`

Supported candidate track:

- Supported frame centers: `2.500s`, `2.533s`, `2.567s`, `2.600s`, `2.633s`
- Image-plane x shift: `478.880 px`
- Image-plane y shift: `10.579 px`
- Net image-plane displacement: `478.997 px`
- Path length: `479.005 px`
- Frame-center span: `0.133s`
- Inclusive frame coverage: `0.167s`
- Median component area: `1284.0 px`
- Median dark contrast delta: `91.0` luma
- Median aspect ratio: `6.0`
- Median candidate center: `x=458.685 px`, `y=779.394 px`

## Interpretation

PR19 now has direct image-plane support for the narrow DVIDS visual description: a dark elongated contrast area appears in the lower display lane and moves left-to-right across five consecutive dense frames. The support is short but visually clean.

This does not validate the D10 possible-missile characterization, physical speed, range, altitude, trajectory, object identity, or whether the object is a missile, bird, dust artifact, sensor effect, or other object. The public MP4 only supports a brief bottom-third left-to-right image-plane event.

## Current Judgment

Treat `DOD_111688723.mp4` as a hard `PR19` / `D10` report-video pair with a brief but strong bottom-third visual alignment to DVIDS. Keep D10 as a mixed-control context because the same report says the four other non-depicted objects fit closer to possible birds and that dust hindered FMV collection.

