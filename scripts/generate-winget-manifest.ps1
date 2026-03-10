param(
    [Parameter(Mandatory = $true)]
    [string]$Version,
    [string]$Publisher = "JLBBARCO",
    [string]$PackageIdentifier = "JLBBARCO.PasswordsManager",
    [string]$InstallerUrl = ""
)

$ErrorActionPreference = "Stop"

if (-not $InstallerUrl) {
    $InstallerUrl = "https://github.com/JLBBARCO/passwords-manager/releases/download/v$Version/install-passwords-manager.exe"
}

Write-Host "Downloading installer to calculate SHA256..." -ForegroundColor Yellow
$tempFile = Join-Path $env:TEMP ("passwords-manager-installer-" + $Version + ".exe")
Invoke-WebRequest -Uri $InstallerUrl -OutFile $tempFile
$sha256 = (Get-FileHash -Path $tempFile -Algorithm SHA256).Hash
Remove-Item -Force $tempFile

$manifestRoot = Join-Path $PSScriptRoot "..\packaging\winget\$Version"
New-Item -ItemType Directory -Path $manifestRoot -Force | Out-Null

$versionManifest = @"
PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
DefaultLocale: en-US
ManifestType: version
ManifestVersion: 1.6.0
"@

$installerManifest = @"
PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
InstallerType: exe
Scope: user
InstallModes:
  - interactive
  - silent
InstallerSwitches:
  Silent: /S
  SilentWithProgress: /S
Installers:
  - Architecture: x64
    InstallerUrl: $InstallerUrl
    InstallerSha256: $sha256
ManifestType: installer
ManifestVersion: 1.6.0
"@

$localeManifest = @"
PackageIdentifier: $PackageIdentifier
PackageVersion: $Version
PackageLocale: en-US
Publisher: $Publisher
PublisherUrl: https://github.com/JLBBARCO
PackageName: Passwords Manager
PackageUrl: https://github.com/JLBBARCO/passwords-manager
License: MIT
LicenseUrl: https://github.com/JLBBARCO/passwords-manager/blob/main/LICENSE
ShortDescription: Password manager with encrypted local storage.
Description: Manage and generate passwords with encrypted local storage under LocalAppData.
Moniker: passwords-manager
ReleaseNotesUrl: https://github.com/JLBBARCO/passwords-manager/releases/tag/v$Version
ManifestType: defaultLocale
ManifestVersion: 1.6.0
"@

Set-Content -Path (Join-Path $manifestRoot "$PackageIdentifier.yaml") -Value $versionManifest -Encoding UTF8
Set-Content -Path (Join-Path $manifestRoot "$PackageIdentifier.installer.yaml") -Value $installerManifest -Encoding UTF8
Set-Content -Path (Join-Path $manifestRoot "$PackageIdentifier.locale.en-US.yaml") -Value $localeManifest -Encoding UTF8

Write-Host "Winget manifests generated at: $manifestRoot" -ForegroundColor Green
Write-Host "Next step: open a PR in microsoft/winget-pkgs with these 3 files." -ForegroundColor Cyan
