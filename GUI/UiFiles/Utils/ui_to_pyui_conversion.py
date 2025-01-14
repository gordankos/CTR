"""
Utility module enabling user interface file conversion from .ui to .py in development environment

"""

from Settings.app_env import working_directory

import os
import subprocess
from pathlib import Path


uic_path = working_directory + "venv\\Scripts\\pyside6-uic.exe"
ui_directory = working_directory + "GUI\\UiFiles\\UI\\"
pyui_directory = working_directory + "GUI\\UiFiles\\PYUI\\"


def convert_working_ui_file(ui_file: str):
    """
    Function converts the given .ui file located in pyui_directory to .py.
    """
    filename = f"{Path(ui_file).stem}.py"
    command = f'"{uic_path}" "{ui_directory + ui_file}" -o "{pyui_directory + filename}"'
    subprocess.run(command, shell=True)
    print(f'Converted {ui_file} to {filename}')


def convert_ui_files(ui_files: list[str]):
    """
    Function converts the given .ui files located in pyui_directory to .py.
    """
    for ui_file in ui_files:
        filename = f"{Path(ui_file).stem}.py"
        command = f'"{uic_path}" "{ui_directory + ui_file}" -o "{pyui_directory + filename}"'
        subprocess.run(command, shell=True)
        print(f'Converted {ui_file} to {filename}')


def convert_all_ui_files():
    """
    Function converts all .ui files to .py.
    To be run after modification of .ui files in QtDesigner.
    """
    ui_files = [f for f in os.listdir(ui_directory) if f.endswith('.ui')]
    for ui_file in ui_files:
        filename = f"{Path(ui_file).stem}.py"
        command = f'"{uic_path}" "{ui_directory + ui_file}" -o "{pyui_directory + filename}"'
        subprocess.run(command, shell=True)
        print(f'Converted {ui_file} to {filename}')


if __name__ == "__main__":
    convert_all_ui_files()
