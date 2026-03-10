# GitHub Actions - Automatic Build and Release

## 📋 Overview

This repository has an automated GitHub Actions workflow that compiles Password Manager for Windows, Linux, and macOS, packages files, and automatically publishes to Releases.

## 🔄 When the Workflow is Executed

The workflow is triggered in the following situations:

1. **Push to `main` branch**: Automatic build and update of "latest" release
2. **Push to `criptograph` branch**: Development build
3. **Tag creation**: To create versioned releases (ex: `v1.0.0`, `v2.1.3`)
4. **Manual execution**: Via GitHub Actions interface

## 🏗️ Build Process

### Windows Build

1. **Environment**: `windows-latest`
2. **Python**: 3.11
3. **Process**:
   - Installs dependencies from `requirements.txt`
   - Installs PyInstaller
   - Compiles `main.py`, `uninstall.py` and `install.py` with PyInstaller (--onefile --noconsole)
   - Includes application icon
   - Creates release structure with `release/uninstall/uninstall.exe`
   - Creates installer package with `install-passwords-manager.exe`
   - Compresses to ZIP file
   - Publishes to release

### Linux Build

1. **Environment**: `ubuntu-latest`
2. **Python**: 3.11
3. **Process**:
   - Installs dependencies from `requirements.txt`
   - Installs PyInstaller
   - Compiles with PyInstaller (--onefile --noconsole)
   - Creates release structure with README, LICENSE and ENCRYPTION.md
   - Sets execution permissions
   - Compresses to TAR.GZ file
   - Publishes to release

### macOS Build

1. **Environment**: `macos-latest`
2. **Python**: 3.11
3. **Process**:
   - Installs dependencies from `requirements.txt`
   - Installs PyInstaller
   - Compiles with PyInstaller (--onefile --windowed)
   - Creates release structure with README, LICENSE and ENCRYPTION.md
   - Sets execution permissions
   - Compresses to TAR.GZ file
   - Publishes to release

## 📦 Generated Files

### Windows

- **File**: `passwords-manager-windows.zip`
- **Installer**: `install-passwords-manager.exe`
- **Content main executable**: `passwords-manager.exe`
- **Content uninstaller**: `uninstall/uninstall.exe`
- **Content docs**: `README.md`, `LICENSE`, `ENCRYPTION.md`

### Linux

- **File**: `passwords-manager-linux.tar.gz`
- **Content**:
  - `passwords-manager` - Main executable (with execution permission)
  - `README.md` - Documentation
  - `LICENSE` - License
  - `ENCRYPTION.md` - Encryption technical documentation

### macOS

- **File**: `passwords-manager-macos.tar.gz`
- **Content**:
  - `passwords-manager` - Main executable (with execution permission)
  - `README.md` - Documentation
  - `LICENSE` - License
  - `ENCRYPTION.md` - Encryption technical documentation

## 🏷️ Release System

### "Latest" Release

- **When**: Created/updated with each push to `main` or `criptograph` branch
- **Type**: Pre-release (development)
- **Tag**: `latest`
- **Description**: Contains the latest build of the code

### Versioned Releases

To create a versioned release:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Or via GitHub:

1. Go to "Releases" → "Create a new release"
2. Create a new tag (ex: `v1.0.0`)
3. Publish the release

The workflow will detect the tag and automatically create:

- Release with version name
- Build for Windows, Linux and macOS
- Compressed files attached

## 📝 Release Information

Each release automatically includes:

- **Version**: Tag or "latest"
- **Program Features**: List of functionalities
- **Important Notices**: About encryption.key and security
- **Changelog**: Commit information
- **Build Metadata**:
  - Build date and time
  - Source branch
  - Commit hash

## 🚀 How to Use the Builds

### Windows (End User)

1. Download `passwords-manager-windows.zip` from release
2. Extract the ZIP file
3. Run `install-passwords-manager.exe`

Alternative (after winget publication):

```powershell
winget install JLBBARCO.PasswordsManager
```

### Linux (End User)

1. Download `passwords-manager-linux.tar.gz` from release
2. Extract the file:

   ```bash
   tar -xzf passwords-manager-linux.tar.gz
   ```

3. Run the program:

   ```bash
   ./passwords-manager
   ```

Alternative installer script:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/passwords-manager/main/scripts/install-unix.sh | bash
```

### macOS (End User)

1. Download `passwords-manager-macos.tar.gz` from release
2. Extract the file:

   ```bash
   tar -xzf passwords-manager-macos.tar.gz
   ```

3. Run the program:

   ```bash
   ./passwords-manager
   ```

Alternative installer script:

```bash
curl -fsSL https://raw.githubusercontent.com/JLBBARCO/passwords-manager/main/scripts/install-unix.sh | bash
```

**Note**: On macOS, you may need to authorize the application execution in Security and Privacy settings.

## 🔧 Workflow Configuration

The workflow is located at: `.github/workflows/build-release.yml`

### Required Permissions

The workflow uses automatic `GITHUB_TOKEN` with permissions for:

- Create and update releases
- Upload assets
- Read repository code

### Modifying the Workflow

To adjust the behavior:

1. **Add more platforms**: Create new jobs (ex: `build-macos`)
2. **Change Python version**: Modify `python-version`
3. **Include more files**: Add to "Prepare release files"
4. **Customize description**: Edit the release `body` section

## ❗ Troubleshooting

### Build Fails

1. Check logs in GitHub Actions
2. Make sure all dependencies are in `requirements.txt`
3. Check for syntax errors in code

### Release Not Updating

1. Check if commit was to correct branch
2. Confirm workflow was executed ("Actions" tab)
3. Check `GITHUB_TOKEN` permissions

### Missing File

1. Confirm file exists in repository
2. Check "Prepare release files" step
3. See artifacts for debugging

## 📊 Monitoring

To track builds:

1. Go to "Actions" on GitHub
2. Select "Build and Release" workflow
3. View execution history
4. Click an execution to see details and logs

## 🔐 Security

- **Secrets**: Workflow uses only automatic `GITHUB_TOKEN`
- **Dependencies**: Installed via pip from official sources
- **Build**: Executed in isolated GitHub environments
- **Assets**: Published directly from build pipeline

## 📚 References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)

## 🤝 Contributing

When contributing:

1. Push to your branch
2. Workflow will create a test build
3. After merge to `main`, "latest" release will be updated
4. For official releases, create a tag with version
