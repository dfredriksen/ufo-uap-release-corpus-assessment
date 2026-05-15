# UFO File Release Analysis Thread

Owner: Dan Fredriksen
Started: 2026-05-09
Source files: official public UFO/UAP release files, not redistributed in this repository
Status: Open analysis thread

## Purpose

Create a durable analysis thread for the recent UFO/UAP file releases collected from public sources. The goal is to inventory the corpus, separate primary records from duplicates and media, extract the strongest factual claims, and build a traceable findings log.

## Initial Inventory

Current folder snapshot:

- Total files: 170
- Total size: about 4.24 GB
- PDFs: 91
- MP4 videos: 41
- JPG images: 34
- PNG images: 4

Major visible groups:

- Historical FBI / archival PDFs, including `65_hs1-834228961_62-hq-83894_*`, `38_143685_box7_incident_summaries_*`, and older general/incident records.
- DOW / DoD UAP mission reports and range-fouler debriefs, mostly named `dow-uap-d*.pdf`.
- DoD video files, mostly named `DOD_*.mp4`, including some duplicate numbered copies.
- NASA Apollo/Gemini/Skylab transcripts and Apollo still images.
- State Department cables for Papua New Guinea and Kazakhstan.
- FBI photo sets named `fbi-photo-a*` and `fbi-photo-b*`.
- Recent slide or summary material, including `western_us_event_slides_5.08.2026.pdf` and `2024-04-30-composite-sketch.pdf`.

## Working Method

1. Preserve source files in place. Do not rename, move, delete, or overwrite Drive files during analysis.
2. Build a manifest from file metadata: name, path, extension, byte size, modified time, hash, inferred source, inferred date, and duplicate group.
3. Extract text from PDFs where available. For scanned PDFs, OCR only copies or derived text outputs, not the source files.
4. For videos and images, extract metadata, representative frames, and visual observations separately from factual conclusions.
5. Classify each file by evidentiary value:
   - primary official record
   - secondary briefing or slide deck
   - media artifact
   - duplicate or variant
   - low-value/noise
6. Every claim must cite the local filename and, for PDFs, a page or excerpt location when possible.
7. Separate "what the document says" from "what is corroborated."

## Initial Priority Order

1. Recent operational reports: `dow-uap-d*.pdf`, especially mission reports and range-fouler debriefs from 2020-2025.
2. Recent summary artifacts: `western_us_event_slides_5.08.2026.pdf`, `2024-04-30-composite-sketch.pdf`, and `dow-uap-pr20.pdf`.
3. DoD videos: deduplicate `DOD_*.mp4`, then sample frames and durations.
4. FBI photo sets: group the `fbi-photo-a*` and `fbi-photo-b*` images with any linked PDFs or serial files.
5. NASA transcripts and imagery: extract exact quoted mission-context language before interpreting.
6. Large historical FBI archive sections: process after the smaller modern files because they are high-volume and likely OCR-heavy.

## Open Questions

- Which release source produced this folder: AARO, DoD FOIA, National Archives, FBI Vault, congressional release, or mixed manual download?
- Are the duplicate MP4s byte-identical or separate versions?
- Do the `dow-uap-d*` PDFs contain embedded text, or do they require OCR?
- Which files contain direct sensor metadata, pilot reports, or chain-of-custody details versus narrative summaries?
- Which files are most probative for a "credible official incident" list?

## Findings Log

### 2026-05-09 First Pass: Folder And Modern Reports

Tooling available locally:

- `pdftotext` for embedded PDF text extraction
- `ffprobe` / `ffmpeg` for video metadata and frame extraction
- Tesseract for OCR where PDFs or images are scan-only

Folder location confirmed as `source-files-not-included`. Analysis ran against the local non-redistributed source corpus.

Generated supporting files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-manifest.csv`: lightweight metadata manifest for all 170 files.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-duplicate-candidates.csv`: duplicate candidates grouped by identical byte size.

Full SHA-256 hashing was started but stopped because the Drive-mounted corpus was slow to hydrate/read. Use targeted hashing later on duplicate candidates and high-value files.

First extraction notes:

- `western_us_event_slides_5.08.2026.pdf` has readable embedded text. It summarizes four Western U.S. sighting clusters: orange objects reportedly launching smaller red objects, a large orange object near a rock pinnacle, a low "dark kite" object with red/white lights, and a later "transparent kite" object seen by some witnesses with NVGs or naked eye.
- `2024-04-30-composite-sketch.pdf` yielded no useful text through `pdftotext`; treat as image-only and send to image/OCR review.
- `dow-uap-d8-mission-report-djibouti-2025.pdf` has a readable UAP line: two round white-hot UAPs moving south at about 240 nautical miles per hour, with location/observer details partly redacted.
- `dow-uap-d50-email-correspondence-indopacom-april-2025.pdf` records that two INDOPACOM UAP tearlines were approved at the unclassified level. The reported observations were 12 seconds and 23 seconds, altitude/speed unknown, no interference noted.
- `dow-uap-d4-mission-report-arabian-gulf-2020.pdf` has a concise readable UAP line: a possible UAP near a redacted location, altitude not estimated, velocity estimated around 321 knots, with speed increase and eastward direction change.
- `dow-uap-d5-mission-report-arabian-gulf-2020.pdf` contains at least two readable UAP lines: one object at FL160-FL170 at about 40 knots, and two possible UAPs later estimated around 278 knots with speed/direction change.
- `dow-uap-d7-mission-report-arabian-gulf-2020.pdf` describes a UAP that looked balloon-like and similar to prior 48FW reports.
- `dow-uap-d38-range-fouler-debrief-middle-east-may-2020.pdf` describes a solid white object crossing an ISR field of view, reacquisition after temporary loss, apparent erratic movement over water, and 4x zoom before track loss.
- `dow-uap-d44-range-fouler-arabian-sea-october-2020.pdf` describes tracking a round cold object in IR over the Gulf of Aden, with sensor geometry values present.
- `dow-uap-d56-range-fouler-debrief-arabian-sea-august-2020.pdf` reports three possible unidentified small air contacts over the North Arabian Sea, with negative ES, radar track, and IFF track, and no interaction.
- `dow-uap-d57-mission-report-gulf-of-aden-september-2020.pdf` describes a round cold object in IR over the Gulf of Aden, with slant range and ground range values present.
- `dow-uap-d58-range-fouler-debrief-na-october-2020.pdf` includes a report of radar lock and two IR-significant contacts, with one range fouler circling around another.
- `dow-uap-d75-mission-report-gulf-of-aden-july-2024.pdf` has a readable line indicating one UAP observed at `140517ZJUL24` in the Gulf of Aden area, with key details redacted.

Triage implications:

- Best first evidence lane: small modern `dow-uap-d*.pdf` files with embedded text, because they are faster to parse and appear to contain structured military reporting lines.
- Best corroboration lane: match `DOD_*.mp4` video IDs against the reports by date, geography, and any visible metadata. Several MP4s are duplicate filenames with `(1)` or `(2)` suffixes and should be hashed before review.
- Highest OCR burden: large historical FBI PDFs and image-only sketch/slide artifacts.
- Treat all coordinates, units, speeds, and classification markings as document claims until cross-checked against another file or public release metadata.

### 2026-05-09 Detailed Modern Report Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/ocr/`: OCR outputs and page images for the three encrypted/no-copy modern reports that `pdftotext` could not extract.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-priority-incidents.md`: ranked digest of the strongest modern records and control/caveat records.

Extraction updates:

- `dow-uap-d60-mission-report-persian-gulf-august-2020.pdf`: OCR recovered a one-UAP FMV observation at 0726Z with no mission impact.
- `dow-uap-d63-mission-report-strait-of-hormuz-october-2020.pdf`: OCR recovered mission narrative language saying one UAP was observed at 1829Z, but did not recover a detailed observation section clearly enough for ranking.
- `dow-uap-d65-mission-report-persian-gulf-july-2020.pdf`: OCR recovered three unidentified-aerial-phenomenon observations at 1830Z, 1920Z, and 2345Z, all in the same broader Arabian Gulf / Strait of Hormuz / Gulf of Oman mission context.

Detailed takeaway:

- The strongest evidentiary lane is the modern structured-report set, not the large historical archive. These records repeatedly include mission timing, platform/sensor context, observed behavior, and formal UAP or range-fouler fields.
- The best single sensor-event candidate so far is `dow-uap-d28-mission-report-east-china-sea-2024.pdf`, because it reports a high-speed heat-source crossing sensor fields between munition release and impact, with MX-20/MX-25 lens flare language and no reported additional aircraft in the airspace.
- The best unusual object-description candidate so far is `dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf`, which reports a glowing hot spherical object with a vertical cylindrical pole/bar underneath, moving at 140 knots over water.
- The best sensor-geometry cluster is the range-fouler set: `d38`, `d44`, `d56`, `d57`, and `d58`. This cluster includes IR observations, slant/ground range fields, intermittent tracking, negative ES/radar/IFF in one case, and radar-lock / target-pod / jamming language in another.
- A Persian Gulf / Strait of Hormuz 2020 pattern cluster is now visible across `d4`, `d5`, `d60`, `d61`, `d62`, `d63`, `d64`, and `d65`. Individually many entries are sparse, but together they justify a timeline pass.
- The Western U.S. 2026 slide deck is the strangest witness-narrative artifact reviewed so far. It is not yet the strongest evidence artifact because it is a briefing/summary layer rather than a raw report or sensor record.
- The corpus includes its own cautionary controls: `d10` says several UAP fit possible bird profiles and dust hindered FMV collection; `d32` appears to be glare/halo on FMV and was assessed benign; `d7` is balloon-like and wind-traveling; `d18` is explicitly UAP/UAV ambiguous.

Current working conclusion:

The material supports a serious unresolved-observation thesis: official records contain multiple structured reports of UAP, possible UAP, range-fouler, and unknown flying-object events that were not resolved inside the released documents. It does not, on this pass, support a stronger claim of non-human technology, recovered material, or a single unified phenomenon without media correlation and cross-document corroboration.

### 2026-05-09 Timeline Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-modern-event-timeline.csv`: normalized event rows for the modern UAP/UFO subset.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-modern-event-timeline.md`: narrative summary of the emerging timeline and correlation gaps.

Timeline findings:

- The densest extracted cluster is maritime: Arabian Gulf, Persian Gulf, Strait of Hormuz, Gulf of Oman, North Arabian Sea, Gulf of Aden, Greece/Eastern Mediterranean, and UAE over-water events.
- 2020 is the largest cluster year in the modern extracted set so far. It includes concise mission-report UAP lines, OCR-recovered UAP observations, and range-fouler debriefs.
- The timeline does not show one consistent object type. It shows multiple reporting lanes and varied object descriptions: round/circular, diamond/probe, triangular/metallic, glowing sphere with pole/bar, white-hot UAPs, cold IR objects, and witness-narrative kite/orb descriptions.
- The strongest analytic structure remains evidence-lane based: structured mission reports, range-fouler forms, tearline/email metadata, briefing summaries, and historical/media artifacts.
- The current MP4 filenames do not expose report IDs. Until video overlays, embedded metadata, or release packaging links videos to specific event rows, the videos should be treated as a media pool rather than directly correlated evidence.

### 2026-05-09 Targeted Duplicate Hash Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-targeted-duplicate-hashes.csv`: SHA-256 hashes for same-size duplicate candidates only.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-targeted-duplicate-summary.csv`: group-level duplicate summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dedupe-summary.md`: narrative duplicate-media summary.

Duplicate findings:

- Every same-size candidate group hashed as identical within its group.
- The MP4 set drops from 41 files to 28 unique videos after exact duplicate copies are excluded from review.
- Two PDF duplicate groups were also confirmed: the `dow-uap-d23` duplicate and the `59_214434_sp_16` filename variant.
- No source files were deleted or modified.

Frame extraction status:

