# Overlay Measurement Residual Remote Review

Owner: Dan Fredriksen
Created: 2026-05-26
Scope: Release 02 residual rows with preflighted public MP4 URLs but no retained local source MP4
Status: bounded remote OCR/manual-candidate review complete; no new positive overlay candidate promoted

## Purpose

This review records the classification effect of the residual remote-frame OCR probe.

The question was:

> Do the remaining Release 02 source-preflighted residual public MP4s contain PR44/PR051/PR059-style or related meter-suffix overlay labels at the bounded 30-second display-focused remote OCR cadence?

## OCR Review

- Records covered: `36`
- OCR/probe rows: `1096`
- Meter-label candidate rows: `8`
- Records with OCR candidates: `6`
- `bounded_residual_remote_ocr_false_ocr_candidate`: `6`
- `bounded_residual_remote_ocr_no_meter_candidate`: `30`

Supporting artifact:

- `research/ufo-overlay-measurement-residual-remote-ocr-probe.md`

## Manual Candidate Review

The eight OCR candidates were reviewed from ignored local candidate crops. All were rejected as terrain, field, shoreline, vessel/wake, reticle, direction-marker, display-geometry, or compression/contrast OCR noise.

Candidate records:

- `DOW-UAP-PR060`: `3` candidate row(s); three OCR candidates at 60s, 90s, and 210s were manually checked and rejected as terrain/shoreline/display-geometry OCR noise; not visible meter labels
- `DOW-UAP-PR061`: `1` candidate row(s); one OCR candidate at 30s was manually checked and rejected as terrain/reticle OCR noise; not a visible meter label
- `DOW-UAP-PR067`: `1` candidate row(s); one OCR candidate at 210s was manually checked and rejected as vessel/wake/reticle OCR noise; not a visible meter label
- `DOW-UAP-PR090`: `1` candidate row(s); one OCR candidate at 90s was manually checked and rejected as field/reticle OCR noise; not a visible meter label
- `DOW-UAP-PR095`: `1` candidate row(s); one OCR candidate at 90s was manually checked and rejected as field/reticle OCR noise; not a visible meter label
- `DOW-UAP-PR096`: `1` candidate row(s); one OCR candidate at 30s was manually checked and rejected as field/reticle OCR noise; not a visible meter label

## Findings

| Record ID | OCR rows | OCR candidates | Classification effect |
|---|---:|---:|---|
| `DOW-UAP-PR050` | `4` | `0` | Not promoted |
| `DOW-UAP-PR053` | `4` | `0` | Not promoted |
| `DOW-UAP-PR054` | `32` | `0` | Not promoted |
| `DOW-UAP-PR056` | `32` | `0` | Not promoted |
| `DOW-UAP-PR060` | `40` | `3` | False OCR candidate; not promoted |
| `DOW-UAP-PR061` | `40` | `1` | False OCR candidate; not promoted |
| `DOW-UAP-PR063` | `40` | `0` | Not promoted |
| `DOW-UAP-PR064` | `4` | `0` | Not promoted |
| `DOW-UAP-PR065` | `8` | `0` | Not promoted |
| `DOW-UAP-PR066` | `8` | `0` | Not promoted |
| `DOW-UAP-PR067` | `40` | `1` | False OCR candidate; not promoted |
| `DOW-UAP-PR068` | `12` | `0` | Not promoted |
| `DOW-UAP-PR070` | `8` | `0` | Not promoted |
| `DOW-UAP-PR071` | `8` | `0` | Not promoted |
| `DOW-UAP-PR072` | `4` | `0` | Not promoted |
| `DOW-UAP-PR075` | `4` | `0` | Not promoted |
| `DOW-UAP-PR076` | `40` | `0` | Not promoted |
| `DOW-UAP-PR077` | `40` | `0` | Not promoted |
| `DOW-UAP-PR078` | `40` | `0` | Not promoted |
| `DOW-UAP-PR080` | `40` | `0` | Not promoted |
| `DOW-UAP-PR081` | `40` | `0` | Not promoted |
| `DOW-UAP-PR082` | `40` | `0` | Not promoted |
| `DOW-UAP-PR084` | `36` | `0` | Not promoted |
| `DOW-UAP-PR085` | `40` | `0` | Not promoted |
| `DOW-UAP-PR086` | `8` | `0` | Not promoted |
| `DOW-UAP-PR087` | `40` | `0` | Not promoted |
| `DOW-UAP-PR089` | `40` | `0` | Not promoted |
| `DOW-UAP-PR090` | `40` | `1` | False OCR candidate; not promoted |
| `DOW-UAP-PR091` | `40` | `0` | Not promoted |
| `DOW-UAP-PR092` | `40` | `0` | Not promoted |
| `DOW-UAP-PR093` | `8` | `0` | Not promoted |
| `DOW-UAP-PR094` | `40` | `0` | Not promoted |
| `DOW-UAP-PR095` | `40` | `1` | False OCR candidate; not promoted |
| `DOW-UAP-PR096` | `12` | `1` | False OCR candidate; not promoted |
| `DOW-UAP-PR098` | `144` | `0` | Not promoted |
| `DOW-UAP-PR099` | `40` | `0` | Not promoted |

Machine-readable review table:

- `research/ufo-overlay-measurement-residual-remote-review.csv`

## Evidence Boundary

This review supports the statement:

> The 36 remaining Release 02 source-preflighted residual public MP4s were triaged with a bounded 30-second display-focused remote-frame OCR pass. No new meter-label candidate was promoted.

The source MP4 not retained or hashed caveat is material: this is a remote triage result, not a source-acquisition result.

This review does not support these broader statements:

- every frame of every residual Release 02 video has been OCR-reviewed
- the residual Release 02 videos contain no telemetry labels of any kind
- the residual corpus has been exhaustively cleared for measurement overlays
- source MP4s have been acquired, retained, or hashed

Use the result as bounded remote triage only. This is not an exhaustive all-frame absence claim and does not replace source acquisition.
