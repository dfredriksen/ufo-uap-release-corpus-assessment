# UFO Next-Value Roadmap

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: maximum-value next steps after Release 02, telemetry screening, and external-methodology feedback
Status: planning artifact

## Purpose

This roadmap identifies the next work that would most improve the repository's evidentiary value, auditability, and publication readiness.

The current corpus is already broad enough. The highest-value work is no longer more speculative interpretation of compressed clips. It is:

- extracting all explicit measurement-like overlays that the public clips preserve
- separating sensor/display annotations from physical object measurements
- hardening manual-review methods with controls and reproducible criteria
- converting the best unresolved cases into source-request packages
- keeping the public publish set curated and reproducible

## Current Baseline

The repository now contains:

- Release 01 and Release 02 manifest normalization.
- Release 02 video, non-video, and synthesis reviews.
- A ranked evidence ladder.
- Publication figures and validation notes.
- Claim-traceability tooling.
- A source-acquisition manifest and gap table.
- Forensic telemetry notes covering methods, evidence inventory, full-stack application, explanation screening, and recovery methods.
- A measurement-overlay audit that indexes explicit PR44/PR051 candidates and metadata-derived video scan targets.
- A measurement-overlay classification matrix that separates positive candidates, negative controls, unresolved semantics, and source requests.
- A measurement-overlay completion audit and residual scan plan that state the remaining scope: known positives and selected controls are exploited, but `75` metadata-only scan targets remain outside exhaustive frame-level coverage.

The current claim ceiling remains unchanged:

> The release corpus contains credible unresolved operational observations and public media, but the public evidence is insufficient for origin determination, extraordinary physical-performance claims, or independent full physical reconstruction.

## Planning Standard

Rank work by whether it can change one of these outcomes:

1. Raise or lower confidence in a specific high-value case.
2. Turn a vague public claim into a bounded, source-backed measurement statement.
3. Improve reproducibility for a skeptical external reviewer.
4. Produce a source-request packet for missing raw data.
5. Reduce overclaim risk by converting apparent anomalies into explicit ambiguity classes.

Do not prioritize work that only increases pattern density, visual drama, or speculation.

## Ranked Next Steps

