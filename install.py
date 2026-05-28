import sys

from src.lib.install import Install, run_non_interactive_install


if __name__ == '__main__':
    install_directory = None
    silent_mode = False

    for raw_argument in sys.argv[1:]:
        argument = raw_argument.strip()
        lower_argument = argument.lower()

        if lower_argument in ('/s', '--silent', '-s', '/silent'):
            silent_mode = True
            continue

        if lower_argument.startswith('/d='):
            install_directory = argument.split('=', 1)[1].strip().strip('"')
            continue

        if lower_argument.startswith('--dir='):
            install_directory = argument.split('=', 1)[1].strip().strip('"')
            continue

    if silent_mode:
        raise SystemExit(run_non_interactive_install(install_directory))

    app = Install()
    app.mainloop()
