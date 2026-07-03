# GitHub Actions - Automatic Build and Release

## Overview

This repository uses a single GitHub Actions workflow, [build-release.yml](.github/workflows/build-release.yml), to build Passwords Manager on Windows.

The workflow:

1. Builds Windows on `main` and `develop`
2. Packages the Windows installers
3. Creates a GitHub Release
4. Computes SHA-256 hashes for the release assets
5. Publishes to WinGet
6. Refreshes the screenshot assets and commits them back to the repository

## Branch Behavior

- `main` creates a latest release
- `develop` creates a pre-release

## Outputs

- Windows: `passwords-manager-windows-installer.exe`, `install-passwords-manager.exe`, and `passwords-manager-windows.zip`
- Hash file: `SHA256SUMS.txt`

## Publication Targets

- WinGet uses the `JLBBARCO/winget-pkgs` fork

## Required Secrets

- `WINGET_PKGS_TOKEN`

## Local Installation

## Notes

- Screenshot refresh commits are made by `github-copilot[bot]`
- Release screenshots are rendered from the app UI assets, not captured from the full desktop
- The workflow fails fast if a required publication token is missing
- The release assets and screenshots are updated from the same workflow run, so the repository stays in sync with the published release
