from pathlib import Path
import shutil
import sys

APP_FOLDER_NAME = 'Passwords Manager'


def normalize_installation_path(path_value):
	path_obj = Path(path_value).expanduser()
	if path_obj.name.lower() != APP_FOLDER_NAME.lower():
		path_obj = path_obj / APP_FOLDER_NAME
	return path_obj


def default_installation_path():
	local_app_data = Path.home() / 'AppData' / 'Local'
	env_local = Path(sys.executable).parent
	if sys.platform.startswith('win'):
		from os import environ

		if environ.get('LOCALAPPDATA'):
			local_app_data = Path(environ['LOCALAPPDATA'])
	return local_app_data / APP_FOLDER_NAME


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

	return default_installation_path()


def _safe_remove_path(path_item):
	if path_item.is_file() or path_item.is_symlink():
		path_item.unlink(missing_ok=True)
		return

	if path_item.is_dir():
		try:
			path_item.rmdir()
		except OSError:
			shutil.rmtree(path_item, ignore_errors=False)


def _collect_removal_items(root_path):
	items = list(root_path.rglob('*'))
	items.sort(key=lambda entry: len(entry.parts), reverse=True)
	items.append(root_path)
	return items


def run_uninstall(installation_path, progress_callback=None):
	root = normalize_installation_path(installation_path)

	if root.name.lower() != APP_FOLDER_NAME.lower():
		raise ValueError('Caminho de desinstalação inválido.')

	if not root.exists():
		return {'removed': 0, 'total': 0}

	items = _collect_removal_items(root)
	total = len(items)
	removed = 0

	for index, item in enumerate(items, start=1):
		_safe_remove_path(item)
		removed += 1
		if progress_callback:
			progress_callback(index, total, str(item))

	return {'removed': removed, 'total': total}
