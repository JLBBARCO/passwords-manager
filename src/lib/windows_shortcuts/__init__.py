from pathlib import Path
import os
import subprocess


def _dedupe_paths(paths):
    unique_paths = []
    seen = set()
    for candidate in paths:
        key = str(candidate).lower()
        if key in seen:
            continue
        seen.add(key)
        unique_paths.append(candidate)
    return unique_paths


def windows_start_menu_directories():
    directories = []
    appdata = os.environ.get('APPDATA')
    programdata = os.environ.get('PROGRAMDATA')

    if appdata:
        directories.append(Path(appdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs')
    if programdata:
        directories.append(Path(programdata) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs')

    if not directories:
        raise EnvironmentError('Nao foi possivel localizar o Menu Iniciar (APPDATA/PROGRAMDATA ausentes).')

    return _dedupe_paths(directories)


def windows_desktop_directories():
    directories = []
    userprofile = os.environ.get('USERPROFILE')
    public_root = os.environ.get('PUBLIC')

    if userprofile:
        directories.append(Path(userprofile) / 'Desktop')
    if public_root:
        directories.append(Path(public_root) / 'Desktop')

    return _dedupe_paths(directories)


def create_windows_shortcut(shortcut_path, target_exe, working_dir, description):
    shortcut_path_ps = str(shortcut_path).replace("'", "''")
    target_exe_ps = str(target_exe).replace("'", "''")
    working_dir_ps = str(working_dir).replace("'", "''")
    description_ps = str(description).replace("'", "''")

    script = (
        "$shell = New-Object -ComObject WScript.Shell;"
        f"$shortcut = $shell.CreateShortcut('{shortcut_path_ps}');"
        f"$shortcut.TargetPath = '{target_exe_ps}';"
        f"$shortcut.WorkingDirectory = '{working_dir_ps}';"
        f"$shortcut.IconLocation = '{target_exe_ps},0';"
        f"$shortcut.Description = '{description_ps}';"
        "$shortcut.Save();"
    )

    result = subprocess.run(
        ['powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', script],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or 'erro desconhecido')


def remove_windows_shortcuts(names):
    if names is None:
        shortcut_names = ()
    else:
        shortcut_names = tuple(names)
    if not shortcut_names:
        return

    directories = []
    try:
        directories.extend(windows_start_menu_directories())
    except Exception:
        pass

    directories.extend(windows_desktop_directories())
    for directory in _dedupe_paths(directories):
        for shortcut_name in shortcut_names:
            (directory / shortcut_name).unlink(missing_ok=True)
