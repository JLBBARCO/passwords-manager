# GitHub Workflows

This directory contains the automated release pipeline for Passwords Manager.

## Workflows

Only one release workflow remains active:

- [build-release.yml](workflows/build-release.yml) - builds Windows, macOS, and Linux on `main` and `develop`, packages installers, creates the GitHub Release, publishes to WinGet and Homebrew, refreshes screenshots, and commits the updated assets back to the repository.

## Branch behavior

- `main` creates a latest release.
- `develop` creates a pre-release.

## Publish targets

- Windows installer publication uses the `JLBBARCO/winget-pkbs` fork.
- Homebrew publication uses the `JLBBARCO/homebrew-tap` repository.

## Required secrets

- `WINGET_TOKEN`
- `HOMEBREW_TAP_TOKEN`

## Notes

- The workflow refreshes `src/assets/screenshot/*.webp` and `src/assets/img/thumbnail.webp` after each successful release build.
- Release screenshots are rendered by the workflow from the app UI, not captured from the full desktop.
- The workflow writes SHA-256 hashes into `SHA256SUMS.txt` and uploads that file to the release.
