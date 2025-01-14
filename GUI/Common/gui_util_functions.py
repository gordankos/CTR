import os
import sys
import enum
from enum import Enum

from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QPixmap, QColor, QFont, QIcon
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QLabel, QTreeWidget, QTreeWidgetItem


class WindowTheme(Enum):
    FUSION = "Fusion"
    LIGHT = "Light"
    DARK = "Dark"


COLOR_EDITABLE_ITEM_LIGHT: QColor = QColor(36, 63, 133, 255)
COLOR_EDITABLE_ITEM_DARK: QColor = QColor(84, 148, 218, 255)
COLOR_NON_EDITABLE_ITEM_LIGHT: QColor = QColor(0, 0, 0, 150)
COLOR_NON_EDITABLE_ITEM_DARK: QColor = QColor(0, 0, 0, 255)


FORBIDDEN_CHARACTERS: list[str] = ['"', '|', ';', '\n', '\r', '\t']


def get_window_theme(
        name: str,
        default: WindowTheme = WindowTheme.FUSION
) -> WindowTheme:
    """
    Returns the WindowTheme Enum based on the Enum name.
    """
    return WindowTheme.__members__.get(name, default)


def update_tooltip_style(theme: WindowTheme, window):
    """
    Updates window tooltip background / text color to the given theme.
    """
    if theme is WindowTheme.FUSION:
        theme_tts = "QToolTip { padding: 0; background-color: white; color: black; border: 1px solid #808080 }"
        window.setStyleSheet(theme_tts)

    elif theme is WindowTheme.LIGHT:
        theme_tts = "QToolTip { padding: 0; background-color: white; color: black; border: 1px solid #808080 }"
        window.setStyleSheet(theme_tts)

    elif theme is WindowTheme.DARK:
        theme_tts = "QToolTip { padding: 0; background-color: #464646; color: white; border: 1px solid white }"
        window.setStyleSheet(theme_tts)


def strip_forbidden_characters(string: str) -> str:
    """
    Function strips all forbidden characters from the input string.
    """
    for char in FORBIDDEN_CHARACTERS:
        string = string.replace(char, "")

    return string.strip()


def get_filepath(directory: str, filename: str) -> str:
    """
    Function returns the absolute filepath to the given file.
        In development Python environment: Path to the given directory - on desktop by default.
        In standalone application: Path to the temporary resources' folder.
    """
    if hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        filepath = os.path.join(sys._MEIPASS, filename)
    else:
        filepath = directory + filename
    return filepath


def enum_values_list(enum_type: enum.EnumType) -> list[str]:
    """
    Function returns all Enum values of the given Enum type.
    :param enum_type: Enum type.
    """
    return [enum_entry.value for enum_entry in enum_type]


def enum_index_in_enum_list(search_enum: Enum, enum_type: enum.EnumType) -> int:
    """
    Function returns the index of a searched Enum in the Enum values list.
    :param search_enum: Searched Enum object.
    :param enum_type: Enum type of the searched Enum object.
    """
    items_list = enum_values_list(enum_type)
    return items_list.index(search_enum.value)


def set_pixmap_to_label(image_directory: str, image_name: str, label: QLabel) -> None:
    """
    Function sets an image to the selected QLabel.
    :param image_directory: Image directory path.
    :param image_name: Image name.
    :param label: QLabel object.
    """
    image_filepath = get_filepath(image_directory, image_name)
    pixmap = QPixmap(image_filepath)
    label.setPixmap(pixmap)
    label.resize(pixmap.width(), pixmap.height())


def table_current_string_value(table: QTableWidget, column: int, selected_row=None) -> str:
    """
    Function returns currently selected QTableWidgetItem string value.
    """
    if selected_row is None:
        row = table.currentRow()
    else:
        row = selected_row

    table_item: QTableWidgetItem = table.item(row, column)

    if table_item is None:
        return str("")
    else:
        return table_item.text()


def table_current_integer_value(table: QTableWidget, column: int, selected_row=None) -> int | None:
    """
    Function returns currently selected QTableWidgetItem integer value.
    """
    if selected_row is None:
        row = table.currentRow()
    else:
        row = selected_row

    table_item: QTableWidgetItem = table.item(row, column)

    if table_item is None:
        return None
    else:
        return int(table_item.text())


def treewidget_get_toplevelitem(item: QTreeWidgetItem) -> QTreeWidgetItem:
    """
    Returns the top level item of the QTreeWidget of any QTreeWidgetItem.
    """
    while item.parent():
        item = item.parent()
    return item


