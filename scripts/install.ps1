param(
    [ValidateSet("codex", "antigravity", "antigravity-plugin", "antigravity-cli", "claude-code")]
    [string]$Target = "codex",

    [string]$DestinationRoot
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$pluginSource = Join-Path $repoRoot "plugins\write-thai-academic-book"
$skillNames = @(
    "write-thai-academic-book",
    "research-outline-evidence",
    "assess-thai-academic-manuscript",
    "orchestrate-thai-academic-writing"
)
$pluginTargets = @("antigravity-plugin", "antigravity-cli")

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
    $destination = Join-Path $base "write-thai-academic-book"
    if (Test-Path -LiteralPath $destination) {
        Remove-Item -LiteralPath $destination -Recurse -Force
    }
    Copy-Item -LiteralPath $pluginSource -Destination $destination -Recurse
    Write-Output "Installed Thai academic writing suite plugin for $Target at $destination"
    exit 0
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
