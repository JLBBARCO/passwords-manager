import os
import sys
from pathlib import Path

from src.lib.app import App
from src.lib.install import Install


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


if __name__ == '__main__':
    app = Install() if _is_running_from_winget_package() else App()
    app.mainloop()
