from src.lib.app import App
from src.lib.shortcuts import (
    ensure_platform_shortcuts_best_effort,
    ensure_windows_start_menu_shortcut_best_effort,
)


if __name__ == '__main__':
    ensure_platform_shortcuts_best_effort()
    ensure_windows_start_menu_shortcut_best_effort()
    app = App()
    app.mainloop()
