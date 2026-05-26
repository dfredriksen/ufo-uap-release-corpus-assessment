# Overlay Measurement P2 Acquired OCR Probe

Owner: Dan Fredriksen
Scope: preflighted Release 02 P2 source MP4s acquired outside Git
Status: bounded OCR triage artifact; no derived media committed

## Purpose

This artifact records a display-focused local OCR probe over the preflighted P2 Release 02 videos after source acquisition outside the repository. It is a triage layer for telemetry-like display text, not a frame-level absence proof.

## Summary

- Cases probed: `9`
- Sample step: `30` seconds
- OCR rows: `268`
- Meter-label candidate rows: `1`
- `no` rows: `267`
- `yes` rows: `1`

## Case Coverage

| Record ID | OCR rows |
|---|---:|
| `DOW-UAP-PR055` | `8` |
| `DOW-UAP-PR057A` | `12` |
| `DOW-UAP-PR057B` | `12` |
| `DOW-UAP-PR062` | `40` |
| `DOW-UAP-PR074` | `40` |
| `DOW-UAP-PR079` | `36` |
| `DOW-UAP-PR083` | `40` |
| `DOW-UAP-PR088` | `40` |
| `DOW-UAP-PR097` | `40` |

## Boundary

OCR text can be noisy on compressed public sensor-display footage. Candidate rows require manual frame/crop review before classification. Non-candidate rows do not prove absence of telemetry labels.

Supporting table:

- `research/ufo-overlay-measurement-p2-acquired-ocr-probe.csv`

Manual candidate review:

- `research/ufo-overlay-measurement-p2-acquired-review.md`
