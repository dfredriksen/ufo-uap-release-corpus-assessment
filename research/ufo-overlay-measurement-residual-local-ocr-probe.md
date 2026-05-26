# Overlay Measurement Residual Local OCR Probe

Owner: Dan Fredriksen
Scope: remaining metadata-only residual rows with local source paths
Status: bounded OCR triage artifact; no derived media committed

## Purpose

This artifact records a display-focused local OCR probe over remaining metadata-only residual rows that already had non-redistributed local source paths. It is a triage layer for telemetry-like display text, not a frame-level absence proof.

## Summary

- Cases probed: `14`
- Sample step: `30` seconds
- OCR rows: `104`
- Meter-label candidate rows: `5`
- `no` rows: `99`
- `yes` rows: `5`

## Case Coverage

| Record ID | OCR rows |
|---|---:|
| `DOW-UAP-PR19` | `4` |
| `DOW-UAP-PR21` | `4` |
| `DOW-UAP-PR22` | `4` |
| `DOW-UAP-PR23` | `4` |
| `DOW-UAP-PR26` | `8` |
| `DOW-UAP-PR28` | `12` |
| `DOW-UAP-PR29` | `4` |
| `DOW-UAP-PR37` | `4` |
| `DOW-UAP-PR39` | `4` |
| `DOW-UAP-PR41` | `16` |
| `DOW-UAP-PR43` | `4` |
| `DOW-UAP-PR46` | `4` |
| `DOW-UAP-PR47` | `16` |
| `DOW-UAP-PR48` | `16` |

## Boundary

OCR text can be noisy on compressed public sensor-display footage. Candidate rows require manual frame/crop review before classification. Non-candidate rows do not prove absence of telemetry labels.

Supporting table:

- `research/ufo-overlay-measurement-residual-local-ocr-probe.csv`