- Local `ffmpeg.exe` and `ffprobe.exe` resolve to zero-byte WinGet link stubs.
- Python OpenCV is not installed in the active Python environment.
- Windows Shell metadata remains sufficient for durations and dimensions, but not for reliable video contact sheets.

### 2026-05-09 Video Contact Sheet Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-unique-video-review-list.csv`: 28-video canonical review list after dedupe.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-contact-sheet-index.csv`: contact sheet path and sample interval for each unique video.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-contact-sheets/*.jpg`: derived contact sheets.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-contact-sheet-notes.md`: first visual triage of the media pool.

Media findings:

- The video pool is mixed. It contains potential UAP/range-fouler media, operational context media, and likely non-UAP/administrative material.
- Higher-priority video candidates for frame-by-frame review include `DOD_111689115.mp4`, `DOD_111688825.mp4`, `DOD_111689090.mp4`, `DOD_111689011.mp4`, `DOD_111689030.mp4`, `DOD_111689083.mp4`, `DOD_111689142.mp4`, `DOD_111689123.mp4`, `DOD_111688964.mp4`, and `DOD_111689022-1920x1080-9000k.mp4`.
- Lower-priority or contextual items include a NASA-logo-only video, urban/compound ISR clips, a building strike/explosion clip, boat/port context, and an aircraft-like centered target.
- The contact sheets do not yet correlate videos to report rows. The next media step is higher-resolution frame extraction from the high-priority videos and comparison against the modern event timeline.

### 2026-05-09 Video Second-Pass Crop Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-second-pass-index.csv`: index of second-pass center-crop sheets and timed frame directories.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/center-crop-sheets/*.jpg`: higher-resolution center-crop sheets for ten priority videos.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-second-pass/timed-frames/*/*.jpg`: representative timed full frames.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-second-pass-notes.md`: second-pass visual triage.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-report-correlation-candidates.csv`: tentative video-to-report-lane candidate map.

Second-pass media findings:

- The strongest video candidates are now `DOD_111689115.mp4`, `DOD_111689090.mp4`, and `DOD_111688964.mp4`.
- `DOD_111689115.mp4` is the best over-water/range-fouler candidate: it begins with a vessel and later shows a small bright object/point near the reticle, including boxed/range-like annotations.
- `DOD_111689090.mp4` is the best multi-contact candidate because multiple small point-like returns are visible across the sensor field.
- `DOD_111688964.mp4` is a short, strong candidate because a bright object/point is visible over a water-like background with track-box changes.
- `DOD_111689123.mp4` and `DOD_111689142.mp4` remain interesting object/track candidates, but the report lane is unclear.
- `DOD_111689022-1920x1080-9000k.mp4` is downgraded toward a control/glare/bird/cloud lane unless full-motion review shows otherwise.

Current correlation status:

No hard report-to-video match is established yet. The best current correlation is by evidence lane: over-water IR point tracks likely belong with the 2020 range-fouler cluster; multiple point returns may belong with `d56` or `d58`; cloud/sky material may belong with caveat/control records such as `d10` or `d32`.

### 2026-05-09 Video Motion Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-motion-pass-index.csv`: one-frame-per-second extraction index for the strongest three videos.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-motion-segment-sheet-index.csv`: segment contact-sheet index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689115.csv`: first compact-return table for the strongest clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689115-ranges.csv`: grouped detection intervals for the strongest clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-source-overlay-dod111689115.csv`: source-resolution overlay crop/OCR index for the strongest clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-ffmpeg-metadata-dod111689115.txt`: source MP4 container metadata for the strongest clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-point-count-dod111689090.csv`: raw compact-point table for the multi-contact candidate.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-point-count-dod111689090-strong.csv`: stricter bright-point count table for the multi-contact candidate.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-point-count-dod111689090-ranges.csv`: grouped bright-point detection intervals.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-point-count-dod111689090-segment-summary.csv`: segment-level point-count summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-point-count-notes-dod111689090.md`: dedicated `DOD_111689090` point-count analysis.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-high-rate-review-dod111689090.csv`: high-rate review index for the two-candidate windows.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-ffmpeg-metadata-dod111689090.txt`: source MP4 container metadata for the multi-contact candidate.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-high-rate-review-dod111688964.csv`: high-rate review index for the full short clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-high-rate-notes-dod111688964.md`: dedicated high-rate analysis for the short over-water clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111688964-fps5.csv`: preliminary bright-blob table for the short over-water clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111688964.csv`: selected-frame manual track for the short over-water clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-full-frame-stills-dod111688964.csv`: full-frame still index for key track-box moments.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-ffmpeg-metadata-dod111688964.txt`: source MP4 container metadata for the short over-water clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/one-fps-center-crops/*/*.jpg`: one-frame-per-second center crops.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/segment-sheets/*.jpg`: segmented motion sheets.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/overlay-crops/DOD_111689115/*`: cropped/zoomed overlay images and OCR outputs.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/source-overlay/DOD_111689115/*`: source-resolution overlay full frames, crops, and OCR outputs.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-motion-pass-notes.md`: motion-pass findings.

Motion-pass findings:

- `DOD_111689115.mp4` is now the strongest media candidate. It has over-water vessel context followed by persistent small bright point returns near the reticle, including later boxed/range-like annotation behavior.
- The first compact-return table for `DOD_111689115.mp4` supports the visual read: after the opening vessel/context segment, compact bright returns recur at one-frame-per-second sampling, with the strongest grouped interval running from about second 154 through second 243.
- A targeted overlay crop/OCR pass on `DOD_111689115.mp4` recovered only a visible `10M`/`10m`-like label beside the track box. It did not recover date-time, coordinates, platform, or report-ID metadata.
- A second source-resolution overlay pass on `DOD_111689115.mp4` reached the same result: `10M`/`10m` is visible, but no hard-link metadata is readable.
- Source MP4 container metadata for `DOD_111689115.mp4` shows a `2026-05-08T01:20:45Z` creation time and `Elemental H.264` encoder, which appears to be file/transcode metadata rather than event metadata.
- `DOD_111689090.mp4` remains the best multi-contact candidate. The motion sheets show repeated faint point-like returns across a long low-texture sequence, with late vessel/over-water context, but the returns are sometimes near the compression/noise threshold.
- A strict bright-point count for `DOD_111689090.mp4` found 211 sampled frames with one strong bright point, 4 sampled frames with two strong bright-point candidates, and none with three or more. This weakens a direct `d56` three-contact visual match and leaves only a limited count-compatible lane for `d58`.
- A higher-rate review of those two-candidate moments further weakens the multi-contact interpretation. The best description is now a persistent single bright-point clip with intermittent weak secondary specks and later dark vessel/scene context.
- `DOD_111688964.mp4` is a clean short candidate: a 22-second water-like sequence with a bright point/object and changing track-box behavior.
- A full-clip 5 fps review strengthens `DOD_111688964.mp4`: the bright object persists through the useful sequence and appears near changing track-box symbology. It is now stronger than `DOD_111689090.mp4` as a visual media anchor, though still not a hard report match.
- A selected-frame manual track for `DOD_111688964.mp4` supports that interpretation: the object moves substantially relative to the reticle and is repeatedly bracketed or overlapped by sensor track-box symbology.
- Full-frame stills for `DOD_111688964.mp4` preserve the wider sensor context at key track-box moments, but no date-time group, coordinates, platform, or report ID is visible.
- A local packaging/name search did not establish a specific pairing between `DOD_111688964.mp4` and `d38`, `d44`, `d57`, or `d58`.
- The video evidence still does not establish a hard report-to-video match. The strongest correlation remains at the evidence-lane level: these clips plausibly align with over-water range-fouler reports such as `d38`, `d44`, `d56`, `d57`, and `d58`, but the derived frames do not yet expose a readable date-time group, coordinates, or report ID.

Updated current media conclusion:

The media pool now gives the modern report set stronger visual context, especially for over-water sensor events. It still supports the same disciplined conclusion: the release contains unresolved official reports and candidate sensor videos, but the reviewed material does not prove origin or a unified phenomenon.

### 2026-05-09 DVIDS Release-Index Correlation Pass

