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


def _ensure_linux_shortcuts(main_executable):
    app_dir = Path.home() / '.local' / 'share' / 'applications'
    app_dir.mkdir(parents=True, exist_ok=True)

    app_entry = app_dir / 'passwords-manager.desktop'
    uninstall_entry = app_dir / 'passwords-manager-uninstall.desktop'
    
    # In development mode, main_executable might be python executable
    # We need to construct the command properly
    if getattr(sys, 'frozen', False):
        exec_command = f'"{main_executable}"'
        uninstall_script = main_executable.parent / 'uninstall.sh'
    else:
        # Development mode: run main.py with python
        main_py = Path(__file__).resolve().parent.parent.parent.parent / 'main.py'
        exec_command = f'"{main_executable}" "{main_py}"'
        uninstall_script = Path(__file__).resolve().parent.parent.parent.parent / 'uninstall.py'

    app_entry.write_text(
        (
            '[Desktop Entry]\n'
            'Type=Application\n'
            'Version=1.0\n'
            'Name=Passwords Manager\n'
            f'Exec={exec_command}\n'
            'Terminal=false\n'
            'Categories=Utility;Security;\n'
        ),
        encoding='utf-8',
    )

    created = [str(app_entry)]

    if uninstall_script.exists():
        uninstall_entry.write_text(
            (
                '[Desktop Entry]\n'
                'Type=Application\n'
                'Version=1.0\n'
                'Name=Uninstall Passwords Manager\n'
                f'Exec="{main_executable}" "{uninstall_script}"\n'
                'Terminal=true\n'
                'Categories=Utility;\n'
            ),
            encoding='utf-8',
        )
        created.append(str(uninstall_entry))
    else:
        uninstall_entry.unlink(missing_ok=True)

    return created


def _ensure_macos_shortcuts(main_executable):
    app_dir = Path.home() / 'Applications'
    app_dir.mkdir(parents=True, exist_ok=True)

    app_launcher = app_dir / 'Passwords Manager.command'
    
    # In development mode, main_executable might be python executable
    if getattr(sys, 'frozen', False):
        app_launcher.write_text(f'#!/bin/bash\n"{main_executable}"\n', encoding='utf-8')
    else:
        # Development mode: run main.py with python
        main_py = Path(__file__).resolve().parent.parent.parent.parent / 'main.py'
        app_launcher.write_text(f'#!/bin/bash\n"{main_executable}" "{main_py}"\n', encoding='utf-8')
    
    app_launcher.chmod(0o755)

    created = [str(app_launcher)]

    uninstall_script = Path(__file__).resolve().parent.parent.parent.parent / 'uninstall.py'
    if getattr(sys, 'frozen', False):
        uninstall_script = main_executable.parent / 'uninstall.sh'
    
    uninstall_launcher = app_dir / 'Uninstall Passwords Manager.command'
    if uninstall_script.exists():
        uninstall_launcher.write_text(f'#!/bin/bash\n"{main_executable}" "{uninstall_script}"\n', encoding='utf-8')
        uninstall_launcher.chmod(0o755)
        created.append(str(uninstall_launcher))
    else:
        uninstall_launcher.unlink(missing_ok=True)

    return created


def ensure_platform_shortcuts():
    main_executable = _runtime_executable()
    if main_executable is None:
        return []

    if os.name == 'nt':
        return _ensure_windows_shortcuts(main_executable)

    if sys.platform.startswith('linux'):
        return _ensure_linux_shortcuts(main_executable)

    if sys.platform == 'darwin':
        return _ensure_macos_shortcuts(main_executable)

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
