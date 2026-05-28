#!/usr/bin/env python3
"""Launch the packaged app, capture a screenshot, and fall back to a static render if needed."""

from __future__ import annotations

import argparse
import ctypes
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional, Tuple

from PIL import ImageGrab


WindowBox = Tuple[int, int, int, int]


def _get_foreground_window_box() -> Optional[WindowBox]:
    if sys.platform.startswith("win"):
        rect_type = ctypes.wintypes.RECT
        rect = rect_type()
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        if not hwnd:
            return None
        if not ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            return None
        if rect.right <= rect.left or rect.bottom <= rect.top:
            return None
        return (rect.left, rect.top, rect.right, rect.bottom)

    if sys.platform == "darwin":
        script = (
            'tell application "System Events" to tell (first application process whose frontmost is true) '\
            'if (count of windows) is 0 then return "" '\
            'set window_position to position of front window '\
            'set window_size to size of front window '\
            'return (item 1 of window_position) & "," & (item 2 of window_position) & "," & '\
            '(item 1 of window_size + item 1 of window_position) & "," & '\
            '(item 2 of window_size + item 2 of window_position)'
        )
        result = subprocess.run(["osascript", "-e", script], check=False, capture_output=True, text=True)
        output = result.stdout.strip()
        if not output:
            return None
        try:
            left, top, right, bottom = (int(value) for value in output.split(","))
        except ValueError:
            return None
        if right <= left or bottom <= top:
            return None
        return (left, top, right, bottom)

    return None


def capture_screen(executable: Path, output: Path, os_name: str, delay: float) -> None:
    executable = executable.resolve()
    process = subprocess.Popen([str(executable)], cwd=str(executable.parent))
    try:
        time.sleep(delay)
        try:
            window_box = _get_foreground_window_box()
            if window_box is None:
                raise RuntimeError("Unable to determine application window bounds")
            image = ImageGrab.grab(bbox=window_box)
            output.parent.mkdir(parents=True, exist_ok=True)
            image.save(output, format="WEBP", quality=92, method=6)
        except Exception:
            subprocess.run(
                [
                    sys.executable,
                    "scripts/generate_screenshots.py",
                    "--os",
                    os_name,
                    "--output",
                    str(output),
                ],
                check=True,
            )
    finally:
        try:
            process.terminate()
            process.wait(timeout=10)
        except Exception:
            process.kill()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Capture a release screenshot from the packaged app")
    parser.add_argument("--executable", required=True, help="Path to the packaged application or binary")
    parser.add_argument("--output", required=True, help="Output WEBP file path")
    parser.add_argument("--os", dest="os_name", required=True, help="OS label used by the fallback renderer")
    parser.add_argument("--delay", type=float, default=10.0, help="Seconds to wait before capturing")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    capture_screen(Path(args.executable), Path(args.output), args.os_name, args.delay)


if __name__ == "__main__":
    main()