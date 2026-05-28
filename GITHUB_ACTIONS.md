# GitHub Actions - Automatic Build and Release

## Overview

This repository uses a single GitHub Actions workflow, [build-release.yml](.github/workflows/build-release.yml), to build Passwords Manager on Windows, macOS, and Linux.

The workflow:

1. Builds each platform on `main` and `develop`
2. Packages the platform-specific installers
3. Creates a GitHub Release
4. Computes SHA-256 hashes for the release assets
5. Publishes to WinGet and Homebrew
6. Refreshes the screenshot assets and commits them back to the repository

## Branch Behavior

- `main` creates a latest release
- `develop` creates a pre-release

## Outputs

- Windows: `passwords-manager-windows-installer.exe`, `install-passwords-manager.exe`, and `passwords-manager-windows.zip`
- macOS: `passwords-manager-macos.dmg` and `passwords-manager-macos.tar.gz`
- Linux: `passwords-manager-linux.AppImage` and `passwords-manager-linux.tar.gz`
- Hash file: `SHA256SUMS.txt`

## Publication Targets

- WinGet uses the `JLBBARCO/winget-pkgs` fork
- Homebrew uses the `JLBBARCO/homebrew-tap` repository

## Required Secrets

- `WINGET_PKGS_TOKEN`
- `HOMEBREW_TAP_TOKEN`

## Local Installation

The Linux and macOS release archives are still compatible with `scripts/install-unix.sh`.

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/passwords-manager/main/scripts/install-unix.sh | bash
```

## Notes

- Screenshot refresh commits are made by `github-copilot[bot]`
- Release screenshots are rendered from the app UI assets, not captured from the full desktop
- The workflow fails fast if a required publication token is missing
- The release assets and screenshots are updated from the same workflow run, so the repository stays in sync with the published release
