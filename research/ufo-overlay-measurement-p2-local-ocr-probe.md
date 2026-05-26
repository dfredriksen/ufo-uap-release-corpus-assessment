# Overlay Measurement P2 Local OCR Probe

Owner: Dan Fredriksen
Scope: P2 residual rows with local source paths listed in the residual scan plan
Status: bounded OCR triage artifact; no derived media committed

## Purpose

This artifact records a lightweight local OCR probe over the P2 residual videos that already had non-redistributed local source paths. It is a triage layer for telemetry-like display text, not a frame-level absence proof.

## Summary

- Cases probed: `6`
- Sample step: `30` seconds
- OCR rows: `128`
- Meter-label candidate rows: `0`
- `no` rows: `128`

## Case Coverage

| Record ID | OCR rows |
|---|---:|
| `DOW-UAP-PR27` | `40` |
| `DOW-UAP-PR35` | `4` |
| `DOW-UAP-PR38` | `16` |
| `DOW-UAP-PR40` | `12` |
| `DOW-UAP-PR42` | `40` |
| `DOW-UAP-PR49` | `16` |

## Boundary

OCR text can be noisy on compressed public sensor-display footage. Candidate rows require manual frame/crop review before classification. Non-candidate rows do not prove absence of telemetry labels, and this pass does not cover P2 rows whose source videos are not yet localized.

Supporting table:

- `research/ufo-overlay-measurement-p2-local-ocr-probe.csv`
