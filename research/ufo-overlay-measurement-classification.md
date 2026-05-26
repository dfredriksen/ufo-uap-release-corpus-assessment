# Overlay Measurement Classification Matrix

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: PR44/PR051/PR059 positive overlay candidates and PR31/PR32/PR33/PR34/PR36/PR45 negative controls
Status: machine-readable classification and source-request map

## Purpose

This matrix is the control surface for the measurement-overlay exploitation lane.

It separates three things that are easy to conflate:

- visible meter-like labels in public video frames
- display/reticle/track-box state changes
- physical claims about object size, range, speed, or acceleration

The first two are supportable from the public corpus. The third is not supportable without source-system documentation and raw telemetry.

## Tables

Classification matrix:

- `research/ufo-overlay-measurement-classification.csv`

Source-request matrix:

- `research/ufo-overlay-measurement-source-requests.csv`

Validator:

- `scripts/validate_overlay_measurement_classification.py`

No-media CI check:

- `.github/workflows/measurement-overlay.yml`

Scope/completion audit:

- `research/ufo-overlay-measurement-completion-audit.md`

Residual scan plan:

- `research/ufo-overlay-measurement-residual-scan-plan.md`
- `research/ufo-overlay-measurement-residual-scan-plan.csv`

## Current Classification

Positive overlay candidates:

- `PR44`: sustained reticle/track-box-associated `12M -> 11M -> 10M -> 9M` sequence from about `204s` to `266s`.
- `PR44`: frame-localized `11M -> 10M` transition around `233.333-233.367s`.
- `PR44`: label/reticle relation remains stable while the bright object candidate moves down-left.
- `PR051`: repeated `5M` / `5m-style` label in the least-altered original excerpt at `007s`, `011s`, and `012s`.
- `PR051`: repeated `5M` / `5m-style` label in the exit replay around `271s`, `275s`, and `276s`.
- `PR051`: separate reticle-lock display state with `31M-like`, `30M-like`, `13M-like`, and lower-confidence smaller meter-like candidates.
- `PR059`: persistent track-box/target-adjacent `M`/`m`-style suffix label from about `23-277s`, manually read as a changing `36M/33M/10M/<4M/2M/23M-style` sequence with unresolved semantics.

Negative controls:

- `PR31`, `PR32`, `PR33`, `PR34`, `PR36`, and `PR45` show no PR44-style reticle-associated meter-label candidate under the current one-second survey geometry.

## Decision Rule

No current overlay candidate is promoted to a physical measurement.

The allowed classification ceiling is:

> unresolved display annotation or display-state-associated overlay candidate

Promotion would require source evidence that public pixels do not provide:

- native display documentation
- raw or uncompressed source video
- frame-level metadata
- FOV/zoom state
- slant range or range-time series
- platform position/attitude
- gimbal pointing/stabilization state
- chain-of-custody records for altered/replayed material

## Validation

Run:

```powershell
python scripts/validate_overlay_measurement_classification.py
```

The validator checks that:

- every classification row has the expected columns
- support artifacts exist
- every source-request ID referenced by a classification row exists
- controlled-vocabulary fields use known values
- no row promotes a physical size/range/speed/acceleration claim
- the matrix contains both positive candidates and negative controls

## Publication Use

Use this matrix as the source of truth for overlay claims:

- Cite PR44, PR051, and PR059 as positive measurement-like overlay candidates.
- Cite PR31/PR32/PR33/PR34/PR36/PR45 as bounded negative controls.
- Do not cite any overlay row as proof of physical size, distance, speed, or extraordinary motion.
