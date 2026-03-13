import os
import platform
import shutil
import sys
from pathlib import Path
from tkinter import filedialog

APP_FOLDER_NAME = "Passwords Manager"
WINDOWS_INSTALL_ROOT = Path("C:/File Programs")
DATA_FILENAMES = (
    "passwords.json",
    "encryption.key",
    "passwords_backup.json",
    "passwords_backup_unencrypted.json",
    "passwords.csv",
)
DATA_FILE_ALIASES = {
    "passwords.json": ("passwords.json",),
    "encryption.key": ("encryption.key", "encrypton.key"),
    "passwords_backup.json": ("passwords_backup.json",),
    "passwords_backup_unencrypted.json": ("passwords_backup_unencrypted.json",),
    "passwords.csv": ("passwords.csv",),
}


def nameSO():
    system = platform.system()

    if system == "Windows":
        return "Windows"
    elif system == "Darwin":
        return "MacOS"
    elif system == "Linux":
        return "Linux"
    else:
        return "Unknown"


def _unique_paths(paths):
    unique_paths = []
    seen = set()
    for candidate in paths:
        normalized = str(candidate)
        if normalized not in seen:
            seen.add(normalized)
            unique_paths.append(candidate)
    return unique_paths


def path():
    name = nameSO()

    if name == "Windows":
        return str(WINDOWS_INSTALL_ROOT / APP_FOLDER_NAME)
    elif name == "Linux" or name == "MacOS":
        return "/usr/local/Passwords Manager"
    else:
        return "Unknown"


def local_data_path():
    if nameSO() == "Windows":
        roaming_app_data = os.environ.get("APPDATA")
        if roaming_app_data:
            return Path(roaming_app_data) / APP_FOLDER_NAME
        return Path.home() / "AppData" / "Roaming" / APP_FOLDER_NAME

    if nameSO() == "Linux":
        return Path.home() / ".local" / "share" / APP_FOLDER_NAME

    if nameSO() == "MacOS":
        return Path.home() / "Library" / "Application Support" / APP_FOLDER_NAME

    return Path.cwd() / APP_FOLDER_NAME


def legacy_local_data_path():
    if nameSO() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / APP_FOLDER_NAME
        return Path.home() / "AppData" / "Local" / APP_FOLDER_NAME

    return local_data_path()


def compatibility_data_paths():
    return _unique_paths([local_data_path(), legacy_local_data_path()])


def compatibility_installation_paths():
    return _unique_paths([Path(path()), legacy_local_data_path()])


def ensure_local_data_dir():
    data_dir = local_data_path()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _runtime_search_paths():
    paths = list(compatibility_data_paths())

    if getattr(sys, "frozen", False):
        paths.append(Path(sys.executable).resolve().parent)

    paths.append(Path.cwd())
    return _unique_paths(paths)


def find_data_file(filename):
    aliases = DATA_FILE_ALIASES.get(filename, (filename,))
    for base_path in _runtime_search_paths():
        for alias in aliases:
            candidate = base_path / alias
            if candidate.exists():
                return candidate
    return ensure_local_data_dir() / filename


def prepare_local_data_file(filename):
    local_file = ensure_local_data_dir() / filename
    if local_file.exists():
        return local_file

    source_file = find_data_file(filename)
    if source_file.exists() and source_file.resolve() != local_file.resolve():
        shutil.copy2(source_file, local_file)

    return local_file


def migrate_legacy_data_files(filenames=None):
    destination_dir = ensure_local_data_dir()
    filenames = tuple(filenames or DATA_FILENAMES)

    migrated_files = []
    skipped_files = []
    skipped_seen = set()

    for source_dir in compatibility_data_paths()[1:]:
        if not source_dir.exists():
            continue

        try:
            if source_dir.resolve() == destination_dir.resolve():
                continue
        except Exception:
            pass

        for filename in filenames:
            destination_file = destination_dir / filename
            if destination_file.exists():
                destination_text = str(destination_file)
                if destination_text not in skipped_seen:
                    skipped_files.append(destination_text)
                    skipped_seen.add(destination_text)
                continue

            source_file = None
            for alias in DATA_FILE_ALIASES.get(filename, (filename,)):
                candidate = source_dir / alias
                if candidate.exists():
                    source_file = candidate
                    break

            if not source_file:
                continue

            destination_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination_file)
            migrated_files.append(str(destination_file))

    return migrated_files, skipped_files


def select_installation_directory(initial_path=None, parent=None):
    initial_directory = initial_path or path()

    if not initial_directory or initial_directory == "Unknown":
        initial_directory = os.path.expanduser("~")

    return filedialog.askdirectory(
        initialdir=initial_directory,
        title="Selecionar pasta de instalação",
        parent=parent,
        mustexist=False,
    ) or None