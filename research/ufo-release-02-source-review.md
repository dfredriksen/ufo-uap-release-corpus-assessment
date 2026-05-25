# UFO Release 02 Source Review

Owner: Dan Fredriksen
Created: 2026-05-24

## Scope

This note is the first-pass source review for the most interesting non-video records in WAR.GOV Release 02. It is intentionally conservative: the goal is to identify which new lanes merit deeper follow-up, not to promote every new file into the main evidence ladder.

Release 02 adds `64` records to the live feed. The strongest new non-video records are the ODNI narrative, the DOE Pantex imagery, the CIA USSR report, the Sandia Base packet, and the Apollo 12 audio control lane.

## Findings

### D017 - Sandia Base packet

The official release blurb presents this as a large Sandia Base correspondence packet with many reported sightings. The local PDF extract is mixed: the first pages are routine 1949 security-inspection correspondence rather than a clean UAP summary. That means the file needs page-level triage before it can be treated as a clean incident packet.

Current treatment:

- Historical archive packet
- Not yet an evidence-ladder promotion
- Needs page-level OCR and sectioning before any claim about the UAP summary can be used

### CIA-UAP-D001 - USSR intelligence report

This is a historical CIA intelligence report with a source account from the USSR in 1973. The extracted text preserves a small but clear narrative: the source describes a bright green circular object or mass, followed by green concentric circles, then fading with no sound.

Current treatment:

- Historical narrative lane
- Useful as a source-family example, not as a physical-performance case
- No raw sensor data or independent confirmation in the release

### ODNI-UAP-D001 - Senior USIC narrative

This is the strongest new narrative record in Release 02. It is a first-hand account from a senior U.S. intelligence official describing a helicopter mission over a test range, with:

- orb-like sightings near the range
- a low-altitude search using FLIR, NVG, and naked-eye observation
- a high-speed hot object that split into two
- multiple orange orbs near the helicopter and above fighter jets
- a direct reference to accompanying infrared imagery from the earlier May 8 release

The rendered PDF is a 2-page, Word-generated document with clean, readable narrative text and no obvious extraction failure. The page layout confirms this is a structured authored statement rather than a scanned note or redaction-heavy packet. The text is internally specific enough to preserve the operational sequence: early search for debris, later radar cueing, FLIR/NVG/naked-eye observation, a hot object that split in two, a hover at approximately 700 feet AGL, a cluster of orange orbs near the helicopter, and repeated appearances above the fighter jets.

Current treatment:

- High-value narrative lane
- Stronger than the CIA entry because it is contemporaneous, multi-sensor, and explicitly tied to related imagery
- Still not enough for a physical kinematics claim without the associated imagery, telemetry, and source metadata

This is also the only Release 02 row that explicitly bundles Release 01 evidence. The linked Phase 1 set is inventoried in `research/ufo-release-02-phase1-linkage-inventory.csv` and consists of the `USPER Statement about UAP Sighting` narrative plus FBI Photo A001-A008 and FBI Photo B001-B024.

The bundle-level reconciliation is now documented in `research/ufo-release-02-phase1-linkage-analysis.md`. The bottom line there is the same: the linked Phase 1 material corroborates the narrative and provenance, but it does not supply public kinematics.

### DOE-UAP-D001 - Pantex imagery

This is an enhanced image package from a ground surveillance radar tower with Sandia National Labs enhanced images of the object. The file is visually important but still needs proper OCR, image extraction, and provenance review.

The PDF is a compact 2-page encrypted packet. The first page presents the Pantex UAP incident report heading with a single red-circled image area; the second page presents a "Sandia National Labs Enhanced Images of the Object" page with two stacked object images. The text layer is minimal, but the visual content is clear enough to establish that this is an image/provenance packet rather than a narrative report. The visible object is small, dark, and blurred, so the current public release supports provenance and enhancement context, not reliable shape or kinematic inference.

Current treatment:

- Image/provenance lane
- Promising for a later visual pass
- Not yet a ranked evidence case

### DOE-UAP-D002 and DOE-UAP-D003

These are context records:

- James Tuck correspondence from the 1970s
- a Pajarito Astronomers invitation for a 1986 talk on UFOs

They are useful for historical context, but they do not currently outrank the more substantive narrative or image records.

### NASA-UAP-D008

Apollo 12 Medical Debriefing - Tape 12 is a control-style historical audio lane. The release framing makes it clear that the observed light-flash phenomena are treated as internal visual effects rather than external sources.

Current treatment:

- Historical control/caveat lane
- Useful for report context
- Not a candidate for promotion

## Working Triage

The Release 02 tranche does not change the main evidence hierarchy yet. `ODNI-UAP-D001` is the strongest new narrative lane, and `DOE-UAP-D001` is the strongest new image/provenance lane, but neither moves above narrative/image-triage without additional source material.

`D017` should stay in the historical archive queue until the packet is page-segmented and the Sandia-specific content is isolated.

## Next Actions

1. Carry ODNI-UAP-D001 and DOE-UAP-D001 into the combined-tranche final report as the strongest new non-video lanes.
2. Keep CIA-UAP-D001, D017, DOE-UAP-D002, DOE-UAP-D003, and NASA-UAP-D008 as lower-priority context or control material unless a later pass reveals a stronger direct linkage.
3. Preserve the Release 02 video review as a standalone release-family note rather than a set of new hard pairings.

## Release 02 Video Review Summary

The associated DVIDS page review for the Release 02 video tranche found `51` video entries, `43` unaltered pages, `8` digitally altered pages, one explicit duplicate pair (`PR057a` / `PR057b`), and one explicit non-duplicate same-title pair (`PR093` / `PR095`).

No Release 02 video page confirmed a new hard local D-report pairing. The tranche is therefore useful as a standalone release family and a control/provenance set, but not as a new source of hard report/video links in this repository.

See also the release-02 non-video review note: `research/ufo-release-02-nonvideo-review.md`.

