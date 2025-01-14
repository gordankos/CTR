

import json
from enum import Enum
from datetime import datetime
from dataclasses import fields
from typing import Type, TypeVar
from PySide6.QtGui import QColor
from Settings.app_env import Program_Version


DataclassType = TypeVar("DataclassType")


def get_numeric_program_version(program_version: str, default_value: float = 0.0) -> float:
    """
    Returns the numeric representation of the given program version.

    :param program_version: Program version (format int.int.int), str.
    :param default_value: Default program version numeric representation.
    """
    split_string = program_version.split(".")
    joined_numr = split_string[0] + "." + "".join(split_string[1:])

    try:
        return float(joined_numr)

    except ValueError:
        return default_value


def get_current_program_version() -> float:
    """
    Returns the numeric representation of the current program version.
    """
    split_string = Program_Version.split(".")
    joined_numr = split_string[0] + "." + "".join(split_string[1:])
    return float(joined_numr)


def get_program_version(csv_file: list[str], version_index: int = 1) -> float:
    """
    Method returns the numeric program version used to save the given csv savefile.
    :param csv_file: Program savefile.
    :param version_index: Index of program version within the savefile. Default = 1 for the standard savefile header.
    """
    line = csv_file[version_index].strip()
    return get_numeric_program_version(line.strip("Version: "))


def savefile_header(savefile_type: str = "", program_version: str = "0.0.0") -> str:
    """
    Returns the header for program savefiles, containing savefile type,
    modification warning, program version, save date and time.

    String data type, with 4 lines total.
    """
    return (f"CTR {savefile_type} savefile. "
            f"Warning: Do not manually edit or modify this file. "
            f"Incorrect data structure may lead to unexpected errors.\n"
            f"Version: {program_version} \n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


def convert_to_color_at_index(split_line: list, index: int, default_value=QColor(0, 0, 0, 255)) -> QColor:
    """
    Function returns a QColor from the split line list containing RGBA values at the given index.
    Returns the default value when attempting to convert a value at an index that is not contained in the list.

    :param split_line: CSV savefile line.
    :param index: Index in the CSV savefile line.
    :param default_value: Default return value, black (RGBA = 0, 0, 0, 255).
    """
    if index >= len(split_line):
        return default_value

    else:
        try:
            rgba_list = split_line[index].strip("\n").strip("[]").split(", ")
            return QColor(*[int(val) for val in rgba_list])

        except ValueError:
            return default_value

        except TypeError:
            return default_value


def convert_to_str_at_index(split_line: list, index: int, default_value=None) -> str:
    """
    Function returns the string value in the split line list at the given index.
    Returns the default value when attempting to convert a value at an index that is not
    contained in the list.

    :param split_line: CSV savefile line.
    :param index: Index in the CSV savefile line.
    :param default_value: Default return value.
    """
    if index >= len(split_line):
        return default_value

    else:
        try:
            return split_line[index].strip()

        except ValueError:
            return default_value


def convert_to_int_at_index(split_line: list, index: int, default_value=None) -> int:
    """
    Function returns the numeric value in the split line list at the given index as an integer.
    Returns the default value when attempting to convert a value at an index that is not
    contained in the list or fails to convert to an integer.
    Strips the newline character "\n" in case the given index is located at the end of the split line.

    :param split_line: CSV savefile line.
    :param index: Index in the CSV savefile line.
    :param default_value: Default return value.
    """
    if index >= len(split_line):
        return default_value

    else:
        try:
            return int(split_line[index].strip())

        except ValueError:
            # value = split_line[index].strip("\n")
            # print(f"Attempted to convert savefile line {split_line}\n"
            #       f" Value {value} {type(value)} At index {index} to a int.\n"
            #       f" Returning the default value {default_value} {type(default_value)}")
            return default_value


def convert_to_bool_at_index(split_line: list, index: int, default_value: bool = False) -> bool:
    """
    Function converts a string boolean representation into a boolean type.
    """
    if index >= len(split_line):
        return default_value

    else:
        try:
            string = split_line[index].strip()

            if string == "True":
                return True
            elif string == "False":
                return False
            else:
                return default_value

        except ValueError:
            return default_value


def convert_to_float_at_index(split_line: list, index: int, default_value=None) -> float:
    """
    Function returns the numeric value in the split line list at the given index as a float.
    Returns the default value when attempting to convert a value at an index that is not
    contained in the list or fails to convert to a floating point number.
    Strips the newline character "\n" in case the given index is located at the end of the split line.

    :param split_line: CSV savefile line.
    :param index: Index in the CSV savefile line.
    :param default_value: Default return value.
    """
    if index >= len(split_line):
        return default_value

    else:
        try:
            return float(split_line[index].strip())

        except ValueError:
            # value = split_line[index].strip("\n")
            # print(f"Attempted to convert savefile line {split_line}\n"
            #       f" Value {value} {type(value)} At index {index} to a float.\n"
            #       f" Returning the default value {default_value} {type(default_value)}")
            return default_value


def convert_to_dict_at_index(split_line: list, index: int, default_value=None) -> dict:
    """
    Function returns the dictionary from the split line list at the given index.
    Returns the default value when attempting to convert a value at an index that is not
    contained in the list or fails to convert using the json loads method.
    Strips the newline character "\n" in case the given index is located at the end of the split line.

    :param split_line: CSV savefile line.
    :param index: Index in the CSV savefile line.
    :param default_value: Default return value.
    """
    if index >= len(split_line):
        return default_value

    else:
        try:
            return json.loads(split_line[index].strip())

        except ValueError:
            return default_value


def convert_string_to_list(string: str) -> list[float]:
    """
    Function converts a list string representation into a list containing floating point numbers.
    Note: use .strip() on the input string in case the list string representation is the last
        item in the CSV line, due to "\n" characters for switching to a new line.
    """
    string = string.strip("[]").split(", ")
    try:
        converted_list = [float(i) for i in string]
        return converted_list
    except ValueError:
        return []


def dataclass_to_dict(obj: DataclassType) -> dict:
    """
    Converts a dataclass to a dictionary for conversion to json.
    Handles only basic data types (int, str, float, Enum).
    """
    result = {}
    for field in fields(obj):
        value = getattr(obj, field.name)
        result[field.name] = value.name if isinstance(value, Enum) else value
    return result


def dict_to_dataclass(dataclass: Type[DataclassType], data: dict) -> DataclassType:
    """
    Converts a dictionary to a given dataclass.
    Handles only basic data types (int, str, float, Enum).
    """
    init_args = {}
    for field in fields(dataclass):
        field_type = field.type
        value = data.get(field.name, None)
        if value is None:
            continue

        if issubclass(field_type, Enum):
            init_args[field.name] = field_type[value]
        else:
            init_args[field.name] = value

    return dataclass(**init_args)
