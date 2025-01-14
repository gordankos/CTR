

from Core.product import Product
from Core.enums import ProductCategory
from Core.units import MeasurementUnit
from GUI.MainWindow.page_base import MainWindowPage
from GUI.Common.event_manager import event_manager
from GUI.Common.custom_widgets import (CustomDataTable, DoubleSpinBoxDelegate,
                                       AutoCompleteDelegate, new_table_item_ne, new_table_item, ComboBoxDelegate)

from enum import Enum, auto
from timeit import default_timer as timer
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QMainWindow, QLayout, QTableWidgetItem, QHeaderView, QMenu, QInputDialog

from Settings.app_env import get_dark_icon, get_light_icon


class TableCol(Enum):
    ID = auto()
    NAME = auto()
    CATEGORY = auto()
    DESCRIPTION = auto()
    MANUFACTURER = auto()
    CALORIES = auto()
    FAT = auto()
    CARBS = auto()
    PROTEIN = auto()
    PACKAGING_AMOUNT = auto()
    PACKAGING_UNIT = auto()
    DENSITY = auto()
    PRICE = auto()
    FILLER = auto()


_ADDITIONAL_DATA_COLUMNS: list[TableCol] = [
    TableCol.DESCRIPTION,
    TableCol.MANUFACTURER,
    TableCol.PACKAGING_AMOUNT,
    TableCol.PACKAGING_UNIT,
    TableCol.DENSITY,
    TableCol.PRICE
]

_NUTRITION_DATA_COLUMNS: list[TableCol] = [
    TableCol.CALORIES,
    TableCol.FAT,
    TableCol.CARBS,
    TableCol.PROTEIN
]


