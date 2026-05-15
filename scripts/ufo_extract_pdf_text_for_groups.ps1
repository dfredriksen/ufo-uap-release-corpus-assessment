param(
    [string]$RepoRoot = ".",
    [string[]]$Groups = @("nasa_transcript_or_image", "state_department_cable"),
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

$research = Join-Path $RepoRoot "research"
$coveragePath = Join-Path $research "ufo-file-coverage-map.csv"
$textDir = Join-Path $research "ufo-derived/text"
$logPath = Join-Path $research "ufo-pdf-text-extraction-log.csv"

New-Item -ItemType Directory -Force -Path $textDir | Out-Null

function Safe-Stem([string]$name) {
    $stem = [System.IO.Path]::GetFileNameWithoutExtension($name)
    $stem = $stem -replace '[<>:"/\\|?*]', '_'
    return $stem
}

$rows = Import-Csv $coveragePath | Where-Object {
    $_.extension -eq ".pdf" -and $Groups -contains $_.group
}

$log = foreach ($row in $rows) {
    $out = Join-Path $textDir ((Safe-Stem $row.name) + ".txt")
    $status = "skipped"
    $chars = 0
    $errorText = ""

    if ((Test-Path $out) -and -not $Overwrite) {
        $status = "exists"
        $chars = (Get-Content -LiteralPath $out -Raw -ErrorAction SilentlyContinue).Length
    } else {
        try {
            & pdftotext -layout -enc UTF-8 "$($row.source_path)" "$out" 2>$null
            if (Test-Path $out) {
                $chars = (Get-Content -LiteralPath $out -Raw -ErrorAction SilentlyContinue).Length
                $status = if ($chars -gt 0) { "extracted" } else { "empty" }
            } else {
                $status = "missing_output"
            }
        } catch {
            $status = "error"
            $errorText = $_.Exception.Message
        }
    }

    [pscustomobject]@{
        name = $row.name
        group = $row.group
        output = $out
        status = $status
        text_chars = $chars
        error = $errorText
    }
}

$existing = @()
if (Test-Path $logPath) {
    $existing = Import-Csv $logPath
}

@($existing + $log) | Export-Csv -Path $logPath -NoTypeInformation
$log | Format-Table -AutoSize
