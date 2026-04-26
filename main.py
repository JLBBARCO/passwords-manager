import os
import subprocess
import sys
from pathlib import Path

from src.lib.app import App
from src.lib.shortcuts import (
    ensure_platform_shortcuts_best_effort,
    ensure_windows_start_menu_shortcut_best_effort,
)
from src.lib.system import path as system_path


def _is_running_from_winget_package():
    if not getattr(sys, 'frozen', False):
        return False

    local_app_data = os.environ.get('LOCALAPPDATA', '')
    if not local_app_data:
        return False

    winget_packages_root = Path(local_app_data) / 'Microsoft' / 'WinGet' / 'Packages'
    executable_dir = Path(sys.executable).resolve().parent

    try:
        executable_dir.relative_to(winget_packages_root)
        return True
    except ValueError:
        return False


def _try_relocate_from_winget_package():
    if not _is_running_from_winget_package():
        return False

    install_root = Path(system_path())
    installed_main_exe = install_root / 'passwords-manager.exe'
    current_main_exe = Path(sys.executable).resolve()

    if installed_main_exe.exists() and installed_main_exe.resolve() != current_main_exe:
        subprocess.Popen([str(installed_main_exe)], close_fds=True)
        return True

    installer_candidates = [
        current_main_exe.parent / 'install-passwords-manager.exe',
        current_main_exe.parent.parent / 'install-passwords-manager.exe',
    ]

    winget_installer = next((candidate for candidate in installer_candidates if candidate.exists()), None)
    if winget_installer is None:
        return False

    install_target_argument = f'/D={install_root}'

    try:
        install_process = subprocess.run(
            [str(winget_installer), '/S', install_target_argument],
            check=False,
            timeout=600,
        )
    except Exception:
        return False

    if install_process.returncode != 0:
        return False

    if not installed_main_exe.exists():
        return False

    subprocess.Popen([str(installed_main_exe)], close_fds=True)
    return True


if __name__ == '__main__':
    if _try_relocate_from_winget_package():
        raise SystemExit(0)

    ensure_platform_shortcuts_best_effort()
    ensure_windows_start_menu_shortcut_best_effort()
    app = App()
    app.mainloop()
