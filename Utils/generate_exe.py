"""
Utility module enabling building of a standalone executable (.exe) using PyInstaller in development environment

"""

from Settings.app_env import working_directory

import subprocess
import os


SCRIPT_NAME: str = "main.py"
OUTPUT_NAME: str = "CTR"
ICON_PATH: str = "GUI\\Icons\\logo.ico"
ONEFILE: bool = True
HIDE_CONSOLE: bool = True


def build_exe():
    os.chdir(working_directory)
    print(f"\n  📂 Changed directory to: {working_directory}")

    command: list[str] = ["pyinstaller"]

    command.append("--onefile") if ONEFILE else command.append("--onedir")
    command.extend(["--name", f"{OUTPUT_NAME}"])

    if os.path.exists(ICON_PATH):
        command.extend(["--icon", ICON_PATH])

    if HIDE_CONSOLE:
        command.append("--windowed")

    command.append(SCRIPT_NAME)

    print("Running:", " ".join(command))
    subprocess.run(command, shell=True)

    if ONEFILE:
        filepath = os.path.join("dist", f"{OUTPUT_NAME}.exe")
    else:
        filepath = os.path.join("dist", OUTPUT_NAME, f"{OUTPUT_NAME}.exe")

    if os.path.exists(filepath):
        print(f"\n  ✅ Build successful! The executable is located at: {filepath}")
    else:
        print("\n  ❌ Build failed. Check the logs above for errors.")


if __name__ == "__main__":
    build_exe()
