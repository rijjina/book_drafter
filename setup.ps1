[CmdletBinding()]
param(
    [string]$VaultPath = (Join-Path ([Environment]::GetFolderPath("MyDocuments")) "Academic-Writing-Vault"),

    [string]$SkillDestination = (Join-Path $HOME ".agents\skills"),

    [switch]$SkipHermes,

    [switch]$SkipValidation
)

$ErrorActionPreference = "Stop"
$repoRoot = $PSScriptRoot
$installScript = Join-Path $repoRoot "scripts\install.ps1"
$hermesSetupScript = Join-Path $repoRoot "scripts\setup-hermes-obsidian.ps1"
$validator = Join-Path $repoRoot "scripts\validate_hermes_obsidian.py"

foreach ($requiredFile in @($installScript, $hermesSetupScript, $validator)) {
    if (-not (Test-Path -LiteralPath $requiredFile -PathType Leaf)) {
        throw "Repository checkout is incomplete. Missing: $requiredFile"
    }
}

Write-Output "[1/3] Installing the complete academic-writing skill set..."
& $installScript `
    -Target codex `
    -DestinationRoot $SkillDestination `
    -IncludeAcademicHarness

$resolvedVaultPath = [System.IO.Path]::GetFullPath($VaultPath)
$initializeVault = -not (Test-Path -LiteralPath $resolvedVaultPath -PathType Container)
$hermesAvailable = $null -ne (Get-Command hermes -ErrorAction SilentlyContinue)

Write-Output "[2/3] Preparing the Obsidian academic-writing vault..."
$vaultArguments = @("-VaultPath", $resolvedVaultPath)
if ($initializeVault) {
    $vaultArguments += "-InitializeVault"
}
if (-not $SkipHermes -and $hermesAvailable) {
    $vaultArguments += "-ConfigureHermes"
}
& $hermesSetupScript @vaultArguments

if (-not $SkipValidation) {
    Write-Output "[3/3] Validating the portable integration..."
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        $pythonCommand = Get-Command py -ErrorAction SilentlyContinue
    }
    if ($pythonCommand) {
        $pythonExecutable = $pythonCommand.Source
        & $pythonExecutable $validator
        if ($LASTEXITCODE -ne 0) {
            throw "Repository validation failed."
        }
    } else {
        Write-Warning "Python was not found; repository validation was skipped."
    }
} else {
    Write-Output "[3/3] Validation skipped by request."
}

Write-Output ""
Write-Output "Setup complete."
Write-Output "Skills: $SkillDestination"
Write-Output "Obsidian vault: $resolvedVaultPath"
if ($SkipHermes) {
    Write-Output "Hermes configuration was skipped by request."
} elseif (-not $hermesAvailable) {
    Write-Warning "Hermes CLI was not found. Install Hermes, then rerun .\setup.ps1 to register the skills and vault."
} else {
    Write-Output "Hermes is configured. Restart Hermes and Codex before using the new skills."
}
