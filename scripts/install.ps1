param(
    [ValidateSet("codex", "antigravity", "antigravity-plugin", "antigravity-cli", "claude-code")]
    [string]$Target = "codex",

    [string]$DestinationRoot
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$pluginSource = Join-Path $repoRoot "plugins\write-thai-academic-book"
$skillSource = Join-Path $pluginSource "skills\write-thai-academic-book"
$pluginTargets = @("antigravity-plugin", "antigravity-cli")
$source = if ($pluginTargets -contains $Target) { $pluginSource } else { $skillSource }

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

$destination = Join-Path $base "write-thai-academic-book"
New-Item -ItemType Directory -Force -Path $base | Out-Null
if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
}
Copy-Item -LiteralPath $source -Destination $destination -Recurse
$kind = if ($pluginTargets -contains $Target) { "plugin" } else { "skill" }
Write-Output "Installed write-thai-academic-book $kind for $Target at $destination"
