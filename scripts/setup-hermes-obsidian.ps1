[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [string]$VaultPath,

    [switch]$InitializeVault,
    [switch]$ForceTemplateFiles,
    [switch]$ConfigureHermes
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$integrationRoot = Join-Path $repoRoot "integrations\hermes-obsidian"
$vaultTemplate = Join-Path $integrationRoot "vault-template"
$skillRoots = @(
    (Join-Path $repoRoot "plugins\write-thai-academic-book\skills"),
    (Join-Path $integrationRoot "skills")
)

foreach ($requiredPath in @($integrationRoot, $vaultTemplate) + $skillRoots) {
    if (-not (Test-Path -LiteralPath $requiredPath)) {
        throw "Required path is missing: $requiredPath"
    }
}

$resolvedVaultPath = [System.IO.Path]::GetFullPath($VaultPath)

if ($InitializeVault) {
    if ($PSCmdlet.ShouldProcess($resolvedVaultPath, "Initialize Obsidian academic-writing vault")) {
        New-Item -ItemType Directory -Force -Path $resolvedVaultPath | Out-Null
        Get-ChildItem -LiteralPath $vaultTemplate -Recurse -File | ForEach-Object {
            $relative = [System.IO.Path]::GetRelativePath($vaultTemplate, $_.FullName)
            $destination = Join-Path $resolvedVaultPath $relative
            $destinationParent = Split-Path -Parent $destination
            New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
            if ((Test-Path -LiteralPath $destination) -and -not $ForceTemplateFiles) {
                Write-Output "Preserved existing vault file: $destination"
            } else {
                Copy-Item -LiteralPath $_.FullName -Destination $destination -Force
                Write-Output "Installed vault template file: $destination"
            }
        }
        foreach ($directory in @("Notes", "Sources", "Projects")) {
            New-Item -ItemType Directory -Force -Path (Join-Path $resolvedVaultPath $directory) | Out-Null
        }
    }
} elseif (-not (Test-Path -LiteralPath $resolvedVaultPath -PathType Container)) {
    throw "VaultPath does not exist. Use -InitializeVault to create it: $resolvedVaultPath"
}

if ($ConfigureHermes) {
    $hermes = Get-Command hermes -ErrorAction SilentlyContinue
    if (-not $hermes) {
        throw "Hermes CLI was not found on PATH. Install Hermes, then rerun with -ConfigureHermes."
    }

    $rawExternalDirs = (& hermes config get skills.external_dirs --json 2>$null | Out-String).Trim()
    $currentDirs = @()
    if ($rawExternalDirs) {
        $jsonMatch = [regex]::Match($rawExternalDirs, '(?s)\[.*\]')
        if ($jsonMatch.Success) {
            $parsed = ConvertFrom-Json $jsonMatch.Value
            if ($null -ne $parsed) {
                $currentDirs = @($parsed)
            }
        }
    }

    $mergedDirs = @($currentDirs + $skillRoots) |
        ForEach-Object { [System.IO.Path]::GetFullPath([string]$_) } |
        Select-Object -Unique
    $externalDirsJson = ConvertTo-Json -Compress -InputObject @($mergedDirs)

    if ($PSCmdlet.ShouldProcess("Hermes configuration", "Register academic skill roots and Obsidian vault")) {
        & hermes config set skills.external_dirs $externalDirsJson
        if ($LASTEXITCODE -ne 0) {
            throw "Hermes rejected skills.external_dirs. No vault files were removed."
        }
        & hermes config set OBSIDIAN_VAULT_PATH $resolvedVaultPath
        if ($LASTEXITCODE -ne 0) {
            throw "Hermes rejected OBSIDIAN_VAULT_PATH."
        }
        & hermes config check
        if ($LASTEXITCODE -ne 0) {
            throw "Hermes configuration check failed. Review the messages above."
        }
    }
}

Write-Output "Repository root: $repoRoot"
Write-Output "Obsidian vault: $resolvedVaultPath"
Write-Output "Hermes skill roots:"
$skillRoots | ForEach-Object { Write-Output "  - $_" }
if ($WhatIfPreference) {
    Write-Output "Dry run complete. No Hermes configuration or vault files were changed."
} elseif (-not $ConfigureHermes) {
    Write-Output "Hermes was not changed. Rerun with -ConfigureHermes to register these paths."
} else {
    Write-Output "Hermes configured. Restart Hermes before using the new skills."
}
