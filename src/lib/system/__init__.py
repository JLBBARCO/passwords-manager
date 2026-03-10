import os
from tkinter import filedialog

from src.lib.external_libs import platform

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
        return "C:\\Program Files\\Passwords Manager"
    elif name == "Linux" or name == "MacOS":
        return "/usr/local/Passwords Manager"
    else:
        return "Unknown"


def select_installation_directory(initial_path=None, parent=None):
    initial_directory = initial_path or path()

    if not initial_directory or initial_directory == "Unknown":
        initial_directory = os.path.expanduser("~")

    return filedialog.askdirectory(
        initialdir=initial_directory,
        title="Select installation folder",
        parent=parent,
        mustexist=False,
    ) or None