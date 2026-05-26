# Overlay Measurement Residual Remote OCR Probe

Owner: Dan Fredriksen
Scope: Release 02 residual rows with preflighted public MP4 URLs but no retained local source MP4
Status: bounded remote-frame OCR triage artifact; no source MP4 or derived media committed

## Purpose

This artifact records a display-focused OCR probe over residual Release 02 public MP4 URLs using temporary remote frame extraction. It is a triage layer for telemetry-like display text, not a source-acquisition manifest and not a frame-level absence proof.

## Summary

- Cases probed: `36`
- Sample step: `30` seconds
- OCR/probe rows: `1096`
- Successful ROI OCR rows: `1096`
- Meter-label candidate rows: `8`
- `no` candidate rows: `1088`
- `yes` candidate rows: `8`

Frame extraction status:
- `ok`: `1096`

## Case Coverage

| Record ID | Probe rows | Candidate rows |
|---|---:|---:|
| `DOW-UAP-PR050` | `4` | `0` |
| `DOW-UAP-PR053` | `4` | `0` |
| `DOW-UAP-PR054` | `32` | `0` |
| `DOW-UAP-PR056` | `32` | `0` |
| `DOW-UAP-PR060` | `40` | `3` |
| `DOW-UAP-PR061` | `40` | `1` |
| `DOW-UAP-PR063` | `40` | `0` |
| `DOW-UAP-PR064` | `4` | `0` |
| `DOW-UAP-PR065` | `8` | `0` |
| `DOW-UAP-PR066` | `8` | `0` |
| `DOW-UAP-PR067` | `40` | `1` |
| `DOW-UAP-PR068` | `12` | `0` |
| `DOW-UAP-PR070` | `8` | `0` |
| `DOW-UAP-PR071` | `8` | `0` |
| `DOW-UAP-PR072` | `4` | `0` |
| `DOW-UAP-PR075` | `4` | `0` |
| `DOW-UAP-PR076` | `40` | `0` |
| `DOW-UAP-PR077` | `40` | `0` |
| `DOW-UAP-PR078` | `40` | `0` |
| `DOW-UAP-PR080` | `40` | `0` |
| `DOW-UAP-PR081` | `40` | `0` |
| `DOW-UAP-PR082` | `40` | `0` |
| `DOW-UAP-PR084` | `36` | `0` |
| `DOW-UAP-PR085` | `40` | `0` |
| `DOW-UAP-PR086` | `8` | `0` |
| `DOW-UAP-PR087` | `40` | `0` |
| `DOW-UAP-PR089` | `40` | `0` |
| `DOW-UAP-PR090` | `40` | `1` |
| `DOW-UAP-PR091` | `40` | `0` |
| `DOW-UAP-PR092` | `40` | `0` |
| `DOW-UAP-PR093` | `8` | `0` |
| `DOW-UAP-PR094` | `40` | `0` |
| `DOW-UAP-PR095` | `40` | `1` |
| `DOW-UAP-PR096` | `12` | `1` |
| `DOW-UAP-PR098` | `144` | `0` |
| `DOW-UAP-PR099` | `40` | `0` |

## Boundary

This probe samples public source URLs directly and does not retain source MP4s. Candidate rows require manual crop/frame review before classification. Non-candidate rows do not prove absence of telemetry labels, and remote sampling does not replace source acquisition, hashing, or all-frame review.

Supporting table:

- `research/ufo-overlay-measurement-residual-remote-ocr-probe.csv`
