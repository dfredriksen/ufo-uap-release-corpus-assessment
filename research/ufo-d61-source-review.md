# D61 Source Review

Owner: Dan Fredriksen
Created: 2026-05-14
Source: `source-files-not-included/dow-uap-d61-mission-report-persian-gulf-august-2020.pdf`
Status: source review complete from local text extraction

## Bottom Line

`D61` is the strongest individual row in the Persian Gulf / Strait of Hormuz 2020 pattern lane. The report preserves a formation observation, a two-minute observation window, coastal movement, partial 39R grid context, AN/DAS-4 / G-MESH sensor context, and a clear reason the event ended: PID was lost in cloud cover and the aircrew could not regain it.

The report does not preserve enough public data to derive physical speed, altitude, range, object count, object size, formation spacing, or acceleration. Treat it as a strong regional pattern row and source-request target, not a performance case.

## Preserved Facts

| Field | Preserved value | Treatment |
|---|---|---|
| Report identity | `dow-uap-d61-mission-report-persian-gulf-august-2020.pdf` | Working source identity. |
| Report/provenance footer | `USCENTCOM MOR 26-0019`; approved for release to MRO/MR; `01/26/26` page footers | Provenance anchor; footer OCR varies by page. |
| Mission date | `2020-08-27` observation date from `271527:00ZAUG20` | Strong event date anchor. |
| Takeoff | `262307:00ZAUG20` from `OKAS` | Mission context. |
| ISR on-station window | `270041:00ZAUG20` to `271840:00ZAUG20` | Mission context. |
| Landing | `272012:00ZAUG20`; total mission time about `21 hours 5 minutes` | Mission context. |
| Supported unit | `NAVCENT` | Operational context. |
| Mission lane | Arabian Gulf / Strait of Hormuz / Gulf of Oman tasking context | Regional pattern context. |
| Mission type | `AREC` | Context only; not enough for object characterization. |
| Target pod / primary sensor | OCR as `ANDAS4`, interpreted as AN/DAS-4 | Sensor context; preserve OCR caveat. |
| Additional sensors | `AH_GMESH` / G-MESH available | Sensor context. |
| Observation DTG | `271527:00ZAUG20` | Direct observation anchor. |
| Observation duration | `1527Z` to `1529Z` | Direct narrative anchor; about two minutes. |
| Aircraft location | Partial `39RVM3...` lane | Redacted/partial grid only. |
| Observed activity location | Partial `39RVM8...` lane | Redacted/partial grid only. |
| Observed activity description | `FORMATION OF UNK FLYING OBJECTS` | Strongest descriptive anchor. |
| Method of observation | `SENSOR` | Direct observation field; FMV was exploited by DGS-1 in mission narrative. |
| Narrative behavior | Formation traveled `NE-NW` along the coast | Direct narrative text; use qualitatively. |
| End condition | PID lost in cloud cover; aircrew unable to regain PID | Strong caveat and event terminus. |
| Weather | Light cloud coverage prevented continuous tracking of the formation | Direct caveat; prevents overclaiming. |

## Claim Tiers

### Directly Preserved

- A formation of unknown flying objects was observed on `2020-08-27` from `1527Z` to `1529Z`.
- The observation was made by sensor during a NAVCENT mission in the Arabian Gulf / Strait of Hormuz / Gulf of Oman operating lane.
- The formation was described as traveling `NE-NW` along the coast.
- The aircrew tracked the formation for about two minutes.
- PID was lost in cloud cover, and the aircrew did not regain PID.
- The report preserves AN/DAS-4-style sensor context and G-MESH availability.

### Bounded Interpretations

- D61 supports a regional pattern claim: repeated official reporting of sparse FMV/sensor UAP or unknown-flying-object observations in the Gulf/Strait lane during 2020.
- D61 is stronger than most `D60-D65` rows because it preserves movement direction, formation behavior, duration, and the loss-of-PID reason.
- The `NE-NW` language should be treated as an operator description of apparent motion, not a reconstructed trajectory.

### Missing Or Redacted

- Number of objects in the formation.
- Object shape, size, color, altitude, speed, range, and spacing.
- Exact unredacted coordinates.
- Raw FMV, still frames, sensor pointing, field of view, platform state, and telemetry.
- Any public DVIDS/PR video pairing.
- Identification follow-up after PID was lost.

## Analytic Controls

Evaluate D61 against these non-extraordinary lanes before any stronger interpretation:

1. Birds or other biological formation movement over a coastal/maritime background.
2. Small aircraft, drones, or distant traffic moving along the coast.
3. Maritime/shoreline features or sensor/background contrast mistaken for a formation.
4. Cloud interruption and reacquisition failure due to weather rather than object behavior.
5. ISR tasking context, where many benign vessels, aircraft, UAS, and coastal activities were being scanned.

## Relationship To The 2020 Gulf/Strait Cluster

- `D65` is the densest single mission in the lane because it has three FMV UAP observations on `2020-07-16`.
- `D61` is the strongest individual behavior row because it has a formation, movement direction, two-minute observation window, and explicit PID-loss caveat.
- `D60`, `D62`, and `D64` are useful sparse FMV UAP rows.
- `D63` remains narrative-only until its observation section is recovered more clearly.
- `D4` and `D5` remain adjacent short quantitative rows, but their full readable grids decode outside the Gulf/Strait lane.

## Source-Request Checklist

Priority follow-up material:

1. FMV or sensor video for `271527:00ZAUG20` to at least `271529:00ZAUG20`.
2. DGS-1 exploitation notes for the observation.
3. Unredacted `39RVM3...` aircraft and `39RVM8...` observed-activity grids.
4. Platform position, altitude, speed, heading, and sensor pointing during the observation.
5. AN/DAS-4 FOV/zoom state and G-MESH context.
6. Weather/cloud imagery or mission weather notes around the observation.
7. Any follow-up classification or PID attempt after cloud loss.
8. Any official video release page or package that names `D61`, `271527ZAUG20`, or the `FORMATION OF UNK FLYING OBJECTS` language.

## Current Judgment

D61 is a strong source-reviewed regional pattern row. It should be used to show that the released collection contains repeated structured operational reports of unresolved aerial/sensor observations. It should not be used to claim anomalous performance, exotic technology, or independent physical formation dynamics without raw sensor data.

