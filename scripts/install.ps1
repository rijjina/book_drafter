param(
    [ValidateSet("codex", "antigravity", "antigravity-cli", "claude-code")]
    [string]$Target = "codex",

    [string]$DestinationRoot
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $repoRoot "plugins\write-thai-academic-book\skills\write-thai-academic-book"

$base = if ($DestinationRoot) {
    $DestinationRoot
} else {
    switch ($Target) {
        "codex" { Join-Path $HOME ".agents\skills" }
        "antigravity" { Join-Path $HOME ".agents\skills" }
        "antigravity-cli" { Join-Path $HOME ".gemini\antigravity-cli\skills" }
        "claude-code" { Join-Path $HOME ".claude\skills" }
    }
}

$destination = Join-Path $base "write-thai-academic-book"
New-Item -ItemType Directory -Force -Path $base | Out-Null
if (Test-Path -LiteralPath $destination) {
    Remove-Item -LiteralPath $destination -Recurse -Force
}
Copy-Item -LiteralPath $source -Destination $destination -Recurse
Write-Output "Installed write-thai-academic-book for $Target at $destination"
