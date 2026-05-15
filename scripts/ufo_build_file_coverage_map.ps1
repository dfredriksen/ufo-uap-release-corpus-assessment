param(
    [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

$research = Join-Path $RepoRoot "research"
$manifestPath = Join-Path $research "ufo-file-manifest.csv"
$outPath = Join-Path $research "ufo-file-coverage-map.csv"
$summaryPath = Join-Path $research "ufo-file-coverage-summary.csv"

function Normalize-Name([string]$name) {
    if ([string]::IsNullOrWhiteSpace($name)) { return "" }
    $base = [System.IO.Path]::GetFileNameWithoutExtension($name).ToLowerInvariant()
    $base = $base -replace "\s+\([0-9]+\)$", ""
    $base = $base -replace "_1_$", ""
    $base = $base -replace "[^a-z0-9]+", ""
    return $base
}

function File-Group([string]$name, [string]$extension) {
    $n = $name.ToLowerInvariant()
    if ($extension -eq ".mp4" -and $n -like "dod_*.mp4") { return "public_dod_video" }
    if ($n -like "dow-uap-d*.pdf" -or $n -like "dow-uap-pr*.pdf") { return "modern_dow_dod_pdf" }
    if ($n -like "dos-uap-*.pdf") { return "state_department_cable" }
    if ($n -like "nasa-uap-*" -or $n -eq "255_t_763_r1b_transcripts.pdf") { return "nasa_transcript_or_image" }
    if ($n -like "fbi-photo-*") { return "fbi_photo_set" }
    if ($n -eq "western_us_event_slides_5.08.2026.pdf" -or $n -eq "2024-04-30-composite-sketch.pdf") { return "recent_witness_or_sketch" }
    if ($n -like "65_hs1-*" -or $n -like "38_143685*" -or $n -like "18_*" -or $n -like "59_*" -or $n -like "331_*" -or $n -like "341_*" -or $n -like "342_*" -or $n -like "255_*" -or $n -like "serial*" -or $n -eq "usper-statement-redacted.pdf" -or $n -like "059uap*.pdf") { return "historical_archive_pdf" }
    return "other"
}

function Add-MapSet($set, [string]$name) {
    $key = Normalize-Name $name
    if ($key) { $set[$key] = $true }
}

$manifest = Import-Csv $manifestPath

$derivedText = @{}
Get-ChildItem (Join-Path $research "ufo-derived/text") -File -ErrorAction SilentlyContinue | ForEach-Object {
    Add-MapSet $derivedText $_.Name
}

$modernTriage = @{}
$modernTriagePath = Join-Path $research "ufo-modern-report-triage.csv"
if (Test-Path $modernTriagePath) {
    Import-Csv $modernTriagePath | ForEach-Object { Add-MapSet $modernTriage $_.file }
}

$contactSheets = @{}
$contactIndexPath = Join-Path $research "ufo-video-contact-sheet-index.csv"
if (Test-Path $contactIndexPath) {
    Import-Csv $contactIndexPath | Where-Object { $_.sheet_exists -eq "True" } | ForEach-Object { Add-MapSet $contactSheets $_.name }
}

$uniqueVideos = @{}
$uniqueVideoPath = Join-Path $research "ufo-unique-video-review-list.csv"
if (Test-Path $uniqueVideoPath) {
    Import-Csv $uniqueVideoPath | ForEach-Object {
        Add-MapSet $uniqueVideos $_.canonical_name
        Add-MapSet $uniqueVideos $_.selected_name
    }
}

$duplicateFiles = @{}
$duplicatePath = Join-Path $research "ufo-targeted-duplicate-summary.csv"
if (Test-Path $duplicatePath) {
    Import-Csv $duplicatePath | ForEach-Object {
        $files = $_.files -split "\s+\|\s+"
        foreach ($f in $files) {
            $key = Normalize-Name $f
            if ($key) { $duplicateFiles[$key] = $_.files }
        }
    }
}

$deepReviewByName = @{}
$deepPairs = @(
    @("dow-uap-d8-mission-report-djibouti-2025.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d8-source-review.md"),
    @("dow-uap-d25-mission-report-greece-january-2024.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d25-source-review.md"),
    @("dow-uap-d27-mission-report-united-arab-emirates-october-2023.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d27-source-review.md"),
    @("dow-uap-d28-mission-report-east-china-sea-2024.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d28-evidence-packet.md"),
    @("dow-uap-d33-mission-report-greece-october-2023.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d33-source-review.md"),
    @("dow-uap-d35-mission-report-greece-october-2023.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d35-source-review.md"),
    @("dow-uap-d38-range-fouler-debrief-middle-east-may-2020.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-notes.md"),
    @("dow-uap-d44-range-fouler-arabian-sea-october-2020.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-cluster-packet.md"),
    @("dow-uap-d54-mission-report-mediterranean-sea-na.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d54-source-review.md"),
    @("dow-uap-d56-range-fouler-debrief-arabian-sea-august-2020.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-cluster-packet.md"),
    @("dow-uap-d57-mission-report-gulf-of-aden-september-2020.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-range-fouler-cluster-packet.md"),
    @("dow-uap-d58-range-fouler-debrief-na-october-2020.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d58-evidence-packet.md"),
    @("dow-uap-d61-mission-report-persian-gulf-august-2020.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d61-source-review.md"),
    @("dow-uap-d65-mission-report-persian-gulf-july-2020.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d65-source-review.md"),
    @("dow-uap-d74-mission-report-syria-november-2023.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d74-source-review.md"),
    @("dow-uap-d75-mission-report-gulf-of-aden-july-2024.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-d75-source-review.md"),
    @("DOD_111688825.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr27-d23-manual-validation-notes.md"),
    @("DOD_111688954.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr28-d25-phase-review-notes.md"),
    @("DOD_111688964.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr29-d27-visual-alignment.md"),
    @("DOD_111689011.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr34-d33-manual-track-notes.md"),
    @("DOD_111689022-1920x1080-9000k.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-pr34-pr35-phase-review-notes.md"),
    @("DOD_111689030.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-d38-anchor-notes.md"),
    @("DOD_111689090.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-video-point-count-notes-dod111689090.md"),
    @("DOD_111689115.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr44-standalone-quant-notes.md"),
    @("DOD_111689123.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr45-standalone-visual-notes.md"),
    @("DOD_111689142.mp4", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-pr47-formation-visual-notes.md"),
    @("western_us_event_slides_5.08.2026.pdf", "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-priority-incidents.md")
)

foreach ($pair in $deepPairs) {
    $key = Normalize-Name $pair[0]
    if ($key) { $deepReviewByName[$key] = $pair[1] }
}

$groupReviewArtifacts = @{}
$nasaDosArtifact = "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-nasa-dos-gap-triage.md"
if (Test-Path (Join-Path $RepoRoot $nasaDosArtifact)) {
    $groupReviewArtifacts["nasa_transcript_or_image"] = $nasaDosArtifact
    $groupReviewArtifacts["state_department_cable"] = $nasaDosArtifact
}

$fbiPhotoArtifact = "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-fbi-photo-gap-triage.md"
if (Test-Path (Join-Path $RepoRoot $fbiPhotoArtifact)) {
    $groupReviewArtifacts["fbi_photo_set"] = $fbiPhotoArtifact
}

$historicalArchiveArtifact = "https://github.com/dfredriksen/ufo-uap-release-corpus-assessment/blob/main/research/ufo-historical-archive-gap-triage.md"
if (Test-Path (Join-Path $RepoRoot $historicalArchiveArtifact)) {
    $groupReviewArtifacts["historical_archive_pdf"] = $historicalArchiveArtifact
}

$rows = foreach ($file in $manifest) {
    $name = $file.name
    $ext = $file.extension
    $key = Normalize-Name $name
    $group = File-Group $name $ext
    $hasText = $derivedText.ContainsKey($key)
    $inTriage = $modernTriage.ContainsKey($key)
    $hasSheet = $contactSheets.ContainsKey($key)
    $isUniqueVideo = $uniqueVideos.ContainsKey($key)
    $dupGroup = if ($duplicateFiles.ContainsKey($key)) { $duplicateFiles[$key] } else { "" }
    $deepArtifact = if ($deepReviewByName.ContainsKey($key)) { $deepReviewByName[$key] } else { "" }
    $groupArtifact = if ($groupReviewArtifacts.ContainsKey($group)) { $groupReviewArtifacts[$group] } else { "" }

    $coverage = "inventory_only"
    $gap = "Needs targeted review before corpus-wide claim"
    $nextAction = "Triage or extract/review source content"
    $evidence = @()

    if ($dupGroup) { $evidence += "exact duplicate group hashed" }
    if ($hasText) { $evidence += "derived text exists" }
    if ($inTriage) { $evidence += "modern triage row" }
    if ($hasSheet) { $evidence += "video contact sheet" }
    if ($isUniqueVideo) { $evidence += "unique video review list" }
    if ($deepArtifact) { $evidence += $deepArtifact }
    if ($groupArtifact) { $evidence += $groupArtifact }

    if ($deepArtifact) {
        $coverage = "deep_review"
        $gap = "No major gap for current final-report use"
        $nextAction = "Use existing review unless new source material appears"
    } elseif ($groupArtifact) {
        $coverage = "targeted_review"
        $gap = "Targeted source triage complete; local extraction or high-resolution review limited by disk"
        $nextAction = "Use triage finding unless deeper source image/PDF review is required"
    } elseif ($group -eq "public_dod_video" -and $hasSheet) {
        $coverage = "visual_triage"
        $gap = "Contact sheet/release identity only; no full object-level review"
        $nextAction = "Deep-review only if promoted by report linkage or visual interest"
    } elseif ($group -eq "modern_dow_dod_pdf" -and ($hasText -or $inTriage)) {
        $coverage = "structured_triage"
        $gap = "Extracted/triaged but no dedicated source packet"
        $nextAction = "Promote only if triage shows high evidentiary value"
    } elseif ($group -eq "recent_witness_or_sketch" -and $hasText) {
        $coverage = "partial_review"
        $gap = "Briefing/sketch context only; no primary source or image provenance"
        $nextAction = "Review images/source records if promoted"
    } elseif ($group -eq "nasa_transcript_or_image" -or $group -eq "state_department_cable" -or $group -eq "fbi_photo_set" -or $group -eq "historical_archive_pdf") {
        if ($hasText) {
            $coverage = "text_extracted_only"
            $gap = "Text exists but targeted analytic review incomplete"
            $nextAction = "Run targeted historical/NASA/FBI/DOS review"
        } else {
            $coverage = "inventory_only"
            $gap = "No deep review yet"
            $nextAction = "Extract text or create image contact/provenance review"
        }
    }

    [pscustomobject]@{
        name = $name
        extension = $ext
        bytes = $file.bytes
        group = $group
        coverage_status = $coverage
        evidence = ($evidence -join "; ")
        derived_text = $hasText
        modern_triage = $inTriage
        video_contact_sheet = $hasSheet
        duplicate_group = $dupGroup
        gap = $gap
        next_action = $nextAction
        source_path = $file.source_path
    }
}

$rows | Sort-Object group,name | Export-Csv -Path $outPath -NoTypeInformation
$rows |
    Group-Object group,coverage_status |
    ForEach-Object {
        $parts = $_.Name -split ", "
        [pscustomobject]@{
            group = $parts[0]
            coverage_status = $parts[1]
            count = $_.Count
        }
    } |
    Sort-Object group,coverage_status |
    Export-Csv -Path $summaryPath -NoTypeInformation

Write-Host "Wrote $outPath"
Write-Host "Wrote $summaryPath"
