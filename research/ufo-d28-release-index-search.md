# UFO D28 Release-Index Search

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: search for any public Release 01 PR/video pairing for `DOW-UAP-D28`
Status: No hard video pairing found

## Bottom Line

No public release-index or DVIDS source found in this pass hard-pairs `DOW-UAP-D28` with a PR video.

The two closest false positives should be kept separate:

- `DOW-UAP-PR28` is a Greece / January 2024 video. DVIDS identifies filename `DOD_111688954`, length `00:01:06`, and says the accompanying mission report is `DoW-UAP-D7`, with a diamond-shaped SWIR-only UAP at about 434 knots. This is not D28.
- `DOW-UAP-PR46` is an INDOPACOM / 2024 video. DVIDS identifies filename `DOD_111689133`, length `00:00:09`, and says the reporter did not provide oral or written description. It is an East China Sea/INDOPACOM standalone video lane and does not mention D28, AGM-176, MX-20, MX-25, Ayn Al Asad, or the D28 event serial.

D28 should remain a high-value document-only case unless a later official index correction or new release explicitly links it to a video.

## Search Terms Used

- `DOW-UAP-D28`
- `202027ZSEP2024-CENTCOM`
- `AGM-176`
- `MX-20`
- `MX-25`
- `Ayn Al Asad`
- `DOW-UAP-PR28`
- `DOW-UAP-PR46`
- `East China Sea`

## Source Findings

| Source | Finding | D28 impact |
|---|---|---|
| Official D28 PDF | Body-controlled event is Iraq / Ayn Al Asad ROZ Raindrop; event serial `202027ZSEP2024-CENTCOM`; sensor lane is MX-20 / MX-25 IR lens flare after AGM-176 employment. | Confirms D28 document content and Iraq location despite filename/title mismatch. |
| Official DVIDS `PR28` page | `PR28` is Greece, filename `DOD_111688954`, and DVIDS says the accompanying report is `DoW-UAP-D7`. | False positive by number only; not D28. |
| Official DVIDS `PR46` page | `PR46` is INDOPACOM 2024, filename `DOD_111689133`, no written/oral reporter description, football-like contrast object. | False positive by East China Sea label only; not D28. |
| Independent release-index mirrors | D28 is listed as `Mission Report, Iraq, September 2024` and appears as a PDF/document record, not a paired video record. | Cross-check only; does not establish official pairing. |

## Working Rule

Do not use the D28 filename/title `East China Sea` label to infer a relationship to PR46. D28's body metadata points to Iraq / USCENTCOM. PR46's official DVIDS page points to INDOPACOM and has no written report description. They should remain separate until an official source directly links them.

## Next Analytic Move

The next best hard-pair target is the PR28/D25-D7 problem:

- Official DVIDS `PR28` says accompanying report `DoW-UAP-D7`.
- The reported SWIR-only diamond / 434-knot language appears in local `D25`, not local `D7`.
- Local `DOD_111688954.mp4` exists and appears to be the PR28 filename from DVIDS.

This is structurally similar to the PR29 D8/D27 discrepancy and should get its own reconciliation note before any detailed video tracking.

