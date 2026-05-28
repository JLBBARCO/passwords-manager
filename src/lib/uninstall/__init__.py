from pathlib import Path
import ctypes
import shutil
import subprocess
import sys
import winreg

from src.lib.system import APP_FOLDER_NAME, compatibility_installation_paths, path as default_install_root
from src.lib.windows_shortcuts import remove_windows_shortcuts


def normalize_installation_path(path_value):
	path_obj = Path(path_value).expanduser()
	if path_obj.name.lower() != APP_FOLDER_NAME.lower():
		path_obj = path_obj / APP_FOLDER_NAME
	return path_obj


def default_installation_path():
	return Path(default_install_root())


def installation_candidates():
	paths = [normalize_installation_path(candidate) for candidate in compatibility_installation_paths()]
	unique_paths = []
	seen = set()
	for candidate in paths:
		normalized = str(candidate)
		if normalized not in seen:
			seen.add(normalized)
			unique_paths.append(candidate)
	return unique_paths


def detect_installation_path(selected_path=None):
	if selected_path:
		return normalize_installation_path(selected_path)

	if getattr(sys, 'frozen', False):
		exe_path = Path(sys.executable).resolve()
		exe_dir = exe_path.parent
		if exe_dir.name.lower() == 'uninstall':
			possible = exe_dir.parent
		else:
			possible = exe_dir
		if possible.name.lower() == APP_FOLDER_NAME.lower():
			return possible

	for candidate in installation_candidates():
		if candidate.exists():
			return candidate

	return default_installation_path()


def _safe_remove_path(path_item):
	current_executable = Path(sys.executable).resolve()
	try:
		if path_item.resolve() == current_executable:
			return False
	except Exception:
		pass

	if path_item.is_file() or path_item.is_symlink():
		try:
			path_item.unlink(missing_ok=True)
			return True
		except PermissionError:
			return False

	if path_item.is_dir():
		try:
			path_item.rmdir()
		except OSError:
			try:
				shutil.rmtree(path_item, ignore_errors=False)
			except PermissionError:
				return False
		return True

	return False


def _remove_windows_integrations():
	if os_name() != 'windows':
		return

	remove_windows_shortcuts(
		(
			'Passwords Manager.lnk',
			'Uninstall Passwords Manager.lnk',
		)
	)

	_delete_windows_uninstall_registry_key()


def _delete_windows_registry_tree(root, subkey):
	try:
		with winreg.OpenKey(root, subkey, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
			children = []
			index = 0
			while True:
				try:
					children.append(winreg.EnumKey(key, index))
					index += 1
				except OSError:
					break
		for child in children:
			_delete_windows_registry_tree(root, f'{subkey}\\{child}')
		winreg.DeleteKey(root, subkey)
	except FileNotFoundError:
		return


def _delete_windows_uninstall_registry_key():
	subkey = r'Software\Microsoft\Windows\CurrentVersion\Uninstall\PasswordsManager'
	_delete_windows_registry_tree(winreg.HKEY_CURRENT_USER, subkey)


def _remove_linux_integrations():
	if os_name() != 'linux':
		return

	desktop_dir = Path.home() / '.local' / 'share' / 'applications'
	(desktop_dir / 'passwords-manager.desktop').unlink(missing_ok=True)
	(desktop_dir / 'passwords-manager-uninstall.desktop').unlink(missing_ok=True)


def _remove_macos_integrations():
	if os_name() != 'macos':
		return

	apps_dir = Path.home() / 'Applications'
	(apps_dir / 'Passwords Manager.command').unlink(missing_ok=True)
	(apps_dir / 'Uninstall Passwords Manager.command').unlink(missing_ok=True)


def _remove_platform_integrations():
	_remove_windows_integrations()
	_remove_linux_integrations()
	_remove_macos_integrations()


def os_name():
	if sys.platform.startswith('win'):
		return 'windows'
	if sys.platform.startswith('linux'):
		return 'linux'
	if sys.platform == 'darwin':
		return 'macos'
	return 'other'


def _collect_removal_items(root_path):
	items = list(root_path.rglob('*'))
	items.sort(key=lambda entry: len(entry.parts), reverse=True)
	items.append(root_path)
	return items


def _schedule_windows_cleanup(root_path):
	if os_name() != 'windows':
		return False

	root = str(root_path)
	command = (
		'for /l %i in (1,1,15) do '
		f'(rmdir /s /q "{root}" && exit /b 0 || timeout /t 1 /nobreak >nul)'
	)

	try:
		subprocess.Popen(
			['cmd', '/c', command],
			creationflags=0x08000000,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
		)
		return True
	except Exception:
		pass

	# Fallback: remove at next reboot.
	try:
		MOVEFILE_DELAY_UNTIL_REBOOT = 0x4
		ctypes.windll.kernel32.MoveFileExW(str(root_path), None, MOVEFILE_DELAY_UNTIL_REBOOT)
		return True
	except Exception:
		return False


def run_uninstall(installation_path, progress_callback=None):
	root = normalize_installation_path(installation_path)

	if root.name.lower() != APP_FOLDER_NAME.lower():
		raise ValueError('Caminho de desinstalação inválido.')

	if not root.exists():
		return {'removed': 0, 'total': 0}

	items = _collect_removal_items(root)
	total = len(items)
	removed = 0
	skipped = 0

	_remove_platform_integrations()

	for index, item in enumerate(items, start=1):
		try:
			if _safe_remove_path(item):
				removed += 1
			else:
				skipped += 1
		except Exception:
			skipped += 1
		if progress_callback:
			progress_callback(index, total, str(item))

	cleanup_scheduled = False
	if skipped > 0 and root.exists() and os_name() == 'windows':
		cleanup_scheduled = _schedule_windows_cleanup(root)

	return {
		'removed': removed,
		'skipped': skipped,
		'total': total,
		'cleanup_scheduled': cleanup_scheduled,
	}
