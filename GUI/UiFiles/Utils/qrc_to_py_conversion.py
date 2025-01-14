"""
Utility module enabling resources file conversion from .qrc to .py in development environment

"""

from Settings.app_env import working_directory

import subprocess

resources_directory = working_directory + "GUI\\Icons\\"
venv_path = working_directory + "venv\\Scripts\\pyside6-rcc"


def convert_resources_file(qrc_filename: str, py_filename: str) -> None:
    """
    Function converts the given .qrc file to .py.
    """
    command = f'"{venv_path}" "{resources_directory + qrc_filename}" -o "{resources_directory + py_filename}"'
    subprocess.run(command, shell=True)

    print(f'Converted {qrc_filename} to {py_filename}')


if __name__ == "__main__":
    convert_resources_file(
        qrc_filename="resources_file.qrc",
        py_filename="resources.py"
    )
