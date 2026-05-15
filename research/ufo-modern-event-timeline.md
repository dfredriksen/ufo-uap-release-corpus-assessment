# UFO Modern Event Timeline

Owner: Dan Fredriksen
Created: 2026-05-09
Source files: official public UFO/UAP release files, not redistributed in this repository
Status: Working timeline

This timeline normalizes the modern UAP/UFO report subset into event rows. It is intentionally conservative: a row means "the released document reports this," not "the event is independently confirmed."

The machine-readable companion file is `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-modern-event-timeline.csv`.

## Timeline Takeaways

- The densest cluster so far is maritime: Arabian Gulf, Persian Gulf, Strait of Hormuz, Gulf of Oman, North Arabian Sea, Gulf of Aden, Greece/Eastern Mediterranean, and UAE over-water events.
- 2020 is a major cluster year in the extracted material, especially around Gulf/Strait missions and range-fouler forms.
- Several stronger records involve sensor-specific or operationally constrained observations: `d28` heat-source/sensor crossing, `d27` glowing sphere with pole/bar, the range-fouler cluster, `d25` SWIR-only diamond/probe, and `d33` ocean-surface 90-degree turns. `d35` is now source-reviewed as the paired Greece ocean-surface comparison case, but remains medium priority because the report lists no maneuverability observations and the public clip is kinematically weak.
- The corpus also contains internal controls: birds/dust in `d10`, glare/halo in `d32`, balloon-like wind-traveling object in `d7`, and UAP/UAV ambiguity in `d18`.

## High-Priority Event Rows

| Event | Source | Why it stays high priority | Main caveat |
|---|---|---|---|
| 2024-09-20 20:27:59Z | `dow-uap-d28-mission-report-east-china-sea-2024.pdf` | UAP crossed sensor field between munition release and impact; MX-20/MX-25 IR lens flare indicates significant heat source | Filename geography conflicts with extracted event context |
| 2024-06-07 04:57Z | `dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf` | Glowing hot spherical object with vertical pole/bar or possible water reflection; straight over water at estimated `140 KNOTS`; precise first accuracy | Best written-report content match for DVIDS `PR29` / `DOD_111688964`; DVIDS labels accompanying report `D8`; filename date and event serial contain date mismatches |
| 2020 range-fouler cluster | `d38`, `d44`, `d56`, `d57`, `d58` | Sensor geometry, IR observations, negative ES/radar/IFF in one case, radar lock/target-pod/jamming language in another | Several details are OCR-noisy and could fit conventional platforms |
| 2024-01-25 05:09Z | `dow-uap-d25-mission-report-greece-january-2024.pdf` | Round/diamond object with non-maneuvering tail/probe, visible only on SWIR, about two minutes; gentext reports approximately `434 KNOTS` | PR28 video supports SWIR sequence, not independent speed/range/altitude/shape validation; DVIDS labels report `D7` |
| 2023-10-27 00:35Z | `dow-uap-d33-mission-report-greece-october-2023.pdf` | Seemingly circular object just above ocean surface making multiple reported 90-degree turns at estimated `80 MPH`; hard PR34 video pairing | Public manual track supports sharp image-plane heading changes, not independent physical turn/speed validation |
| N/A 13:19Z | `dow-uap-d54-mission-report-mediterranean-sea-na.pdf` | Triangular and metallic UAP over `363453N 0255943E`, at `24,989FT MSL` and `168KTS` | Full date, sensor, event serial, raw imagery, FOV, range, and telemetry not public; PDF metadata says `DoW-UAP-D31` |
| 2023-11-09 21:53Z | `dow-uap-d74-mission-report-syria-november-2023.pdf` | Seven-minute probable-UAP pass during Syria / Operation Inherent Resolve ISR mission; near co-altitude, estimated `424KN`, no emissions/effects | Document-only; speed and shape are report-derived; PDF metadata says `DoW-UAP-D42`; no hard video pairing found |
| 2024-07-14 05:17Z | `dow-uap-d75-mission-report-gulf-of-aden-july-2024.pdf` | Gulf of Aden FMV mission report; straight same-altitude path, estimated low altitude, estimated NW trajectory, followed until too distant, faster than observing platform | Description/gentext redacted; no public absolute velocity, shape, or video pairing |
| 2025 16:53Z | `dow-uap-d8-mission-report-djibouti-2025.pdf` | Two round white-hot UAPs moving south at about `240NM/HOUR` near `35SQT3423692957` | Full date not public; grid decodes to Eastern Mediterranean despite Djibouti filename/title; no video pairing |

## Pattern Notes

The emerging pattern is not one object type. It is a set of recurring reporting situations: over-water sensor tracks, FMV-observed unknowns during ISR missions, range-fouler forms, and short aircraft observations. Object descriptions vary widely: round/circular, diamond/probe, triangular/metallic, glowing sphere with pole/bar, white-hot UAPs, cold IR objects, and kite/orb witness narratives.

That variability matters. It argues against treating the corpus as one phenomenon at this stage. The better analytic structure is by evidence lane:

1. Structured mission reports with exact DTGs.
2. Range-fouler forms with sensor geometry.
3. Email/tearline authorization metadata.
4. Briefing/witness summaries.
5. Historical archive and media awaiting correlation.

## Next Correlation Step

The next useful move is to map `DOD_*.mp4` files against high-priority event DTGs. The current video filenames do not expose report IDs, so correlation needs one of:

- embedded video metadata beyond Shell properties,
- frame overlays visible in the videos,
- source release page metadata,
- or exact matching from DoD release packaging.

Until that link is made, the MP4s remain a media pool rather than evidence tied to specific report rows.
