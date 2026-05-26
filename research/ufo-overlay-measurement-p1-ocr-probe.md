# Overlay Measurement P1 OCR Probe

Owner: Dan Fredriksen
Scope: optional local OCR triage over P1 residual source MP4s
Status: bounded text-probe artifact

## Purpose

This artifact records a local Tesseract OCR probe over sampled P1 residual video crops. It is a triage layer for manual review, not a substitute for frame-level visual validation.

## Summary

- Cases probed: `5`
- Sample step: `15` seconds
- OCR rows: `212`
- Meter-label candidate rows: `2`

## Boundary

OCR text can be noisy on compressed sensor-display footage. Candidate rows require manual frame review before classification. Non-candidate rows do not prove absence of telemetry text.

Supporting table:

- `research/ufo-overlay-measurement-p1-ocr-probe.csv`
