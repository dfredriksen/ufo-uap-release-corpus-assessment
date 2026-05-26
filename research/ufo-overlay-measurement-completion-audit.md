# Overlay Measurement Completion Audit

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: measurement-overlay exploitation lane
Status: bounded lane complete for known positives, selected controls, and residual OCR triage; corpus-wide exhaustive frame inspection remains out of scope

## Purpose

This audit records what the measurement-overlay lane currently proves, what it does not prove, and what evidence supports that boundary.

The key distinction is:

> The repo has an auditable overlay-exploitation lane for PR44, PR051, PR059, six selected controls, and bounded OCR triage of residual overlay targets. It does not prove that every frame of every public-release video has been exhaustively inspected for every possible telemetry label.

That distinction is important because the public claim should be strong enough to use, but not broader than the evidence.

## Requirement Audit

| Requirement | Current evidence | Status |
|---|---|---|
| Identify explicit measurement-like overlay candidates. | `research/ufo-overlay-measurement-audit.csv` and `research/ufo-overlay-measurement-audit.md` index `83` rows, including `9` explicit candidates and `74` scan-target rows. The residual plan now separates zero still metadata-only rows from thirty-six bounded residual-remote non-promotions, four bounded-reviewed P1 non-promotions, fifteen bounded P2 non-promotions, fourteen bounded residual-local non-promotions, and five selected negative controls. | satisfied for known/manifest-derived candidates; not exhaustive frame-level coverage |
| Exploit PR44 as a positive overlay case. | `research/ufo-overlay-measurement-pr44-full-label-survey.md`, `research/ufo-overlay-measurement-pr44-label-value-intervals.csv`, `research/ufo-overlay-measurement-pr44-transition-pass.md`, and `research/ufo-overlay-measurement-pr44-motion-compare.md`. | satisfied |
| Exploit PR051 as a positive overlay case. | `research/ufo-overlay-measurement-pr051-source-acquisition.csv`, `research/ufo-overlay-measurement-pr051-label-survey.md`, and `research/ufo-pr051-overlay-and-motion-review.md`. | satisfied |
| Compare against negative controls. | `research/ufo-overlay-measurement-control-comparison.md` and per-case control survey CSVs for PR31, PR32, PR33, PR34, PR36, and PR45. | satisfied for selected PR44-style controls |
| Classify overlay candidates without promoting physical claims. | `research/ufo-overlay-measurement-classification.csv` and `research/ufo-overlay-measurement-classification.md`; validator enforces `physical_claim_status=not_promoted`. | satisfied |
| Tie unresolved claims to source requests. | `research/ufo-overlay-measurement-source-requests.csv` maps PR44, PR051, and control-limit claims to raw-data/display-documentation requests. | satisfied |
| Make the lane reproducible without source media. | `.github/workflows/measurement-overlay.yml` validates classification, residual plan consistency, P1/P2/residual review artifacts, path hygiene, script compilation, temporary-output overlay-audit rebuilds, and generated-output drift checks without MP4s. | satisfied |
| Support optional local-media regeneration. | PR44/PR051/PR059, P1 quicklook, and control scripts can rerun when excluded source MP4s are present; derived crops remain under ignored `research/ufo-derived/`. | satisfied with local-source caveat |
| Prove corpus-wide exhaustive overlay absence/presence. | Default audit still reports `74` residual scan-target rows and local-media scan mode `no`; `research/ufo-overlay-measurement-residual-scan-plan.md` separates zero still metadata-only rows from bounded P1/P2/residual-local/residual-remote non-promotions and five selected negative controls. The Release 02 residual remote pass does not retain/hash source MP4s and is not all-frame review. | not satisfied; explicitly out of current claim scope |
| Advance P1 residuals when public source assets are available. | `research/ufo-overlay-measurement-p1-source-acquisition.csv`, `research/ufo-overlay-measurement-p1-quicklook-samples.csv`, `research/ufo-overlay-measurement-p1-ocr-probe.md`, and `research/ufo-overlay-measurement-p1-review.md` record all five P1 source acquisitions outside Git plus one-frame-per-second full-frame/focus-crop review. PR059 is now promoted as a positive overlay candidate. | satisfied for bounded P1 quicklook; not exhaustive all-frame OCR |
| Advance P2 residuals when local source paths already exist. | `research/ufo-overlay-measurement-p2-local-ocr-probe.md` records a 30-second cadence display-focused OCR pass over six local-source P2 videos. No meter-label candidates were promoted. | satisfied for bounded local OCR triage; not exhaustive frame-level review |
| Localize remaining P2 source assets without download. | `research/ufo-overlay-measurement-p2-source-preflight.md` records DVIDS metadata, embedded MP4 URLs, durations, and advertised sizes for the nine remaining P2 Release 02 rows. Total advertised size is `570.51 MB`; no source media is redistributed. | satisfied |
| Acquire and triage preflighted P2 Release 02 sources. | `research/ufo-overlay-measurement-p2-source-acquisition.md`, `research/ufo-overlay-measurement-p2-acquired-ocr-probe.md`, and `research/ufo-overlay-measurement-p2-acquired-review.md` record eight unique source MP4s acquired outside Git for nine P2 records, with hashes and a 30-second display-focused OCR probe. PR097 had one OCR candidate that manual crop review rejected as an `N` marker/texture false positive. | satisfied for bounded acquired-source OCR triage; not exhaustive frame-level review |
| Localize remaining residual source assets without download. | `research/ufo-overlay-measurement-residual-source-preflight.md` records DVIDS metadata, embedded MP4 URLs, durations, and advertised sizes for the remaining thirty-six Release 02 residual rows. Total advertised size is `2641.60 MB`; no source media is redistributed. | satisfied for source localization; not source-acquired/hash-verified |
| Triage remaining Release 01 local-source residuals. | `research/ufo-overlay-measurement-residual-local-ocr-probe.md` and `research/ufo-overlay-measurement-residual-local-review.md` record a 30-second display-focused OCR probe over fourteen local-source Release 01 residual rows. Five OCR candidates were manually rejected as direction-marker, reticle, terrain/edge, or texture OCR noise. | satisfied for bounded local OCR triage; not exhaustive frame-level review |
| Triage remaining Release 02 source-preflighted residuals without full download. | `research/ufo-overlay-measurement-residual-remote-ocr-probe.md` and `research/ufo-overlay-measurement-residual-remote-review.md` record a 30-second display-focused remote-frame OCR probe over thirty-six Release 02 residual public MP4 URLs. Eight OCR candidates across six records were manually rejected as terrain, field, shoreline, vessel/wake, reticle, direction-marker, display-geometry, or compression/contrast OCR noise. | satisfied for bounded remote OCR triage; not source-acquired/hash-verified or exhaustive frame-level review |