| Rank | Workstream | Why It Matters | Concrete Output | Success Criteria |
|---:|---|---|---|---|
| 1 | Measurement-overlay exploitation lane | PR44 has a repo-local `10M` / `10m` candidate, and PR051 now has a source-MP4-confirmed `5M` / `5m-style` reticle annotation. These are the best public handles for telemetry-like extraction. | `ufo-overlay-measurement-audit.md`, `ufo-overlay-measurement-audit.csv`, `ufo-overlay-measurement-classification.md`, `ufo-overlay-measurement-classification.csv`, and `ufo-overlay-measurement-source-requests.csv`. | Every `5m`, `10m`, `10M`, range-box, reticle, and scale-like label is classified as a positive unresolved display annotation, a bounded negative control, or a source-request target; no row promotes physical size/range/speed. |
| 2 | PR051 acquisition and bounded analysis | PR051 is officially titled as an instant-acceleration clip, but DVIDS states the media was digitally altered before upload and describes the key exit as sensor tracking stopping. That makes it a high-value test case and a high-risk overclaim case. | `ufo-pr051-overlay-and-motion-review.md`, `ufo-overlay-measurement-pr051-label-survey.md`, and source-acquisition row for `DOD_111719715` / `DOW-UAP-PR051`. | The repo records official URL, download resolution, file size/hash if retained locally, frame ranges for original vs altered/replayed intervals, and whether the `5M` / `5m-style` label persists across adjacent frames. |
| 3 | Manual-review validation hardening | External review correctly identified that quantitative manual counts need explicit criteria and controls. | Written per-frame validation protocol, blinded re-review sample, control clip pass, and false-positive table. | D23/PR27, PR34/D33, PR36/D38, PR44, and PR051 all use the same acceptance vocabulary, and at least one conventional/control clip is processed identically. |
| 4 | Source-request packet buildout | D58, D28, D33/PR34, PR44, PR051, D44/D57, and Release 02 operational clips need raw data before claims can be promoted. | Case-specific source-request matrix with requested raw video, telemetry, range-time series, platform state, gimbal state, radar tracks, EW logs, and chain-of-custody records. | Every Tier 1/Tier 2 unresolved case has a missing-data request list tied to the specific claim it would test. |
| 5 | Public-repo curation sync | The canonical public target is `ufo-uap-release-corpus-assessment`, while this workspace is the larger working tree. | Publish-set checklist and sync diff from this repo to the curated repo. | Only paper-grade notes, scripts, validation outputs, figures, manifests, and review packets are published; source media and large derived caches remain excluded. |
| 6 | Release 02 targeted frame review | Release 02 expanded breadth, but many video rows are altered, duplicated, or only title-level. The highest-value subset needs bounded frame-level review. | Prioritized review notes for PR050, PR051, PR052-PR056, PR065-PR071, PR077-PR079, PR091, PR093, PR095, and PR098. | Altered clips are held out of kinematic reconstruction; unaltered or original-resolution intervals receive the same overlay/object/control vocabulary as Release 01. |
| 7 | Archive snapshots and citation stability | DVIDS and War.gov pages can change. Source identity should not depend only on live pages. | Archived URL list with access dates and local manifest references. | Every cited official webpage for Tier 1, Tier 2, PR044, and PR051 has an archive/access record or an explicit reason why it could not be archived. |
| 8 | Figure and paper pruning | Figure 5 keyword frequencies are illustrative and partly author-vocabulary-dependent. Publication value may improve by reducing weak visuals. | Figure-retention decision note and revised paper figure callouts if needed. | Every figure supports a necessary claim; illustrative-only visuals are moved to supplement or removed. |

## PR051 Immediate Work Plan

Treat `DOW-UAP-PR051` as a measurement-overlay and provenance-control case before treating it as a motion case.

Required steps:

1. Record official source identity: DVIDS video ID `1007707`, filename `DOD_111719715`, title `DOW-UAP-PR051, "Syrian UAP instant acceleration"`, posted `2026-05-22`, length `00:05:02`, location `SY`.
2. Download or locally acquire the highest useful public MP4 only if it can be stored outside the publish set. Current local source-acquisition row: `research/ufo-overlay-measurement-pr051-source-acquisition.csv`.
3. Hash the retained local file and add it to the acquisition manifest or local-only working inventory.
4. Split the timeline into original, altered, replayed, slowed, inverted, zoomed, and no-content sections.
5. Extract source-resolution crops around the reticle and `5M` / `5m-style` label for the original-resolution interval first.
6. Run adjacent-frame label persistence checks before reading the label as anything. Initial survey: `research/ufo-overlay-measurement-pr051-label-survey.md`.
7. Compare the label against PR44's `10M` / `10m` candidate and against reticle/control clips.
8. Explicitly test these hypotheses:
   - the label is an object-size estimate
   - the label is a range or slant-range readout
   - the label is a track-box/gate/display parameter
   - the label is a reticle or zoom-state annotation
   - the label is an enhancement/replay artifact
   - the label is a human-readable overlay added before the public upload
9. Only after overlay semantics are classified, run image-plane motion review on the original interval.
10. Keep the final PR051 conclusion bounded unless raw sensor telemetry, FOV/zoom state, slant range, platform state, and chain-of-custody records appear.

## Overlay Audit Implementation

The initial exploitation lane is implemented by `scripts/build_ufo_overlay_measurement_audit.py`.

Default fresh-clone pass:

```powershell
python scripts/build_ufo_overlay_measurement_audit.py
```

This produces:

- `research/ufo-overlay-measurement-audit.csv`
- `research/ufo-overlay-measurement-audit.md`

The default pass is intentionally conservative. It records explicit PR44/PR051 measurement-like labels and metadata-derived scan targets from the release manifests. It does not claim that all frames have been inspected.

