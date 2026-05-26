# PR051 Overlay Label Survey

Owner: Dan Fredriksen
Created: 2026-05-25
Scope: `DOW-UAP-PR051` / `DOD_111719715.mp4`
Status: source MP4 acquired outside repo; interval crop review complete

## Source Acquisition

The official DVIDS page exposes login-gated download rows, but the public asset page embeds a CloudFront MP4 URL that was acquired outside the repo:

- Source page: `https://www.dvidshub.net/video/1007707/dow-uap-pr051-syrian-uap-instant-acceleration`
- Embedded public MP4: `https://d34w7g4gy10iej.cloudfront.net/video/2605/DOD_111719715/DOD_111719715.mp4`
- Local path, not redistributed: `source-files-not-included/DOD_111719715.mp4`
- Bytes: `154585431`
- SHA-256: `034759DFC01CB87C718968F3012A57D89ACAE7BAED3A52D60041A59098DF2007`
- OpenCV metadata: `1280x720`, `30.0 fps`, `9063` frames, `302.1s`

Machine-readable acquisition row:

- `research/ufo-overlay-measurement-pr051-source-acquisition.csv`

## Reproducible Crop Generation

Command:

```powershell
python scripts/ufo_pr051_interval_sheets.py
```

Derived contact sheets are written under ignored local output:

- `research/ufo-derived/overlay-measurement-audit/DOD_111719715-pr051-crops/`

The sheets are inspection aids only. They are not redistributed source media.

## Manual Label Survey

Machine-readable table:

- `research/ufo-overlay-measurement-pr051-label-survey.csv`

Key bounded observations:

- The `5M` / `5m-style` annotation is visible in the least-altered original excerpt at `007s`, `011s`, and `012s`.
- The same `5M` / `5m-style` annotation is visible again in the later replay of the exit interval around `271s`, `275s`, and `276s`.
- The `005s-006s`, `008s-010s`, `013s-019s`, and `020s-021s` samples show label structure or the same label region, but the text is degraded or not reliably readable.
- The reticle-lock / zoomed segment around `249s-257s` shows a different display state with a large box and meter-like suffix values manually read as `31M-like`, `30M-like`, `13M-like`, and lower-confidence `6M-like` / `9M-like` candidates.

## Interpretation

PR051 is now stronger than a single user-provided still:

> The public MP4 contains a persistent measurement-like overlay candidate in the original/replayed tracking interval, including repeated `5M` / `5m-style` visibility near the reticle/object region.

That does not make the label a physical object-size, range, slant-range, or speed measurement.

The strongest supported interpretation is:

> PR051 contains telemetry-like display annotations whose semantics are unresolved. The annotations should be used to request display documentation, raw video, and frame metadata, not to infer extraordinary performance from the altered public release.

## Relation To PR44

PR44 and PR051 now form the core positive overlay pair:

- PR44: sustained reticle/track-box-associated `12M -> 11M -> 10M -> 9M` sequence from about `204s` to `266s`.
- PR051: repeated `5M` / `5m-style` visibility in the least-altered original excerpt and exit replay, plus a separate reticle-lock display state with larger meter-like values.

The pair is useful because both cases show meter-like display annotations near reticle/track symbology. The pair is not enough to decide semantics because neither public clip provides display documentation, FOV/zoom state, slant range, platform state, or raw telemetry.

## Claim Boundaries

Allowed:

- PR051 has a repeated measurement-like overlay candidate in the public MP4.
- The `5M` / `5m-style` label is not merely a one-frame artifact.
- Later reticle-lock segments show a separate display-state sequence with meter-like suffixes.
- Public PR051 motion claims must be bounded because DVIDS states the media was digitally altered before upload and because the key exit is described as sensor tracking stopping.

Not allowed:

- The object is five meters wide.
- The label is definitively range, slant range, object size, or gate size.
- The clip proves instant acceleration or extraordinary performance.
- The replay/altered public segments support physical kinematic reconstruction.

## Next Actions

1. Run frame-level crops around `007s-012s` and `271s-276s` if a publication figure or appendix needs source-frame examples.
2. Add display-documentation requests for the PR051 `5M` / `5m-style` and reticle-lock labels.
3. Keep PR051 as a positive overlay-semantics case but not a physical-performance case until raw telemetry or display documentation appears.
