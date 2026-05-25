# UFO PR28 / D25 / D7 Reconciliation

Owner: Dan Fredriksen
Created: 2026-05-12
Scope: reconcile DVIDS `DOW-UAP-PR28` with local/War.gov `D25` and `D7`
Status: DVIDS video identity hard; DVIDS written-report label disputed

## Bottom Line

`DOD_111688954.mp4` is the hard local video identity for DVIDS `DOW-UAP-PR28`, Greece, January 2024.

The accompanying-report label appears wrong in the public DVIDS text. DVIDS says the accompanying mission report is `DoW-UAP-D7`, but the SWIR-only diamond / approximately 434-knot / vertical trailing probe language is in local/War.gov `DoW-UAP-D25`, not local/War.gov `D7`.

Use this working treatment:

- Video identity: `DOD_111688954.mp4` / `DOW-UAP-PR28`.
- Best written-report content match: `DoW-UAP-D25`.
- Official label discrepancy: DVIDS says `DoW-UAP-D7`.
- Local/War.gov `D7`: separate Arabian Gulf 2020 balloon-like/TFLIR case.

This is structurally similar to the PR29 discrepancy, where DVIDS says `D8` but the matching written-report content is in local/War.gov `D27`.

Follow-on source review: `research/ufo-d25-source-review.md`

That review confirms D25 as the report-content match while adding stricter constraints: the structured kinetic-velocity field is blank, the `434 KNOTS` value appears in the gentext, the kinetic altitude is estimated `FL200`, and the public PR28 video supports the SWIR sequence rather than independent physical kinematics.

## Official DVIDS PR28 Metadata

| Field | Value |
|---|---|
| DVIDS release | `DOW-UAP-PR28, Unresolved UAP Report, Greece, January 2024` |
| Video ID | `1006073` |
| Filename | `DOD_111688954` |
| Length | `00:01:06` |
| Location | Greece |
| DVIDS report label | `DoW-UAP-D7` |
| DVIDS reported description | Diamond-shaped UAP, about 434 knots, only detectable via SWIR |
| DVIDS visual sequence | Split EO/SWIR display, then full-screen SWIR, visible-spectrum loss, SWIR black-hot non-reacquisition |

## Local/War.gov D25 Match

`D25` contains the report text DVIDS summarizes:

| Field | Value |
|---|---|
| PDF title | `DOW-UAP-D25, Mission Report, Greece, January 2024` |
| Event time | `250509:00ZJAN24` |
| Event serial | `250509ZJAN2024-CENTCOM 001` |
| Originator | 33 SOS |
| Takeoff / landing | LGLR / LGLR |
| Targeting/sensor field | AN/DAS-4; UAP signatures `SWIR WHT` |
| Reported shape | round diamond shape with straight, non-maneuverable tail/probe |
| Reported speed | approximately 434 knots |
| Visibility lane | only appeared on SWIR camera |
| Duration | approximately two minutes, ending at 0511Z |
| Caveats | no effects on persons/equipment; no recovered material; observer assessed benign; kinematic values are report estimates |

## Local/War.gov D7 Mismatch

Local/War.gov `D7` does not contain the PR28 SWIR diamond content. It is a separate Arabian Gulf 2020 report:

| Field | Value |
|---|---|
| PDF title | `DOW-UAP-D7, Mission Report, Arabian Gulf, 2020` |
| Reported shape | looks like a balloon, similar to previously reported UAP from 48FW |
| Reported motion/context | traveling with the winds at 31,000 ft MSL |
| Sensor/track language | weapons-quality track; visually identified in TFLIR |
| Mismatch | no Greece / January 2024 / 434-knot / diamond / SWIR-only lane |

## Judgment

PR28 should be treated as a hard video identity and a strong D25 report-content match, with the DVIDS `D7` label preserved as an official-source discrepancy. Do not analyze PR28 as local `D7` unless an official correction explains how D7 is intended to map to the Greece/SWIR event.

## Phase Review

Dedicated note: `research/ufo-video-pr28-d25-phase-review-notes.md`

The bounded PR28/D25 phase review of `DOD_111688954.mp4` confirms the DVIDS visual sequence:

1. Split-screen EO/SWIR context in the opening seconds.
2. Right-frame SWIR contrast by the `4s-10s` interval.
3. Persistent full-screen SWIR compact contrast through `10.0s-55.5s`.
4. Loss at the visible-spectrum switch around `56s`.
5. No robust high-or-medium reacquisition in the `57.0s-65.5s` SWIR black-hot interval.

This supports the public-release visual sequence and the `D25` content lane, but it does not independently validate speed, range, object size, altitude, or the detailed shape/tail/probe description.

## Next Step

Do not run physical kinematics on PR28 from the public MP4 alone. Keep PR28 as a hard video identity plus strong `D25` report-content match, and continue corpus-level source reconciliation on the remaining PR/D-label mismatches.