Local-media pass:

```powershell
python scripts/build_ufo_overlay_measurement_audit.py --scan-local-video --sample-step-seconds 1
```

This optional pass requires excluded MP4s. It writes source crops under `research/ufo-derived/overlay-measurement-audit/`, which remains outside Git. These crops are triage artifacts for manual/OCR review, not publication claims by themselves.

Current exploitation result:

- PR44 focused local-media scan complete for `DOD_111689115.mp4`.
- PR44 manual label-persistence table added at `research/ufo-overlay-measurement-pr44-label-persistence.csv`.
- PR44 label is manually read as `11M` from about `230-233s` and `10M` from about `234-249s`.
- PR44 high-rate transition pass localizes the label change between frame `7000` and frame `7001`, around `233.333-233.367s`.
- PR44 motion-compare pass shows the label stays tied to the reticle/track-box display while the bright object candidate moves down-left; label semantics remain unresolved, so do not treat it as physical size or range.
- PR44 full-label survey extends the sequence to about `204-266s`, manually read as `12M -> 11M -> 10M -> 9M`, reinforcing the display-state interpretation while preserving unresolved physical semantics.
- Direct one-second control scans for PR31, PR32, PR33, PR34, PR36, and PR45 found no PR44-like reticle-associated meter-label candidates under the current survey geometry.
- PR051 public MP4 was acquired outside the repo, hashed, and reviewed with interval crops; it contains repeated `5M` / `5m-style` visibility in the original excerpt and exit replay, plus a separate reticle-lock display state with larger meter-like values.
- Unified classification and source-request tables now map PR44, PR051, and six controls into one auditable decision matrix.
- Completion audit added at `research/ufo-overlay-measurement-completion-audit.md`; it records that the lane is bounded to known positives and selected controls and is not a claim of corpus-wide exhaustive label discovery.
- Residual scan plan added at `research/ufo-overlay-measurement-residual-scan-plan.md`; it prioritizes the `75` metadata-only targets into `5` P1, `15` P2, `50` P3, and `5` P4 follow-up rows.
- P1 source preflight added at `research/ufo-overlay-measurement-p1-source-preflight.md`; all five P1 residual DVIDS pages expose embedded public MP4 URLs, but no source media is redistributed.

## Overlay Measurement Decision Rule

A visible `5m`, `10m`, or similar label should not be promoted to object size unless all of the following are true:

- The label appears in the unaltered/original-resolution segment, not only in a replay, enhancement, threshold, inverted, or zoomed segment.
- The label persists across adjacent frames in a way consistent with native sensor overlay, not compression or editing.
- Its position and behavior are consistent with the target/reticle annotation rather than a generic display parameter.
- Comparable labels in the same sensor family are documented or independently interpretable.
- The public video provides enough context to distinguish size from range, gate width, zoom state, or track-box setting.

If any condition fails, preserve the label as an explicit measurement-like overlay candidate, not as physical object size.

## Work Not Worth Prioritizing Now

- Stronger origin claims from compressed public clips.
- Kinematic claims from altered Release 02 replay segments.
- More keyword-frequency interpretation from author-curated tables.
- Exhaustive historical OCR that does not affect a ranked claim, source-request target, or provenance problem.
- Treating visually striking clips as stronger than report/video pairings, raw telemetry, or source-chain evidence.

## Definition Of Done

This roadmap is complete when:

- A PR051 overlay/motion note exists and is linked from the Release 02 video review.
- The telemetry evidence inventory includes PR051 as a separate repo-local source-acquired case, with source media retained outside the publish set.
- The overlay measurement audit is rebuilt from committed manifests and known candidates.
- Overlay measurement candidates across PR44 and PR051 are classified with the same decision rule, and controls are classified with the same bounded vocabulary.
- Manual-review validation criteria and direct overlay-label control runs are documented.
- Source-request targets are tied to the exact claims they would validate or falsify.
- The curated public repo has only the intended publish set and can pass its reproducibility checks from a fresh clone.
