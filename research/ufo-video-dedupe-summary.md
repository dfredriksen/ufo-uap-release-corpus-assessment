# UFO Video Dedupe Summary

Owner: Dan Fredriksen
Created: 2026-05-09
Source files: official public UFO/UAP release files, not redistributed in this repository
Status: Targeted duplicate hash pass complete

## Result

The same-size duplicate candidates were hashed with SHA-256. Every candidate group hashed as identical within its group.

Generated files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-targeted-duplicate-hashes.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-targeted-duplicate-summary.csv`

## Video Count

- MP4 files in folder: 41
- Exact duplicate MP4 groups: 11
- Exact duplicate MP4 copies removable from review set: 13
- Unique MP4 files after dedupe: 28

No source files were deleted or modified.

## Exact Duplicate MP4 Groups

| Canonical review name | Duplicate files in group |
|---|---|
| `DOD_111688970.mp4` | `DOD_111688970.mp4`, `DOD_111688970 (1).mp4` |
| `DOD_111689133.mp4` | `DOD_111689133.mp4`, `DOD_111689133 (1).mp4` |
| `DOD_111689022-1920x1080-9000k.mp4` | base, `(1)`, `(2)` |
| `DOD_111689044.mp4` | base, `(1)` |
| `DOD_111689759.mp4` | base, `(1)` |
| `DOD_111689123.mp4` | base, `(1)` |
| `DOD_111688816.mp4` | base, `(1)` |
| `DOD_111689051.mp4` | base, `(1)` |
| `DOD_111689115.mp4` | base, `(1)` |
| `DOD_111689167.mp4` | base, `(1)`, `(2)` |
| `DOD_111689090.mp4` | base, `(1)` |

## Non-Video Duplicate Groups

- `dow-uap-d23-mission-report-united-arab-emirates-october-2023.pdf` and `(1)` are exact duplicates.
- `59_214434_sp_16_[7.18.1963].pdf` and `59_214434_sp_16_7.18.1963.pdf` are exact duplicates.

## Frame Extraction Status

Frame extraction is now partially complete. Local `ffmpeg.exe` and `ffprobe.exe` still resolve to zero-byte WinGet link stubs, and Python OpenCV is not installed in the active Python environment. A temporary `imageio-ffmpeg` package target was used to create derived contact sheets without modifying the source UFO folder.

Generated files:

- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-unique-video-review-list.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-contact-sheet-index.csv`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-derived/video-contact-sheets/*.jpg`
- `https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-contact-sheet-notes.md`

Practical next options:

1. Use the temporary ffmpeg path again for high-resolution frame extraction from the top-priority clips.
2. Repair/install ffmpeg in PATH for repeatable media processing.
3. Use another local media tool if already installed outside PATH.

Until video overlays or release metadata are tied to report rows, the videos remain deduped media assets, not correlated report evidence.
