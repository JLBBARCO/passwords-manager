#!/usr/bin/env python3
"""Launch the packaged app, capture a screenshot, and fall back to a static render if needed."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from PIL import ImageGrab


def capture_screen(executable: Path, output: Path, os_name: str, delay: float) -> None:
    executable = executable.resolve()
    process = subprocess.Popen([str(executable)], cwd=str(executable.parent))
    try:
        time.sleep(delay)
        try:
            image = ImageGrab.grab(all_screens=True)
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