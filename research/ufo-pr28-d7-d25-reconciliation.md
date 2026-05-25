# UFO PR28 D7/D25 Reconciliation

Owner: Dan Fredriksen
Created: 2026-05-10
Scope: `DOD_111688954.mp4`, DVIDS `DOW-UAP-PR28`, local/War.gov `DoW-UAP-D7`, and local/War.gov `DoW-UAP-D25`

## Bottom Line

`DOD_111688954.mp4` is hard-identified by DVIDS as `DOW-UAP-PR28`, "Unresolved UAP Report, Greece, January 2024." DVIDS also states that the accompanying mission report is `DoW-UAP-D7`.

That report label does not reconcile cleanly with the local/War.gov PDFs:

- DVIDS `PR28` describes a Greece January 2024 event, a diamond-shaped object, about `434 knots`, SWIR-only detectability, and an inverted-teardrop-like area of contrast with a vertical trailing mass.
- Local/War.gov `DoW-UAP-D25` is the Greece January 2024 mission report lane with the SWIR/round-diamond/tail-probe/about-434-knot content.
- Local/War.gov `DoW-UAP-D7` is an Arabian Gulf 2020 lane: a balloon-like UAP, similar to prior 48FW reports, traveling with the winds at `31,000 ft MSL`, with TFLIR visual ID language.

Current treatment:

- Treat `DOD_111688954.mp4` as hard `DOW-UAP-PR28`.
- Treat the matching written-report content as `DoW-UAP-D25`.
- Treat the DVIDS `DoW-UAP-D7` accompanying-report label as an unresolved official-source discrepancy unless DVIDS or War.gov later corrects or explains it.

This is the same class of source problem already documented for `PR29`, where DVIDS says `D8` but local/War.gov content resolves to `D27`.

## Source Check

| Item | Source path or URL | Verified detail |
|---|---|---|
| DVIDS PR28 page | `https://www.dvidshub.net/video/1006073/dow-uap-pr28-unresolved-uap-report-greece-january-2024` | Page title names `DOW-UAP-PR28`, Greece, January 2024; thumbnail filename contains `DOD_111688954`; page metadata states accompanying report `DoW-UAP-D7`. |
| Local source MP4 | `I:\My Drive\UFO\DOD_111688954.mp4` | `15,992,674` bytes; SHA256 `9AA868828E0B7BE178604162A8ABC1E11F0EE6E27D9C48EABBEE4D032A50FD72`. |
| War.gov/local `D25` PDF | `I:\My Drive\UFO\dow-uap-d25-mission-report-greece-january-2024.pdf` | `680,054` bytes; SHA256 `BD5478D2E420F6FF46FB06014E39027E1CAA415F55EFDC9BD70A849FF6990356`; content lane matches Greece/SWIR/round-diamond/434-knot PR28 description. |
| War.gov/local `D7` PDF | `I:\My Drive\UFO\dow-uap-d7-mission-report-arabian-gulf-2020.pdf` | `27,337` bytes; SHA256 `C4CAE44B6AC7B4F4916DDFF140D47B1E2A6DDC80ED72985877C07401D17FD76A`; content lane is Arabian Gulf 2020 balloon-like/wind-traveling UAP. |

Official PDF URLs used for source identity:

- `DoW-UAP-D25`: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d25-mission-report-greece-january-2024.pdf`
- `DoW-UAP-D7`: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d7-mission-report-arabian-gulf-2020.pdf`

## Analytical Implication

PR28 should be promoted from an unreviewed local video to a high-priority reconciliation case. The public MP4 and DVIDS release page are enough to establish release identity, but the report-label mismatch means any downstream matrix row must keep two separate claims apart:

1. `DOD_111688954.mp4` is PR28.
2. The written-report content aligned to PR28 is D25, not local/War.gov D7.

Follow-on work complete: `research/ufo-pr28-d25-video-review-notes.md` now records a one-fps full-clip pass and five-fps SWIR-track pass against the D25 content lane. That review supports the public MP4's compact bright SWIR return and loss/non-reacquisition sequence at image-plane level, but it still does not validate report-derived speed or geometry without telemetry.

