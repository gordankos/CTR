
import enum

from GUI.Common.gui_util_functions import COLOR_EDITABLE_ITEM_DARK
from Settings.app_env import get_light_icon

from PySide6.QtCore import (Qt, QEvent, QLocale, QModelIndex, QPropertyAnimation, QEasingCurve, QSortFilterProxyModel,
                            QRect, QAbstractTableModel, Signal, QPoint, QObject)
from PySide6.QtGui import QFontMetrics, QStandardItem, QKeySequence, QColor, QBrush, QFont, QAction
from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QComboBox, QHeaderView, QDoubleSpinBox,
                               QStyledItemDelegate, QApplication, QWidget, QVBoxLayout, QToolButton,
                               QLabel, QHBoxLayout, QPushButton, QSpinBox, QAbstractSpinBox, QFrame,
                               QCheckBox, QLineEdit, QCompleter, QStyle,
                               QStyleOptionComboBox, QScrollArea, QMenu, QWidgetAction, QListWidget, QTextEdit,
                               QAbstractItemDelegate, QCalendarWidget)

from typing import Any
from enum import Enum
from collections.abc import Callable


class ScrollableMenu(QWidget):
    def __init__(self, parent=None, menu: QMenu | None = None,
                 max_height: int = 200, min_width: int = 150):
        super().__init__(parent)
        self.menu = menu
        self.max_height = max_height
        self.min_width = min_width

        self.layout = QVBoxLayout(self)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setFrameShadow(QFrame.Shadow.Plain)
        self.scroll_area.setLineWidth(0)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(0)
        self.content_layout.setContentsMargins(9, 0, 9, 0)

        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setMinimumWidth(self.min_width)
        self.scroll_area.setMaximumHeight(self.max_height)

        self.layout.addWidget(self.scroll_area)

    def add_action(self, action: QAction):
        """
        Adds an action to the scrollable menu by creating a QPushButton.
        """
        button = QPushButton(action.text(), self)
        button.setMinimumHeight(25)
        button.setFlat(True)
        button.clicked.connect(self.on_menu_close)
        button.clicked.connect(action.trigger)
        self.content_layout.addWidget(button)

    def on_menu_close(self):
        if self.menu is not None:
            self.menu.close()


def add_scrollable_submenu(menu: QMenu, submenu_title: str, options: list[str],
                           on_selection: Callable[[int], None], parent=None,
                           menu_top_title: str | None = None):
    submenu = menu.addMenu(submenu_title)
    submenu_widget = ScrollableMenu(parent, menu=menu)

    if menu_top_title is not None:
        submenu_label = submenu.addAction(menu_top_title)
        submenu_label.setEnabled(False)

    for index, option in enumerate(options):
        action = QAction(f"{option}", parent)
        action.triggered.connect(lambda _=None, i=index: on_selection(i))
        submenu_widget.add_action(action)

    submenu_widget_action = QWidgetAction(submenu)
    submenu_widget_action.setDefaultWidget(submenu_widget)
    submenu.addAction(submenu_widget_action)

    menu.addMenu(submenu)


class CustomTextEdit(QTextEdit):
    editingFinished = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.editingFinished.emit()


