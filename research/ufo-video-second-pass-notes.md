# UFO Video Second-Pass Notes

Owner: Dan Fredriksen
Created: 2026-05-09
Source files: official public UFO/UAP release files, not redistributed in this repository
Derived artifacts: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass`
Status: Second visual triage

## Method

The ten highest-priority MP4s from the first contact-sheet pass were processed again with derived center-crop sheets and representative timed frames. The center crop keeps the reticle/track-box area at higher visible resolution.

Generated files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-second-pass-index.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/center-crop-sheets/*.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/*/*.jpg`

No source files in `source-files-not-included` were modified.

## Priority Changes

### Strongest Media Candidates

| File | Second-pass observation | Candidate report lane |
|---|---|---|
| `DOD_111689115.mp4` | Starts with an over-water vessel, then tracks a small bright point/object near the reticle, later with a box and range-like annotations visible. | Best candidate for range-fouler / over-water sensor reports such as `d38`, `d44`, `d56`, `d57`, or `d58`. |
| `DOD_111689090.mp4` | Multiple small point-like returns appear across the field; some frames show more than one point. | Candidate for multi-contact reports such as `d56` or `d58`, but needs motion review. |
| `DOD_111688964.mp4` | Short sequence with bright object/point over water-like texture and visible tracking box changes. | Candidate for over-water range-fouler lane. |
| `DOD_111689123.mp4` | Stable track/circle symbology around an object-like return over a relatively clean background. | Candidate for focused motion/track review; report link unclear. |
| `DOD_111689142.mp4` | Reticle-centered sequence with a loop/paired-bright shape near the crosshair across many frames. | Candidate for object-shape review, but could be aircraft/sensor artifact without motion context. |

### Still Useful, But More Contextual

| File | Second-pass observation | Reason |
|---|---|---|
| `DOD_111688825.mp4` | Coastal/harbor and over-water scene, with later small bright points at the edge of the frame. | Useful for geography/context and possible over-water object review, but the object is not consistently centered in the crop. |
| `DOD_111689011.mp4` | One small point appears in early frames, then sensor/contrast changes dominate. | Could still be a sensor-review candidate, but weaker than `111689115`, `111689090`, and `111688964`. |
| `DOD_111689030.mp4` | Starts with a vessel or feature, then small bright returns near green symbology. | Superseded by DVIDS release-index lookup: this is `DOW-UAP-PR36` and is explicitly paired with `DoW-UAP-D38`. Treat as the current hard report-video anchor even though the second-pass visual crop alone looked only medium-strength. |
| `DOD_111689083.mp4` | Bright point over terrain/cloud background appears in repeated frames. | Candidate for motion review, but less directly tied to maritime/range-fouler records. |
| `DOD_111689022-1920x1080-9000k.mp4` | Cloud/shore background with small bright points and bright cloud features. | Possible control/glare/bird/cloud case unless motion strongly contradicts. |

## Correlation Assessment

This section has been superseded by the later DVIDS release-index pass. The second pass alone did not create a hard report-to-video match, but external release metadata now does: `DOD_111689030.mp4` is `DOW-UAP-PR36` and is explicitly paired with `DoW-UAP-D38`.

The remaining visual linkage is still useful by scene type:

- Over-water small bright/cold/hot point tracks: likely candidates for the 2020 range-fouler cluster.
- Multiple small returns: possible match lane for `d56` three contacts or `d58` two IR-significant contacts.
- Cloud/sky clips: possible match lane for `d10` or other bird/glare/control records.
- Vessel/port/shore clips: likely context or mission video unless paired with a UAP track in the same sequence.

## Next Best Work

Motion extraction has now been completed for the strongest three clips:

1. `DOD_111689115.mp4`
2. `DOD_111689090.mp4`
3. `DOD_111688964.mp4`

See `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-motion-pass-notes.md` for the follow-up results. The short version: `DOD_111689115.mp4` is now the strongest media candidate; `DOD_111689090.mp4` remains the best multi-contact candidate; `DOD_111688964.mp4` is a clean short over-water candidate.

Later update: `DOD_111689030.mp4` has since been promoted to the hard report-video anchor after DVIDS pairing and a 2026-05-10 quantitative D38 pass. See `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-notes.md`.
