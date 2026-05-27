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

The GitHub Actions workflow publishes manifests to the forked package repository used by this project:

`https://github.com/JLBBARCO/winget-pkbs`

The generated files are copied into the package path expected by winget manifests and committed by the workflow.

After merge, users can install with:

```powershell
winget install JLBBARCO.PasswordsManager
```

The generated manifests now target machine scope and set the install location to:

`C:\File Programs (x86)\Passwords Manager`
