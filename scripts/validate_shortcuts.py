#!/usr/bin/env python3
"""
Validator script to check if shortcuts were created correctly on first run.
Supports Windows (Start Menu + Desktop).
"""

import os
import sys
from pathlib import Path


def validate_windows_shortcuts():
    """Validate Windows Start Menu and Desktop shortcuts."""
    from src.lib.windows_shortcuts import (
        windows_start_menu_directories,
        windows_desktop_directories,
    )

    errors = []
    found_shortcuts = []

    try:
        start_menu_dirs = windows_start_menu_directories()
    except Exception as error:
        errors.append(f"Failed to get Start Menu directories: {error}")
        return found_shortcuts, errors

    for start_menu_dir in start_menu_dirs:
        start_menu_shortcut = start_menu_dir / "Passwords Manager.lnk"
        if start_menu_shortcut.exists():
            found_shortcuts.append(str(start_menu_shortcut))
        else:
            errors.append(f"Start Menu shortcut not found: {start_menu_shortcut}")

    for desktop_dir in windows_desktop_directories():
        desktop_shortcut = desktop_dir / "Passwords Manager.lnk"
        if desktop_shortcut.exists():
            found_shortcuts.append(str(desktop_shortcut))
        else:
            errors.append(f"Desktop shortcut not found: {desktop_shortcut}")

    return found_shortcuts, errors


def main():
    """Main validation routine."""
    print("=" * 70)
    print("Passwords Manager - Shortcut Validation")
    print("=" * 70)
    print()

    all_found = []
    all_errors = []

    if os.name == "nt":
        print("Validating Windows shortcuts...")
        found, errors = validate_windows_shortcuts()
        all_found.extend(found)
        all_errors.extend(errors)
    else:
        print(f"Unsupported platform: {sys.platform}")
        return 1

    print()
    if all_found:
        print("✓ Shortcuts found:")
        for shortcut in all_found:
            print(f"  - {shortcut}")
    else:
        print("✗ No shortcuts found")

    print()
    if all_errors:
        print("✗ Issues detected:")
        for error in all_errors:
            print(f"  - {error}")
        print()
        return 1
    else:
        print("✓ All shortcuts validated successfully!")
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
