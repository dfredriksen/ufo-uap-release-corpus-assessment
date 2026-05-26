# Overlay Measurement P2 Acquired Review

Owner: Dan Fredriksen
Created: 2026-05-26
Scope: preflighted Release 02 P2 source MP4s acquired outside Git
Status: bounded OCR/manual-candidate review complete; no new positive overlay candidate promoted

## Purpose

This review records the classification effect of the acquired-source P2 OCR probe.

The question was:

> Do the nine preflighted Release 02 P2 source videos contain PR44/PR051/PR059-style or related meter-suffix overlay labels at the bounded 30-second display-focused OCR cadence?

## Source Acquisition

The source MP4s were downloaded outside the repository and recorded as `source-files-not-included/` paths in:

- `research/ufo-overlay-measurement-p2-source-acquisition.csv`
- `research/ufo-overlay-measurement-p2-source-acquisition.md`

The source MP4s are not redistributed.

## OCR Review

The OCR probe generated:

- `268` OCR rows
- `1` meter-label candidate row
- `9` P2 record rows covered

Supporting artifact:

- `research/ufo-overlay-measurement-p2-acquired-ocr-probe.md`

## Manual Candidate Review

The only OCR candidate was:

- `DOW-UAP-PR097`
- `90s`
- `center_reticle`
- OCR noise read included `X5 M0`-like text

Manual crop review rejected the candidate. The frame shows reticle brackets and a cyan `N` direction marker, not a visible meter-suffix label. The debug crop was generated under the ignored derived-artifact tree and is not committed.

## Findings

| Record ID | OCR rows | OCR candidates | Classification effect |
|---|---:|---:|---|
| `DOW-UAP-PR055` | `8` | `0` | Not promoted |
| `DOW-UAP-PR057A` | `12` | `0` | Not promoted |
| `DOW-UAP-PR057B` | `12` | `0` | Not promoted |
| `DOW-UAP-PR062` | `40` | `0` | Not promoted |
| `DOW-UAP-PR074` | `40` | `0` | Not promoted |
| `DOW-UAP-PR079` | `36` | `0` | Not promoted |
| `DOW-UAP-PR083` | `40` | `0` | Not promoted |
| `DOW-UAP-PR088` | `40` | `0` | Not promoted |
| `DOW-UAP-PR097` | `40` | `1` | False OCR candidate; not promoted |

Machine-readable review table:

- `research/ufo-overlay-measurement-p2-acquired-review.csv`

## Evidence Boundary

This review supports the statement:

> The nine preflighted Release 02 P2 source videos were acquired outside Git, hashed, and triaged with a bounded 30-second display-focused OCR pass. No new meter-label candidate was promoted.

This review does not support these broader statements:

- every frame of every acquired P2 source video has been OCR-reviewed
- the acquired P2 videos contain no telemetry labels of any kind
- the residual corpus has been exhaustively cleared for measurement overlays

Use the result as bounded triage only.

This is not an exhaustive all-frame absence claim.
