# Range-Fouler Cluster Packet

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: `D38`, `D44`, `D56`, `D57`, and `D58` range-fouler / sensor-geometry lane
Status: cluster packet complete; keep as high-value but not unified

## Bottom Line

The range-fouler set is the strongest "sensor geometry / range safety" cluster in the current corpus, but it should not be treated as one event or one object class. The cluster is high-value because several reports preserve sensor mode, contact count, altitude/range geometry, relative movement, and negative identification fields. The evidence is still limited by one-page forms, redactions, OCR noise, and missing raw video/telemetry.

Current treatment:

- `D38` is the strongest hard video/report anchor through DVIDS `PR36` and local `DOD_111689030.mp4`.
- `D44` and `D57` form a close Gulf of Aden IR/black-hot geometry pair: round cold objects, bright-white in black-hot IR, slant/ground range values, downward sensor angle, and abrupt direction-change language.
- `D56` is a separate North Arabian Sea three-contact lane with negative ES/radar/IFF and cloud-loss/reacquisition context.
- `D58` is the most operationally complex report: KINGPIN-directed ID, radar lock, target-pod video, two IR-significant contacts, red blinking strobes, and noise-jamming indications. Those details make it important, but they also keep conventional military-platform explanations open.

## Cluster Rows

| Report | Local file | Event lane | Strongest preserved details | Main caveat |
|---|---|---|---|---|
| `D38` | `dow-uap-d38-range-fouler-debrief-middle-east-may-2020.pdf` | Hard report/video anchor | DVIDS `PR36` pairs D38 with `DOD_111689030.mp4`; local validation supports a compact point-return track in the useful interval. | Public video still does not independently validate speed/range/physical trajectory. |
| `D44` | `dow-uap-d44-range-fouler-arabian-sea-october-2020.pdf` | Gulf of Aden IR geometry | `10/15/20 14:18:39Z`; one contact; round cold object in IR; `19,073 HAT`; about one-minute contact; sensor `-50 deg`; slant range `4.06 NM`; ground range `4.78 KM`; black-hot bright-white object. | Filename says Arabian Sea, narrative says Gulf of Aden; direction/speed field is OCR-noisy versus narrative. |
| `D56` | `dow-uap-d56-range-fouler-debrief-arabian-sea-august-2020.pdf` | North Arabian Sea three-contact lane | `08/24/20 00:04:30Z`; three possible unidentified small air contacts; negative ES, radar track, and IFF track; one contact lost behind cloud, then reacquired with two additional contacts east of it. | PDF metadata title says `DoW-UAP-D33`; distance, speed, precise course, and contact geometry are unknown. |
| `D57` | `dow-uap-d57-mission-report-gulf-of-aden-september-2020.pdf` | Gulf of Aden IR geometry | `09/04/20 21:09Z-21:17Z`; one contact; round cold object in IR; `23,819 HAT`; `168/277` direction/speed field; sensor `-39 deg`; slant range approximately `6.1? NM`; ground range `8.81 KM`; black-hot bright-white object. | PDF metadata title says `DoW-UAP-D34`; slant range character is OCR-uncertain; no hard video pairing. |
| `D58` | `dow-uap-d58-range-fouler-debrief-na-october-2020.pdf` | Radar-lock / target-pod / jamming lane | `10/27/20 01:12:21Z`; two contacts; KINGPIN-directed ID; radar lock; target-pod video; two IR-significant contacts; 2x red blinking strobes; noise jamming indicated by two chevrons; closest range `16.9 NM`. | PDF metadata title says `DoW-UAP-D35`; red strobes and jamming are compatible with conventional military aircraft, drones, or EW platforms. |

## Cross-Case Pattern

The cluster has three separable sub-lanes:

1. **IR geometry lane:** `D44` and `D57` both describe round cold objects over the Gulf of Aden, visible as bright-white in black-hot IR, with sensor depression angle, slant range, ground range, and abrupt direction changes.
2. **Multi-contact ambiguity lane:** `D56` describes three small air contacts with negative ES/radar/IFF and cloud interruption, but without strong geometry or speed.
3. **Military-platform ambiguity lane:** `D58` has the richest operational detail but also the strongest conventional-confound indicators: red blinking strobes, noise jamming, radar lock, target-pod video, and a KINGPIN-directed identification attempt.

These lanes are related by reporting format and theater, not by demonstrated object identity.

## Metadata Issues

The release files contain a recurring metadata problem:

- `D56` PDF metadata title/subject: `DoW-UAP-D33`
- `D57` PDF metadata title/subject: `DoW-UAP-D34`
- `D58` PDF metadata title/subject: `DoW-UAP-D35`

These metadata labels conflict with the local filenames and with other local/War.gov D-report identities already analyzed. Treat the filename and body content as the working analytic identity unless an official release index corrects the mapping. Do not merge `D56-D58` with the Greece `D33/D35` lanes based only on PDF metadata.

## Confidence Tiers

### Stronger

- D38 official video/report pairing through DVIDS `PR36`.
- D44/D57 body-level similarity as Gulf of Aden IR/black-hot range-fouler records.
- D58 as an operationally important EW/target-pod/radar-lock report.

### Moderate

- D44/D57 direction/speed and range-geometry values, because the OCR is readable but one-page forms preserve limited context.
- D56 as a three-contact report, because the narrative is clear but geometry and kinematics are not.

### Weak

- Any claim that D44, D57, or D58 match PR44 or `DOD_111689115.mp4`.
- Any claim that the cluster is one phenomenon.
- Any physical-performance derivation without raw video, platform telemetry, sensor FOV, and range/angle time series.

## Analytic Treatment

Use the range-fouler cluster as a structured evidence lane, not as proof of exotic technology. It is valuable because the records repeatedly capture formal range-fouler reporting with sensor context and operational language. It is not conclusive because the released records do not provide enough data to rule out conventional aircraft, drones, electronic warfare platforms, sensor artifacts, or range activity.

## Follow-Up

1. Search for official PR/video releases that explicitly name `D44`, `D56`, `D57`, or `D58`; do not infer from PR numbers.
2. If raw tapes are ever located, prioritize D58 first, then D57/D44, because D58's radar-lock/target-pod/noise-jamming combination is the highest-value test case.
3. Build a geometry worksheet for D44 and D57 only if the source images become clearer or raw forms are available; current OCR is enough for triage but not enough for formal reconstruction.
4. Keep `DOD_111689115.mp4` in the standalone `PR44` lane unless a source explicitly links it to local `D44`, `D57`, or `D58`.

## Sources

- War.gov D44 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d44-range-fouler-arabian-sea-october-2020.pdf`
- War.gov D56 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d56-range-fouler-debrief-arabian-sea-august-2020.pdf`
- War.gov D57 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d57-mission-report-gulf-of-aden-september-2020.pdf`
- War.gov D58 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d58-range-fouler-debrief-na-october-2020.pdf`
- DVIDS PR36 / D38 anchor: `https://www.dvidshub.net/video/1006083/dow-uap-pr36-unresolved-uap-report-middle-east-may-2020`
- DVIDS PR44 standalone caution: `https://www.dvidshub.net/video/1006104/dow-uap-pr44-unresolved-uap-report-middle-east-2020`
