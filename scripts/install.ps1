param(
    [ValidateSet("codex", "antigravity", "antigravity-plugin", "antigravity-cli", "claude-code")]
    [string]$Target = "codex",

    [string]$DestinationRoot,

    [switch]$IncludeAcademicHarness
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$pluginSource = Join-Path $repoRoot "plugins\write-thai-academic-book"
$skillNames = @(
    "write-thai-academic-book",
    "research-outline-evidence",
    "assess-thai-academic-manuscript",
    "orchestrate-thai-academic-writing"
)
$pluginTargets = @("antigravity-plugin", "antigravity-cli")
$harnessSkillsRoot = Join-Path $repoRoot "integrations\hermes-obsidian\skills"

$base = if ($DestinationRoot) {
    $DestinationRoot
} else {
    switch ($Target) {
        "codex" { Join-Path $HOME ".agents\skills" }
        "antigravity" { Join-Path $HOME ".gemini\config\skills" }
        "antigravity-plugin" { Join-Path $HOME ".gemini\config\plugins" }
        "antigravity-cli" { Join-Path $HOME ".gemini\antigravity-cli\plugins" }
        "claude-code" { Join-Path $HOME ".claude\skills" }
    }
}

New-Item -ItemType Directory -Force -Path $base | Out-Null
if ($pluginTargets -contains $Target) {
    if ($IncludeAcademicHarness) {
        throw "-IncludeAcademicHarness is supported only for skill targets, not plugin targets."
    }
    $destination = Join-Path $base "write-thai-academic-book"
    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -LiteralPath $pluginSource -Destination $destination -Recurse
    Write-Output "Installed Thai academic writing suite plugin for $Target at $destination"
    exit 0
}

foreach ($skillName in $skillNames) {
    $requiredSource = Join-Path (Join-Path $pluginSource "skills") $skillName
    if (-not (Test-Path -LiteralPath $requiredSource -PathType Container)) {
        throw "Required skill source is missing or unavailable: $requiredSource"
    }
}
if ($IncludeAcademicHarness -and -not (Test-Path -LiteralPath $harnessSkillsRoot -PathType Container)) {
    throw "Academic harness skills are missing: $harnessSkillsRoot"
}

foreach ($skillName in $skillNames) {
    $source = Join-Path (Join-Path $pluginSource "skills") $skillName
    $destination = Join-Path $base $skillName
    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -LiteralPath $source -Destination $destination -Recurse
    Write-Output "Installed $skillName skill for $Target at $destination"
}

if ($IncludeAcademicHarness) {
    Get-ChildItem -LiteralPath $harnessSkillsRoot -Directory | ForEach-Object {
        $source = $_.FullName
        $destination = Join-Path $base $_.Name
        if (Test-Path -LiteralPath $destination) {
            Remove-Item -LiteralPath $destination -Recurse -Force
        }
        Copy-Item -LiteralPath $source -Destination $destination -Recurse
        Write-Output "Installed $($_.Name) academic harness skill for $Target at $destination"
    }
}
