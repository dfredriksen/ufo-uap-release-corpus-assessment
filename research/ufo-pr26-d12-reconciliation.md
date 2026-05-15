# PR26 / D12 Reconciliation

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: reconcile `DOD_111688816.mp4`, DVIDS `DOW-UAP-PR26`, and War.gov/local `DoW-UAP-D12`
Status: reconciliation complete; treat as metadata-mismatch control case

## Bottom Line

`DOD_111688816.mp4` is a hard official DVIDS identity for `DOW-UAP-PR26`, and DVIDS explicitly names `DoW-UAP-D12` as the accompanying mission report. The DVIDS body text also matches the D12 UAP description: one object moving north to northeast, with no positive identification.

The unresolved issue is the release metadata, not the report-content pairing. DVIDS titles PR26 as United Arab Emirates / October 2023 and records `Date Taken: 10.01.2023`, while War.gov/local D12 is an Iraq / May 2022 mission report with initial UAP contact at `202043:00ZMAY22`.

Use PR26 as the official release/video identity and D12 as the matching report-content lane, but preserve the title/date/location mismatch as a provenance caveat. Do not use this case for physical kinematics.

## Source Comparison

| Field | DVIDS PR26 | War.gov/local D12 |
|---|---|---|
| Release/report label | `DOW-UAP-PR26` | `DoW-UAP-D12` |
| Video filename | `DOD_111688816` | DVIDS-stated accompanying report for the video |
| Public title metadata | United Arab Emirates, October 2023 | Iraq, May 2022 |
| Date metadata | DVIDS `Date Taken: 10.01.2023`; DVIDS body says source material came from 2022 | Mission timeline spans `200542:00ZMAY22` to `210036:00ZMAY22`; UAP initial contact `202043:00ZMAY22` |
| Operational context | USCENTCOM AOR, according to DVIDS body | Operation Inherent Resolve, USCENTCOM, OKAS launch/recovery |
| UAP description | Still image from a U.S. military system; original reporter added a red line around the area of interest; D12 described north-to-northeast movement and no positive ID | One UAP, altitude/depth/velocity/trajectory `UNK`; observed at 2043Z flying north to northeast; screener could not get a positive ID |

## Local Video Review

Generated support files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr26_d12_still_review.py`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr26-d12-still-review-dod111688816.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr26-d12-still-review-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr26-d12-still-review-assets.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-phase-review/DOD_111688816/DOD_111688816-sample-contact-sheet.jpg`

Local `DOD_111688816.mp4` review results:

- Duration: `43.167s`
- Frame count: `1295`
- Frame size: `1920x1080`
- Sample count: `12`
- Median mean absolute difference between sampled frames: `9.92`
- Median changed-pixel percentage above threshold 12: `34.3742%`
- Maximum red/orange overlay proxy count: `0`

Interpretation: the local MP4 is not a single frozen still for all 43 seconds. It behaves like a video derivative or presentation around source imagery, with stronger changes early and late and a near-static middle segment from roughly `16s-24s`. The red-line annotation described by DVIDS was not detected in the sampled local MP4 frames, so local analysis should not depend on that overlay being visible.

## Analytic Treatment

- Confidence is high for the DVIDS filename-to-release identity: `DOD_111688816` equals `DOW-UAP-PR26`.
- Confidence is high that DVIDS intended `DoW-UAP-D12` as the accompanying report and that the DVIDS body text matches local/War.gov D12 content.
- Confidence is low for the PR26 title/date/location as event metadata, because it conflicts with the D12 mission report.
- Treat event content as Iraq / May 2022 when analyzing D12, while retaining the official PR26 UAE / October 2023 title as a source-index discrepancy.
- This is a provenance/control case, not a promoted physical-performance case.

## Sources

- DVIDS PR26: `https://www.dvidshub.net/video/1006063/dow-uap-pr26-unresolved-uap-report-united-arab-emirates-october-2023`
- War.gov D12 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d12-mission-report-iraq-may-2022.pdf`
