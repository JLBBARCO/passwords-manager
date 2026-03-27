from pathlib import Path
import os
import subprocess
import tempfile


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
    def _escape_vbs(value):
        return str(value).replace('"', '""')

    shortcut_path_str = _escape_vbs(shortcut_path)
    target_exe_str = _escape_vbs(target_exe)
    working_dir_str = _escape_vbs(working_dir)
    description_str = _escape_vbs(description)

    vbs_script = (
        'Set shell = CreateObject("WScript.Shell")\n'
        f'Set shortcut = shell.CreateShortcut("{shortcut_path_str}")\n'
        f'shortcut.TargetPath = "{target_exe_str}"\n'
        f'shortcut.WorkingDirectory = "{working_dir_str}"\n'
        f'shortcut.IconLocation = "{target_exe_str},0"\n'
        f'shortcut.Description = "{description_str}"\n'
        'shortcut.Save\n'
    )

    script_file = None
    script_path = None
    try:
        script_file = tempfile.NamedTemporaryFile('w', suffix='.vbs', delete=False, encoding='utf-8')
        script_file.write(vbs_script)
        script_file.close()
        script_path = Path(script_file.name)

        result = subprocess.run(
            ['cscript.exe', '//NoLogo', str(script_path)],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        if script_file is not None and not script_file.closed:
            script_file.close()
        if script_path is not None:
            script_path.unlink(missing_ok=True)

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
