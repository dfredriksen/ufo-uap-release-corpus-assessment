# UFO DVIDS Release Identity Backfill

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: backfill official DVIDS identities for local MP4s not yet represented in the main report-video matrix
Status: source-index update complete

## Bottom Line

Several local videos already have official DVIDS release identities that were missing from the main matrix. Most are low-evidence control cases, short standalone clips, or videos without written/oral reporter descriptions. The main analytic promotion from this pass is `DOD_111688825.mp4` / `DOW-UAP-PR27` / `DoW-UAP-D23`, because it is a long hard report-video pairing and should be the next bounded phase-review target.

The backfill also adds a PR26 caveat: DVIDS titles PR26 as United Arab Emirates / October 2023, but also says the underlying material is a still image from 2022 and names `DoW-UAP-D12` as the accompanying report. Local/War.gov `D12` is an Iraq / May 2022 mission report, and its UAP description matches DVIDS PR26's body text. Treat PR26 as a hard DVIDS video identity and D12 content match with conflicting release-title metadata.

## Hard Report-Video Pairings Added

| Local video | DVIDS release | DVIDS-stated report | Analytic treatment |
|---|---|---|---|
| `DOD_111688723.mp4` | `DOW-UAP-PR19`, Middle East, May 2022 | `DoW-UAP-D10` | Hard pair, low evidentiary value; DVIDS says one possible missile-like object is shown and four other objects were possible birds. |
| `DOD_111688762.mp4` | `DOW-UAP-PR21`, Iraq, May 2022 | `DoW-UAP-D14` | Hard pair, conventional-control lane; DVIDS says D14 described a probable `SU-27/35`. |
| `DOD_111688775.mp4` | `DOW-UAP-PR22`, Syria, July 2022 | `DoW-UAP-D16` | Hard pair, short movement clip; DVIDS says D16 described movement from north to south. |
| `DOD_111688809.mp4` | `DOW-UAP-PR23`, Iraq, December 2022 | `DoW-UAP-D18` | Hard pair, ambiguity-control lane; local D18 frames the observation as possible UAP/UAV. |
| `DOD_111688816.mp4` | `DOW-UAP-PR26`, United Arab Emirates, October 2023 | `DoW-UAP-D12` | Hard DVIDS identity and D12 content match; PR26 title/date/location conflict with War.gov/local D12 Iraq / May 2022 mission metadata. Treat as a still-image/provenance-control case. |
| `DOD_111688825.mp4` | `DOW-UAP-PR27`, United Arab Emirates, October 2023 | `DoW-UAP-D23` | Hard pair and best new video-review target; four minutes and 57 seconds of IR footage, with contrast acquisition, zoom, tracking, and repeated loss/reacquisition. |
| `DOD_111688970.mp4` | `DOW-UAP-PR31`, Syria, October 2024 | `DoW-UAP-D32` | Hard pair, glare/control lane. |
| `DOD_111688997.mp4` | `DOW-UAP-PR32`, Syria, October 2024 | `DoW-UAP-D32` | Hard pair, glare/control lane. |
| `DOD_111689005.mp4` | `DOW-UAP-PR33`, Syria, October 2024 | `DoW-UAP-D32` | Hard pair, glare/control lane. |

## Standalone Release Identities Added

| Local video | DVIDS release | DVIDS treatment |
|---|---|---|
| `DOD_111689044.mp4` | `DOW-UAP-PR37`, Middle East, 2020 | No oral/written reporter description; nine-second IR contrast clip. |
| `DOD_111689051.mp4` | `DOW-UAP-PR38`, Middle East, 2013 | No oral/written reporter description; 106-second clip with eight-pointed-star-like contrast and visible trail. |
| `DOD_111689057.mp4` | `DOW-UAP-PR39`, Middle East, 2020 | No oral/written reporter description; five-second faint contrast clip. |
| `DOD_111689082.mp4` | `DOW-UAP-PR40`, Middle East, 2020 | No oral/written reporter description; 63-second clip annotated by original reporter with `U/I SMALL THERMAL SIGNATURE`. |
| `DOD_111689133.mp4` | `DOW-UAP-PR46`, INDOPACOM, 2024 | No oral/written reporter description; DVIDS describes a football-shaped contrast with three radial projections. The East China Sea release-index label is a false positive for D28. |
| `DOD_111689167.mp4` | `DOW-UAP-PR48`, INDOPACOM, 2024 | No oral/written reporter description; 99-second centered area-of-contrast track. |
| `DOD_111689168.mp4` | `DOW-UAP-PR49`, Department of the Army, 2026 | No oral/written reporter description; two areas of contrast tracked with zoom/contrast cycling. |
| `DOD_111689759.mp4` | `DOW-UAP-PR43`, Africa, 2025 | No oral/written reporter description; looped two-second event in an 11-second file. |

