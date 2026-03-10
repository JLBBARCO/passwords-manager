# Winget packaging

This folder contains tooling to publish Passwords Manager in winget.

## Generate manifests for a version

Run in PowerShell:

```powershell
./scripts/generate-winget-manifest.ps1 -Version 1.2.3
```

This creates 3 files in `packaging/winget/1.2.3/`:

- `JLBBARCO.PasswordsManager.yaml`
- `JLBBARCO.PasswordsManager.installer.yaml`
- `JLBBARCO.PasswordsManager.locale.en-US.yaml`

## Publish to winget

1. Fork `microsoft/winget-pkgs`
2. Copy the generated files to the package path used by winget-pkgs
3. Open a PR

After merge, users can install with:

```powershell
winget install JLBBARCO.PasswordsManager
```