class PageCatalogue(MainWindowPage):
    def __init__(self, mw: QMainWindow):
        super().__init__(mw)
        self.mw = mw

        self.table = CustomDataTable(self.mw)
        self.layout: QLayout = self.main_window.verticalLayout_frame_catalogue
        self.layout.addWidget(self.table)

        self.column: list[TableCol] = [
            TableCol.ID,
            TableCol.NAME,
            TableCol.CATEGORY,
            TableCol.DESCRIPTION,
            TableCol.MANUFACTURER,
            TableCol.PACKAGING_AMOUNT,
            TableCol.PACKAGING_UNIT,
            TableCol.DENSITY,
            TableCol.PRICE,
            TableCol.CALORIES,
            TableCol.FAT,
            TableCol.CARBS,
            TableCol.PROTEIN,
            TableCol.FILLER,
        ]

        self.setup_page()

    def setup_page(self) -> None:
        self.setup_buttons()
        self.setup_catalogue_table()
        self.setup_search_function()
        self.setup_auto_complete_delegate()
        self.setup_custom_spinbox_delegate()
        self.setup_cbox_delegates()
        self.table.set_rmb_action_method(self.custom_rmb_action_menu)

    def set_dark_theme_button_icons(self) -> None:
        icons = {
            "cancel_dark.png": self.main_window.pushButton_clear_catalogue_search,
        }

        for icon, button in icons.items():
            button.setIcon(get_dark_icon(icon))
            button.setIconSize(QSize(24, 24))

    def set_light_theme_button_icons(self) -> None:
        icons = {
            "cancel.png": self.main_window.pushButton_clear_catalogue_search,
        }

        for icon, button in icons.items():
            button.setIcon(get_light_icon(icon))
            button.setIconSize(QSize(24, 24))

    def setup_buttons(self):
        self.main_window.pushButton_clear_catalogue_search.clicked.connect(self.clear_search_field)

    def setup_catalogue_table(self) -> None:
        headers = [("ID", 30, self.column.index(TableCol.ID)),
                   ("Name", 180, self.column.index(TableCol.NAME)),
                   ("Category", 120, self.column.index(TableCol.CATEGORY)),
                   ("Description", 260, self.column.index(TableCol.DESCRIPTION)),
                   ("Manufacturer", 100, self.column.index(TableCol.MANUFACTURER)),
                   ("Packaging\nAmount", 70, self.column.index(TableCol.PACKAGING_AMOUNT)),
                   ("Packaging\nUnit", 70, self.column.index(TableCol.PACKAGING_UNIT)),
                   ("Density\n[kg/l]", 70, self.column.index(TableCol.DENSITY)),
                   ("Price\n[€]", 70, self.column.index(TableCol.PRICE)),
                   ("Calories\n[kcal]", 60, self.column.index(TableCol.CALORIES)),
                   ("Fat\n[g]", 60, self.column.index(TableCol.FAT)),
                   ("Carbs\n[g]", 60, self.column.index(TableCol.CARBS)),
                   ("Protein\n[g]", 60, self.column.index(TableCol.PROTEIN)),
                   ("", 1, self.column.index(TableCol.FILLER)),
                   ]

        self.table.set_headers_specified(headers)
        self.table.set_header_settings(height=40)

        self.table.horizontalHeader().setSectionResizeMode(self.column.index(TableCol.FILLER),
                                                           QHeaderView.ResizeMode.Stretch)

        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_catalogue_data)
        self.table.set_column_non_editable(column_index=self.column.index(TableCol.FILLER))

        self.table.setSortingEnabled(True)

    def setup_search_function(self) -> None:
        self.main_window.lineEdit_catalogue_search.textChanged.connect(self.filter_table)

    def clear_search_field(self):
        self.main_window.lineEdit_catalogue_search.clear()

    def setup_auto_complete_delegate(self) -> None:
        ac_delegate = AutoCompleteDelegate(self.table)

        self.table.setItemDelegateForColumn(self.column.index(TableCol.NAME), ac_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.DESCRIPTION), ac_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.MANUFACTURER), ac_delegate)

    def setup_custom_spinbox_delegate(self) -> None:
        nutrition_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=999.0, min_val=0.0, decimals=1, decimals_display=1)
        numeric_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=999.0, min_val=0.0, decimals=5, decimals_display=2)
        monetary_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=999.0, min_val=0.0, decimals=2, decimals_display=2)

        self.table.setItemDelegateForColumn(self.column.index(TableCol.PACKAGING_AMOUNT), numeric_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.DENSITY), numeric_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.PRICE), monetary_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.CALORIES), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.FAT), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.CARBS), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.PROTEIN), nutrition_value_delegate)

    def setup_cbox_delegates(self) -> None:
        category_data = {}
        for category in ProductCategory:
            category_data[category] = category.value
        category_delegate = ComboBoxDelegate(category_data, self.table)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.CATEGORY), category_delegate)

        units_data = {}
        for unit in MeasurementUnit:
            units_data[unit] = unit.value
        units_delegate = ComboBoxDelegate(units_data, self.table)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.PACKAGING_UNIT), units_delegate)

    def filter_table(self, query) -> None:
        query = query.lower()
        for row in range(self.table.rowCount()):
            match = False
            for column in range(self.table.columnCount()):
                item = self.table.item(row, column)
                if item:
                    if query in item.text().lower():
                        match = True
                        break
            self.table.setRowHidden(row, not match)

    def row_items_dictionary(self, item: Product) -> dict:
        """
        Returns a dictionary of QTableWidgetItems for adding to the table row.
        """
        item_id = new_table_item_ne(value=item.item_id)
        item_name = new_table_item(value=item.name)
        category_combobox = new_table_item(value=item.category.value)
        category_combobox.setData(Qt.ItemDataRole.UserRole, item.category)
        item_description = new_table_item(value=item.additional_data.description)
        item_manufacturer = new_table_item(value=item.additional_data.manufacturer)
        item_package_amount = new_table_item(value=item.additional_data.packaging_amount)
        packaging_unit_cbox = new_table_item(value=item.additional_data.packaging_unit.value)
        packaging_unit_cbox.setData(Qt.ItemDataRole.UserRole, item.additional_data.packaging_unit)
        item_density = new_table_item(value=item.additional_data.density)
        item_price = new_table_item(value=item.additional_data.price)
        item_calories = new_table_item(value=item.nutrition_data.calories)
        item_fat = new_table_item(value=item.nutrition_data.fat)
        item_carbs = new_table_item(value=item.nutrition_data.carbs)
        item_protein = new_table_item(value=item.nutrition_data.protein)

        custom_table_dict = {
            self.column.index(TableCol.ID): item_id,
            self.column.index(TableCol.NAME): item_name,
            self.column.index(TableCol.CATEGORY): category_combobox,
            self.column.index(TableCol.DESCRIPTION): item_description,
            self.column.index(TableCol.MANUFACTURER): item_manufacturer,
            self.column.index(TableCol.PACKAGING_AMOUNT): item_package_amount,
            self.column.index(TableCol.PACKAGING_UNIT): packaging_unit_cbox,
            self.column.index(TableCol.DENSITY): item_density,
            self.column.index(TableCol.PRICE): item_price,
            self.column.index(TableCol.CALORIES): item_calories,
            self.column.index(TableCol.FAT): item_fat,
            self.column.index(TableCol.CARBS): item_carbs,
            self.column.index(TableCol.PROTEIN): item_protein,
        }

        return custom_table_dict

    def refresh_table(self) -> None:
        """
        Refreshes the table data from the current tracker data.
        Table itemChanged signal is disconnected for the duration of the data refresh.
        """
        start = timer()
        self.table.set_item_changed_signal(connection_status=False, on_changed=self.set_catalogue_data)
        self.table.save_scroll_bar_location()
        self.table.clear_table()

        self.table.setRowCount(len(self.ctr_data.product_catalogue))
        for index, item in enumerate(self.ctr_data.product_catalogue.values()):
            self.table.update_table_row(row=index, row_items=self.row_items_dictionary(item))

        self.table.restore_scroll_bar_location()
        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_catalogue_data)
        end = timer()
        print(f"Catalogue table refreshed in {end - start} s")

    @staticmethod
    def get_selected_category(item: QTableWidgetItem) -> ProductCategory | None:
        return item.data(Qt.ItemDataRole.UserRole)

    @staticmethod
    def get_selected_unit(item: QTableWidgetItem) -> MeasurementUnit | None:
        return item.data(Qt.ItemDataRole.UserRole)

    def get_selected_item(self, selected_row: int | None = None) -> Product | None:
        """
        Method returns the currently selected catalogue item.
        """
        item_id = self.table.get_current_integer_value(self.column.index(TableCol.ID), selected_row)

        if item_id is None:
            return None

        return self.ctr_data.product_catalogue.get(item_id, None)

    def get_selected_items(self) -> list[Product]:
        selected_item_ids = self.table.get_selected_ids(id_column_index=self.column.index(TableCol.ID))
        selected_items: list = []

        for item_id in selected_item_ids:
            item = self.ctr_data.product_catalogue.get(item_id, None)
            if item is None:
                print(f"Selected Item ID {item_id} could not be found!")
                continue
            selected_items.append(item)

        return selected_items

    def custom_rmb_action_menu(self, event) -> None:
        table_item = self.table.itemAt(event.pos())
        if table_item is None:
            return

        items = self.get_selected_items()

        if not items or len(items) == 1:
            self.action_menu_single_selection(selected_row=table_item.row())
        else:
            # self.action_menu_multiple_selection(selected_items=items)
            print("Multiple selection action menu not implemented!")

    def action_menu_single_selection(self, selected_row: int) -> None:
        menu = QMenu(self.mw)

        menu.addAction("Duplicate", lambda: self.on_duplicate_catalogue_item(selected_row))
        menu.addAction("Add to Today's Daily Intake", lambda: self.on_add_to_daily_intake(selected_row))
        menu.addAction("Set IDs", lambda: self.on_set_product_id(selected_row))
        menu.addAction("Remove", lambda: self.on_remove_catalogue_item(selected_row))

        menu.addSeparator()

        menu.addAction("Add New", self.on_add_new_catalogue_item)
        menu.addAction("Renumber IDs", self.on_renumber_product_ids)
        menu.addAction("Refresh Table", self.refresh_table)

        menu.exec_(QCursor.pos())

    def on_add_new_catalogue_item(self) -> None:
        self.ctr_data.add_product("New Food Product")

        event_manager().emit_data_changed(f"Catalogue Page: Added a new Product")
        self.refresh_table()

    def on_duplicate_catalogue_item(self, selected_row: int) -> None:
        item_id = self.table.get_current_integer_value(self.column.index(TableCol.ID), selected_row)
        duplicate_product = self.ctr_data.duplicate_product(product_id=item_id)

        event_manager().emit_data_changed(f"Catalogue Page: Duplicated product {duplicate_product.identifier_string}")
        self.refresh_table()

    def on_renumber_product_ids(self):
        self.ctr_data.renumber_products()

        event_manager().emit_data_changed(f"Catalogue Page: Renumbered all product IDs")
        self.refresh_table()

    def on_set_product_id(self, selected_row: int):
        product: Product = self.get_selected_item(selected_row=selected_row)
        if product is None:
            return

        value, confirmation = QInputDialog.getInt(
            self.mw,
            "Enter New ID",
            f"Enter a new ID for {product.name}",
            value=product.item_id,
            minValue=1,
            maxValue=len(self.ctr_data.product_catalogue),
            step=1)

        if confirmation:
            self.ctr_data.set_product_id(product, new_id=value)

            event_manager().emit_data_changed(f"Catalogue Page: Changed product {product.name} ID to {value}")
            self.refresh_table()

    def on_add_to_daily_intake(self, selected_row: int) -> None:
        print(f"Adding catalogue item at row {selected_row} to daily intake record... WIP - Not Implemented")

    def on_remove_catalogue_item(self, selected_row: int) -> None:
        item_id = self.table.get_current_integer_value(self.column.index(TableCol.ID), selected_row)
        self.ctr_data.remove_product(product_id=item_id)

        event_manager().emit_data_changed(f"Catalogue Page: Removed product ID {item_id}")
        self.refresh_table()

    def set_catalogue_data(self, changed_item: QTableWidgetItem) -> None:
        """
        Modifies catalogue data based on the changed QTableWidgetItem.
        """
        row_index = changed_item.row()
        column_index = changed_item.column()
        column = self.column[column_index]

        item: Product = self.get_selected_item(selected_row=row_index)
        if item is None:
            return

        if column is TableCol.NAME:
            self.set_item_name(item, row_index)

        elif column is TableCol.CATEGORY:
            self.set_item_category(changed_item, item)

        elif column is TableCol.PACKAGING_UNIT:
            self.set_packaging_unit(changed_item, item)

        elif column in _ADDITIONAL_DATA_COLUMNS:
            self.set_item_additional_data(item, row_index)

        elif column in _NUTRITION_DATA_COLUMNS:
            self.set_item_nutrition_data(item, row_index)

    def set_item_name(self, item: Product, row: int) -> None:
        item.name = self.table.get_current_string_value(self.column.index(TableCol.NAME), row)

        event_manager().emit_data_changed(f"Catalogue Page: Changed name for {item.identifier_string}")

    def set_item_category(self, widget_item: QTableWidgetItem, item: Product) -> None:
        category = self.get_selected_category(widget_item)
        if category is None:
            category = ProductCategory.OTHER
        item.category = category

        event_manager().emit_data_changed(f"Catalogue Page: Changed category to {category.value} "
                                          f"for {item.identifier_string}")

    def set_item_additional_data(self, item: Product, row: int) -> None:
        data = item.additional_data

        data.description = self.table.get_current_string_value(self.column.index(TableCol.DESCRIPTION), row)
        data.manufacturer = self.table.get_current_string_value(self.column.index(TableCol.MANUFACTURER), row)
        data.packaging_amount = self.table.get_current_float_value(self.column.index(TableCol.PACKAGING_AMOUNT), row)
        data.price = self.table.get_current_float_value(self.column.index(TableCol.PRICE), row)

        event_manager().emit_data_changed(f"Catalogue Page: Changed additional data of {item.identifier_string}")

    def set_packaging_unit(self, widget_item: QTableWidgetItem, item: Product) -> None:
        unit = self.get_selected_unit(widget_item)
        if unit is None:
            unit = MeasurementUnit.KG

        item.additional_data.packaging_unit = unit

        event_manager().emit_data_changed(f"Catalogue Page: Changed packaging unit to {unit.value} "
                                          f"for {item.identifier_string}")

    def set_item_nutrition_data(self, item: Product, row: int) -> None:
        data = item.nutrition_data

        data.calories = self.table.get_current_float_value(self.column.index(TableCol.CALORIES), row)
        data.fat = self.table.get_current_float_value(self.column.index(TableCol.FAT), row)
        data.carbs = self.table.get_current_float_value(self.column.index(TableCol.CARBS), row)
        data.protein = self.table.get_current_float_value(self.column.index(TableCol.PROTEIN), row)

        event_manager().emit_data_changed(f"Catalogue Page: Changed nutrition data of {item.identifier_string}")
