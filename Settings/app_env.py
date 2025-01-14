from __future__ import annotations

from enum import Enum

from GUI.Common.gui_util_functions import get_filepath

import os
import sys
import subprocess
from PySide6.QtGui import QIcon


Program_Version = "0.0.0"


working_directory = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop\\CTR\\")
desktop_path = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop\\")
configs_directory = working_directory + "Config Files\\"

config_filename = "settings.ini"
default_config_filename = "default settings.ini"

config_filepath = get_filepath(configs_directory, config_filename)
default_config_filepath = get_filepath(configs_directory, default_config_filename)

light_theme_icon_path: str = ":/Light theme/"
dark_theme_icon_path: str = ":/Dark theme/"


class WindowTheme(Enum):
    FUSION = "Fusion"
    LIGHT = "Light"
    DARK = "Dark"


def get_light_icon(icon: str) -> QIcon:
    """
    Function returns a Light theme icon from the resources file.
    :param icon: Icon name including file extension.
    """
    return QIcon(f"{light_theme_icon_path}{icon}")


def get_dark_icon(icon: str) -> QIcon:
    """
    Function returns a Dark theme icon from the resources file.
    :param icon: Icon name including file extension.
    """
    return QIcon(f"{dark_theme_icon_path}{icon}")


def get_window_icon() -> QIcon:
    """
    Function returns a logo from the resources file for use in window icons.
    """
    return QIcon(f"{light_theme_icon_path}logo.png")


def get_cpu_count() -> int | None:
    """
    Method attempts to identify the number of CPUs on the system.
    """
    cpu_count = os.cpu_count()

    if cpu_count is not None:
        print(f"Identified {cpu_count} CPUs.")
        return int(cpu_count)
    else:
        print("Could not identify number of CPUs!")
        return None


def get_physical_CPU_cores() -> int | None:
    """
    Method attempts to identify the number of CPU cores on the system. Windows OS only.
    """
    try:
        result = subprocess.run(['wmic', 'cpu', 'get', 'NumberOfCores'], stdout=subprocess.PIPE, text=True)
        cores = [int(s) for s in result.stdout.split() if s.isdigit()]
        if cores:
            cpu_count = cores[0]
            print(f"Identified {cpu_count} CPU cores.")
            return cpu_count
        else:
            print("Could not identify number of CPU cores! Attempting to identify number of CPUs...")
            return get_cpu_count()

    except Exception as e:
        print(f"Raised exception getting physical cores: {e}")
        return get_cpu_count()


def get_object_size(obj, seen=None):
    """
    Recursively find the size of objects including referenced objects, bytes.
    """
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(get_object_size(k, seen) + get_object_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset)):
        size += sum(get_object_size(i, seen) for i in obj)
    elif hasattr(obj, '__dict__'):
        size += get_object_size(vars(obj), seen)
    elif hasattr(obj, '__slots__'):
        size += sum(
            get_object_size(getattr(obj, slot), seen) for slot in obj.__slots__ if hasattr(obj, slot))
    return size
