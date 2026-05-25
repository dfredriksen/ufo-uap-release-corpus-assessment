# Persian Gulf / Strait Of Hormuz 2020 Timeline

Owner: Dan Fredriksen
Created: 2026-05-14
Scope: `D4`, `D5`, and `D60-D65`
Status: timeline pass complete; core Gulf/Strait cluster is `D60-D65`

## Bottom Line

The core Persian Gulf / Strait of Hormuz 2020 pattern is `D60-D65`, not the full `D4`, `D5`, `D60-D65` set.

`D60-D65` preserve repeated FMV or sensor-observed UAP/unknown-flying-object rows during NAVCENT tasking in the Arabian Gulf / Strait of Hormuz / Gulf of Oman operating lane. The strongest row is `D61`, because it describes a formation of unknown flying objects moving NE-NW along the coast and being tracked for about two minutes before PID was lost in cloud cover. The densest single mission is `D65`, which preserves three FMV UAP observations on `2020-07-16` and is now source-reviewed.

`D4` and `D5` remain useful short quantitative UAP lines, but they should no longer be treated as core Persian Gulf / Strait rows without resolving their source-label/grid mismatch. Their filenames say Arabian Gulf 2020, but the readable full MGRS grids decode to Eastern Mediterranean / Black Sea-area coordinates, not the Gulf.

## Key Correction

| Source | Readable grid | Local decode | Treatment |
|---|---:|---|---|
| `D4` | `34SDG9041417044` | approx `37.199812N, 20.891980E` | Quantitative short UAP line; exclude from core Gulf/Strait cluster until label/grid mismatch is resolved. |
| `D5` row 1 | `34SCE7566990098` | approx `36.047497N, 19.619714E` | Quantitative short UAP line; exclude from core Gulf/Strait cluster until label/grid mismatch is resolved. |
| `D5` row 2 | `35TQK1580995057` | approx `45.076058N, 29.741793E` | Quantitative short UAP line; exclude from core Gulf/Strait cluster until label/grid mismatch is resolved. |
| `D65` row 3 | `39RUN6234236874` | approx `29.253233N, 49.583281E` | Confirms at least one `D65` observation sits in the northern Persian Gulf grid lane. |

## Core Timeline

| Date / DTG | Source | Location lane | Sensor / method | Observation | Caveat |
|---|---|---|---|---|---|
| `2020-07-16 18:30Z` | `D65` | Arabian Gulf / Strait / Gulf of Oman mission; observed activity near `39RVM...` | FMV; aircraft `FL200`, `98 KIAS`, heading `152M` | One unidentified aerial phenomenon observed. | OCR-derived but observation block is readable; no range, object size, speed, or video pairing. |
| `2020-07-16 19:20Z` | `D65` | Arabian Gulf / Strait / Gulf of Oman mission; observed activity near `39RUN...` | FMV; aircraft `FL190`, `90 KIAS`, heading `34M` | Second unidentified aerial phenomenon observed. | OCR-derived; no range, object size, speed, or video pairing. |
| `2020-07-16 23:45Z` | `D65` | `39RUN6234236874`, approx `29.253233N, 49.583281E` | FMV; aircraft `FL191`, `115 KIAS`, heading `331M` | Third unidentified aerial phenomenon observed. | OCR-derived but coordinate is full enough to decode; no range, object size, speed, or video pairing. |
| `2020-08-08 07:26Z` | `D60` | Arabian Gulf / Strait / Gulf of Oman mission; observed activity near partial `39RVL/39RWL` OCR lane | FMV; primary sensor `AN/DAS-4` | `1X UAP`, described as transiting; no mission impact. | OCR-derived; observation is sparse; no altitude, speed, range, or object description. |
| `2020-08-27 15:27Z-15:29Z` | `D61` | Persian Gulf / coastal context; observed activity near `39RVM8...` | Sensor observation; primary sensor `AN/DAS-4`; FMV exploited by DGS-1 | Formation of unknown flying objects traveled NE-NW along the coast and was tracked for about two minutes. | PID lost in cloud cover; no object count, altitude, speed, range, or raw video pairing. |
| `2020-09-16 17:32Z` | `D62` | Strait of Hormuz / Arabian Gulf mission; observed activity near `39RVM5...` | FMV; primary sensor `AN/DAS-4`; aircraft `FL180`, `90 KIAS` | One UAP observed. | Sparse observation row; same mission has guard calls and lost-link/EMI entries, but no public link between those and the UAP. |
| `2020-10-02 18:29Z` | `D63` | Strait of Hormuz / Arabian Gulf mission | Mission narrative; primary sensor `AN/DAS-4` | Narrative says `1X UAP` observed. | Detailed observation row was not recovered clearly; heavy haze precluded IMINT analysis elsewhere in the report. |
| `2020-11-02 21:43Z` | `D64` | Arabian Gulf / Iran context; observed activity near `39RWK...` | FMV; primary sensor `AN/DAS-4`; aircraft `FL220`, `105 KIAS`, heading `110T` | One unidentified aerial phenomenon observed; altitude unknown; bearing `080T`. | Haze precluded IMINT collection elsewhere in the ISR section; no object speed/range/video pairing. |
| `2020-11-02 21:48Z` | `D64` | Arabian Gulf / Iran context; observed activity near `39RWK...` | FMV; aircraft `FL220`, `107 KIAS`, heading `110T` | Additional UAP traveling northwest. | Sparse row; no range, altitude, object count beyond "additional", or video pairing. |

## Adjacent But Not Core Rows

| Source | Observation | Why it is not core Gulf/Strait evidence right now |
|---|---|---|
| `D4` | At `1258Z`, possible UAP near `34SDG9041417044`; altitude not estimated; velocity estimated `321 KNOTS`; increased speed and changed direction east. | Full grid decodes outside the Gulf lane despite Arabian Gulf filename. |
| `D5` row 1 | At `1354Z`, one UAP near `34SCE7566990098`; `40 KNOTS`, `FL160` to `FL170`; speed remained constant. | Full grid decodes outside the Gulf lane despite Arabian Gulf filename. |
| `D5` row 2 | At `2243Z`, two possible UAPs near `35TQK1580995057`; estimated `278 KNOTS`; increased speed and changed direction south. | Full grid decodes outside the Gulf lane despite Arabian Gulf filename. |

## Pattern Assessment

The `D60-D65` pattern is a reporting-density lane, not a performance lane. It shows repeated official mission-report observations during NAVCENT ISR pattern-of-life tasking in the Arabian Gulf / Strait / Gulf of Oman area. It does not provide enough public data to derive object size, speed, altitude, range, or physical maneuvering.

The cluster has three useful sub-lanes:

1. Repeated sparse FMV UAP observations: `D60`, `D62`, `D64`, `D65`.
2. Formation behavior: `D61`, the strongest row in this lane.
3. Mission-context/environment caveats: Iranian guard calls, haze, cloud cover, lost-link/EMI entries, and redacted grids.

## Current Judgment

Keep `D60-D65` in Tier 4 as a regional pattern cluster. Promote `D61` as the best individual follow-up inside the cluster. Demote `D4/D5` out of the Gulf/Strait cluster until the Arabian Gulf filename labels are reconciled against their readable MGRS grids.

## Next Action

The focused `D61` and `D65` source reviews are complete. The next useful step is to use this lane in the final-report coverage audit as a regional reporting-density pattern, not as a physical-performance case.

