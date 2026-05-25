# D8 Source Review

Owner: Dan Fredriksen
Created: 2026-05-12
Source file: `I:\My Drive\UFO\dow-uap-d8-mission-report-djibouti-2025.pdf`
Official URL: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d8-mission-report-djibouti-2025.pdf`
Status: source review complete; heavily redacted document-only case

## Bottom Line

`D8` is a short, high-signal but heavily redacted mission-report case. The only useful public content is on the final UAP page: at `1653Z`, the observer reported `2X ROUND WHITE HOT UAPS` moving south at approximately `240NM/HOUR` near `35SQT3423692957`.

The report does not publicly preserve the full incident date, event serial, platform, unit, sensor name, first/last coordinates, altitude, range, FOV, or raw imagery. The title says Djibouti, 2025, but the visible MGRS grid `35SQT3423692957` decodes to approximately `34.2514N, 29.5437E`, which is in the Eastern Mediterranean, not Djibouti. Treat D8 as another source-label/location mismatch unless an official correction reconciles the title and coordinate.

## Source Metadata

| Field | Value |
|---|---|
| PDF filename | `dow-uap-d8-mission-report-djibouti-2025.pdf` |
| PDF title/subject metadata | `DOW-UAP-D8, Mission Report, Djibouti, 2025` |
| Pages | `7` |
| Creation date | `2026-04-29 05:12:29 PDT` |
| Modification date | `2026-05-07 13:33:35 PDT` |
| File size | `29154` bytes |
| Encryption | Copy disabled; print allowed |
| Embedded files / images | No embedded files; no image objects reported by `pdfdetach` / `pdfimages` |

Most pages contain only redaction markers in public text extraction. The usable UAP content appears on page 7.

Generated page render:

- `research/ufo-derived/source-page-renders/D8/d8-page-7.png`

## Preserved UAP Text

The page-7 UAP description says the observer reported two round white-hot UAPs moving south at approximately `240NM/HOUR` in the vicinity of `35SQT3423692957`. The gentext repeats the same substance with less shape detail: two UAPs moving south at approximately `240NM/HOUR` near the same grid.

Publicly preserved facts:

- Time of day: `1653Z`
- Count: `2X`
- Description: round, white-hot UAPs
- Movement: dynamic south
- Estimated speed: approximately `240NM/HOUR`, or about `276 mph`
- Location field: `IVO 35SQT3423692957`
- Classification caveat visible in the UAP text: `SECRET//REL TO USA, FIN, SWE, FVEY, NATO`

## Location Finding

The filename and PDF metadata identify the report as Djibouti, 2025. The visible MGRS grid does not fit Djibouti.

Local conversion of `35SQT3423692957` using the Python `mgrs` library returned:

| Field | Value |
|---|---|
| Latitude | `34.25138347257769` |
| Longitude | `29.543663371905804` |
| Approximate region | Eastern Mediterranean |

This is an analytic conversion from the released grid string, not a separate official location statement. The conservative treatment is to keep the official filename/title as the release identity, but use the grid-derived Eastern Mediterranean lane for geospatial analysis.

## Analytic Treatment

- Confidence is high that D8 is a separate case from the PR29/D27 UAE pole/bar report. The D8 source text describes two round white-hot UAPs, while PR29/D27 describes one pole/bar or possible-reflection object.
- Confidence is high for the visible time-of-day, object count, white-hot description, southward movement, and estimated speed as report text.
- Confidence is medium for the grid-derived location because the grid is visible and decodable, but the filename/title says Djibouti.
- Confidence is low for exact event date. The public release preserves the year `2025` in the title, but the full date is redacted or absent from the public text.
- Confidence is low for physical kinematics. The `240NM/HOUR` value is reporter-estimated and no raw imagery, FOV, range, platform motion, or telemetry is public.
- No hard video pairing has been found for D8. DVIDS `PR29` names `D8`, but its body summary matches local/War.gov `D27`, not this D8 text.

## Follow-Up

1. Keep D8 as a high-priority document-only quantitative case, but preserve the source-label/location mismatch.
2. Do not use D8 as the written report for `DOD_111688964.mp4` / `PR29`; use D27 as the content match and keep the DVIDS D8 label as a discrepancy.
3. Search only for official metadata that names `35SQT3423692957`, `240NM/HOUR`, or a two-white-hot-UAP event in the Eastern Mediterranean / Djibouti 2025 lane.
4. If source video appears, require FOV/range/platform data before treating `240NM/HOUR` as a validated physical speed.

## Sources

- War.gov D8 PDF: `https://www.war.gov/medialink/ufo/release_1/dow-uap-d8-mission-report-djibouti-2025.pdf`
- War.gov PURSUE release page: `https://www.war.gov/UFO/`