## Judgment

This backfill increases source discipline more than it increases evidentiary strength. The new hard pairings mostly reinforce the corpus controls: possible missile/birds, probable aircraft, possible UAP/UAV, glare/halo effects, and a still-image case with metadata mismatch.

The exception is `DOD_111688825.mp4` / PR27 / D23. It is long enough and officially paired enough to deserve phase review.

Dedicated PR26/D12 reconciliation note: `research/ufo-pr26-d12-reconciliation.md`

The PR26/D12 pass narrows that caveat. DVIDS PR26 names `DoW-UAP-D12`, and its body text matches local/War.gov D12's north-to-northeast/no-positive-ID description. The unresolved problem is the DVIDS PR26 title/date/location against D12's Iraq / May 2022 mission metadata. Local review of `DOD_111688816.mp4` found a 43.167-second video derivative with frame changes and no sampled red/orange overlay pixels, so PR26/D12 remains a provenance-control case rather than a physical-performance case.

Dedicated phase-review note: `research/ufo-video-pr27-d23-phase-review-notes.md`

The phase review supports the DVIDS acquisition/zoom/center-track/loss-reacquisition sequence, with strong caveats for shoreline, reticle, and water-texture artifacts. It does not validate physical velocity, range, or assignment to either of D23's two UAP lines.

Dedicated manual-validation note: `research/ufo-video-pr27-d23-manual-validation-notes.md`

The validation layer narrows the claim: `175/327` active rows validate as compact-return candidates, with the strongest support in the `207.0s-297.0s` loss/reacquisition interval.

## Sources

- DVIDS PR19: `https://www.dvidshub.net/video/1006056/dow-uap-pr19-unresolved-uap-report-middle-east-may-2022`
- DVIDS PR21: `https://www.dvidshub.net/video/1006059/dow-uap-pr21-unresolved-uap-report-iraq-may-2022`
- DVIDS PR22: `https://www.dvidshub.net/video/1006060/dow-uap-pr22-unresolved-uap-report-syria-july-2022`
- DVIDS PR23: `https://www.dvidshub.net/video/1006062/dow-uap-pr23-unresolved-uap-report-iraq-december-2022`
- DVIDS PR26: `https://www.dvidshub.net/video/1006063/dow-uap-pr26-unresolved-uap-report-united-arab-emirates-october-2023`
- War.gov D12: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d12-mission-report-iraq-may-2022.pdf`
- DVIDS PR27: `https://www.dvidshub.net/video/1006067/dow-uap-pr27-unresolved-uap-report-united-arab-emirates-october-2023`
- DVIDS PR31: `https://www.dvidshub.net/video/1006076/dow-uap-pr31-unresolved-uap-report-syria-october-2024`
- DVIDS PR32: `https://www.dvidshub.net/video/1006078/dow-uap-pr32-unresolved-uap-report-syria-october-2024`
- DVIDS PR33: `https://www.dvidshub.net/video/1006079/dow-uap-pr33-unresolved-uap-report-syria-october-2024`
- DVIDS PR37: `https://www.dvidshub.net/video/1006087/dow-uap-pr37-unresolved-uap-report-middle-east-2020`
- DVIDS PR38: `https://www.dvidshub.net/video/1006088/dow-uap-pr38-unresolved-uap-report-middle-east-2013`
- DVIDS PR39: `https://www.dvidshub.net/video/1006089/dow-uap-pr39-unresolved-uap-report-middle-east-2020`
- DVIDS PR40: `https://www.dvidshub.net/video/1006093/dow-uap-pr40-unresolved-uap-report-middle-east-2020`
- DVIDS PR43: `https://www.dvidshub.net/video/1006159/dow-uap-pr43-unresolved-uap-report-africa-2025`
- DVIDS PR46: `https://www.dvidshub.net/video/1006106/dow-uap-pr46-unresolved-uap-report-indopacom-2024`
- DVIDS PR48: `https://www.dvidshub.net/video/1006110/dow-uap-pr48-unresolved-uap-report-indopacom-2024`
- DVIDS PR49: `https://www.dvidshub.net/video/1006111/dow-uap-pr49-unresolved-uap-report-department-army-2026`

