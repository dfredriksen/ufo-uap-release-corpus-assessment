# Overlay Measurement P1 Quicklook Review

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: all five P1 residual overlay targets with locally acquired source MP4s
Status: bounded quicklook/OCR review complete; PR059 promoted as a positive overlay candidate

## Purpose

This note records the P1 follow-on review after all five highest-priority residual overlay targets were acquired outside the repository. It answers a narrow question:

> Which P1 residual assets contain visible PR44/PR051-style or related meter-suffix overlay labels in the public MP4s?

The result is mixed: PR059 is a new positive measurement-like overlay case; PR052, PR058, PR069, and PR073 do not get promoted under the current bounded review.

## Acquisition

The source MP4s were retained outside Git and are not redistributed. The committed acquisition table records DVIDS pages, CloudFront source URLs, local excluded paths, byte sizes, hashes, and OpenCV metadata:

- `research/ufo-overlay-measurement-p1-source-acquisition.csv`

Reviewed source assets:

| Case | Record ID | Source video | Samples | SHA-256 |
|---|---|---:|---:|---|
| PR052 | DOW-UAP-PR052 | `DOD_111719718.mp4` | `496` | `e67b3a3b3d863ef88cc8c4e6b73e9c9bff896506a2962956ed70f508fd8815f5` |
| PR058 | DOW-UAP-PR058 | `DOD_111719800.mp4` | `649` | `610d6dc9da3c72c6a273e2458962fbef10f7caacf2107f7eb9c567d9b289a2e0` |
| PR059 | DOW-UAP-PR059 | `DOD_111719809.mp4` | `292` | `11698020b966a3b38178f9ab66272f49d4400feb178fb269229009fbb08b3365` |
| PR069 | DOW-UAP-PR069 | `DOD_111720700.mp4` | `30` | `7e81fd782a5b98af5cb941b6e5cce865f15324dea41b8c4cf4577f3d02c3fd66` |
| PR073 | DOW-UAP-PR073 | `DOD_111720765.mp4` | `89` | `19538301dd75d63746d3a3cc2da7cdd0418f0372130984b68030a4bb1eb7f48e` |

## Method

The quicklook pass was generated with:

```powershell
python scripts/ufo_overlay_p1_quicklook.py
```

The script samples at a one-frame-per-second cadence, emits full-frame contact sheets, and emits case-specific focus-crop sheets under the ignored derived-artifact directory:

- `research/ufo-derived/overlay-measurement-audit/p1-quicklook/`

A bounded OCR triage probe was also generated:

```powershell
python scripts/ufo_overlay_p1_ocr_probe.py --sample-step-seconds 15
```

The OCR probe is only triage and not an exhaustive all-frame OCR pass. Candidate OCR rows require manual image review; non-candidate rows do not prove absence of telemetry text.

## Findings

| Case | Review coverage | Result | Classification effect |
|---|---:|---|---|
| PR052 | `496` one-fps samples, `25` full sheets, `42` focus sheets, `68` OCR rows | No explicit PR44/PR051/PR059-style meter-label candidate promoted in bounded review. | Not promoted. |
| PR058 | `649` one-fps samples, `33` full sheets, `55` focus sheets, `88` OCR rows | OCR produced one candidate at `75s`; manual review rejected it as target-shape/processing noise, not a label. | Not promoted. |
| PR059 | `292` one-fps samples, `15` full sheets, `25` focus sheets, `40` OCR rows, dedicated label survey | Persistent cyan track-box/target-adjacent `M`/`m`-style suffix label from about `23-277s`. | Promoted to positive overlay candidate; physical claim not promoted. |
| PR069 | `30` one-fps samples, `2` full sheets, `3` focus sheets, `4` OCR rows | Reticle/sensor symbology visible; no PR44/PR051-style explicit meter-like label identified at reviewed sheet scale. | Not promoted. |
| PR073 | `89` one-fps samples, `5` full sheets, `8` focus sheets, `12` OCR rows | Boxed target/reticle display visible; no PR44/PR051-style explicit meter-like label identified at reviewed sheet scale. | Not promoted. |

Supporting machine-readable table:

- `research/ufo-overlay-measurement-p1-review.csv`

PR059-specific support:

- `research/ufo-overlay-measurement-pr059-label-survey.md`
- `research/ufo-overlay-measurement-pr059-label-intervals.csv`

## Evidence Boundary

This review supports the statement:

> All five P1 residual assets were acquired, hashed, sampled at one frame per second, and triaged with a bounded OCR probe. PR059 contains a visible changing meter-suffix-like overlay label; PR052, PR058, PR069, and PR073 were not promoted under this bounded review.

This review does not support these broader statements:

- every frame of every P1 asset has been OCR-reviewed
- non-promoted P1 assets contain no telemetry labels of any kind
- PR059's label is object size, slant range, speed, acceleration, or flight performance
- all remaining P2/P3/P4 residual targets lack telemetry labels

## Publication Use

Use PR059 as a positive display-annotation case alongside PR44 and PR051. Keep the public conclusion bounded: visible labels are unresolved display annotations until source-system documentation or native metadata defines them; this review does not support physical reconstruction.
