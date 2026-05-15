# UFO D28 Source Review

Owner: Dan Fredriksen
Created: 2026-05-12
Source file: `source-files-not-included/dow-uap-d28-mission-report-east-china-sea-2024.pdf`
Official URL: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d28-mission-report-east-china-sea-2024.pdf`
Status: Focused source review

## Bottom Line

`D28` remains one of the strongest single-document sensor-event records in the local corpus, but the source review resolves the geography issue against the filename. The PDF filename and PDF metadata title say `East China Sea, 2024`; the report body is consistently a USCENTCOM / Operation Inherent Resolve / OKAS / Ayn Al Asad ROZ Raindrop event. Treat this as an Iraq / Ayn Al Asad-area report with a source metadata or naming mismatch, not as an East China Sea event.

The core claim is still narrow: during an AGM-176 employment sequence on 2024-09-20, operators reported a UAP crossing the aircraft sensor field between munition release and impact, producing IR lens flare on MX-20 and MX-25 sensors. The report does not provide enough public data to derive speed, range, size, altitude, or object identity.

## Extracted Source Fields

| Field | Value |
|---|---|
| Internal PDF title | `DOW-UAP-D28, Mission Report, East China Sea, 2024` |
| Report type | MISREP |
| Operation | Operation Inherent Resolve |
| Combatant command | USCENTCOM |
| Major command | AFSOC |
| Originator | SOTU 016 |
| Takeoff / landing | OKAS / OKAS |
| Takeoff DTG | `201740:00ZSEP24` |
| On-station DTG | `201930:00ZSEP24` |
| Off-station DTG | `202323:00ZSEP24` |
| Initial UAP contact | `202027:59ZSEP24` |
| Event serial | `202027ZSEP2024-CENTCOM` |
| Operational range | Ayn Al Asad ROZ Raindrop |
| Friendly aircraft altitude | FL130 |
| Friendly aircraft speed | 170 KIAS |
| Friendly aircraft trajectory | 096, straight and level |
| Sensor/signature language | IR signature detectable by MX-20 and MX-25 |
| UAP event type | UAP incident |
| Observer assessment | Benign |
| Third-party aircraft reporting | No additional aircraft reported in the relevant airspace |
| Effects on persons/equipment | No effects on persons; no equipment effects |
| Recovered material | No |
| Engagement | No observer engagement of UAP |
| Kinematic fields | Altitude, velocity, and trajectory fields are blank or marked estimated without public values |

## Evidence Value

D28 is high value because it combines:

- A precise event time.
- A mission phase with a narrow operational sequence: munition release to impact.
- Named sensor systems: MX-20 and MX-25.
- A stated heat-signature interpretation.
- Negative controls: no reported third-party aircraft, no effects on equipment or persons, no recovered material, no observer engagement, and no reobservation.

The most important evidentiary feature is the dual-sensor IR/lens-flare claim. The public release describes the sensor effect and operator interpretation, but it does not include raw sensor telemetry, targeting video, platform motion, slant range, FOV/zoom state, target coordinates, or munition timing logs.

## Caveats

- The filename/internal title conflicts with the report body. Use the body-controlled location and event metadata for analysis.
- The body references MGRS `38S` coordinates and Ayn Al Asad, which are inconsistent with an East China Sea label.
- The report describes a lens flare and inferred heat source. It does not prove an object size, shape, or propulsion mechanism.
- The "high rate of speed" language is reporter characterization; public kinematic fields do not preserve a measured speed.
- No local MP4 has been hard-paired to D28 in the current report-video matrix.

## Follow-Up

1. Keep D28 in the high-priority document lane, but relabel the analytic region as Iraq / Ayn Al Asad area.
2. Treat East China Sea / INDOPACOM 2024 videos as a separate lane unless a source index explicitly connects them to this report.
3. If a video match appears in a later release or correction, prioritize frame review around the munition-release-to-impact interval and look for dual-sensor or lens-flare cues before doing any kinematic analysis.

## Evidence Packet Addendum

Dedicated packet: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-evidence-packet.md`

Constraint table: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-evidence-constraints.csv`

The evidence-packet pass keeps D28 high in the document-only lane and narrows what can be claimed. The official PDF preserves a strong event anchor, `202027:59ZSEP24`, and a dual-sensor IR/lens-flare claim involving `MX-20` and `MX-25`, but it does not preserve the raw imagery, release/impact timestamps, FOV, range, sensor pointing, object size, altitude, speed, or trajectory needed for physical-performance analysis.

A local corpus scan for D28's unique anchors (`AGM-176`, `MX-20`, `MX-25`, `202027ZSEP2024-CENTCOM`, `AYN AL ASAD`, `ROZ RAINDROP`, `MUNITION RELEASE`, and `MUNITION IMPACT`) found matches only in D28 and our derived notes. Treat D28 as a single-document lane unless new official metadata links it to another release.

## Release-Index Search Addendum

Dedicated note: `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-release-index-search.md`

The release-index search found no hard public PR/video pairing for D28. `DOW-UAP-PR28` is a Greece case tied by DVIDS to filename `DOD_111688954` and accompanying report `DoW-UAP-D7`; `DOW-UAP-PR46` is an INDOPACOM/East China Sea standalone video tied by DVIDS to filename `DOD_111689133` with no oral or written reporter description. Neither official DVIDS page mentions D28, `202027ZSEP2024-CENTCOM`, AGM-176, MX-20/MX-25, or Ayn Al Asad.

D28 therefore remains document-only in the current correlation matrix. The next similar reconciliation target is PR28, because DVIDS's `DoW-UAP-D7` label conflicts with the local text lane where the SWIR-only diamond / 434-knot language appears in `D25`.
