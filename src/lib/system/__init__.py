import os
import shutil
import sys
from pathlib import Path
from tkinter import filedialog

from src.lib.external_libs import platform

APP_FOLDER_NAME = "Passwords Manager"

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

def path():
    name = nameSO()

    if name == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return os.path.join(local_app_data, APP_FOLDER_NAME)
        return os.path.join(os.path.expanduser("~"), "AppData", "Local", APP_FOLDER_NAME)
    elif name == "Linux" or name == "MacOS":
        return "/usr/local/Passwords Manager"
    else:
        return "Unknown"


def local_data_path():
    if nameSO() == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / APP_FOLDER_NAME
        return Path.home() / "AppData" / "Local" / APP_FOLDER_NAME

    if nameSO() == "Linux":
        return Path.home() / ".local" / "share" / APP_FOLDER_NAME

    if nameSO() == "MacOS":
        return Path.home() / "Library" / "Application Support" / APP_FOLDER_NAME

    return Path.cwd() / APP_FOLDER_NAME


def ensure_local_data_dir():
    data_dir = local_data_path()
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _runtime_search_paths():
    paths = [ensure_local_data_dir()]

    if getattr(sys, "frozen", False):
        paths.append(Path(sys.executable).resolve().parent)

    paths.append(Path.cwd())

    unique_paths = []
    seen = set()
    for candidate in paths:
        normalized = str(candidate.resolve())
        if normalized not in seen:
            seen.add(normalized)
            unique_paths.append(candidate)

    return unique_paths


def find_data_file(filename):
    for base_path in _runtime_search_paths():
        candidate = base_path / filename
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