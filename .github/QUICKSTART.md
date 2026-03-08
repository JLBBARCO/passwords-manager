# 🚀 Quick Start Guide - GitHub Actions

## For Developers

### Deploy Automatically (Latest)

```bash
# 1. Make your changes
git add .
git commit -m "feat: new feature"

# 2. Push to GitHub
git push origin main

# 3. Wait ~5-10 minutes
# The build will be done automatically!

# 4. Access the release
# https://github.com/JLBBARCO/passwords-manager/releases/latest
```

### Create Official Version

```bash
# 1. Make sure you're on main
git checkout main
git pull

# 2. Create the tag with version
git tag v1.0.0

# 3. Push the tag
git push origin v1.0.0

# 4. Wait for build
# The release v1.0.0 will be created automatically!
```

### Local Build (Test)

**Windows (PowerShell):**

```powershell
.\build-local.ps1
```

**Windows (CMD):**

```cmd
build.bat
```

## For Users

### Download Latest Version

1. Visit: [Latest Release](https://github.com/JLBBARCO/passwords-manager/releases/latest)

2. Download:
   - **Windows**: `passwords-manager-windows.zip`
   - **Linux**: `passwords-manager-linux.tar.gz`
   - **macOS**: `passwords-manager-macos.tar.gz`

3. Extract and run!

## Release Checklist

Before creating an official release:

- [ ] Code is working locally
- [ ] Tests have been performed
- [ ] README.md is updated
- [ ] ENCRYPTION.md is updated
- [ ] Version was incremented correctly
- [ ] CHANGELOG was updated (if exists)

## Build Status

Check current status:

[![Build Status](https://github.com/JLBBARCO/passwords-manager/actions/workflows/build-release.yml/badge.svg)](https://github.com/JLBBARCO/passwords-manager/actions/workflows/build-release.yml)

## Quick Troubleshooting

### Build Failed?

1. Go to: [GitHub Actions](https://github.com/JLBBARCO/passwords-manager/actions)
2. Click on failed build
3. View logs to identify the issue
4. Fix and make new commit

### Release Not Showing Up?

1. Check if workflow was executed
2. Confirm there were no errors
3. Wait a few minutes (there may be delay)
4. Check repository permissions

### Want to Delete a Release?

```bash
# Delete on GitHub (UI)
# Releases → Select release → Delete

# Delete tag locally
git tag -d v1.0.0

# Delete tag remotely
git push origin :refs/tags/v1.0.0
```

## Useful Commands

```bash
# List all tags
git tag -l

# View latest tag
git describe --tags

# View commits since latest tag
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Create annotated tag (recommended)
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push all tags
git push origin --tags
```

## Tips

💡 **Use Semantic Versioning**: MAJOR.MINOR.PATCH (ex: 1.0.0)

- **MAJOR**: Incompatible changes
- **MINOR**: New compatible feature
- **PATCH**: Bug fixes

💡 **Prefix tags with 'v'**: v1.0.0 (common convention)

💡 **Test locally first**: Use `build-local.ps1` to test

💡 **Clear commits**: Use conventional commits (feat:, fix:, docs:)

## Quick Links

- 📦 [Releases](https://github.com/JLBBARCO/passwords-manager/releases)
- 🔄 [Actions](https://github.com/JLBBARCO/passwords-manager/actions)
- 📚 [Complete Documentation](../GITHUB_ACTIONS.md)
- 🐛 [Issues](https://github.com/JLBBARCO/passwords-manager/issues)