## Current Evidence Ceiling

The current overlay lane supports these claims:

- PR44 has a sustained reticle/track-box-associated meter-like sequence manually read as `12M -> 11M -> 10M -> 9M`.
- PR051 has repeated `5M` / `5m-style` label visibility in the acquired public MP4 and separate reticle-lock meter-like candidates.
- PR059 has a persistent track-box/target-adjacent `M`/`m`-style label sequence from about `23-277s`; exact values vary and semantics remain unresolved.
- Six selected controls did not reproduce a PR44-style reticle-associated meter-label sequence under the current one-second survey geometry.
- PR052, PR058, PR069, and PR073 were not promoted under the bounded P1 quicklook/OCR review.
- PR27, PR35, PR38, PR40, PR42, and PR49 were not promoted under the bounded P2 display-focused local OCR probe.
- PR055, PR057A, PR057B, PR062, PR074, PR079, PR083, PR088, and PR097 were acquired outside Git and not promoted under bounded acquired-source P2 OCR review; PR097's single OCR candidate was manually rejected as an `N` marker/texture false positive.
- Fourteen Release 01 residual local-source rows were not promoted under bounded residual-local OCR review; five OCR candidates were manually rejected as direction-marker, reticle, terrain/edge, or texture false positives.
- Thirty-six Release 02 residual public MP4 URLs were sampled with bounded 30-second remote-frame OCR; eight OCR candidates across six records were manually rejected as visual/OCR noise, and no new meter-label candidate was promoted. Source MP4s were not acquired, retained, or hashed.
- All positive overlay labels remain unresolved display annotations, not physical size, range, speed, or acceleration measurements.

The current overlay lane does not support these claims:

- every public-release frame has been inspected for all telemetry labels
- PR44 or PR051 labels are physical object size or range measurements
- PR051 proves instant acceleration or extraordinary physical performance
- negative controls prove no telemetry-like labels exist elsewhere in the corpus

## Residual Work

Residual work is still useful, but it should be framed as follow-up rather than a blocker for the current bounded overlay lane:

1. Acquire and hash the thirty-six Release 02 residual MP4s outside the repo only if a stronger source-retained claim is needed. The bounded remote-frame OCR triage is complete, but the advertised source total remains `2641.60 MB`.
2. Add crop presets for non-PR44 display geometry, especially PR051-style original-excerpt labels and reticle-lock labels.
3. Add known-conventional or source-documented display examples if available, so false-negative behavior can be tested beyond the selected UAP corpus controls.
4. Update `research/ufo-overlay-measurement-classification.csv` only when a new visible label is manually reviewed and bounded by the same decision rule.
5. Continue residual work only with source-localization/acquisition discipline and no redistribution of source media.

## Publication Guidance

Use this language:

> We identified and exploited three positive measurement-like overlay cases, PR44, PR051, and PR059, and compared PR44-style label behavior against six selected controls. The labels are telemetry-like display annotations with unresolved semantics, not physical measurements.

Avoid this language:

> We found every telemetry label in the release corpus.

The second statement is not supported by the current audit because `74` residual scan-target rows remain as bounded non-promotions or selected controls, including thirty-six Release 02 rows that were remote-reviewed but not source-retained/hash-verified and not exhaustively all-frame cleared.