Generated supporting files added or updated in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.csv`: structured matrix of local reports, local videos, DVIDS release identities, and confidence levels.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.md`: narrative report-video correlation summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-notes.md`: first dedicated anchor note for the hard `DOD_111689030` / `DoW-UAP-D38` pair.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-report-correlation-candidates.csv`: updated candidate map with hard DVIDS pairings and corrected `PR` versus `D` nomenclature.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-high-rate-notes-dod111688964.md`: updated `DOD_111688964` notes with the official `PR29` / `D8` pairing and local `D8` mismatch.

Release-index findings:

- `DOD_111689030.mp4` is now the strongest hard report-video anchor. DVIDS identifies it as `DOW-UAP-PR36`, Middle East, May 2020, and explicitly states that the accompanying Range Fouler report is `DoW-UAP-D38`.
- A qualitative re-review of the existing `DOD_111689030` contact sheets supports the D38/PR36 lane: initial maritime subject matter, then a small bright contrast area over water texture, with zoom/contrast/symbology changes. A quantitative tracking table still needs a working video decoder because local `ffmpeg`/`ffprobe` resolve to zero-byte WinGet stubs and Python video/image libraries are not installed.
- `DOD_111689011.mp4` is externally paired to `DOW-UAP-PR34` / `DoW-UAP-D33`, Greece, October 2023.
- `DOD_111689022-1920x1080-9000k.mp4` is likely the local export variant of DVIDS filename `DOD_111689022`, paired to `DOW-UAP-PR35` / `DoW-UAP-D35`, Greece, October 2023.
- Local text reconciliation confirms the DVIDS summaries for `D33` and `D35`: `D33` contains the near-ocean-surface, multiple 90-degree-turns, estimated 80 mph language; `D35` contains the near-ocean-surface, toward-land language.
- `DOD_111688964.mp4` is externally paired to `DOW-UAP-PR29` / `DoW-UAP-D8`, United Arab Emirates, June 2024. However, the local file named `dow-uap-d8-mission-report-djibouti-2025.pdf` describes two round white-hot UAPs near Djibouti in 2025, so the local `D8` source appears mismatched or separately packaged.
- `DOD_111689115.mp4` is externally identified as `DOW-UAP-PR44`, Middle East, 2020. It remains the strongest visual media candidate from the local motion pass, but `PR44` must not be conflated with local report `DoW-UAP-D44`; the DVIDS page does not state an accompanying written report.
- `DOD_111689090.mp4`, `DOD_111689123.mp4`, `DOD_111689142.mp4`, and `DOD_111689083.mp4` now have hard DVIDS release identities (`PR42`, `PR45`, `PR47`, and `PR41` respectively), but no DVIDS-stated accompanying `D` report was found in this pass.

Updated current correlation conclusion:

The corpus now has at least one hard report-video pair (`DOD_111689030` with `DoW-UAP-D38`) plus several official release identities. The prior evidence-lane analysis remains useful, but release-index metadata should now take priority over visual similarity when assigning MP4s to specific reports.

### 2026-05-10 D38 Quantitative Anchor Pass

Generated supporting files added or updated in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_anchor_video_pass.py`: repeatable OpenCV/FFprobe extraction and compact bright-candidate detector.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-extraction-index.csv`: extraction artifact index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-timeline.csv`: structured DVIDS/local phase alignment table.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-ffmpeg-metadata-dod111689030.txt`: source metadata for `DOD_111689030.mp4`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030.csv`: one-fps compact bright-candidate table.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030-ranges.csv`: one-fps detector-active ranges.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030-fps5.csv`: five-fps compact bright-candidate table.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-object-position-dod111689030-fps5-ranges.csv`: five-fps detector-active ranges.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/one-fps-center-crops/DOD_111689030/*`: one-fps center-crop frames.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/high-rate/DOD_111689030/fps5-center-crops/*`: five-fps center-crop frames.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/segment-sheets/DOD_111689030/*`: one-fps and five-fps contact sheets.

Quantitative findings:

- The source MP4 reads as 1920x1080 H.264, 30 fps, 4121 frames, 137.366667 seconds.
- The strongest local quantitative anchor is `50-87s`.
- From `50-75s`, inside DVIDS's `00:20-01:15` generally-in-field interval, the one-fps table has 26/26 medium-or-strong detections and the five-fps table has 124/126 medium-or-strong detections.
- From `76-87s`, immediately after the DVIDS `01:16` zoom/narrow-field point, the one-fps table has 12/12 strong detections and the five-fps table has 54/56 strong detections.
- Later windows (`91-108s`, `110-121s`, `127-134s`) align with the DVIDS later zoom/reticle/loss sequence, but are weaker for object-position claims because the zoomed water texture produces more detector ambiguity.

Updated D38 judgment:

`DOD_111689030.mp4` is now the project's hard report-video anchor. The pairing itself is established externally by DVIDS. The local extraction supports the DVIDS-described timeline and gives a defensible audit track for the strongest `50-87s` interval. After the manual-validation pass below, the remaining caveat is that final speed/trajectory work still needs a denser independent manual marking pass.

### 2026-05-10 D38 Manual Validation Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_manual_review_assets.py`: exports raw one-fps crops and zoomed candidate patches for manual review.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-manual-review-assets.csv`: index of manual-review frames and candidate patches.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-manual-track-dod111689030.csv`: manually accepted one-fps track table for `50s-87s`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-manual-validation-notes.md`: manual validation memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/manual-validation/DOD_111689030/*`: raw crops, candidate patches, and review sheets.

Manual validation findings:

- Reviewed raw one-fps crops and zoomed patches from `50s` through `87s`.
- Accepted all 38 one-second samples as containing a visible compact bright object/contrast candidate.
- Quality split: 31 high-quality accepted points and 7 medium-quality accepted points.
- The result upgrades the `50s-87s` interval from automated audit track to manually validated audit track.

Updated caveat:

The manual table is not a final hand-click kinematic track. It accepts detector-centered coordinates after visual review. That is sufficient for report-video correlation and interval validation, but final speed/trajectory work should use a denser independent manual marking pass.

### 2026-05-10 PR29 / D8 / D27 Reconciliation

Generated supporting files added or updated in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d8-d27-reconciliation.md`: focused reconciliation memo for `DOD_111688964`, DVIDS `PR29`, local/War.gov `D8`, and local/War.gov `D27`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d8-d27-reconciliation.csv`: structured evidence table for the same mismatch.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-visual-alignment.md`: visual-summary alignment note comparing the existing `DOD_111688964` high-rate frames to the PR29/D27 description.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-visual-alignment.csv`: structured key-frame alignment table.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.md`: updated matrix narrative with the resolved PR29/D8/D27 treatment.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-report-video-correlation-matrix.csv`: added `D27` as the PR29 report-content match and separated local/War.gov `D8` as Djibouti 2025.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-high-rate-notes-dod111688964.md`: updated the correlation assessment for the PR29 clip.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-report-correlation-candidates.csv`: updated the candidate lane for `DOD_111688964.mp4`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-modern-event-timeline.md` and `.csv`: annotated the D27 timeline row with the PR29 content match and D8 label discrepancy.

Reconciliation findings:

- `DOD_111688964.mp4` remains a hard DVIDS `DOW-UAP-PR29` video identity.
- DVIDS `PR29` says the accompanying mission report is `DoW-UAP-D8`, but official/local `D8` describes two round white-hot UAPs near Djibouti in 2025.
- Official/local `D27` contains the report text summarized by `PR29`: a UAE over-water object with vertical pole/bar or possible water-reflection language, about 140 knots, and initial contact at `070457ZJUN24`.
- Working treatment: use `D27` for the written-report content lane, use `PR29` for the video release identity, and keep the DVIDS `D8` label as an unresolved official-source discrepancy.
- Existing high-rate frames support visual-summary alignment: one persistent bright object/contrast feature over water-like texture, repeated track-box association, and intermittent short downward/vertical smear. This supports the PR29/D27 description but does not independently validate speed, altitude, exact event time, or reflection interpretation.

### 2026-05-10 PR29 / D27 Dense Marking Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr29_dense_marking_pass.py`: repeatable dense sampling and marking script for `DOD_111688964.mp4`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-track-dod111688964.csv`: 101-row 5 fps dense object/overlay mark table for `1.0s-21.0s`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-track-dod111688964-summary.csv`: confidence, vertical-feature, overlay-relation, and manual-control summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dense-marking-assets-dod111688964.csv`: generated artifact index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-dense-marking-notes.md`: dense marking memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111688964/*`: annotated crops, zoom patches, and contact sheets.

Dense marking findings:

- Sampled `DOD_111688964.mp4` from `1.0s` through `21.0s` at 5 fps, yielding 101 samples.
- Confidence split: 62 high, 35 medium, 4 low.
- The four low-confidence samples are at about `8.4s`, `8.6s`, `10.4s`, and `10.6s`, where the object is faint, low in field, or partly confused with tracking symbology/background.
- The marked object spans about `x=77.2-801.1` and `y=94.6-500.9` in the 960x540 center crop.
- Forty samples place the object inside, intersecting, or near colored track-box symbology.
- Ninety-five samples have a `yes` or `possible` vertical-feature flag. This supports the PR29/D27 pole-bar/reflection description at the visual-review level, but it is not proof of a physical appendage.

Updated PR29/D27 judgment:

`DOD_111688964.mp4` is now the strongest second visual-report lane after the hard `DOD_111689030.mp4` / `D38` anchor. Its report-label caveat remains: DVIDS says `D8`, but the matching written content is local/War.gov `D27`.

### 2026-05-10 PR29 / D27 Speed-Geometry Feasibility

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr29_geometry_feasibility.py`: reproducible pixel-rate and FOV/range scenario calculation.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility.md`: feasibility memo for the D27 `140 knots` value.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility-summary.csv`: dense/manual pixel-rate summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-geometry-feasibility-scenarios.csv`: implied slant-range scenarios for `140 knots` under assumed full-frame horizontal FOV values.

Feasibility findings:

- Dense 5 fps audit track: net rate `21.6 px/s`, path-average rate `159.2 px/s`, median step rate `124.4 px/s`.
- Manual 1 fps control track: net rate `19.2 px/s`, path-average rate `135.6 px/s`, median step rate `122.8 px/s`.
- `140 knots` is about `72.0 m/s`.
- If the dense net rate represented `140 knots`, the implied slant range would be about `99.1 nm` at `2 deg` full-frame HFOV, `49.5 nm` at `4 deg`, and `24.8 nm` at `8 deg`.
- If the dense median step rate represented `140 knots`, the implied slant range would be about `17.2 nm` at `2 deg`, `8.6 nm` at `4 deg`, and `4.3 nm` at `8 deg`.

Updated speed judgment:

The MP4 does not falsify the D27 `140 knots` value, but it also cannot validate it independently. The speed remains report-derived unless sensor FOV/zoom, slant range, platform motion, gimbal pointing, target coordinates, or original frame-level telemetry appear.

### 2026-05-10 D38 Dense Marking And Geometry Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_dense_marking_pass.py`: repeatable dense sampling and marking script for the validated D38 anchor interval.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_d38_geometry_feasibility.py`: D38 image-plane rate and FOV/range scenario calculator.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-track-dod111689030.csv`: 186-row 5 fps dense mark table for `50.0s-87.0s`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-track-dod111689030-summary.csv`: dense confidence, phase, overlay, and control-delta summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-marking-assets-dod111689030.csv`: generated dense artifact index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-dense-marking-notes.md`: dense audit-track memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility.md`: D38 motion-geometry feasibility memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility-summary.csv`: phase-specific image-plane rates.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-geometry-feasibility-scenarios.csv`: illustrative FOV/range-to-speed scenarios.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/dense-marking/DOD_111689030/*`: dense annotated frames, zoom patches, and contact sheets.

Dense marking findings:

- Sampled `50.0s` through `87.0s` at 5 fps, yielding 186 samples.
- Confidence split: 148 high, 33 medium, 5 low.
- Primary `50.0s-75.0s`: 126 samples; 106 high, 17 medium, 3 low.
- Zoom-transition lead-in `75.2s-75.8s`: 4 samples; 2 medium, 2 low.
- Post-zoom `76.0s-87.0s`: 56 samples; 42 high, 14 medium, 0 low.
- The dense marks closely agree with the prior one-fps manual controls: mean delta `1.0 px`, max delta `3.17 px`.

Geometry findings:

- Dense primary `50s-75s`: net rate `8.7 px/s`, path-average rate `72.4 px/s`, median step rate `48.3 px/s`.
- Dense post-zoom `76s-87s`: net rate `9.5 px/s`, path-average rate `97.1 px/s`, median step rate `81.6 px/s`.
- Because the DVIDS `01:16` zoom/narrow-field event sits between those intervals, primary and post-zoom image-plane rates should not be merged into a single real-world speed estimate.
- The public MP4 still lacks FOV/zoom state, slant range, platform motion, gimbal pointing, and frame-level telemetry, so D38 remains an image-plane audit track rather than a real-world kinematic reconstruction.

Updated D38 judgment:

`DOD_111689030.mp4` / `DoW-UAP-D38` is now the corpus gold-standard anchor: hard report-video pairing, manually validated one-fps interval, dense 5 fps audit track, and explicit geometry caveats.

Updated caveat:

This is not a claim that the PR29 video has been independently proven to show the D27 object kinematically. It is a source-index reconciliation: the release page's narrative summary matches `D27` and conflicts with official/local `D8`.

### 2026-05-10 PR34 / D33 And PR35 / D35 Phase Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr34_pr35_phase_review.py`: repeatable phase-aligned sampling script for `DOD_111689011.mp4` and `DOD_111689022-1920x1080-9000k.mp4`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-pr35-phase-review-notes.md`: focused phase-review memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-pr35-phase-summary.csv`: combined phase-summary table.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111689011-phase-track.csv` and `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111689022-phase-track.csv`: two-fps phase-aligned sample tables.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-pr35-phase-review-assets.csv`: generated artifact index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-phase-review/*`: annotated frames, zoom patches, and contact sheets.

Phase-review findings:

- `DOD_111689011.mp4` is a hard PR34/D33 pair. DVIDS names `DOD_111689011` and `DoW-UAP-D33`; local D33 text confirms the near-ocean-surface, sharp-turns, estimated `80 MPH`, and loss-from-feed lane.
- The PR34/D33 first minute is the useful object-level interval: entry `4.0-6.9s` had 5 high and 1 medium sample; horizontal back-and-forth `7.0-19.9s` had 23 high and 3 medium samples; generally-centered `20.0-59.9s` had 59 high, 19 medium, and 2 low samples.
- After about `60s`, PR34/D33 becomes a phase-alignment case rather than a clean object-track case. Blue reticle, black redaction boxes, and the contrast-filter window dominate the detector, so automated centroids are not reliable kinematic marks.
- `DOD_111689022-1920x1080-9000k.mp4` is a strong local PR35/D35 export match: DVIDS names `DOD_111689022` and `DoW-UAP-D35`, while the local suffixed file is `24.5s`, matching the DVIDS `24s` release duration.
- PR35/D35 supports the DVIDS phase sequence at scene level: zoom near `2s`, ocean-background tracking through `19.9s`, then land/shore transition and loss from `20s` onward.
- PR35/D35 is not a good kinematic target from this pass. The automated detector frequently selects cloud, shoreline, or high-contrast terrain features.

Updated Greece judgment:

PR34/D33 is the better next manual-review target. Use a bounded independent manual track from roughly `4s-60s` if we want image-plane support for the report's maneuver narrative. PR35/D35 should stay in the release/report completeness lane unless new cleaner source frames or telemetry appear.

### 2026-05-10 PR34 / D33 Manual-Review Track

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr34_d33_manual_track_pass.py`: bounded pre-reticle manual-review track script for `DOD_111689011.mp4`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-manual-track-notes.md`: focused PR34/D33 manual-review memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-d33-manual-track-dod111689011.csv`: cleaned two-fps track table for `4.0s-59.0s`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-manual-track-summary.csv`: summary counts and image-plane motion metrics.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-image-plane-turn-events.csv`: smoothed heading-change event table.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-d33-manual-track-assets.csv`: generated artifact index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr34-d33-manual-track/DOD_111689011/*`: annotated frames, zoom patches, contact sheets, and trajectory plot.

Manual-review findings:

- Reviewed the pre-reticle interval `4.0s-59.0s` at `2 fps`, yielding `111` samples.
- Accepted `97` detector-centered marks after rejecting the recurring false top-edge artifact near `x=1827, y=1`.
- Interpolated `14` bounded detector dropouts for continuity visualization; no rows were excluded.
- Quality/status split: `87 high`, `8 medium`, `2 low`, and `14 interpolated`.
- Image-plane path length was `6536.08 px`, with path-average rate `118.84 px/s` and median 0.5-second step rate `84.04 px/s`.
- The turn-event table found seven smoothed image-plane heading changes of at least `60 deg`: `12.0s`, `15.0s`, `18.0s`, `32.5s`, `35.5s`, `39.0s`, and `42.5s`.

Updated PR34/D33 judgment:

The PR34/D33 clip now supports a narrow maneuver-level conclusion: the public MP4 contains multiple sharp apparent image-plane heading changes in the pre-reticle interval. That is consistent with the D33 sharp-turn narrative at image-plane review level, but it is not independent proof of real-world 90-degree turns or the report's `80 MPH` speed. Sensor pan/track behavior, missing FOV/range, platform motion, and missing telemetry remain decisive caveats.

### 2026-05-10 PR34 / D33 Geometry Feasibility

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr34_d33_geometry_feasibility.py`: D33 image-plane rate and `80 MPH` scenario calculator.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility.md`: feasibility memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-summary.csv`: track and phase-level image-plane rate summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-range-scenarios.csv`: implied slant ranges if `80 MPH` is true.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-speed-scenarios.csv`: implied speeds under assumed FOV/range combinations.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-geometry-feasibility-turn-radius-scenarios.csv`: illustrative turn-radius values if image-plane heading changes were physical turns.

Geometry findings:

- The cleaned `4.0s-59.0s` track has net rate `8.455 px/s`, path-average rate `118.837 px/s`, and median 0.5-second step rate `84.039 px/s`.
- Accepted-marks-only rates are nearly the same at the whole-track level: net rate `8.455 px/s`, path-average rate `118.837 px/s`, and median step rate `82.309 px/s`.
- If the path-average rate represented `80 MPH`, implied slant range would be about `8.94 nm` at `2 deg` full-frame HFOV, `4.47 nm` at `4 deg`, and `2.23 nm` at `8 deg`.
- If the median step rate represented `80 MPH`, implied slant range would be about `12.64 nm` at `2 deg`, `6.32 nm` at `4 deg`, and `3.16 nm` at `8 deg`.
- The seven image-plane heading-change events would imply simple turn radii of roughly `36.5 m` to `100.0 m` at `80 MPH`, but that is not a physical conclusion because the heading changes are image-plane events from a panning/tracking sensor.

Updated speed judgment:

The public PR34/D33 MP4 does not falsify the D33 `80 MPH` report value, but it cannot validate it independently. The speed remains report-derived unless actual FOV/zoom state, slant range, platform motion, gimbal pointing, target coordinates, or original telemetry appear.

### 2026-05-10 PR44 Standalone Quantitative Pass

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr44_standalone_quant_pass.py`: seeded dense-track audit for `DOD_111689115.mp4` / `DOW-UAP-PR44`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr44-standalone-quant-notes.md`: focused PR44 standalone memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-dense-track-dod111689115.csv`: 5 fps seeded dense table for `154.0s-243.0s`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-dense-track-summary.csv`: image-plane rate, path, confidence, and overlay summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-dense-track-assets.csv`: generated artifact index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr44-standalone/DOD_111689115/*`: annotated frames, zoom patches, contact sheets, and trajectory plot.

PR44 findings:

- DVIDS hard-identifies `DOD_111689115.mp4` as `DOW-UAP-PR44`, Middle East, 2020, but says the reporter did not provide an oral or written description. This remains a standalone public-release video, not a local `D44`, `D57`, or `D58` match.
- The dense pass sampled the strongest seed interval, `154.0s-243.0s`, at `5 fps`, producing `446` rows across `89.0s`.
- The full interval has net image-plane displacement `256.427 px`, total path `3651.620 px`, path-average rate `41.029 px/s`, median step rate `36.418 px/s`, and p95 step rate `83.860 px/s`.
- Confidence split was `155 high`, `154 medium`, and `137 low`. The reticle-cycling portion, `205.0s-243.0s`, was cleaner than the earlier primary portion: `82 high`, `100 medium`, and `9 low`.
- Marking basis split was `320` local compact-bright refinements and `126` seed-only/interpolated marks. This is a seeded dense audit, not an independent hand-clicked track.
- Overlay relation was mostly favorable: `382` rows separate from colored overlay, `58` near overlay, and `6` intersecting overlay.

Updated PR44 judgment:

`DOD_111689115.mp4` is now the strongest standalone visual clip in the local corpus: it supports a sustained compact point-return track through the main PR44 tracking interval and into the reticle-cycling interval. It still does not provide a report pairing, speed, range, altitude, platform motion, FOV, target coordinates, or event timestamp. The next PR44 step should be hand validation of the low-confidence and seed-only `154.0s-204.8s` rows, then a separate qualitative pass over the later `244s-290s` zoom-out/loss/exit sequence.

### 2026-05-10 PR44 Primary Validation And Late Phase Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr44_primary_visual_validation.py`: expanded-window validation pass for the weaker `154.0s-204.8s` primary PR44 rows.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr44_late_phase_review.py`: one-fps qualitative review for `244s-294s`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr44-primary-validation-late-phase-notes.md`: follow-on PR44 validation memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-primary-visual-validation-dod111689115.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-primary-visual-validation-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-late-phase-review-dod111689115.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr44-late-phase-review-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr44-primary-validation/DOD_111689115/*`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr44-late-phase-review/DOD_111689115/*`

Primary validation findings:

- The `154.0s-204.8s` primary interval has `255` dense rows.
- The validation pass classified `121` high, `83` medium, and `51` low visual-quality rows.
- This raises the high-or-medium supported subset from `127/255` rows in the original dense audit to `204/255` rows in the validation layer.
- Validation status split: `163` confirmed dense mark, `39` confirmed near dense mark, `2` recentered visual candidate, `15` weak visual candidate, and `36` unconfirmed seed/dense mark.
- The remaining low rows cluster around `181s-199s`, especially `192s-198s`, where the target is close to reticle/overlay graphics and dark-field texture.

Late phase findings:

- The `244s-294s` review sampled `51` one-fps rows.
- Conservative compact-return detections were found in `26/51` rows.
- Reticle-cycling tail `244s-263s`: `8/20` compact-return detections.
- Zoom-out continued-track interval `264s-290s`: `18/27` compact-return detections.
- Loss/exit interval `291s-294s`: `0/4` compact-return detections.

Updated PR44 judgment:

PR44 is now reasonably complete as a standalone public-release video case. The dense track, primary validation, and late-phase review support sustained then intermittent compact-return behavior through the DVIDS-described tracking/zoom-out sequence, followed by loss/exit at scene level. The case still has no hard `D` report pairing and no public speed/range/telemetry basis.

### 2026-05-12 D28 Source Review

Generated supporting file added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-source-review.md`: focused source review for `dow-uap-d28-mission-report-east-china-sea-2024.pdf`.

D28 findings:

- D28 remains a high-value structured sensor-event report because it preserves a precise initial contact time, operation context, platform/sensor fields, and a narrow munition-release-to-impact observation window.
- The geography issue is now resolved as a source metadata mismatch. The filename/internal PDF title says `East China Sea, 2024`, but the report body is consistently USCENTCOM / Operation Inherent Resolve / OKAS / Ayn Al Asad ROZ Raindrop.
- The body-controlled analytic location should be Iraq / Ayn Al Asad area, not East China Sea.
- The reported sensor lane is MX-20 / MX-25 IR lens flare interpreted as a significant heat source, with the object described as moving through the sensor field between munition release and impact.
- Public kinematic fields do not provide speed, slant range, object size, altitude, FOV, zoom state, platform motion, munition timing logs, or raw telemetry. The "high rate of speed" and heat-source language remain report claims, not independently derived measurements.

Updated D28 judgment:

`D28` should stay near the top of the document-priority list, but it should be kept separate from East China Sea / INDOPACOM video lanes unless official release metadata explicitly links them. The next D28 step is release-index search for any PR/video entry referencing `D28`, `202027ZSEP2024-CENTCOM`, AGM-176, MX-20/MX-25, or Ayn Al Asad.

### 2026-05-12 D28 Release-Index Search

Generated supporting file added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-release-index-search.md`: source-index search for a D28 PR/video pairing.

Release-index findings:

- No hard public PR/video pairing was found for D28.
- `DOW-UAP-PR28` is a false positive by number only. DVIDS identifies it as a Greece / January 2024 video, filename `DOD_111688954`, and says the accompanying mission report is `DoW-UAP-D7`.
- `DOW-UAP-PR46` is a false positive by the `East China Sea` label only. DVIDS identifies it as an INDOPACOM / 2024 standalone video, filename `DOD_111689133`, with no oral or written reporter description.
- Neither PR page mentions D28, `202027ZSEP2024-CENTCOM`, AGM-176, MX-20/MX-25, or Ayn Al Asad.

Updated D28 video judgment:

`D28` remains a high-priority document-only case. Do not infer a PR46 pairing from D28's filename/title mismatch. The next analogous reconciliation target is PR28, because official DVIDS points PR28 to `DoW-UAP-D7`, while the SWIR-only diamond / 434-knot written-report content appears in local `D25`.

### 2026-05-12 PR28 / D25 / D7 Reconciliation

Generated supporting file added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr28-d25-d7-reconciliation.md`: focused reconciliation memo for `DOD_111688954`, DVIDS `PR28`, local/War.gov `D25`, and local/War.gov `D7`.

Reconciliation findings:

- `DOD_111688954.mp4` is now a hard DVIDS `DOW-UAP-PR28` video identity. DVIDS identifies filename `DOD_111688954`, length `00:01:06`, Greece / January 2024.
- DVIDS says the accompanying report is `DoW-UAP-D7`, but the DVIDS description is the SWIR-only diamond / approximately `434 knots` / vertical trailing mass or probe lane.
- Local/War.gov `D25` contains that written-report content: event `250509ZJAN24`, `SWIR WHT`, round diamond shape with straight non-maneuverable tail/probe, approximately `434 knots`, and only visible on SWIR camera.
- Local/War.gov `D7` is a separate Arabian Gulf 2020 balloon-like/TFLIR case: looks like a balloon, traveling with winds at `31,000 ft MSL`, weapons-quality track, visual ID in TFLIR.

Updated PR28 treatment:

Use `DOD_111688954.mp4` for the hard PR28 video identity, use `D25` for the matching written-report content lane, and preserve the DVIDS `D7` label as an official-source discrepancy. The bounded PR28/D25 phase review was completed in the next pass.

### 2026-05-12 PR28 / D25 Phase Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr28_d25_phase_review.py`: phase-aligned sampler for `DOD_111688954.mp4` / PR28 using local `D25` as the working report-content match.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr28-d25-phase-review-notes.md`: focused PR28/D25 phase memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688954-metadata.txt`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688954-phase-track.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688954-phase-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr28-d25-phase-review-assets.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-phase-review/DOD_111688954/*`

Phase-review findings:

- The source video is `66.0s`, `1920x1080`, `30.0 fps`.
- The opening split-screen and right-frame contrast phases are consistent with the DVIDS visual sequence, but include display-context and overlay artifacts.
- The full-screen SWIR interval from `10.0s-55.9s` is the useful object-level interval: `86/92` samples are high-or-medium confidence and no sampled row is a no-candidate row.
- The visible-spectrum switch at `56s` does not preserve a robust track: the two sampled rows are one low-confidence mark and one no-candidate row.
- The `57.0s-65.5s` SWIR black-hot segment has `0/18` high-or-medium detections. Low marks are edge, cloud, or overlay artifacts, consistent with non-reacquisition.

Updated PR28 video judgment:

The local phase review supports PR28 as a hard video identity and strengthens the `D25` report-content lane. It does not validate `434 knots`, range, size, altitude, or the detailed physical shape/tail/probe description from the public MP4. Treat those as report-derived unless telemetry or sensor metadata appears.

### 2026-05-12 DVIDS Release Identity Backfill

Generated supporting file added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-dvids-release-identity-backfill.md`: source-index backfill for local MP4s not yet represented in the main matrix.

Backfill findings:

- Added hard report-video rows for `PR19/D10`, `PR21/D14`, `PR22/D16`, `PR23/D18`, `PR26/D12`, `PR27/D23`, and the `PR31-PR33/D32` glare-control cluster.
- Added standalone release rows for `PR37`, `PR38`, `PR39`, `PR40`, `PR43`, `PR46`, `PR48`, and `PR49`.
- Most new hard pairings are controls or ambiguity lanes: possible missile/birds, probable `SU-27/35`, possible UAP/UAV, and glare/halo artifacts.
- `PR26/D12` has a metadata mismatch: DVIDS titles it as UAE / October 2023 but names `D12`, while local/War.gov `D12` is Iraq / May 2022. Treat PR26 as a hard DVIDS identity but not as a clean report-content lane.
- `DOD_111688825.mp4` / `PR27` / `D23` is now the best next phase-review target because it is a long hard-paired IR sequence with acquisition, zoom, tracking, and repeated loss/reacquisition.

Updated next action:

Run a bounded PR27/D23 phase review of `DOD_111688825.mp4` using DVIDS time anchors: initial contrast around `01:56`, pan/center at `02:04`, zoom at `02:14`, center track through `03:26`, and sensor-motion-driven loss/reacquisition through `04:57`.

### 2026-05-12 PR27 / D23 Phase Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr27_d23_phase_review.py`: DVIDS-anchor phase sampler for `DOD_111688825.mp4` / PR27 / D23.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-phase-review-notes.md`: focused PR27/D23 phase memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688825-metadata.txt`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688825-phase-track.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111688825-phase-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-phase-review-assets.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-phase-review/DOD_111688825/*`

Phase-review findings:

- The source video is `297.33s`, `1920x1080`, `30.0 fps`.
- D23 contains two report lines: UAP 1 at `240241:00ZOCT23` with estimated `320 MPH` and `THERMAL SHOWED COLD`; UAP 2 at `240322:00ZOCT23` with estimated `440 MPH` and signature `UNK`.
- The public DVIDS page does not identify which D23 UAP line the PR27 MP4 depicts.
- The no-content lead-in produced only low-confidence scene-context marks.
- The initial `116.0s-123.5s` right-side contrast window produced `0/16` high-or-medium rows after ROI tightening, so the first DVIDS "becomes distinguishable" moment is not independently confirmed by the detector.
- The `134.0s-206.5s` zoom/centered-track interval produced `101/146` high-or-medium candidate rows.
- The `207.0s-297.0s` loss/reacquisition interval produced `180/181` high-or-medium candidate rows, consistent with frequent compact-return candidates through the DVIDS-described repeated loss/reacquisition phase.

Updated PR27 video judgment:

PR27/D23 is a long hard-paired visual-sequence case, but it is not a public kinematics case. The phase review supports the DVIDS acquisition/zoom/center-track/loss-reacquisition sequence with caveats for shoreline, reticle, and water-texture artifacts. Velocity, range, and D23 UAP-line assignment remain report-derived.

### 2026-05-12 PR27 / D23 Manual Validation

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr27_d23_manual_validation.py`: category validation layer for active PR27/D23 phase-track rows.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-notes.md`: focused PR27/D23 validation memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-dod111688825.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-compact-return-segments.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-assets.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-manual-validation/DOD_111688825/*`

Manual-validation findings:

- Reviewed `327` active rows from `134.0s-297.0s`.
- Classified `175` rows as true compact-return candidates.
- Artifact/uncertain split: `88` reticle/overlay artifacts, `27` frame-edge artifacts, `23` water-texture artifacts, `3` shoreline/terrain artifacts, `10` uncertain, and `1` no-candidate.
- The `207.0s-297.0s` loss/reacquisition phase is strongest: `144/181` rows validated as compact-return candidates.
- The `134.0s-206.5s` zoom/centered-track phase is weaker than the raw phase summary suggested: only `31/146` rows validated as compact-return candidates, with `86` reticle/overlay artifacts and `23` water-texture artifacts.
- The longest validated compact-return run is `PR27-C16`, from `235.00s-266.00s`, with `62` samples.

Updated PR27 validation judgment:

PR27/D23 remains promoted as a long hard-paired visual-sequence case, but the support is strongest in the late loss/reacquisition phase, not across the whole centered-track interval. Do not use the public MP4 to derive speed, range, or physical trajectory.

### 2026-05-12 PR26 / D12 Reconciliation

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr26_d12_still_review.py`: sampled-frame review for `DOD_111688816.mp4` / PR26 / D12.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr26-d12-reconciliation.md`: focused source reconciliation memo.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr26-d12-still-review-dod111688816.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr26-d12-still-review-summary.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr26-d12-still-review-assets.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-hard-pair-phase-review/DOD_111688816/*`

Reconciliation findings:

- `DOD_111688816.mp4` is a hard DVIDS `DOW-UAP-PR26` video identity.
- DVIDS PR26 explicitly names `DoW-UAP-D12`, and the DVIDS body text matches local/War.gov D12's UAP description: movement north to northeast and no positive ID.
- The conflict is official release metadata: DVIDS PR26 is titled United Arab Emirates / October 2023 and lists `Date Taken: 10.01.2023`, while local/War.gov D12 is Iraq / May 2022 with UAP initial contact `202043:00ZMAY22`.
- Local video review measured `43.167s`, `1295` frames, `1920x1080`, and `12` sampled frames.
- The sampled local MP4 is not a single frozen still for all 43 seconds; median sampled-frame difference was `9.92`, with stronger changes early and late and a near-static middle segment.
- The red/orange overlay proxy found `0` red/orange pixels in sampled frames, so the DVIDS-described reporter-added red line is not visible in the sampled local MP4.

Updated PR26 treatment:

Treat PR26/D12 as a hard video identity and D12 content match with a release-title/date/location metadata mismatch. Use D12's Iraq / May 2022 event metadata for report analysis, preserve DVIDS PR26's UAE / October 2023 title as a source-index discrepancy, and do not use the public MP4 for physical kinematics.

### 2026-05-12 D28 Evidence Packet

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-evidence-packet.md`: document-only evidence packet for D28.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-evidence-constraints.csv`: machine-readable constraint table.

D28 packet findings:

- D28 remains high-value because it preserves an exact event anchor, `202027:59ZSEP24`, an official event serial, named sensors (`MX-20` and `MX-25`), and the narrow between-release-and-impact mission phase.
- It remains document-only: no DVIDS/PR page found names D28, `202027ZSEP2024-CENTCOM`, `AGM-176`, `MX-20`, `MX-25`, or Ayn Al Asad.
- The local corpus scan found D28's unique anchors only in D28 and derived notes, which supports treating it as a single-document lane.
- The public report does not preserve raw imagery, release/impact timestamps, FOV, range, sensor pointing, object speed, altitude, size, or trajectory.
- The strongest conservative interpretation is "unresolved sensor/operational observation during active weapons employment," not a public physical-performance case.

Updated D28 treatment:

Keep D28 near the top of document-only priorities, but stop spending correlation time on PR46 or East China Sea label matches unless a new official source explicitly links them. The next useful D28 work would be a targeted source request or source search for raw MX-20/MX-25 imagery and weapon-release/impact timing.

### 2026-05-12 Range-Fouler Cluster Packet

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-cluster-packet.md`: focused packet for `D38`, `D44`, `D56`, `D57`, and `D58`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-cluster-constraints.csv`: machine-readable cluster constraint table.

Cluster findings:

- The cluster should be treated as a range-safety/sensor-geometry lane, not as one unified phenomenon.
- `D38` remains the hard report/video anchor through DVIDS `PR36` and local `DOD_111689030.mp4`.
- `D44` and `D57` are the closest internal pair: both are Gulf of Aden IR/black-hot records of round cold objects with sensor depression angle, slant range, ground range, and abrupt direction-change language.
- `D56` is a separate three-contact North Arabian Sea lane with negative ES, radar track, and IFF track, but unknown speed/distance/precise course.
- `D58` is the highest-value unresolved follow-up target in the cluster because it combines KINGPIN-directed ID, radar lock, target-pod video, two IR-significant contacts, red blinking strobes, and noise-jamming indications.
- `D58` is also the strongest conventional-confound case: red strobes, noise jamming, and radar/target-pod context can fit military aircraft, drones, or EW platforms.
- PDF metadata for `D56`, `D57`, and `D58` says `DoW-UAP-D33`, `DoW-UAP-D34`, and `DoW-UAP-D35` respectively, conflicting with local filenames and already-analyzed Greece lanes. Treat as metadata noise unless official release indexing corrects it.

Updated range-fouler treatment:

Keep D44/D57 as a geometry-rich Gulf of Aden IR pair, D56 as a multi-contact ambiguity lane, and D58 as the next best unresolved source-request target. Do not map PR44 or `DOD_111689115.mp4` to local D44/D57/D58 without an explicit source link.

### 2026-05-12 D75 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d75-source-review.md`: source review for `dow-uap-d75-mission-report-gulf-of-aden-july-2024.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d75-evidence-constraints.csv`: machine-readable D75 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D75/d75-page-7.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D75/d75-page-8.png`

D75 findings:

- D75 is a useful Gulf of Aden document-only case, but the detailed object description is not recoverable from the released PDF.
- The page-8 render confirms the visible UAP description stops at `UAP HAD`; the following `Gentext` box is redacted as `1.4a`.
- Strong preserved anchors: `140517:00ZJUL24`, MISREP `10194673`, `124 ATKS`, `132 Wing`, USCENTCOM / `609th`, NAVCENT first tasking, FMV primary sensor, and redacted `38P MT` coordinate lanes.
- Structured UAP fields preserve: straight flight path at same altitude, estimated low altitude, estimated northwest trajectory, followed until distance became too far, and speed faster than the observing platform's flying speed.
- The actual kinetic velocity, detailed shape/color/markings, exact coordinates, event serial, platform speed, and raw video are not public.
- PDF metadata title/subject says `DoW-UAP-D43`, conflicting with the D75 filename/release identity. Treat as metadata mismatch.

Updated D75 treatment:

Keep D75 high-priority in the document-only Gulf of Aden lane, but remove the previous "needs OCR review" caveat. The issue is source redaction, not extraction failure. Do not use D75 for shape or absolute-speed claims unless new source imagery or telemetry appears.

### 2026-05-12 D74 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d74-source-review.md`: source review for `dow-uap-d74-mission-report-syria-november-2023.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d74-evidence-constraints.csv`: machine-readable D74 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D74/d74-page-08.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D74/d74-page-09.png`

D74 findings:

- D74 is stronger than D75 as a descriptive document-only case because the UAP gentext narrative is mostly readable.
- Strong preserved anchors: MISREP `9381202`, Operation `INHERENT RESOLVE`, USCENTCOM / `609th`, air ISR mission, FMV/SIGINT collection context, initial contact `092153:00ZNOV23`, event serial `092153ZNOV2023-CENTCOM`, and DoD acquisition date `092153:00ZNOV23`.
- The public report narrative says a probable UAP shaped like a bouncy ball came from the south near co-altitude, dropped altitude, safely passed the aircraft, maintained about `424KN`, and became out of range after about seven minutes.
- Negative controls are useful: benign observer assessment, no emissions, no interrogation, no observer engagement, no effects on persons or equipment, and no recovered material.
- The structured description field is still redacted after `SHOWED AS`; the shape and speed are report-derived, not image-verified.
- No hard PR/DVIDS video pairing has been found for D74, `092153ZNOV2023-CENTCOM`, `424KN`, or the bouncy-ball description.
- PDF metadata title/subject says `DoW-UAP-D42`, conflicting with the D74 filename/release identity. Treat as metadata mismatch.

Updated D74 treatment:

Keep D74 high-priority in the document-only lane. It is now the best readable later USCENTCOM mission-report narrative, but it should not be used for independent physical-performance claims without source video, range, FOV, and platform telemetry.

### 2026-05-12 D8 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d8-source-review.md`: source review for `dow-uap-d8-mission-report-djibouti-2025.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d8-evidence-constraints.csv`: machine-readable D8 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D8/d8-page-7.png`

D8 findings:

- D8 is a short but useful document-only report. The public text preserves one main UAP line: at `1653Z`, an observer reported `2X ROUND WHITE HOT UAPS` moving dynamic south at approximately `240NM/HOUR` near `35SQT3423692957`.
- The PDF is heavily redacted. The public release does not preserve full incident date, platform, unit, sensor, event serial, first/last coordinates, altitude, range, FOV, raw imagery, or telemetry.
- The filename and PDF metadata say Djibouti, 2025, but the visible MGRS grid `35SQT3423692957` decodes to approximately `34.2514N, 29.5437E`, which is Eastern Mediterranean. Treat this as a title/grid location mismatch.
- D8 is confirmed as separate from the PR29/D27 UAE pole/bar case. D8 has two round white-hot UAPs; PR29/D27 has one pole/bar or possible-reflection object.
- Installed the local Python `mgrs` package to decode the coordinate.

Updated D8 treatment:

Keep D8 high-priority as a quantitative, heavily redacted document-only case. Use the grid-derived Eastern Mediterranean lane for geospatial analysis, preserve the official Djibouti title as a source-label mismatch, and do not use D8 as the written-report content for `DOD_111688964.mp4` / `PR29`.

### 2026-05-12 D54 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d54-source-review.md`: source review for `dow-uap-d54-mission-report-mediterranean-sea-na.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d54-evidence-constraints.csv`: machine-readable D54 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D54/d54-page-7.png`

D54 findings:

- D54 is a short, heavily redacted Mediterranean mission-report case. The public UAP text reports one triangular and metallic UAP observed during RTB at `1319Z`.
- The released coordinate `363453N 0255943E` converts to approximately `36.58138889N, 25.99527778E`, putting it in the Aegean Sea / Eastern Mediterranean lane.
- The report gives `24,989FT MSL` and `168KTS`, but no public sensor, platform, range, FOV, track duration, raw imagery, or telemetry.
- The full incident date and event serial are not public; the filename/title date field is `NA`.
- PDF metadata title/subject says `DoW-UAP-D31`, conflicting with the D54 filename/release identity. Treat as metadata mismatch.
- No hard PR/DVIDS video pairing has been found for D54, the coordinate, `168KTS`, or the triangular/metallic description.

Updated D54 treatment:

Keep D54 in the Greece / Eastern Mediterranean document-only cluster, below the hard-paired PR28/D25 and PR34/D33 lanes. It is useful because it has shape, coordinate, altitude, and speed fields, but it should not be used as public video evidence or validated kinematics.

### 2026-05-12 D27 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d27-source-review.md`: source review for `dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d27-evidence-constraints.csv`: machine-readable D27 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D27/d27-page-5.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D27/d27-page-6.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D27/d27-page-7.png`

D27 findings:

- D27 is now source-reviewed as the strongest written-report content match to `DOD_111688964.mp4` / DVIDS `PR29`.
- Strong preserved anchors: Operation `ENDURING SENTINEL`, USCENTCOM / `609th`, AFSOC / `3 SOS`, ISR mission, target pod `AN/DAS-1`, FMV-supported NIB windows, initial contact `070457:00ZJUN24`, and DoD acquisition date `070457:00ZJUN24`.
- The report description says the UAP was a glowing hot spherical object with a vertical unwavering cylindrical pole/bar attached to the bottom, with a caveat that it may instead be a reflection from the object in the water.
- The UAP speed field is estimated `140 KNOTS`; the friendly aircraft context is `23,999FT`, `163 KNOTS`, trajectory `294`, and redacted `40RFM60` lane.
- D27 contains several provenance constraints: filename/title says United Arab Emirates / October 2023 while the body timeline is June 2024; event serial is printed as `060457ZJUN2024-CENTCOM` while initial contact is `070457:00ZJUN24`; DVIDS `PR29` labels the accompanying report as `D8` even though the body summary matches D27.
- No new public telemetry, FOV, range, platform motion, or gimbal data was found, so the `140 KNOTS` value remains report-derived.

Updated D27 treatment:

Keep `DOD_111688964.mp4` as hard `PR29` media, keep D27 as the written-report content match, and keep the DVIDS `D8` report label as an official-source discrepancy. D27/PR29 remains the strongest second visual-report lane after the D38/PR36 anchor, but not a public kinematics case.

### 2026-05-12 D25 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d25-source-review.md`: source review for `dow-uap-d25-mission-report-greece-january-2024.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d25-evidence-constraints.csv`: machine-readable D25 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D25/d25-page-5.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D25/d25-page-6.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D25/d25-page-7.png`

D25 findings:

- D25 is now source-reviewed as the written-report content match for `DOD_111688954.mp4` / DVIDS `PR28`.
- Strong preserved anchors: Greece / January 2024 mission report, USCENTCOM / `603rd`, AFSOC / `33 SOS`, target pod `AN/DAS-4`, UAP signature `SWIR WHT`, initial contact `250509:00ZJAN24`, event serial `250509ZJAN2024-CENTCOM 001`, and DoD acquisition date `250509:00ZJAN24`.
- The report says the UAP appeared as a round/diamond shape with a straight non-maneuverable tail or probe, only appeared on SWIR, moved at approximately `434 KNOTS`, and lasted about two minutes ending at `0511Z`.
- Structured fields preserve estimated `FL200` kinetic altitude and estimated westward trajectory, but the structured kinetic-velocity field is blank; `434 KNOTS` comes from the gentext.
- Prior PR28 phase review supports the SWIR-only visual sequence: persistent full-screen SWIR detections from `10.0s-55.9s` and no robust reacquisition in the `57.0s-65.5s` SWIR black-hot segment.
- DVIDS labels the accompanying report as `D7`, but the matching written-report content is D25; local/War.gov D7 remains a separate Arabian Gulf 2020 balloon-like/TFLIR case.

Updated D25 treatment:

Keep PR28/D25 as a high-priority hard media-plus-report-content lane. It supports the SWIR-only observation sequence, but not independent physical speed, range, altitude, size, or detailed shape validation from the public MP4.

### 2026-05-12 D33 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d33-source-review.md`: source review for `dow-uap-d33-mission-report-greece-october-2023.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d33-evidence-constraints.csv`: machine-readable D33 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D33/d33-page-5.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D33/d33-page-6.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D33/d33-page-7.png`

D33 findings:

- D33 is source-reviewed as a hard media-plus-report case: DVIDS `PR34` identifies local `DOD_111689011.mp4` and states the accompanying report is `DoW-UAP-D33`.
- Strong preserved anchors: MISREP `9329374`, USCENTCOM / `603rd`, AFSOC / `33 SOS`, target pod `AN/DAS-4`, FMV primary sensor, G-MESH available sensor, initial contact `270035:12ZOCT23`, DoD acquisition date `270035:00ZOCT23`, and DVIDS filename `DOD_111689011`.
- The report says a seemingly circular UAP flew just above the ocean surface, made multiple sharp 90-degree turns at estimated `80 MPH`, and was lost from feed around `0038Z`.
- Negative controls include benign assessment, no effects on persons/equipment, no material recovered, no observer engagement, under intelligent control marked `NO`, and UAP signatures `NONE`.
- The event serial field is `-`; do not fabricate a serial.
- Prior manual track work supports multiple sharp apparent image-plane heading changes, but true physical 90-degree turns and `80 MPH` remain report-derived without FOV, slant range, platform/gimbal motion, and telemetry.

Updated D33 treatment:

Keep D33/PR34 as the strongest Greece ocean-surface hard-paired case. It is a public image-plane maneuver-support case, not a solved physical-speed or true-turn-geometry case.

### 2026-05-13 D35 Source Review

Completed source review for `source-files-not-included/dow-uap-d35-mission-report-greece-october-2023.pdf` and reconciled it against DVIDS `DOW-UAP-PR35`.

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d35-source-review.md`: source review for `dow-uap-d35-mission-report-greece-october-2023.pdf`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d35-evidence-constraints.csv`: machine-readable D35 constraints.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D35/d35-page-5.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D35/d35-page-6.png`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/source-page-renders/D35/d35-page-7.png`

D35 findings:

- D35 is source-reviewed as a hard media-plus-report case: DVIDS `PR35` identifies video filename `DOD_111689022` and states the accompanying report is `DoW-UAP-D35`.
- The local `DOD_111689022-1920x1080-9000k.mp4` file matches the DVIDS filename stem and release duration; all three local copies share SHA-256 `05FD161A5155DAF49E14E99C517CDB1B35E7491611F448DDB026D9FA0DF63D42`.
- Strong preserved anchors: MISREP `9337873`, USCENTCOM / `603rd`, AFSOC / `33 SOS`, target pod `AN/DAS-4`, FMV primary sensor, G-MESH available sensor, initial contact `290811:00ZOCT23`, DoD acquisition date `290811:00ZOCT23`, and estimated kinetic velocity `30 MPH`.
- The report says a seemingly circular UAP flew just above the ocean surface toward land and was lost from feed at `0811Z`.
- Negative controls include benign assessment, no maneuverability observations, no effects on persons/equipment, no material recovered, no observer engagement, under intelligent control marked `NO`, and UAP signatures `NONE`.
- The event serial field is `-`; do not fabricate a serial.
- The public PR35 clip supports the zoom/ocean-background/land-transition sequence, but cloud, shoreline, and terrain confounds make it weak for object kinematics.

Updated D35 treatment:

Keep D35/PR35 as a hard-paired Greece ocean-surface completeness case, below D33/PR34 for anomaly strength and motion analysis. Its `30 MPH` value and toward-land trajectory remain report-derived unless source telemetry appears.

### 2026-05-13 PR45 Standalone Visual Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr45_standalone_visual_pass.py`: PR45 standalone central-contrast review script.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr45-standalone-visual-notes.md`: dedicated PR45 note.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr45-standalone-review-dod111689123.csv`: per-sample review rows.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr45-standalone-summary.csv`: phase summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr45-standalone-assets.csv`: generated asset index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111689123-metadata.txt`: OpenCV source metadata and review settings.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr45-standalone/DOD_111689123/*`: annotated crops, contrast patches, and contact sheets.

PR45 findings:

- `DOD_111689123.mp4` is locally validated as a meaningful standalone visual-interest clip for DVIDS `DOW-UAP-PR45`.
- The strongest support is the `35.0s-57.0s` window, where the central contrast area is consistently visible and grows in detected area.
- Across `293` sampled rows, the pass produced `105` high, `50` medium, `117` low, and `21` none classifications.
- The median detected central-contrast area rises from `52.5 px` in the initial interval to `204.0 px` in the growth interval and `425.0 px` in the late interval, with a late maximum of `2168 px`.
- The late sequence shows lower-right exit-adjacent motion: by `56.0s-58.4s`, the contrast complex moves away from the reticle center and toward the lower crop boundary.
- The detector rows are still reticle/track-box-confounded, so they should be treated as central-contrast audit rows rather than physical object centroids.

Updated PR45 treatment:

Keep PR45 as a standalone visual lane: tracked central contrast, apparent growth, and lower-right exit-adjacent motion. Do not use it as a physical kinematics case, do not infer size/speed/range/altitude, and do not force a D44/D56/D58 range-fouler pairing without source metadata. The next standalone visual target is PR47 (`DOD_111689142.mp4`) because it tests the separate three-contrast-area / fixed-relative-position lane.

### 2026-05-13 PR47 Formation Fallback Review

Attempted the next standalone visual target, `DOD_111689142.mp4` / DVIDS `DOW-UAP-PR47`.

Blocker:

- The full Drive-backed MP4 could not be opened because the local filesystem reported zero free bytes.
- Raw reads from `source-files-not-included/DOD_111689142.mp4` failed with `No space left on device`.
- OpenCV could not open the PR47 MP4, so a dense full-video pass could not run in this turn.

Generated supporting files added in this fallback pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_pr47_formation_visual_pass.py`: PR47 full-video formation-pass script, ready to run once disk space is available.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr47-formation-fallback-notes.md`: fallback note.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-fallback-frame-review-dod111689142.csv`: eight-frame fallback rows from existing extracted frames.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-fallback-frame-summary.csv`: fallback summary.

Fallback findings:

- The fallback pass used the eight existing second-pass full-frame JPGs for PR47.
- Five frames had high-confidence three-component detections: `12s`, `30s`, `48s`, `65s`, and `115s`.
- One frame had medium partial formation support at `101s`; one frame was low at `0s`; one frame had no conservative detection at `83s`.
- The three-component rows have compact max pair distances: `49.664 px`, `61.493 px`, `42.348 px`, `60.842 px`, and `48.235 px`.
- The cluster is high in the crop from `12s-65s`, not conservatively recovered at `83s`, partially recovered at `101s`, and recovered again lower in the field at `115s`.

Updated PR47 treatment:

Keep PR47 as the strongest standalone multi-object/formation lane so far, but only at fallback confidence until local disk space is freed and the full `5 fps` MP4 pass can run. Do not use PR47 for physical kinematics, object size, range, altitude, or speed.

### 2026-05-13 PR47 Full Formation Visual Review

The full PR47 MP4 pass completed after local disk availability recovered.

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr47-formation-visual-notes.md`: full PR47 formation note.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-formation-review-dod111689142.csv`: per-sample full-video formation rows.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-formation-summary.csv`: phase summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr47-formation-assets.csv`: generated asset index.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-dod_111689142-metadata.txt`: OpenCV source metadata and review settings.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-motion-pass/pr47-standalone/DOD_111689142/*`: annotated crops, formation patches, and contact sheets.

PR47 full-pass findings:

- Across `598` sampled rows, the pass produced `341` high, `125` medium, `76` low, and `56` none classifications.
- It found three-component groups in `349/598` rows and high-or-medium support in `466/598` rows.
- Median max pair distance stayed close across phases: `48.430 px`, `51.264 px`, `51.080 px`, and `48.911 px`.
- The cluster persists while moving through the field: high in the crop, then upper-to-mid descent, then reticle-near, then late lower-field recovery.
- Overlay/reticle confounding remains the main caveat, especially near the centerline.

Updated PR47 treatment:

Promote PR47 to the strongest standalone multi-object/formation visual lane in the local corpus. It supports the public-release description of three contrast areas maintaining fixed relative positions, but it still does not establish independent objects, physical separation, speed, range, altitude, or a hard `D` report pairing.

### 2026-05-14 Evidence Ladder Synthesis

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-evidence-ladder.md`: ranked synthesis of hard paired cases, document-only cases, standalone video lanes, pattern lanes, controls, and next work queue.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-evidence-ladder.csv`: machine-readable evidence ladder with rank, tier, evidence class, pairing status, confidence, caveat, and next action fields.

Evidence ladder findings:

- The strongest public evidence lanes remain hard report/video or strong report-content/video reconciliations: `D38/PR36`, `D33/PR34`, `D25/PR28`, `D27/PR29`, `D23/PR27`, and `D35/PR35`.
- `D38/PR36` remains the calibration anchor because DVIDS explicitly pairs `DOD_111689030.mp4` with `DoW-UAP-D38`.
- `D33/PR34` is the strongest Greece ocean-surface maneuver lane, but only at the image-plane support level; the true physical turns and `80 MPH` remain report-derived.
- `D25/PR28` and `D27/PR29` stay high because the report-content matches are strong despite DVIDS `D7` and `D8` label conflicts.
- `D58` is promoted to the immediate next analytic target because it combines radar lock, target-pod video, KINGPIN-directed identification, two IR-significant contacts, red blinking strobes, and noise-jamming language.
- `PR44`, `PR47`, and `PR45` remain standalone visual lanes with no hard `D` report pairing. `PR44` is the compact-return benchmark; `PR47` is the formation-like benchmark; `PR45` stays below both.

Updated treatment:

Use the evidence ladder as the active triage map. The next work item is a dedicated `D58` evidence packet and source-request checklist, not another generic video pass.

### 2026-05-14 D58 Evidence Packet

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d58-evidence-packet.md`: dedicated D58 evidence packet and source-request checklist.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d58-evidence-constraints.csv`: machine-readable D58 constraints.

D58 findings:

- D58 is the highest-value unresolved document-only target in the range-fouler set.
- Preserved anchors include `10/27/20`, `01:12:21Z`, night `DCA` context, contact altitude `26000`, altitude constant `No`, moving contact `Yes`, stable trackfile `Yes`, and `2` contacts in the group.
- The narrative preserves KINGPIN-directed ID, radar lock, target-pod video, closest range `16.9NM`, two IR-significant contacts, `2X RED BLINKING STROBES`, and noise jamming indicated by two chevrons.
- The apparent relative-motion phrase about one range fouler circling the other is important but should not be used for turn-rate, acceleration, or exotic-motion claims without video/radar data.
- Red strobes, jamming, radar lock, target-pod video, and directed ID are strong operational details, but also strong conventional-confound details.
- No hard public PR/DVIDS video pairing is known for D58 in the current local notes.

Updated D58 treatment:

Keep D58 as a source-request target, not a public kinematics case. The required next evidence is target-pod video, radar track data, EW/noise-jamming logs, KINGPIN communications, platform state, unredacted coordinate/bullseye context, and any official PR/DVIDS page explicitly naming D58 or its unique anchors.

### 2026-05-14 Range-Fouler Official Metadata Check

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-official-metadata-check.md`: live official-source check for `D44`, `D56`, `D57`, and `D58`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-official-metadata-check.csv`: machine-readable official-source check rows.

Metadata check findings:

- War.gov directly serves all four checked PDFs: `D44`, `D56`, `D57`, and `D58`.
- No new public DVIDS/PR video pairing was found for `D44`, `D56`, `D57`, or `D58`.
- `D38/PR36` remains the only hard DVIDS report/video anchor in the range-fouler lane.
- `PR42`, `PR44`, and `PR47` remain standalone public videos. Their DVIDS pages do not name `D44`, `D56`, `D57`, or `D58`, and each lacks an oral/written reporter description.
- The War.gov PDFs preserve the already-known metadata collisions: `D56` displays PDF title metadata as `DoW-UAP-D33`, `D57` as `DoW-UAP-D34`, and `D58` as `DoW-UAP-D35`. Treat these as official-source metadata noise rather than merging them with the Greece `D33/D35` lanes.

Updated treatment:

The range-fouler source posture is stable: no public video pairing should be asserted for `D44`, `D56`, `D57`, or `D58`. The next analytic lane is the Persian Gulf / Strait of Hormuz 2020 timeline across `D4`, `D5`, and `D60-D65`.

### 2026-05-14 Persian Gulf / Strait Of Hormuz 2020 Timeline

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-persian-gulf-2020-timeline.md`: focused timeline and pattern assessment for `D4`, `D5`, and `D60-D65`.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-persian-gulf-2020-timeline.csv`: machine-readable timeline rows.

Timeline findings:

- The core Persian Gulf / Strait of Hormuz 2020 pattern is `D60-D65`, not the full `D4`, `D5`, `D60-D65` set.
- `D60-D65` preserve nine core observation rows from July-November 2020 during NAVCENT Arabian Gulf / Strait of Hormuz / Gulf of Oman tasking.
- `D65` is the densest single mission: three FMV unidentified-aerial-phenomenon observations on `2020-07-16`, with one full readable grid, `39RUN6234236874`, decoding to approximately `29.253233N, 49.583281E`.
- `D61` is the strongest individual row: a formation of unknown flying objects moved NE-NW along the coast and was tracked for about two minutes before PID was lost in cloud cover.
- `D4` and `D5` remain useful quantitative short UAP lines, but they are demoted from the core Gulf/Strait cluster because their readable MGRS grids decode outside the Gulf lane despite Arabian Gulf filenames.
- `D4` grid `34SDG9041417044` decodes to approximately `37.199812N, 20.891980E`; `D5` grids `34SCE7566990098` and `35TQK1580995057` decode to approximately `36.047497N, 19.619714E` and `45.076058N, 29.741793E`.

Updated treatment:

Keep `D60-D65` in Tier 4 as a regional reporting-density pattern, not a physical-performance lane. Use `D61` as the next focused source-review target if this lane stays active. Keep `D4/D5` adjacent until their source-label/grid mismatch is resolved.

### 2026-05-14 D61 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d61-source-review.md`: focused source review for the strongest Persian Gulf / Strait of Hormuz 2020 row.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d61-evidence-constraints.csv`: machine-readable D61 constraints.

D61 findings:

- D61 is the strongest individual row in the `D60-D65` Gulf/Strait pattern lane.
- Preserved anchors include `271527:00ZAUG20`, a `1527Z-1529Z` observation window, NAVCENT Arabian Gulf / Strait of Hormuz / Gulf of Oman tasking, AN/DAS-4-style sensor context, G-MESH availability, partial `39RVM3` aircraft-location and `39RVM8` observed-activity grid lanes, and method of observation `SENSOR`.
- The source describes a `FORMATION OF UNK FLYING OBJECTS` traveling `NE-NW` along the coast and tracked for about two minutes.
- PID was lost in cloud cover, the aircrew could not regain PID, and light cloud coverage prevented continuous tracking.
- D61 does not preserve object count, size, shape, altitude, speed, range, formation spacing, raw video, sensor FOV, platform state, or a public PR/DVIDS video pairing.

Updated D61 treatment:

Use D61 as a source-reviewed regional pattern row, not a performance case. The next useful step inside this lane is a compact `D65` source review, because D65 is the densest single mission with three FMV UAP observations on `2020-07-16`.

### 2026-05-14 D65 Source Review

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d65-source-review.md`: focused source review for the densest Persian Gulf / Strait of Hormuz 2020 mission.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d65-evidence-constraints.csv`: machine-readable D65 constraints.

D65 findings:

- D65 is the densest single mission in the `D60-D65` Gulf/Strait pattern lane.
- The source is MISREP `4472514`, a NAVCENT mission in the Arabian Gulf / Strait of Hormuz / Gulf of Oman lane with AN/DAS-4-style sensor context, G-MESH availability, and FMV exploited by `DGS-1`.
- The mission report preserves three FMV UAP observations on `2020-07-16`: `161830:00ZJUL20`, `161920:00ZJUL20`, and `162345:00ZJUL20`.
- The first observation preserves aircraft partial `39RXK3...`, heading `152M`, `FL200`, `98 KIAS`, observed activity near partial `39RVM...`, description `UAP`, and method `FMV`.
- The second observation preserves aircraft location OCR likely partial `39RUN...`, heading `34M`, `FL190`, `90 KIAS`, observed activity near partial `39RUN...`, description `UAP`, and method `FMV`.
- The third observation preserves aircraft partial `39RUN...`, heading `331M`, `FL191`, `115 KIAS`, observed activity grid `39RUN6234236874`, description `UAP`, and method `FMV`.
- The full third-observation grid `39RUN6234236874` decodes to approximately `29.253233N, 49.583281E`, confirming at least one D65 observation in the northern Persian Gulf lane.
- Each UAP observation block states that weather was not a factor.
- D65 does not preserve public object shape, size, altitude, speed, range, bearing, trajectory, raw FMV, FOV, platform state, or a public PR/DVIDS video pairing.

Updated D65 treatment:

Use D65 as the strongest reporting-density row in the Gulf/Strait cluster. Pair it with D61 in the final report: D61 is the strongest behavior row, while D65 is the densest single-mission row. Neither should be used for anomalous-performance claims without raw FMV and telemetry.

### 2026-05-14 Final Report Coverage Audit And Scaffold

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-report-coverage-audit.md`: final-report readiness audit across the full local corpus and evidence lanes.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-report-coverage-audit.csv`: machine-readable coverage status by corpus area.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-scientific-report-outline.md`: final scientific report scaffold.

Coverage findings:

- The local UFO folder has `170` inventoried files: `91` PDFs, `41` MP4 videos, `34` JPG images, and `4` PNG images, totaling about `4.24 GB`.
- The modern DoW/DoD operational subset and public DoD video set are ready for a defensible professional report.
- The historical FBI/NASA/DOS/archive/image material is inventoried and triaged, but not exhaustively OCR-reviewed or interpreted at the same depth.
- The final report should therefore be framed as a scientific assessment of the release with strongest conclusions drawn from modern operational records and public media, while the broader historical corpus remains lower-priority context unless future work promotes specific records.
- The stable report conclusion is that the corpus supports credible unresolved operational observations, not non-human technology, recovered materials, or independent public kinematic reconstruction.

Updated treatment:

Use the coverage audit and scaffold as the bridge into the final report. The next useful action is to draft the final scientific report itself, then run a consistency pass against the evidence ladder, correlation matrix, priority digest, and source packets before marking the overall UFO-analysis goal complete.

### 2026-05-14 Final Scientific Report Draft

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-scientific-report.md`: professional scientific report draft for the UFO/UAP release corpus.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-report-consistency-check.md`: consistency check for report references, evidence-ladder alignment, source-index handling, scope language, origin claims, and kinematics claims.

Final report findings:

- The report assesses the full local folder inventory but explicitly scopes the strongest conclusions to the deeply reviewed modern DoW/DoD operational subset and public DoD media.
- The stable conclusion is that the corpus supports credible unresolved operational observations, not non-human technology, recovered material, or independent public reconstruction of extraordinary physical performance.
- The evidence ranking has `18` rows and aligns with `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-evidence-ladder.csv`.
- The report preserves D38/PR36 as the hard calibration anchor, D33/PR34 as the image-plane maneuver benchmark, D25/PR28 and D27/PR29 as source-index-corrected report/video lanes, D58 and D28 as the top document-only source-request targets, and D61/D65 as the Persian Gulf / Strait 2020 pattern lane.
- The consistency check found `43` unique local support-file references in the report and `0` missing referenced files.
- The report keeps historical FBI/NASA/DOS/archive/image material as inventoried and triaged context, not as an exhausted basis for strong scientific claims.

Updated treatment:

The final report draft is ready for review as a professional scientific report focused on the modern operational evidence. The remaining decision is scope: accept it as a modern-release report with explicit limits, or run targeted historical/NASA/FBI image review before calling the entire 170-file corpus exhausted.

### 2026-05-14 Goal Completion Audit

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_build_file_coverage_map.ps1`: repeatable file-level coverage mapper.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-map.csv`: file-level coverage map for all `170` manifest rows.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-summary.csv`: grouped coverage summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-goal-completion-audit.md`: prompt-to-artifact completion audit for the active UFO-analysis goal.

Audit findings:

- The current final scientific report is valid as a scoped modern-operational-release report.
- The literal goal is not complete yet because it asks for the entirety of the documents, videos, and images.
- Current file-level coverage: `32` deep-review files, `26` structured-triage PDFs, `26` visual-triage videos, `1` partial-review file, and `85` inventory-only files.
- Inventory-only groups include `37` historical FBI/archive PDFs, `13` NASA transcript/image files, `2` DOS cables, and `33` FBI photo-set files.
- The final report should not be treated as corpus-exhaustive until those groups receive at least a targeted triage pass and any resulting insights are incorporated or ruled out.

Updated treatment:

Keep the active goal open. The next concrete work is a whole-corpus gap pass focused on historical/NASA/DOS PDFs and image sets, starting with text extraction/keyword triage and image contact-sheet/provenance review.

### 2026-05-14 NASA And DOS Gap Triage

Generated supporting files added in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_extract_pdf_text_for_groups.ps1`: attempted local PDF extraction for NASA/DOS groups.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pdf-text-extraction-log.csv`: extraction log showing local extraction blocked by disk/read errors.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-nasa-dos-gap-triage.md`: targeted NASA/DOS gap triage using official War.gov sources and official-source indexed mirrors.

NASA/DOS findings:

- Local extraction failed because the mounted filesystems had only about `0.16 GB` free and Drive-mounted PDF reads returned `There is not enough space on the disk`.
- The pass used official War.gov source URLs where possible, plus official-source indexed mirrors when War.gov PDF fetches were unavailable through the browser.
- NASA records add useful historical spaceflight context but do not outrank the modern DoW/DoD operational evidence.
- Apollo 12 records are bounded by particles, tracking-light, water-boiler, and spacecraft-material context.
- Gemini 7 preserves the "bogey" language, but the same transcript includes booster and particle/debris context.
- Apollo 17 is the strongest NASA lane, but the transcript contains S-IVB/SLA-panel and fragment explanations, while the VM6 image lacks enough calibration for object claims.
- Skylab is useful as a control because it explicitly discusses satellites, Skylab pieces, and cosmic-particle-like light flashes.
- The 1985 Papua New Guinea DOS cable is a sketchy diplomatic inquiry over high-altitude/high-speed objects and contrails, not a resolved physical case.
- The 1994 Tajik Air / Kazakhstan DOS cable is the strongest historical witness/diplomatic narrative so far, but the extraterrestrial/intelligent-control language is pilot opinion; the embassy records no opinion.

Updated treatment:

Promote NASA/DOS from inventory-only to targeted triage. This adds historical breadth but does not change the final scientific report's main conclusion: the modern operational DoW/DoD records remain the strongest evidence lane, and the broader corpus still does not support non-human-technology or independently reconstructed extraordinary-physics claims.

### 2026-05-14 Coverage Map Refresh After NASA/DOS Triage

Generated supporting files updated in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_build_file_coverage_map.ps1`: now recognizes group-level targeted review artifacts for NASA transcript/image files and DOS cables.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-map.csv`: regenerated file-level coverage map.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-summary.csv`: regenerated grouped coverage summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-goal-completion-audit.md`: revised audit counts and remaining-gap table.

Coverage refresh findings:

- NASA transcript/image files and DOS cables are no longer inventory-only; they are now counted as `targeted_review` based on `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-nasa-dos-gap-triage.md`.
- Current file-level coverage: `32` deep-review files, `26` structured-triage PDFs, `15` targeted-review NASA/DOS files, `26` visual-triage videos, `1` partial-review file, and `70` inventory-only files.
- The remaining inventory-only groups are now narrowed to `37` historical FBI/archive PDFs and `33` FBI photo-set files.

Updated treatment:

The next highest-value gap is the FBI photo-set lane, because it is image-heavy and the literal goal requires analysis of images as well as documents and videos. The pass should focus on provenance and contact-sheet-level review first, not unsupported pixel-level claims.

### 2026-05-14 FBI Photo Set Gap Triage

Generated supporting files added or updated in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-gap-triage.md`: targeted source/provenance triage for the FBI photo set.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-record-index.csv`: machine-readable mapping from local FBI photo files to official War.gov records.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_build_file_coverage_map.ps1`: now recognizes the FBI photo triage as a group-level targeted review artifact.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-map.csv`: regenerated file-level coverage map.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-summary.csv`: regenerated grouped coverage summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-goal-completion-audit.md`: revised audit counts and remaining-gap table.

FBI photo findings:

- The `33` local FBI photo-set files correspond to `32` official records: `8` A-series image files and `24` B-series PDF still-image records.
- `B6` appears twice locally because the folder contains both `fbi-photo-b6.pdf` and an extracted `fbi-photo-b6.jpg`.
- The A-series consists of late-2025 FBI/AARO still images derived from a U.S. government system, without event location, specific date, mission report, platform data, calibration, range, or kinematics.
- The B-series consists of late-2025 western-U.S. FBI/AARO still images derived from a U.S. military system. The embedded image timestamp is not reliable because the system date/time was not set.
- `B5` is useful as a control-like frame because no distinct central object is clearly visible.
- `B6` and `B7` are the strongest visual examples in the FBI photo set, but `B7` is officially described as consistent in appearance with a helicopter, which weakens the case for exotic interpretation.
- The FBI photo set broadens image coverage but does not outrank the modern DoW/DoD operational evidence lanes.

Updated coverage:

- Current file-level coverage: `32` deep-review files, `26` structured-triage PDFs, `48` targeted-review NASA/DOS/FBI-photo files, `26` visual-triage videos, `1` partial-review file, and `37` inventory-only files.
- The only remaining inventory-only group is now `37` historical archive PDFs.

Updated treatment:

Use the FBI photo set as a low-weight static-image appendix in the final report. The next highest-priority gap is the historical archive PDF group, because it is now the only untouched file family left under the literal whole-corpus completion standard.

### 2026-05-14 Historical Archive Gap Triage And Final Report Update

Generated supporting files added or updated in this pass:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-gap-triage.md`: targeted source-family triage for the remaining historical/archive PDF group.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-record-index.csv`: machine-readable mapping for all `36` historical/archive rows after moving the Gemini 7 transcript into NASA coverage.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/scripts/ufo_build_file_coverage_map.ps1`: now classifies `255_t_763_r1b_transcripts.pdf` as NASA material and recognizes the historical archive triage artifact.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-map.csv`: regenerated file-level coverage map.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-file-coverage-summary.csv`: regenerated grouped coverage summary.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-scientific-report.md`: updated with broader-corpus Finding 9.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-final-report-consistency-check.md`: refreshed after final report update.
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-goal-completion-audit.md`: updated to show `0` inventory-only files.

Historical archive findings:

- The remaining historical/archive files divide into source families: wartime foo-fighter context, early Air Materiel/Air Force reporting, Project Blue Book style incident summaries, Cold War air-intelligence reports, FBI HQ `62-HQ-83894` files, State/public-discourse context, and recent FBI/AARO witness or site reports.
- `342_hs1-416511228_box186_319.1-flying-discs-1949.pdf` and the two `38_143685` incident-summary files are the best future OCR candidates because they are most likely to preserve structured dates, locations, weather, altitude, movement, and witness fields.
- The FBI HQ `62-HQ-83894` sections are valuable for institutional history and public-report intake, not stronger physical evidence than the modern operational records.
- The recent FBI/AARO witness records, especially `usper-statement-redacted.pdf`, are useful narrative outliers but remain statement/reporting evidence without public telemetry, imagery, or physical samples.
- The State/public-discourse files are context only and should not be elevated into physical or biological evidence.

Updated coverage:

- Current file-level coverage: `32` deep-review files, `26` structured-triage PDFs, `85` targeted-review files, `26` visual-triage videos, `1` partial-review file, and `0` inventory-only files.
- The final report now states that historical and static-image material adds breadth but does not change the main conclusion.

Updated treatment:

The active UFO analysis is now complete as a targeted whole-corpus scientific assessment. It remains non-exhaustive in the forensic sense: future work can still deepen OCR, photogrammetry, raw-video reconstruction, and source requests, but no unreviewed file family remains.
