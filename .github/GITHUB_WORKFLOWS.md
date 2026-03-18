# GitHub Workflows

This directory contains GitHub Actions workflows to automate builds and releases.

## 📁 Structure

```text
.github/
└── workflows/
   ├── build-release.yml        # Main build and release workflow
   └── build-android-apk.yml    # Android APK workflow with readiness checks
```

## 🔄 Available Workflows

### build-release.yml

**Description**: Compiles Password Manager for Windows, Linux, and macOS, packages and publishes to releases.

**Triggers**:

- Push to `main` and `criptograph` branches
- Tag creation (ex: `v1.0.0`)
- Manual execution via GitHub Actions UI

**Jobs**:

1. **build-windows**: Compiles for Windows
   - Generates `passwords-manager-windows.zip`
   - Includes executable + documentation

2. **build-linux**: Compiles for Linux
   - Generates `passwords-manager-linux.tar.gz`
   - Includes executable + documentation

3. **build-macos**: Compiles for macOS
   - Generates `passwords-manager-macos.tar.gz`
   - Includes executable + documentation

**Outputs**:

- Push to `main`: creates next patch tag automatically and triggers versioned release flow
- Tag events (`v*`): versioned release for builds and distribution
- Package publication: Winget always, Homebrew only when tap repository is configured
- Artifacts available for 90 days

### build-android-apk.yml

**Description**: Attempts automatic Android APK generation when Android prerequisites are present.

**Triggers**:

- Release published
- Manual execution via GitHub Actions UI

**Jobs**:

1. **android-readiness**: Validates if Android build is possible
   - Checks for `buildozer.spec`
   - Checks for `android/main.py`
   - Validates `source.dir = android` in `buildozer.spec`
   - Writes readiness reason to workflow summary

2. **build-android-apk**: Builds APK only when readiness checks pass
   - Installs Buildozer toolchain
   - Runs `buildozer android debug`
   - Uploads generated APK artifact
   - Attaches APK to release when trigger is release event

3. **android-not-ready**: Completes workflow with clear skip reason

## 🚀 How to Use

### Create Automatic Release (Latest)

Just commit and push to `main`:

```bash
git add .
git commit -m "Your message"
git push origin main
```

The workflow will create the next patch tag automatically (for example `v1.0.3`), then publish release + Winget + Homebrew from the tag run.

### Create Versioned Release

Create and push a tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

The workflow will create an official release with version `v1.0.0`.

### Manual Execution

1. Go to "Actions" on GitHub
2. Select "Build and Release"
3. Click "Run workflow"
4. Choose the branch and execute

## 📝 Configuration

### Environment Variables

The workflow uses only `GITHUB_TOKEN` (automatic), no additional secrets needed.

For Homebrew publishing, set `HOMEBREW_TAP_REPOSITORY` in workflow env (example: `JLBBARCO/homebrew-tap`).
If the tap is private or restricted, use a PAT with repository access.

### Modify the Workflow

To customize:

1. Edit `.github/workflows/build-release.yml`
2. Commit and push changes
3. Workflow will be updated automatically

### Add New Workflow

1. Create new YAML file in `.github/workflows/`
2. Use GitHub Actions syntax
3. Commit and push

## 🔍 Monitoring

Track builds at:

- **Actions Tab**: [GitHub Actions](https://github.com/JLBBARCO/passwords-manager/actions)
- **Status Badge**: Visible in main README.md

## 📚 Documentation

For more details about the build and release process, see:

- [GITHUB_ACTIONS.md](../GITHUB_ACTIONS.md) - Complete documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions) - Official documentation

## ⚠️ Important Notes

- Failed builds do not create/update releases
- Artifacts are kept for 90 days
- Tags should follow semantic versioning (ex: v1.0.0)