def add_tree_widget_item(parent: QTreeWidgetItem | QTreeWidget, label: str, item_data,
                         editable: bool = False, icon: QIcon | None = None) -> QTreeWidgetItem:
    """
    Adds a new QTreeWidgetItem to the parent QTreeWidgetItem.
    :param parent: Parent QTreeWidgetItem.
    :param label: Label of the new QTreeWidgetItem in the tree widget.
    :param item_data: Data of the QTreeWidgetItem.
    :param editable: Is the QTreeWidgetItem label editable.
    :param icon: Item icon.
    """
    widget_item = QTreeWidgetItem(parent, [label])
    if editable:
        widget_item.setFlags(Qt.ItemFlag.ItemIsEnabled |
                             Qt.ItemFlag.ItemIsSelectable |
                             Qt.ItemFlag.ItemIsEditable)
    widget_item.setData(1, 0, item_data)
    if icon is not None:
        widget_item.setIcon(0, icon)
    return widget_item


def get_item_data(item: QTreeWidgetItem):
    """
    Returns the given tree widget item data.
    """
    return item.data(1, 0)


def treewidget_add_categories(tree_widget: QTreeWidget, categories: list[str]) -> None:
    """
    Function adds top level items to the tree widget geometry.
    :param tree_widget: Sections tree QTreeWidget
    :param categories: List of categories to be added.
    """
    geo_count = tree_widget.topLevelItemCount()
    local_id = geo_count - 1
    for category in categories:
        QTreeWidgetItem(tree_widget.topLevelItem(local_id), [category])


def collapse_treewidget_item(item: QTreeWidgetItem):
    """
    Recursively collapse all child items and their descendants of a QTreeWidgetItem.
    """
    if item is None:
        return
    item.setExpanded(False)
    for i in range(item.childCount()):
        child = item.child(i)
        collapse_treewidget_item(child)
        child.setExpanded(False)


def expand_treewidget_item(item: QTreeWidgetItem):
    """
    Recursively expand all child items and their descendants of a QTreeWidgetItem.
    """
    if item is None:
        return
    item.setExpanded(True)
    for i in range(item.childCount()):
        child = item.child(i)
        expand_treewidget_item(child)
        child.setExpanded(True)


def table_item_checkable(value:  float | str,
                         color: QColor | None = None,
                         background: QColor | None = None,
                         weight: QFont.Weight = QFont.Weight.Normal) -> QTableWidgetItem:
    """
    Returns a checkable, editable QTableWidgetItem.
    Sets the value under QTableWidgetItem data DisplayRole.
    """
    widget_item = QTableWidgetItem()
    widget_item.setData(Qt.ItemDataRole.DisplayRole, value)
    widget_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable |
                         Qt.ItemFlag.ItemIsEnabled |
                         Qt.ItemFlag.ItemIsSelectable |
                         Qt.ItemFlag.ItemIsEditable)
    if color is not None:
        widget_item.setForeground(color)
    if background is not None:
        widget_item.setBackground(background)
    font = widget_item.font()
    font.setWeight(weight)
    widget_item.setFont(font)
    return widget_item


def table_item_numeric_ne(value: int | float,
                          decimals: int = 2,
                          # color: QColor = QColor(0, 0, 0, 255),
                          # background: QColor = QColor(0, 0, 0, 0),
                          weight: QFont.Weight = QFont.Weight.Normal) -> QTableWidgetItem:
    """
    Returns a non-editable QTableWidgetItem for display of numeric values.
    """
    try:
        numeric_value = float(value)
    except ValueError as err:
        print(f"Encountered value error, attempted to convert value {value} to a float. {err}")
        numeric_value = 0.0

    custom_locale = QLocale.system()
    custom_locale.setNumberOptions(QLocale.NumberOption.OmitGroupSeparator)
    display_value = custom_locale.toString(numeric_value, 'f', decimals)
    # print(f"{value = }, {numeric_value = }")
    widget_item = QTableWidgetItem(display_value)
    widget_item.setFlags(Qt.ItemFlag.ItemIsEnabled |
                         Qt.ItemFlag.ItemIsSelectable)
    # widget_item.setForeground(color)
    # widget_item.setBackground(background)
    font = widget_item.font()
    font.setWeight(weight)
    widget_item.setFont(font)
    return widget_item