class CheckableComboBox(QComboBox):
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.setItemDelegate(CheckableComboBox.Delegate())
        # noinspection PyUnresolvedReferences
        self.model().dataChanged.connect(self.update_text)
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False
        # self.setMinimumSize(0, 25)
        self.last_selected_index: int | None = None

        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        self.update_text()
        super().resizeEvent(event)

    def eventFilter(self, object, event):
        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonPress:
                return True
            return False

        elif object == self.view().viewport():
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:

                if QApplication.keyboardModifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.select_all()
                    return True

                elif QApplication.keyboardModifiers() == Qt.KeyboardModifier.AltModifier:
                    selected_index = self.view().indexAt(event.pos())
                    self.select_range(last_selected=self.last_selected_index,
                                      currently_selected=selected_index.row())
                    return True

                else:
                    selected_index = self.view().indexAt(event.pos())
                    selected_item = self.model().item(selected_index.row())
                    self.last_selected_index = selected_index.row()

                    if selected_item.checkState() == Qt.CheckState.Checked:
                        selected_item.setCheckState(Qt.CheckState.Unchecked)
                    else:
                        selected_item.setCheckState(Qt.CheckState.Checked)
                    return True

            elif event.type() == QEvent.MouseButtonPress and event.button() == Qt.RightButton:
                selected_index = self.view().indexAt(event.pos())
                selected_item = self.model().item(selected_index.row())
                self.last_selected_index = selected_index.row()

                self.unselect_all()
                selected_item.setCheckState(Qt.CheckState.Checked)

        return False

    def select_range(self, last_selected: int, currently_selected: int):
        if last_selected is None or currently_selected is None:
            return
        min_index, max_index = sorted([last_selected, currently_selected])

        for index in range(min_index, max_index + 1):
            item = self.model().item(index)
            item.setCheckState(Qt.CheckState.Checked)

    def select_all(self):
        for index in range(self.count()):
            item = self.model().item(index)
            item.setCheckState(Qt.CheckState.Checked)

    def unselect_all(self):
        for index in range(self.count()):
            item = self.model().item(index)
            item.setCheckState(Qt.CheckState.Unchecked)

    def select_item_at_index(self, index: int):
        selected_item = self.model().item(index)
        selected_item.setCheckState(Qt.CheckState.Checked)

    def update_text(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        metrics = QFontMetrics(self.lineEdit().font())

        elidedText = metrics.elidedText(text, Qt.TextElideMode.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def add_item(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable)
        item.setData(Qt.CheckState.Unchecked, Qt.ItemDataRole.CheckStateRole)
        self.model().appendRow(item)

    def current_data(self):
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.CheckState.Checked:
                res.append(self.model().item(i).data())
        return res


class SearchableComboBox(QComboBox):
    def __init__(self, parent=None):
        super(SearchableComboBox, self).__init__(parent)

        self.item_identifier: int | None = None

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setEditable(True)

        self.filter_model = QSortFilterProxyModel(self)
        self.filter_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.filter_model.setSourceModel(self.model())

        self.completer = QCompleter(self.filter_model, self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.setCompleter(self.completer)

        self.lineEdit().textEdited.connect(self.filter_model.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)

    def set_colors(self, text: QColor, background: QColor):
        self.setStyleSheet(f"QComboBox {{"
                           f" background-color: {background.name()};"
                           f" color: {text.name()}; }}")

    def set_background_color(self, color: QColor | None):
        if color is not None:
            self.setStyleSheet(f"QComboBox {{ background-color: {color.name()}; }}")

    def set_text_color(self, color: QColor | None):
        if color is not None:
            current_style = self.styleSheet()
            settings = f"QComboBox {{ color: {color.name()}; }}"
            self.setStyleSheet(current_style + settings)

    def on_completer_activated(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)

    def setModel(self, model):
        super(SearchableComboBox, self).setModel(model)
        self.filter_model.setSourceModel(model)
        self.completer.setModel(self.filter_model)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.filter_model.setFilterKeyColumn(column)
        super(SearchableComboBox, self).setModelColumn(column)

    def wheelEvent(self, event):
        # if not self.rect().contains(event.position().toPoint()):
        #     print("Mouse is not over the custom QComboBox being modified, ignoring mouse wheel event...")
        #     event.ignore()
        if not self.hasFocus():
            event.ignore()
        else:
            super().wheelEvent(event)


class ComboBoxEnumDropdown(QComboBox):
    def __init__(self, parent, enum_object):
        """
        :param parent: Parent PyQt window.
        :param enum_object: Enum object.
        """
        super().__init__(parent)
        self.parent = parent
        self.enum_object = enum_object

        self.setup_items()
        self.set_alignment()

    # def update_combobox_value(self):
    #     current_text = self.currentText()
    #     self.parent.update_combobox_value(current_text)

    def setup_items(self):
        for entry in self.enum_object:
            self.addItem(entry.value, userData=entry)

    # color_function: Callable[[Enum], QColor] | None = None
    # def setup_color_items(self):
    #     model = self.model()
    #     for row, entry in enumerate(self.enum_object):
    #         self.addItem(entry.value, userData=entry)
    #         color = self.color_function(entry)
    #         print(f"Setting Color {color} for Enum {entry}")
    #         model.setData(model.index(row, 0), color, Qt.ItemDataRole.DisplayRole)

    def set_alignment(self):
        self.setEditable(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.lineEdit().setReadOnly(True)


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, data: dict[Any, str],
                 parent: QTableWidget | None = None,
                 alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignCenter):
        super().__init__(parent)
        self.data = data
        self.alignment = alignment

    def createEditor(self, parent, option, index):
        cbox = QComboBox(parent)
        for key, value in self.data.items():
            cbox.addItem(value, userData=key)
        cbox.setEditable(False)

        parent: QTableWidget = self.parent()
        rect: QRect = parent.visualRect(index)
        geo_width = parent.horizontalHeader().geometry().width()
        # print(f"Setting maximum width to {geo_width-rect.left()}, header_width = {geo_width}")
        cbox.setMaximumWidth(geo_width - rect.left())

        return cbox

    def setEditorData(self, editor: QComboBox, index: QModelIndex):
        user_data = index.data(Qt.ItemDataRole.UserRole)
        if user_data is not None:
            keys = list(self.data.keys())
            if user_data in keys:
                editor.setCurrentIndex(keys.index(user_data))
            else:
                print(f"Warning: Combobox editor item user data is not none but index is unknown, setting index 0")
                editor.setCurrentIndex(0)
        else:
            value = index.data()
            print(f"Warning: Combobox editor item user data is None, setting text value {value}")
            editor.setCurrentText(value)

        editor.setEditable(True)
        editor.lineEdit().setAlignment(self.alignment)
        editor.lineEdit().setReadOnly(True)
        editor.showPopup()

    def setModelData(self, editor: QComboBox, model: QAbstractTableModel, index: QModelIndex):
        data = editor.itemData(editor.currentIndex())
        displayed_text = editor.currentText()

        self.parent().blockSignals(True)
        model.setData(index, data, Qt.ItemDataRole.UserRole)
        self.parent().blockSignals(False)
        model.setData(index, displayed_text, Qt.ItemDataRole.DisplayRole)

    # def editorEvent(self, event, model, option, index: QModelIndex):
    #     """
    #     Handle mouse clicks to trigger the dropdown for the combo box.
    #     """
    #     if event.type() == QMouseEvent.Type.MouseButtonRelease:
    #         arrow_rect = QRect(option.rect.right() - 20, option.rect.top(), 20, option.rect.height())
    #         if arrow_rect.contains(event.pos()):
    #             print(f"Click detected in the dropdown menu arrow area... {index = } {index.row() = } WIP...")
    #             editor = self.createEditor(self.parent(), option, index)
    #             editor.setGeometry(option.rect)
    #             self.setEditorData(editor, index)
    #
    #             def on_item_selected(cbox_index):
    #                 print(f"Item activated {index}")
    #                 # Emit commitData when an item is selected
    #                 self.setModelData(editor, model, index)
    #
    #             editor.activated.connect(on_item_selected)
    #
    #             return True
    #     return super().editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        combo_option = QStyleOptionComboBox()
        arrow_width = 24
        combo_option.rect = QRect(option.rect.right() - arrow_width, option.rect.top(), arrow_width, option.rect.height())
        combo_option.rect.moveRight(option.rect.right()-0.5)
        combo_option.rect.moveTop(option.rect.top() + (option.rect.height() - combo_option.rect.height()) // 2)
        QApplication.style().drawComplexControl(QStyle.ComplexControl.CC_ComboBox, combo_option, painter)


class ComboBoxDropdown(QComboBox):
    def __init__(self, parent, data: dict):
        """
        :param parent: Parent PyQt window.
        :param data: Data for the combobox label (value) and data (key).
        """
        super().__init__(parent)
        self.parent = parent
        self.data = data

        self.setup_items()
        self.set_alignment()

    def setup_items(self):
        for key, value in self.data.items():
            self.addItem(str(value), userData=key)

    def set_alignment(self):
        self.setEditable(True)
        self.lineEdit().setAlignment(Qt.AlignCenter)
        self.lineEdit().setReadOnly(True)


class NoStepDoubleSpinBox(QDoubleSpinBox):
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key.Key_Up, Qt.Key.Key_Down]:
            event.ignore()
        else:
            super().keyPressEvent(event)


class AutoCompleteDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        column = index.column()
        unique_items = set()
        for row in range(self.parent.rowCount()):
            item = self.parent.item(row, column)
            if item:
                unique_items.add(item.text())

        completer = QCompleter(list(unique_items), parent)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        editor.setCompleter(completer)

        editor.editingFinished.connect(lambda: self.commitData.emit(editor))
        editor.editingFinished.connect(lambda: self.closeEditor.emit(editor,
                                                                     QAbstractItemDelegate.EndEditHint.NoHint))

        return editor

    def setEditorData(self, editor, index):
        if isinstance(editor, QLineEdit):
            text = index.data(Qt.ItemDataRole.EditRole) or ""
            editor.setText(str(text))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), Qt.ItemDataRole.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class DoubleSpinBoxDelegate(QStyledItemDelegate):
    def __init__(self, parent=None,
                 max_val: float = 500000,
                 min_val: float = -500000,
                 decimals: int = 2,
                 val_step: float = 0.0,
                 decimals_display: int = 2):
        super().__init__(parent)
        self.max_val = max_val
        self.min_val = min_val
        self.decimals = decimals
        self.val_step = val_step
        self.decimals_display = decimals_display

    def setEditorData(self, editor: NoStepDoubleSpinBox, index: QModelIndex):
        """
        Method sets the current table widget item data in the custom QDoubleSpinBox editor.
        """
        value = index.model().data(index, Qt.ItemDataRole.EditRole)
        if value is not None:
            try:
                editor.setValue(float(value))
            except ValueError:
                print(f"Raised ValueError converting value to float in NoStepDoubleSpinBox editor: {value = }. "
                      f"Setting editor value to 0.0.")
                editor.setValue(0.0)
        else:
            print("Received None value in NoStepDoubleSpinBox editor data. "
                  "Setting editor value to 0.0.")
            editor.setValue(0.0)

    def createEditor(self, parent, option, index):
        editor = NoStepDoubleSpinBox(parent)
        editor.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
        editor.setDecimals(self.decimals)
        editor.setMinimum(self.min_val)
        editor.setMaximum(self.max_val)
        editor.setSingleStep(self.val_step)
        editor.editingFinished.connect(lambda: self.commitData.emit(editor))
        editor.editingFinished.connect(lambda: self.closeEditor.emit(editor,
                                                                     QAbstractItemDelegate.EndEditHint.NoHint))

        return editor

    def displayText(self, value, locale):
        if isinstance(value, str):
            return value
        try:
            number = float(value)
            locale = QLocale.system()
            locale.setNumberOptions(QLocale.NumberOption.OmitGroupSeparator)
            formatted_number = locale.toString(number, 'f', self.decimals_display)
            return formatted_number
        except ValueError:
            print(f"Raised value error in double spin box delegate on conversion to float, {value = }")
            return value


class CheckableComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, data: Callable[[], dict[int, str]], parent=None,
                 on_data_change: Callable[[], None] | None = None):
        """
        Custom checkable combobox delegate, supports dynamic data change by implementing
        callable functions for retrieving dropdown menu data.

        :param parent: Parent widget, QTableWidget.
        :param data: Callable function that returns the checkable combobox data in the form of a dictionary.
        """
        super().__init__(parent)
        self.data = data
        self.on_data_change = on_data_change

    def createEditor(self, parent, option, index):
        editor = CheckableComboBox(parent)
        for key, value in self.data().items():
            editor.add_item(value, data=key)
        editor.model().dataChanged.connect(self.on_data_change)
        return editor

    def setEditorData(self, editor, index):
        if isinstance(editor, CheckableComboBox):
            editor.model().dataChanged.disconnect(self.on_data_change)

            data = index.data(Qt.EditRole)
            if data:
                selected_items = data.split(", ")
                for i in range(editor.model().rowCount()):
                    item = editor.model().item(i)

                    if item.text() in selected_items:
                        item.setCheckState(Qt.CheckState.Checked)
                    else:
                        item.setCheckState(Qt.CheckState.Unchecked)

            editor.model().dataChanged.connect(self.on_data_change)

    def setModelData(self, editor, model, index):
        if isinstance(editor, CheckableComboBox):
            identifiers_list = list(self.data().values())
            selected_data = ", ".join(identifiers_list)
            model.setData(index, selected_data, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, parent=None, identifier_id: int = 0, identifier_type: Any = None):
        """
        :param parent: Parent PyQt window.
        :param identifier_id: Unique object identifier associated with the table widget item.
        """
        super().__init__(parent)
        self.parent = parent
        self.identifier_id = identifier_id
        self.identifier_type = identifier_type


class CustomDataTable(QTableWidget):
    def __init__(self, parent):
        """
        Custom QTableWidget subclass enabling common functionality of filling rows,
        moving rows up/down inside the table, setting item alignments and other
        common settings across all input tables.
        """
        super().__init__(parent)
        self.parent = parent

        # locale = QLocale(QLocale.Language.Croatian, QLocale.Country.Croatia)
        # QLocale.setDefault(locale)
        # self.setLocale(locale)
        self.numeric_input_columns: list[int] = []
        self.non_numeric_input_columns: list[int] = []
        self.numeric_display_columns: list[int] = []

        self.item_selected_signal_connected: bool = False
        self.item_changed_signal_connected: bool = False

        self.selected_table_row: int | None = None          # For use on right click only!
        self.selected_table_column: int | None = None       # For use on right click only!

        self._on_lmb_press_event_method = None
        self._on_rmb_press_event_method = None

        self._scroll_bar_position: int = 0

    def set_headers(self, column_headers: list[tuple[str, int]]):
        """
        Sets the header labels and column widths. Adds column index to data of each header QTableWidgetItem.
        :param column_headers: List of header names (str) and column widths (int).
        """
        self.setColumnCount(len(column_headers))
        for index, data in enumerate(column_headers):
            name, col_width = data
            self.setColumnWidth(int(index), int(col_width))
            header_item = QTableWidgetItem(str(name))
            # header_item.setData(Qt.ItemDataRole.UserRole, index)
            self.setHorizontalHeaderItem(int(index), header_item)

    def set_headers_specified(self, column_header_data: list[tuple[str, int, int]]):
        """
        Sets the header labels and column widths for the specified column index.
        :param column_header_data: List of header names (str), column widths (int) and column indicies (int).
        """
        self.setColumnCount(len(column_header_data))
        for data in column_header_data:
            name, col_width, col_index = data
            self.setColumnWidth(int(col_index), int(col_width))
            header_item = QTableWidgetItem(str(name))
            self.setHorizontalHeaderItem(int(col_index), header_item)

    def set_header_settings(self, height: int = 30, show_vertical_header: bool = False):
        """
        Sets the minimum header height and hides the vertical header.
        """
        self.horizontalHeader().setMinimumHeight(height)
        self.verticalHeader().setVisible(show_vertical_header)

    def set_column_widths(self, widths: list):
        """
        Sets table column widths.
        """
        for column in range(0, self.columnCount()):
            self.setColumnWidth(column, widths[column])

    def set_column_non_editable(self, column_index: int) -> None:
        """
        Method sets all table widget items in the given column as non-editable.
        """
        for row in range(self.rowCount()):
            item = self.item(row, column_index)
            if item is None:
                item = QTableWidgetItem()
                self.setItem(row, column_index, item)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)

    def resize_to_fit(self):
        """
        Sets table column widths to fit contents.
        """
        for column in range(0, self.columnCount()):
            self.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.ResizeToContents)

    def set_row_center_alignment(self, row):
        """
        Sets the given row QTableWidgetItems alignment to center.
        """
        for column in range(0, self.columnCount()):
            item = self.item(row, column)
            if item is not None:
                item.setTextAlignment(Qt.AlignCenter)

    @staticmethod
    def table_data_dictionary(values: list):
        """
        Returns a dictionary of numeric QTableWidgetItems for adding to the table row.
        Setting of data DisplayRole to each item allows for column sorting by value.
        """
        data_dict = {}
        for index, value in enumerate(values):
            item = QTableWidgetItem()

            if str(value).replace(".", "").replace("-", "").isnumeric():
                item.setData(Qt.ItemDataRole.DisplayRole, float(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            else:
                item.setData(Qt.ItemDataRole.DisplayRole, str(value))
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

            data_dict[index] = item
        return data_dict

    def add_table_row(self, row_items: dict, new_row=None):
        """
        Adds a new table row to the custom data table.
        :param row_items:
        :param new_row:
        :return:
        """
        if new_row is None:
            row_count = self.rowCount()
            self.setRowCount(row_count + 1)
            row = row_count
        else:
            row = new_row

        for index, item in row_items.items():
            if isinstance(item, QTableWidgetItem):
                self.setItem(row, index, item)
            else:
                self.setCellWidget(row, index, item)

        self.set_row_center_alignment(row)

    def update_table_row(self, row: int, row_items: dict):
        """
        Updates the custom data table row with new data.
        """
        for index, item in row_items.items():
            if isinstance(item, QTableWidgetItem):
                self.setItem(row, index, item)
                self.set_row_center_alignment(row)
            else:
                self.setCellWidget(row, index, item)

    def set_item_changed_signal(self, connection_status: bool, on_changed):
        """
        Method connects the on_item_changed method to item changed signal of the table.
        """
        if connection_status and not self.item_changed_signal_connected:
            self.itemChanged.connect(on_changed)
            self.item_changed_signal_connected = True

        elif not connection_status and self.item_changed_signal_connected:
            self.itemChanged.disconnect(on_changed)
            self.item_changed_signal_connected = False

    def set_item_selection_signal(self, connection_status: bool, on_select):
        """
        Method connects the on_item_changed method to item changed signal of the table.
        """
        if connection_status and not self.item_selected_signal_connected:
            # noinspection PyUnresolvedReferences
            self.selectionModel().selectionChanged.connect(on_select)
            self.item_selected_signal_connected = True

        elif not connection_status and self.item_selected_signal_connected:
            # noinspection PyUnresolvedReferences
            self.selectionModel().selectionChanged.disconnect(on_select)
            self.item_selected_signal_connected = False

    def move_table_row_up(self, row_items: dict):
        """
        Moves the selected row to the row above.
        """
        row = self.selected_table_row

        if row == 0:
            pass

        else:
            self.insertRow(row - 1)
            self.add_table_row(row_items, new_row=row - 1)
            self.removeRow(row + 1)

    def move_table_row_down(self, row_items: dict):
        """
        Moves the selected row to the row below.
        """
        row = self.selected_table_row

        if row == self.rowCount() - 1:
            pass

        else:
            self.insertRow(row + 2)
            self.add_table_row(row_items, new_row=row + 2)
            self.removeRow(row)

    def show_all_columns(self):
        """
        Shows all columns of the data table.
        """
        for column in range(0, self.columnCount()):
            self.showColumn(column)

    def get_item_value(self, row: int, column: int) -> str | int | float | Enum:
        """
        Method returns the value of a QTableWidgetItem at the selected table row and column index,
        stored under the item data DisplayRole.
        :param row: Row index.
        :param column: Column index.
        """
        return self.item(row, column).data(Qt.ItemDataRole.DisplayRole)

    def get_row_from_value(self, value, column: int):
        """
        Returns the custom data table row index of the given value in the given column.
        """
        for row in range(0, self.rowCount()):
            table_item: QTableWidgetItem = self.item(row, column)
            if str(value) == table_item.text():
                return row

    def get_current_numeric_value(self, row: int, column: int) -> float | None:
        """
        Function returns the numeric value of a QTableWidgetItem at the selected row and column index.
        If the field value is a empty string, method returns None.
        :param row: Row index.
        :param column: Column index.
        """
        table_item: QTableWidgetItem = self.item(row, column)

        if table_item is not None:
            item_value = table_item.text()

            if item_value == "":
                return None
            else:
                return float(item_value)

        else:
            return None

    def get_current_string_value(self, column: int, selected_row=None) -> str:
        """
        Returns the currently selected QTableWidgetItem string value.
        """
        if selected_row is None:
            row = self.currentRow()
        else:
            row = selected_row

        table_item: QTableWidgetItem = self.item(row, column)

        if table_item is None:
            return str("")
        else:
            return table_item.text()

    def get_current_integer_value(self, column: int, selected_row: int | None = None,
                                  default: int | None = None) -> int | None:
        """
        Returns the currently selected QTableWidgetItem integer value.
        """
        if selected_row is None:
            row = self.currentRow()
        else:
            row = selected_row

        item: QTableWidgetItem = self.item(row, column)

        if item is None:
            return default
        else:
            return int(item.text())

    def get_current_float_value(self, column: int, selected_row=None,
                                default: float | None = None) -> float | None:
        """
        Returns the currently selected QTableWidgetItem float value.
        """
        if selected_row is None:
            row = self.currentRow()
        else:
            row = selected_row

        if self.item(row, column) is None:
            return default
        else:
            try:
                return float(self.item(row, column).text())

            except ValueError:
                return default

    def get_current_checkstate_bool(self, column: int, selected_row=None) -> bool:
        """
        Returns the currently selected QTableWidgetItem checkstate boolean value.
        """
        if selected_row is None:
            row = self.currentRow()
        else:
            row = selected_row

        table_item: QTableWidgetItem = self.item(row, column)

        if table_item is None:
            return False

        else:
            if table_item.checkState() is Qt.CheckState.Checked:
                return True
            else:
                return False

    def get_current_checkbox_state(self, column: int, selected_row=None) -> bool:
        """
        Returns the currently selected cellWidget QCheckBox state boolean value.
        """
        if selected_row is None:
            row = self.currentRow()
        else:
            row = selected_row

        checkbox = self.cellWidget(row, column)

        if checkbox is None:
            return False

        else:
            # noinspection PyUnresolvedReferences
            return checkbox.isChecked()

    def clear_table(self):
        """
        Method clears the data table by setting the row count to 0.
        """
        self.setRowCount(0)

    def select_last_row(self):
        """
        Selects the last table row based on the table row count.
        """
        self.selectRow(self.rowCount() - 1)

    def remove_selected_row(self, selected_row: int | None = None):
        """
        Removes the currently selected table row.
        """
        if selected_row is None:
            self.removeRow(self.selected_table_row)
        else:
            self.removeRow(selected_row)

    def get_selected_rows(self) -> list[int]:
        """
        Returns a list of selected table rows.
        """
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return []

        selected_rows = []
        for selected_range in selected_ranges:
            top_row = selected_range.topRow()
            bottom_row = selected_range.bottomRow()

            selected_rows.extend(range(top_row, bottom_row + 1))

        return selected_rows

    def get_selected_column_numeric_data(self, column_index: int = None) -> list[float]:
        """
        Returns a list containing numeric values from the currently selected table column.
        :param column_index: Selected column index. Set None for use with right click context menus.
        """
        if column_index is None:
            column = self.selected_table_column
        else:
            column = column_index

        data_list = []
        for row in range(self.rowCount()):
            table_item: QTableWidgetItem = self.item(row, column)
            item_value = float(table_item.text())
            data_list.append(item_value)

        return data_list

    def get_selected_ids(self, id_column_index: int) -> list[int]:
        """
        Method returns IDs of all selected objects in the table.
        Assuming the given column contains integer ID numbers for each object.

        :param id_column_index: Column index of the unique integer object ID.
        """
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return []

        selected_ids: list[int] = []

        for selected_range in selected_ranges:
            top_row = selected_range.topRow()
            bottom_row = selected_range.bottomRow()

            for row in range(top_row, bottom_row + 1):
                selected_ids.append(self.get_current_integer_value(id_column_index, row))

        print(f"Selected IDs: {selected_ids}")
        return selected_ids

    def save_scroll_bar_location(self):
        """
        Saves the table scroll bar position, to be used before table refresh.
        """
        self._scroll_bar_position = self.verticalScrollBar().value()

    def restore_scroll_bar_location(self):
        """
        Restores the last table scroll bar position, to be used after table refresh.
        """
        self.verticalScrollBar().setValue(self._scroll_bar_position)

    def reset_stylesheet(self):
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                self.item(row, col).setSelected(False)
                self.item(row, col).setStyleSheet("")

    def highlight_selection(self, highlight_color: QColor = QColor(255, 0, 0, 255)):
        """
        Method highlights the selected table item by placing a red border around the item.
        """
        selected_items = self.selectedItems()
        if not selected_items:
            self.setStyleSheet("")
            return
        stylesheet = f"""
        QTableWidget::item:selected {{
            border: 2px solid rgba{str(highlight_color.toTuple())};
        }}
        """
        self.setStyleSheet(stylesheet)

    def highlight_row(self, background_color: QColor = QColor(173, 216, 230),
                      text_color: QColor = QBrush(QColor(0, 0, 0))) -> None:
        """
        Method highlights the selected table row by changing the background and text color.
        """
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if self.cellWidget(row, col):
                    continue
                else:
                    item = self.item(row, col)
                    if item:
                        self.blockSignals(True)
                        item.setBackground(QBrush(self.palette().base()))
                        item.setForeground(QBrush(self.palette().text()))
                        self.blockSignals(False)

        selected_items = self.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            row = item.row()
            for col in range(self.columnCount()):
                if self.cellWidget(row, col):
                    continue
                else:
                    item = self.item(row, col)
                    if item:
                        self.blockSignals(True)
                        item.setBackground(background_color)
                        item.setForeground(text_color)
                        self.blockSignals(False)

    def set_lmb_action_method(self, method):
        self._on_lmb_press_event_method = method

    def set_rmb_action_method(self, method):
        self._on_rmb_press_event_method = method

    def mousePressEvent(self, event):
        """
        Custom table mouse press event detection for RMB action menu.
        """
        if (self._on_rmb_press_event_method is not None
                and (event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.RightButton)):
            self._on_rmb_press_event_method(event)

        elif (self._on_lmb_press_event_method is not None
              and (event.type() == QEvent.Type.MouseButtonPress
              and event.button() == Qt.MouseButton.LeftButton)):
            self._on_lmb_press_event_method(event)

        return super().mousePressEvent(event)

    def keyPressEvent(self, event):
        """
        Custom table key press event detection for Copy / Paste functionality.
        """
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_selection()
        elif event.matches(QKeySequence.StandardKey.Paste):
            self.paste_selection()
        else:
            super().keyPressEvent(event)

    def copy_selection(self):
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        locale = QLocale.system()
        locale.setNumberOptions(QLocale.NumberOption.OmitGroupSeparator)

        clipboard_text = []
        for selected_range in selected_ranges:
            top_row = selected_range.topRow()
            bottom_row = selected_range.bottomRow()
            left_column = selected_range.leftColumn()
            right_column = selected_range.rightColumn()

            for row in range(top_row, bottom_row + 1):
                row_data = []
                for col in range(left_column, right_column + 1):
                    item = self.item(row, col)
                    if item is not None:
                        item_data = item.data(Qt.ItemDataRole.DisplayRole)

                        if item_data is None or item_data is type(None):
                            row_data.append(item.text())

                        else:
                            if col in self.numeric_input_columns or col in self.numeric_display_columns:
                                try:
                                    formatted_number = locale.toString(float(item_data), 'f', 2)
                                    row_data.append(str(formatted_number))
                                except ValueError:
                                    row_data.append(str(item_data))
                            else:
                                row_data.append(str(item_data))
                    else:
                        row_data.append("")
                clipboard_text.append("\t".join(row_data))

        clipboard = QApplication.clipboard()
        clipboard.setText("\n".join(clipboard_text))

    def paste_selection(self):
        clipboard = QApplication.clipboard()
        clipboard_text = clipboard.text().strip()

        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        top_range = selected_ranges[0]
        top_row = top_range.topRow()
        left_column = top_range.leftColumn()

        rows = clipboard_text.split("\n")
        for row, row_data in enumerate(rows):
            cols = row_data.split("\t")
            for column, value in enumerate(cols):
                if top_row + row < self.rowCount() and left_column + column < self.columnCount():
                    item_row = top_row + row
                    item_column = left_column + column

                    current_item = self.item(item_row, item_column)
                    if current_item is not None and Qt.ItemFlag.ItemIsEditable not in current_item.flags():
                        print("Item is not editable!")
                        continue

                    if item_column in self.numeric_input_columns or item_column in self.numeric_display_columns:
                        locale = QLocale.system()
                        numeric_value, success = locale.toFloat(value)
                        if success:
                            value = numeric_value

                    item = new_table_item(value=value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.setItem(item_row, item_column, item)


class CustomListWidget(QListWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self._on_rmb_press_event_method = None

    def set_rmb_action_method(self, method):
        self._on_rmb_press_event_method = method

    def mousePressEvent(self, event):
        """
        Custom list mouse press event detection for RMB action menu.
        """
        if self._on_rmb_press_event_method is None:
            return super().mousePressEvent(event)

        if (event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.RightButton):
            self._on_rmb_press_event_method(event)

        return super().mousePressEvent(event)


class CollapsibleSectionWidget(QFrame):
    def __init__(
            self, title="Section",
            alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignHCenter,
            parent=None):
        """
        Custom collapsable widget for a Settings GUI section.
        """
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setContentsMargins(5, 5, 5, 5)

        self.header_widget = QWidget()
        self.header_widget.installEventFilter(self)
        self.header_widget.mousePressEvent = self.on_header_click

        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(5, 5, 5, 5)
        self.header_layout.setSpacing(5)

        self.toggle_button = QToolButton()
        self.toggle_button.setCheckable(True)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.clicked.connect(self.toggle)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-weight: bold;")

        self.header_layout.addWidget(self.toggle_button)
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()

        self.options_area = QWidget()
        self.options_layout = QVBoxLayout(self.options_area)
        self.options_layout.setContentsMargins(20, 5, 10, 5)
        self.options_layout.setAlignment(alignment)

        self.animation = QPropertyAnimation(self.options_area, b"maximumHeight")
        self.animation.setDuration(100)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addWidget(self.options_area)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def on_header_click(self, event):
        self.toggle_button.toggle()
        self.toggle()

    def toggle(self):
        if self.toggle_button.isChecked():
            self.toggle_button.setArrowType(Qt.DownArrow)
            self.animation.stop()
            self.animation.setStartValue(self.options_area.maximumHeight())
            self.animation.setEndValue(self.options_area.sizeHint().height())
            self.animation.start()
            self.options_area.setVisible(True)
        else:
            self.toggle_button.setArrowType(Qt.RightArrow)
            self.animation.stop()
            self.animation.setStartValue(self.options_area.maximumHeight())
            self.animation.setEndValue(0)
            self.animation.start()
            self.animation.finished.connect(self.on_animation_finished)

    def on_animation_finished(self):
        if not self.toggle_button.isChecked():
            self.options_area.setVisible(False)

    def add_numeric_integer_setting(
            self,
            label: str,
            tooltip: str = "",
            min_val: int = 0,
            max_val: int = 100,
            unit: str = "-",
            step: int = 0,
            default_value: int = 0,
            name: str = "",
            row_height: int = 25,
            enabled: bool = True,
            set_value_func: Callable[[], None] | None = None,
            action_menu_func: Callable[[QSpinBox, str], None] | None = None
    ):
        """
        Method adds an input for an integer number setting.

        :param label: Option label.
        :param tooltip: Option tooltip.
        :param min_val: Minimum value.
        :param max_val: Maximum value.
        :param unit: Option unit.
        :param step: Value step.
        :param default_value: Default value.
        :param name: Unique name for the QSpinBox object, enabling identification on editingFinished.
        :param row_height: Option row height.
        :param enabled: Is the input field enabled.
        :param set_value_func: Set value function connected to the editing finished signal.
        :param action_menu_func: RMB Action menu function.
        """
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        option_label = QLabel(label)
        option_label.setFixedSize(180, row_height)

        spinbox = QSpinBox()
        spinbox.setValue(default_value)
        spinbox.setSingleStep(step)
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setToolTip(tooltip)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spinbox.setFixedSize(80, row_height)
        spinbox.setObjectName(name)
        spinbox.setEnabled(enabled)

        if set_value_func is not None:
            spinbox.valueChanged.connect(set_value_func)

        if action_menu_func is not None:
            spinbox.setContextMenuPolicy(Qt.CustomContextMenu)
            spinbox.customContextMenuRequested.connect(lambda: action_menu_func(spinbox, label))

        unit_label = QLabel(unit)
        unit_label.setFixedSize(40, row_height)

        row_layout.addWidget(option_label)
        row_layout.addWidget(spinbox)
        row_layout.addWidget(unit_label)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.options_layout.addWidget(row_widget)

    def add_numeric_float_setting(
            self,
            label: str,
            tooltip: str = "",
            min_val: float = 0.0,
            max_val: float = 100.0,
            unit: str = "-",
            decimals: int = 0,
            step: float = 0.0,
            default_value: float = 0.0,
            name: str = "",
            row_height: int = 25,
            enabled: bool = True,
            set_value_func: Callable[[], None] | None = None,
            action_menu_func: Callable[[QDoubleSpinBox, str], None] | None = None
    ):
        """
        Method adds an input for a floating point number setting.

        :param label: Option label.
        :param tooltip: Option tooltip.
        :param min_val: Minimum value.
        :param max_val: Maximum value.
        :param unit: Option unit.
        :param decimals: Decimal places (precision).
        :param step: Value step.
        :param default_value: Default value.
        :param name: Unique name for the QDoubleSpinBox object, enabling identification on editingFinished.
        :param row_height: Option row height.
        :param enabled: Is the input field enabled.
        :param set_value_func: Set value function connected to the editing finished signal.
        :param action_menu_func: RMB Action menu function.
        """
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        option_label = QLabel(label)
        option_label.setFixedSize(180, row_height)

        spinbox = QDoubleSpinBox()
        spinbox.setValue(default_value)
        spinbox.setDecimals(decimals)
        spinbox.setSingleStep(step)
        spinbox.setMinimum(min_val)
        spinbox.setMaximum(max_val)
        spinbox.setToolTip(tooltip)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
        spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        spinbox.setFixedSize(80, row_height)
        spinbox.setObjectName(name)
        spinbox.setEnabled(enabled)
        # spinbox.setSuffix(f" {unit}")

        if set_value_func is not None:
            spinbox.valueChanged.connect(set_value_func)

        if action_menu_func is not None:
            spinbox.setContextMenuPolicy(Qt.CustomContextMenu)
            spinbox.customContextMenuRequested.connect(lambda: action_menu_func(spinbox, label))

        unit_label = QLabel(unit)
        unit_label.setFixedSize(40, row_height)

        row_layout.addWidget(option_label)
        row_layout.addWidget(spinbox)
        row_layout.addWidget(unit_label)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.options_layout.addWidget(row_widget)

    def add_enum_combobox_option(
        self,
        label: str,
        enum_type: enum.EnumType,
        tooltip: str = "",
        name: str = "",
        row_height: int = 25,
        cbox_width: int = 50,
        enabled: bool = True,
        current_index: int = 0,
        set_value_func: Callable[[], None] | None = None,
        action_menu_func: Callable[[QPushButton, str], None] | None = None
    ):
        """
        Method adds a button for color selection.

        :param label: Option label next to the button.
        :param enum_type: Enum type for adding combobox options.
        :param tooltip: Option tooltip.
        :param name: Unique name for the QComboBox object, enabling identification on currentTextChanged.
        :param row_height: Option row height.
        :param cbox_width: Combobox width.
        :param enabled: Is the input field enabled.
        :param current_index: Current combobox index.
        :param set_value_func: Set value function connected to the editing finished signal.
        :param action_menu_func: RMB Action menu function.
        """
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        option_label = QLabel(label)
        option_label.setFixedSize(120, row_height)

        cbox = QComboBox()
        cbox.setFixedSize(cbox_width, row_height)
        cbox.setObjectName(name)
        cbox.setEnabled(enabled)
        cbox.setToolTip(tooltip)

        for enum_item in enum_type:
            cbox.addItem(str(enum_item.value), userData=enum_item)
        cbox.setCurrentIndex(current_index)

        if set_value_func is not None:
            cbox.currentTextChanged.connect(set_value_func)

        if action_menu_func is not None:
            cbox.setContextMenuPolicy(Qt.CustomContextMenu)
            cbox.customContextMenuRequested.connect(lambda: action_menu_func(cbox, label))

        row_layout.addWidget(option_label)
        row_layout.addWidget(cbox)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.options_layout.addWidget(row_widget)

    def add_checkbox_option(
            self,
            label: str,
            tooltip: str = "",
            name: str = "",
            row_height: int = 25,
            enabled: bool = True,
            initial_state: bool = False,
            set_value_func: Callable[[], None] | None = None,
            action_menu_func: Callable[[QPushButton, str], None] | None = None
    ):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        cbox = QCheckBox()
        cbox.setText(label)
        cbox.setToolTip(tooltip)
        cbox.setObjectName(name)
        cbox.setEnabled(enabled)
        cbox.setFixedHeight(row_height)

        if initial_state:
            cbox.setCheckState(Qt.CheckState.Checked)
        else:
            cbox.setCheckState(Qt.CheckState.Unchecked)

        if set_value_func is not None:
            cbox.stateChanged.connect(set_value_func)

        if action_menu_func is not None:
            cbox.setContextMenuPolicy(Qt.CustomContextMenu)
            cbox.customContextMenuRequested.connect(lambda: action_menu_func(cbox, label))

        row_layout.addWidget(cbox)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.options_layout.addWidget(row_widget)

    def add_button_option(
        self,
        label: str,
        name: str = "",
        button_tooltip: str = "",
        text: str = "",
        row_height: int = 25,
        button_width: int = 50,
        enabled: bool = True,
        set_value_func: Callable[[], None] | None = None,
        action_menu_func: Callable[[QPushButton, str], None] | None = None
    ):
        """
        Method adds a button for color selection.

        :param label: Option label next to the button.
        :param name: Unique name for the QPushButton object, enabling identification on clicked.
        :param button_tooltip: Button tooltip.
        :param text: Text displayed in the button.
        :param row_height: Option row height.
        :param button_width: Button width.
        :param enabled: Is the input field enabled.
        :param set_value_func: Set value function connected to the editing finished signal.
        :param action_menu_func: RMB Action menu function.
        """
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        option_label = QLabel(label)
        option_label.setFixedSize(160, row_height)

        button = QPushButton()
        button.setText(text)
        button.setFixedSize(button_width, row_height)
        button.setObjectName(name)
        button.setToolTip(button_tooltip)
        button.setEnabled(enabled)

        if set_value_func is not None:
            button.clicked.connect(set_value_func)

        if action_menu_func is not None:
            button.setContextMenuPolicy(Qt.CustomContextMenu)
            button.customContextMenuRequested.connect(lambda: action_menu_func(button, label))

        row_layout.addWidget(option_label)
        row_layout.addWidget(button)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.options_layout.addWidget(row_widget)

    def add_path_select_option(
            self,
            description: str,
            lineedit_name: str = "",
            button_name: str = "",
            lineedit_tooltip: str = "",
            button_tooltip: str = "",
            path: str = "",
            row_height: int = 25,
            enabled: bool = True,
            set_value_func: Callable[[], None] | None = None,
            file_browser_func: Callable[[], None] | None = None,
            action_menu_func: Callable[[QPushButton, str], None] | None = None
    ):
        """
        Method adds a button for color selection.

        :param description: Option label for the custom action menu.
        :param lineedit_name: Unique name for the QLineEdit object, enabling identification on editingFinished.
        :param button_name: Unique name for the QPushButton object, enabling identification on clicked.
        :param lineedit_tooltip: Line edit tooltip.
        :param button_tooltip: Button tooltip.
        :param path: Default path displayed in the lineedit.
        :param row_height: Option row height.
        :param enabled: Is the input field enabled.
        :param set_value_func: Set value function connected to the editing finished signal.
        :param file_browser_func: File or directory browser function on click of the path button.
        :param action_menu_func: RMB Action menu function.
        """
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(5)

        line_edit = QLineEdit()
        line_edit.setText(path)
        line_edit.setToolTip(lineedit_tooltip)
        line_edit.setFixedHeight(row_height)
        line_edit.setObjectName(lineedit_name)
        line_edit.setEnabled(enabled)

        if set_value_func is not None:
            line_edit.editingFinished.connect(set_value_func)

        if action_menu_func is not None:
            line_edit.setContextMenuPolicy(Qt.CustomContextMenu)
            line_edit.customContextMenuRequested.connect(lambda: action_menu_func(line_edit, description))

        button = QPushButton()
        button.setObjectName(button_name)
        button.setToolTip(button_tooltip)
        button.setFixedSize(row_height, row_height)
        button.setIcon(get_light_icon("open_file.png"))

        if file_browser_func is not None:
            button.clicked.connect(file_browser_func)

        row_layout.addWidget(line_edit)
        row_layout.addWidget(button)
        row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self.options_layout.addWidget(row_widget)


class CustomCalendarWidget(QCalendarWidget):
    def __init__(self):
        super().__init__()

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.clicked.connect(self.handle_date_click)
        # self.selectionChanged.connect(self.handle_date_changed)
        self._on_rmb_press_event_method: Callable[[QPoint, str], None] | None = None

    def set_rmb_action_method(self, method: Callable[[QPoint, str], None]):
        self._on_rmb_press_event_method = method

    def handle_date_changed(self):
        date = self.selectedDate()
        print(f"Left-clicked on Date: {date.toString('yyyy-MM-dd')}")

    def handle_date_click(self, date):
        print(f"Left-clicked on Date: {date.toString('yyyy-MM-dd')}")

    def show_context_menu(self, position: QPoint):
        global_position = self.mapToGlobal(position)
        clicked_date = self.selectedDate()

        clicked_date_string = clicked_date.toString('yyyy-MM-dd')

        if self._on_rmb_press_event_method is not None:
            self._on_rmb_press_event_method(global_position, clicked_date_string)

        # menu = QMenu(self)
        #
        # action_add_event = menu.addAction("Add Event")
        # action_view_details = menu.addAction("View Details")
        # action_remove_event = menu.addAction("Remove Event")
        #
        # action = menu.exec(global_position)
        #
        # if action == action_add_event:
        #     QMessageBox.information(
        #         self, "Add Event", f"Adding event on {clicked_date.toString('yyyy-MM-dd')}"
        #     )
        # elif action == action_view_details:
        #     QMessageBox.information(
        #         self, "View Details", f"Viewing details for {clicked_date.toString('yyyy-MM-dd')}"
        #     )
        # elif action == action_remove_event:
        #     QMessageBox.information(
        #         self, "Remove Event",
        #         "Removing event on {clicked_date.toString('yyyy-MM-dd')}"
        #     )


class ComboClickFilter(QObject):
    """
    Event filter to detect LMB clicks on SearchableComboBox and its QLineEdit inside QTableWidget.
    """
    def __init__(self, function: Callable[[int], None], parent=None):
        super().__init__(parent)
        self.function = function

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
            if isinstance(obj, SearchableComboBox) or isinstance(obj, QLineEdit):
                combo = obj if isinstance(obj, SearchableComboBox) else obj.parent()
                if isinstance(combo, SearchableComboBox):
                    # print(f"LMB clicked on SearchableComboBox or its lineEdit...{combo.item_identifier = } "
                    #       f"{obj} {combo} {event}")
                    if combo.item_identifier is not None:
                        self.function(combo.item_identifier)
                    # combo.showPopup()  # Open dropdown immediately
                    return True
        return super().eventFilter(obj, event)


def new_table_item_ne(value: float | str,
                      color: QColor | None = None,
                      background: QColor | None = None,
                      weight: QFont.Weight = QFont.Weight.Bold) -> QTableWidgetItem:
    """
    Returns a general purpose, selectable and non-editable QTableWidgetItem.
    Sets the value under QTableWidgetItem data DisplayRole.
    """
    widget_item = QTableWidgetItem()
    widget_item.setData(Qt.ItemDataRole.DisplayRole, value)
    widget_item.setFlags(Qt.ItemFlag.ItemIsEnabled |
                         Qt.ItemFlag.ItemIsSelectable)
    if color is not None:
        widget_item.setForeground(color)
    if background is not None:
        widget_item.setBackground(background)
    font = widget_item.font()
    font.setWeight(weight)
    widget_item.setFont(font)
    return widget_item


def new_table_item(value: float | str,
                   color: QColor | None = COLOR_EDITABLE_ITEM_DARK,
                   background: QColor | None = None,
                   weight: QFont.Weight = QFont.Weight.Bold,
                   identifier_id: int = 0,
                   identifier_type: Enum | None = None) -> QTableWidgetItem:
    """
    Returns a general purpose, editable QTableWidgetItem.
    Sets the value under QTableWidgetItem data DisplayRole.
    Widget item contains the unique identifier associated with the object.
    """
    widget_item = CustomTableWidgetItem(identifier_id=identifier_id, identifier_type=identifier_type)
    widget_item.setData(Qt.ItemDataRole.DisplayRole, value)
    widget_item.setFlags(Qt.ItemFlag.ItemIsEnabled |
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
