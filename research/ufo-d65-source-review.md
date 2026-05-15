# D65 Source Review

Owner: Dan Fredriksen
Created: 2026-05-14
Source: `source-files-not-included/dow-uap-d65-mission-report-persian-gulf-july-2020.pdf`
Status: source review complete from local OCR extraction

## Bottom Line

`D65` is the densest single mission in the Persian Gulf / Strait of Hormuz 2020 pattern lane. The mission report preserves three separate FMV observations of unidentified aerial phenomena on `2020-07-16` during NAVCENT tasking in the Arabian Gulf / Strait of Hormuz / Gulf of Oman operating lane.

The report is useful for reporting density and mission context, not for physical-performance claims. It does not preserve public object shape, object size, object altitude, object speed, range, sensor field of view, platform state, raw FMV, or a specific public PR/DVIDS video pairing.

## Preserved Facts

| Field | Preserved value | Treatment |
|---|---|---|
| Report identity | `dow-uap-d65-mission-report-persian-gulf-july-2020.pdf` | Working source identity. |
| MISREP | `4472514` | Source anchor from OCR page 1. |
| Release/provenance footer | `USCENTCOM MDR 26-0028 Approved for Release to AARO - FOUO/PA applies 03/16/26` | Provenance anchor; footer OCR varies by page. |
| Originator / command context | `482ATKS`; `609 AOC/CAOC`; Air Force / USCENTCOM context | Operational context. |
| Mission date | `2020-07-16` to `2020-07-17` mission window | Mission context. |
| Takeoff | `160443:00ZJUL20` from `OKAS` | Mission start anchor. |
| LRE handover | Approx `0504Z` | Mission context; OCR is noisy. |
| ISR on-station window | `160552:00ZJUL20` to `170012:00ZJUL20` | Primary mission-window anchor. |
| Off-station / RTB | Cleared RTB at `0012Z`; off-station `170124:00ZJUL20` | Mission context. |
| Landing | `170200:00ZJUL20` at `OKAS`; shutdown `170210:00ZJUL20` | Mission end anchor. |
| Mission duration | Narrative says `20.3` mission hours; landing block says `21 hours 17 minutes` total mission time | Preserve both values as source-internal timing noise. |
| Supported unit | `NAVCENT` | Operational context. |
| Mission lane | Arabian Gulf / Strait of Hormuz / Gulf of Oman tasking context | Regional pattern context. |
| Mission type | `AREC` | Context only. |
| Target pod / primary sensor | OCR as `ANDAS4`, interpreted as AN/DAS-4 with OCR caveat | Sensor context. |
| Additional sensors | `AH_GMESH` / G-MESH available | Sensor context. |
| Exploitation | FMV exploited by `DGS-1` | Strong source-quality context. |
| ISR tasking | Scans for identified vessels, UAS activity, pattern of life, and activity outside ports | Important control context. |
| Guard call | `160615:00ZJUL20`; aircraft near partial `39RUN...`; heading `131M`; altitude `FL180`; standard response; no mission impact | Mission-environment context, not linked to the UAP observations. |
| Observation 1 | `161830:00ZJUL20`; aircraft partial `39RXK3...`; heading `152M`; `FL200`; `98 KIAS`; observed activity near partial `39RVM...`; description `UAP`; method `FMV` | First UAP observation. |
| Observation 2 | `161920:00ZJUL20`; aircraft location OCR likely partial `39RUN...`; heading `34M`; `FL190`; `90 KIAS`; observed activity near partial `39RUN...`; description `UAP`; method `FMV` | Second UAP observation. |
| Observation 3 | `162345:00ZJUL20`; aircraft partial `39RUN...`; heading `331M`; `FL191`; `115 KIAS`; observed activity near `39RUN6234236874`; description `UAP`; method `FMV` | Third UAP observation and strongest geospatial anchor. |
| Decoded D65 row 3 grid | `39RUN6234236874` -> approx `29.253233N, 49.583281E` | Confirms at least one D65 observation sits in the northern Persian Gulf grid lane. |
| Observation weather | Each UAP observation states weather was not a factor | Use as a source-stated weather field, not as proof of sensor clarity. |

## Claim Tiers

### Directly Preserved

- The mission report records three FMV observations of unidentified aerial phenomena on `2020-07-16`.
- The observations occurred during a NAVCENT mission supporting Arabian Gulf / Strait of Hormuz / Gulf of Oman tasking.
- The mission used AN/DAS-4-style sensor context with G-MESH availability, and the FMV was exploited by `DGS-1`.
- Observation times are preserved at `1830Z`, `1920Z`, and `2345Z`.
- The third observation preserves a full observed-activity grid, `39RUN6234236874`, which decodes to the northern Persian Gulf lane.
- Each observation block states that weather was not a factor.

### Bounded Interpretations

- D65 supports a regional reporting-density claim: one released mission report preserved three separate FMV UAP observations in the same NAVCENT Gulf/Strait operating lane.
- D65 is stronger than most sparse `D60-D65` rows for density, but weaker than D61 for behavior because it does not preserve formation movement, duration, or a loss-of-PID narrative.
- The three observations may represent separate unresolved observations during one mission. The public record does not establish whether they were the same object, different objects, or repeated observations of conventional traffic.

### Missing Or Redacted

- Object shape, size, color, altitude, speed, range, bearing, and trajectory.
- Exact unredacted coordinates for observations 1 and 2.
- Raw FMV, still frames, sensor pointing, field of view, zoom state, platform state, and telemetry.
- Object-level exploitation findings from `DGS-1`.
- Public PR/DVIDS video pairing.
- Identification follow-up or final disposition.

## Analytic Controls

Evaluate D65 against these non-extraordinary lanes before any stronger interpretation:

1. Distant aircraft, small drones, or UAS activity inside a busy maritime/coastal ISR tasking area.
2. Maritime or shoreline activity producing airborne-looking contrast in FMV.
3. Sensor, compression, or track-cue artifacts in public or source FMV.
4. Multiple benign objects or repeated observations during a long ISR mission.
5. Redaction and OCR noise masking details that would normally support identification.

## Relationship To The 2020 Gulf/Strait Cluster

- `D65` is the densest mission: three FMV UAP observations on `2020-07-16`.
- `D61` is the strongest behavior row: formation, NE-NW coastal movement, two-minute tracking, and PID loss in cloud cover.
- `D60`, `D62`, and `D64` are sparse single or paired FMV UAP rows.
- `D63` remains narrative-only until its observation section is recovered more clearly.
- `D4` and `D5` remain adjacent short quantitative rows, but their full readable grids decode outside the Gulf/Strait lane.

## Source-Request Checklist

Priority follow-up material:

1. FMV clips and still frames for `161830Z`, `161920Z`, and `162345Z` on `2020-07-16`.
2. DGS-1 exploitation notes for all three observations.
3. Unredacted aircraft-location and observed-activity grids for observations 1 and 2.
4. Platform position, altitude, speed, heading, and sensor pointing for each observation.
5. AN/DAS-4 FOV/zoom state, metadata overlay, and G-MESH context.
6. Any track files, manual operator notes, or identification follow-up.
7. Weather/visibility details around each observation, despite the source-stated weather-not-a-factor fields.
8. Any official video release page or package that names `D65`, `4472514`, `161830Z`, `161920Z`, `162345Z`, or `39RUN6234236874`.

## Current Judgment

D65 is a strong source-reviewed reporting-density row. It should be used to show that the released collection contains repeated operational UAP observations within a single NAVCENT Gulf/Strait mission. It should not be used to claim anomalous speed, acceleration, advanced technology, or a single coherent object track without raw sensor data and telemetry.
