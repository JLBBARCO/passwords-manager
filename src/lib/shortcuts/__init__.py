from pathlib import Path
import os
import subprocess
import sys

from src.lib.windows_shortcuts import (
    create_windows_shortcut,
    windows_desktop_directories,
    windows_start_menu_directories,
)


def _runtime_executable():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve()
    
    # In development mode, use Python executable running main.py from the project root.
    main_script = Path(__file__).resolve().parent.parent.parent.parent / 'main.py'
    if main_script.exists():
        return Path(sys.executable).resolve()
    
    return None


def _windows_uninstall_target(main_executable):
    uninstall_exe = main_executable.parent / 'uninstall' / 'uninstall.exe'
    if uninstall_exe.exists():
        return uninstall_exe
    return None


def _ensure_windows_shortcuts(main_executable):
    created = []
    failures = []

    shortcut_definitions = [('Passwords Manager.lnk', main_executable, 'Passwords Manager')]
    uninstall_target = _windows_uninstall_target(main_executable)
    if uninstall_target is not None:
        shortcut_definitions.append(
            ('Uninstall Passwords Manager.lnk', uninstall_target, 'Uninstall Passwords Manager')
        )

    # Determine working directory and arguments based on frozen/development mode
    if getattr(sys, 'frozen', False):
        working_dir = main_executable.parent
        main_arguments = None
        uninstall_arguments = None
    else:
        # Development mode: main_executable is Python, pass main.py as argument
        working_dir = Path(__file__).resolve().parent.parent.parent.parent
        main_py = working_dir / 'main.py'
        main_arguments = f'"{main_py}"' if main_py.exists() else None
        
        uninstall_py = working_dir / 'uninstall.py'
        uninstall_arguments = f'"{uninstall_py}"' if uninstall_py.exists() else None

    for start_menu_dir in windows_start_menu_directories():
        try:
            start_menu_dir.mkdir(parents=True, exist_ok=True)
        except Exception as directory_error:
            failures.append(f'{start_menu_dir}: {directory_error}')
            continue

        for shortcut_name, target_executable, description in shortcut_definitions:
            shortcut_path = start_menu_dir / shortcut_name
            
            # Use appropriate arguments based on shortcut type
            arguments = main_arguments if 'Passwords Manager.lnk' in shortcut_name else uninstall_arguments
            
            try:
                create_windows_shortcut(
                    shortcut_path, 
                    target_executable, 
                    working_dir, 
                    description,
                    arguments=arguments
                )
                created.append(str(shortcut_path))
            except Exception as shortcut_error:
                failures.append(f'{shortcut_path}: {shortcut_error}')

    for desktop_dir in windows_desktop_directories():
        try:
            desktop_dir.mkdir(parents=True, exist_ok=True)
        except Exception as directory_error:
            failures.append(f'{desktop_dir}: {directory_error}')
            continue

        desktop_shortcut = desktop_dir / 'Passwords Manager.lnk'
        try:
            create_windows_shortcut(
                desktop_shortcut,
                main_executable,
                working_dir,
                'Passwords Manager',
                arguments=main_arguments
            )
            created.append(str(desktop_shortcut))
        except Exception as shortcut_error:
            failures.append(f'{desktop_shortcut}: {shortcut_error}')

    if not created and failures:
        raise RuntimeError('Falha ao criar atalhos no Windows: ' + '; '.join(failures[:3]))

    return created


def ensure_windows_start_menu_shortcut(main_executable=None):
    if os.name != 'nt':
        return []

    runtime_executable = main_executable or _runtime_executable()
    if runtime_executable is None:
        return []

    created = []
    failures = []

    for start_menu_dir in windows_start_menu_directories():
        try:
            start_menu_dir.mkdir(parents=True, exist_ok=True)
        except Exception as directory_error:
            failures.append(f'{start_menu_dir}: {directory_error}')
            continue

        shortcut_path = start_menu_dir / 'Passwords Manager.lnk'
        try:
            create_windows_shortcut(
                shortcut_path,
                runtime_executable,
                runtime_executable.parent,
                'Passwords Manager',
            )
            created.append(str(shortcut_path))
        except Exception as shortcut_error:
            failures.append(f'{shortcut_path}: {shortcut_error}')

    if not created and failures:
        raise RuntimeError('Falha ao criar atalho no Menu Iniciar: ' + '; '.join(failures[:3]))

    return created


def ensure_platform_shortcuts():
    main_executable = _runtime_executable()
    if main_executable is None:
        return []

    if os.name == 'nt':
        return _ensure_windows_shortcuts(main_executable)

    return []


def ensure_platform_shortcuts_best_effort():
    try:
        return ensure_platform_shortcuts()
    except Exception:
        return []


def ensure_windows_start_menu_shortcut_best_effort(main_executable=None):
    try:
        return ensure_windows_start_menu_shortcut(main_executable)
    except Exception:
        return []
