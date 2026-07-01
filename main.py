import os
import subprocess
import sys
from pathlib import Path


    if not installed_main_exe.exists():
        return False


if __name__ == '__main__':
    if _try_relocate_from_winget_package():
        raise SystemExit(0)

    ensure_platform_shortcuts_best_effort()
    ensure_windows_start_menu_shortcut_best_effort()
    app = App()
    app.mainloop()
