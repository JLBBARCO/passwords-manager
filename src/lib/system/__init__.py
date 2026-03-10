import platform

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