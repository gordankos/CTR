
from Core.product import Product, NutritionData
from Core.enums import ProductCategory
from Core.recipe import Recipe
from Core.ingredient import Ingredient, AmountDefinition, NetAmountDefinition
from GUI.MainWindow.page_base import MainWindowPage
from GUI.Common.event_manager import event_manager
from GUI.Common.custom_widgets import (CustomDataTable, new_table_item_ne, new_table_item,
                                       SearchableComboBox, CustomListWidget, CustomTableWidgetItem,
                                       DoubleSpinBoxDelegate, CustomTextEdit, ComboClickFilter)

from enum import Enum, auto
from timeit import default_timer as timer
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCursor, QColor, QFont
from PySide6.QtWidgets import (QTableWidgetItem, QHeaderView, QMenu, QListWidgetItem, QSplitter,
                               QComboBox, QDoubleSpinBox, QInputDialog, QMessageBox)

from Settings.app_env import get_dark_icon, get_light_icon
from Settings.config_enums import ConfirmationCategory


class TableCol(Enum):
    ID = auto()
    INGREDIENT = auto()
    AMOUNT = auto()
    AMOUNT_UNIT = auto()
    NET_AMOUNT = auto()
    NET_AMOUNT_UNIT = auto()
    NET_MASS = auto()
    PRICE = auto()
    CALORIES = auto()
    FAT = auto()
    CARBS = auto()
    PROTEIN = auto()
    FILLER = auto()


class PageRecipes(MainWindowPage):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw

        self.table = CustomDataTable(self.mw)
        self.recipes_list: CustomListWidget = CustomListWidget(self.mw)
        self.description_input = CustomTextEdit(self.mw)

        self.filter = ComboClickFilter(function=self.on_ingredient_name_cbox_selection, parent=self.table)

        self.column: list[TableCol] = [
            TableCol.ID,
            TableCol.INGREDIENT,
            TableCol.AMOUNT,
            TableCol.AMOUNT_UNIT,
            TableCol.NET_AMOUNT,
            TableCol.NET_AMOUNT_UNIT,
            TableCol.NET_MASS,
            TableCol.PRICE,
            TableCol.CALORIES,
            TableCol.FAT,
            TableCol.CARBS,
            TableCol.PROTEIN,
            TableCol.FILLER,
        ]

        self.selected_recipe_id: int | None = None

        self.setup_page()

    def setup_page(self) -> None:
        self.setup_buttons()
        self.setup_recipes_list()
        self.setup_recipe_data_table()
        self.setup_custom_spinbox_delegate()
        self.setup_recipe_description_text_edit()
        self.setup_horizontal_splitter()
        self.setup_vertical_splitter()
        self.setup_mass_input_groupbox()
        self.setup_recipe_detail_inputs()
        self.setup_recipe_detail_tooltips()
        self.setup_amount_definition_cbox()
        self.setup_net_amount_definition_cbox()
        self.setup_relative_amount_ingredient_cbox()
        self.setup_search_function()
        self.setup_identifier_label_fonts()

    def set_dark_theme_button_icons(self) -> None:
        icons = {
            "cancel_dark.png": self.main_window.pushButton_clear_recipe_list_search,
        }

        for icon, button in icons.items():
            button.setIcon(get_dark_icon(icon))
            button.setIconSize(QSize(24, 24))

    def set_light_theme_button_icons(self) -> None:
        icons = {
            "cancel.png": self.main_window.pushButton_clear_recipe_list_search,
        }

        for icon, button in icons.items():
            button.setIcon(get_light_icon(icon))
            button.setIconSize(QSize(24, 24))

    def setup_buttons(self):
        self.main_window.pushButton_clear_recipe_list_search.clicked.connect(self.clear_search_field)

    def setup_recipes_list(self) -> None:
        self.main_window.verticalLayout_frame_recipes_list.addWidget(self.recipes_list)
        self.recipes_list.currentItemChanged.connect(self.on_recipe_selection_change)
        self.recipes_list.itemChanged.connect(self.on_rename_recipe)
        self.recipes_list.set_rmb_action_method(self.custom_rmb_action_menu_list)

    def setup_recipe_data_table(self) -> None:
        self.main_window.verticalLayout_frame_recipe_data_table.addWidget(self.table)

        headers = [("ID", 30, self.column.index(TableCol.ID)),
                   ("Ingredient", 180, self.column.index(TableCol.INGREDIENT)),
                   ("Amount", 70, self.column.index(TableCol.AMOUNT)),
                   ("", 30, self.column.index(TableCol.AMOUNT_UNIT)),
                   ("Net Amount", 70, self.column.index(TableCol.NET_AMOUNT)),
                   ("", 30, self.column.index(TableCol.NET_AMOUNT_UNIT)),
                   ("Net Mass\n[g]", 70, self.column.index(TableCol.NET_MASS)),
                   ("Price\n[€]", 70, self.column.index(TableCol.PRICE)),
                   ("Calories\n[kcal]", 60, self.column.index(TableCol.CALORIES)),
                   ("Fat\n[g]", 60, self.column.index(TableCol.FAT)),
                   ("Carbs\n[g]", 60, self.column.index(TableCol.CARBS)),
                   ("Protein\n[g]", 60, self.column.index(TableCol.PROTEIN)),
                   ("", 1, self.column.index(TableCol.FILLER)),
                   ]

        self.table.set_headers_specified(headers)
        self.table.set_header_settings(height=40, show_vertical_header=False)

        self.table.horizontalHeader().setSectionResizeMode(self.column.index(TableCol.FILLER),
                                                           QHeaderView.ResizeMode.Stretch)

        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_recipe_data)
        self.table.currentItemChanged.connect(self.on_ingredient_selection_change)

        self.table.set_rmb_action_method(self.custom_rmb_action_menu_table)

        # self.table.setSortingEnabled(True)

    def setup_custom_spinbox_delegate(self) -> None:
        nutrition_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=9999.0, min_val=0.0, decimals=1, decimals_display=1)
        numeric_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=9999.0, min_val=0.0, decimals=1, decimals_display=0)
        monetary_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=9999.0, min_val=0.0, decimals=2, decimals_display=2)

        self.table.setItemDelegateForColumn(self.column.index(TableCol.AMOUNT), numeric_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.NET_AMOUNT), numeric_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.NET_MASS), numeric_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.PRICE), monetary_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.CALORIES), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.FAT), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.CARBS), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.PROTEIN), nutrition_value_delegate)

    def setup_recipe_description_text_edit(self):
        self.main_window.verticalLayout_frame_recipe_description.addWidget(self.description_input)
        self.description_input.setMinimumHeight(60)

    def setup_horizontal_splitter(self) -> None:
        h_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_window.horizontalLayout_recipe_frames.addWidget(h_splitter)
        h_splitter.addWidget(self.main_window.frame_recipes_list)
        h_splitter.addWidget(self.main_window.frame_recipes_tables)
        h_splitter.addWidget(self.main_window.frame_ingredient_details)
        h_splitter.setSizes([180, 800, 200])

    def setup_vertical_splitter(self) -> None:
        v_splitter_left = QSplitter(Qt.Orientation.Vertical)
        self.main_window.verticalLayout_frame_recipes_tables.addWidget(v_splitter_left)
        v_splitter_left.addWidget(self.main_window.frame_recipe_data_table)
        v_splitter_left.addWidget(self.main_window.frame_recipe_details)
        v_splitter_left.setSizes([400, 200])

    def setup_mass_input_groupbox(self):
        self.main_window.groupBox_measured_mass.toggled.connect(self.set_recipe_adjust_for_evaporation)

    def setup_recipe_detail_inputs(self):
        self.description_input.editingFinished.connect(self.set_recipe_description)
        self.main_window.doubleSpinBox_recipe_measured_mass.editingFinished.connect(self.set_recipe_measured_mass)
        self.main_window.doubleSpinBox_mass_reduction.editingFinished.connect(self.set_recipe_mass_reduction)

    def setup_recipe_detail_tooltips(self):
        self.main_window.groupBox_measured_mass.setToolTip(
            "Use measured mass of the meal to account\n"
            "for water evaporation after cooking in net\n"
            "nutrition value calculations.")
        self.main_window.doubleSpinBox_recipe_measured_mass.setToolTip(
            "Measured net mass of the dish.")
        self.main_window.doubleSpinBox_mass_reduction.setToolTip(
            "Mass to be deducted from the measured mass value,\n"
            "such as known pan, pot or container mass, included\n"
            "in the given measured total mass.")
        self.main_window.doubleSpinBox_net_mass_total.setToolTip(
            "Calculated net mass after reduction.")
        self.main_window.doubleSpinBox_mass_ratio.setToolTip(
            "Calculated total net mass to measured mass ratio.")

    def setup_amount_definition_cbox(self) -> None:
        cbox: QComboBox = self.main_window.comboBox_ingredient_amount_definition
        for definition in AmountDefinition:
            cbox.addItem(str(definition.value), userData=definition)

        cbox.currentIndexChanged.connect(self.set_ingredient_amount_definition)

    def setup_net_amount_definition_cbox(self) -> None:
        cbox: QComboBox = self.main_window.comboBox_ingredient_net_amount_definition
        for definition in NetAmountDefinition:
            cbox.addItem(str(definition.value), userData=definition)

        cbox.currentIndexChanged.connect(self.set_ingredient_net_amount_definition)

    def setup_relative_amount_ingredient_cbox(self) -> None:
        cbox: QComboBox = self.main_window.comboBox_relative_amount_ingredient

        cbox.currentIndexChanged.connect(self.set_ingredient_relative_amount_reference)

    def setup_search_function(self) -> None:
        self.main_window.lineEdit_recipe_list_search.textChanged.connect(self.filter_recipes_list)

    def clear_search_field(self):
        self.main_window.lineEdit_recipe_list_search.clear()

    def setup_identifier_label_fonts(self):
        font = QFont()
        font.setBold(True)

        self.main_window.label_selected_recipe_identifier.setFont(font)
        self.main_window.label_selected_ingredient_identifier.setFont(font)

    def set_relative_inputs_status(self, active: bool):
        self.main_window.comboBox_ingredient_amount_definition.setEnabled(active)
        self.main_window.comboBox_relative_amount_ingredient.setEnabled(active)
        self.main_window.comboBox_ingredient_net_amount_definition.setEnabled(active)

    @staticmethod
    def get_recipe_name(list_item: QListWidgetItem) -> int:
        """
        Returns the Recipe name stored in the list item data.
        """
        return list_item.data(0)

    @staticmethod
    def get_recipe_id(list_item: QListWidgetItem) -> int:
        """
        Returns the Recipe ID stored in the list item data.
        """
        return list_item.data(1)

    def on_ingredient_selection_change(self, table_item: QTableWidgetItem | CustomTableWidgetItem):
        if table_item is None:
            print("No table item selected!")
            self.update_relative_inputs(recipe=None, ingredient=None)
            return

        ingredient = self.get_selected_ingredient(table_item.row())
        if ingredient is None:
            print("No recipe ingredient selected!")
            self.update_relative_inputs(recipe=None, ingredient=None)
            return

        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        self.update_relative_inputs(recipe=recipe, ingredient=ingredient)

        print(f"Changed ingredient selection in the recipes table to {ingredient.product.identifier_string}")

    def on_ingredient_name_cbox_selection(self, item_id: int):
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            self.update_relative_inputs(recipe=None, ingredient=None)
            return None

        ingredient = recipe.get_ingredient(item_id)
        if ingredient is None:
            print("No recipe ingredient selected!")
            self.update_relative_inputs(recipe=None, ingredient=None)
            return

        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        self.update_relative_inputs(recipe=recipe, ingredient=ingredient)

        print(f"Changed ingredient Cbox selection to ID {item_id} "
              f"in the recipes table, ingredient {ingredient.product.identifier_string}")

    def on_recipe_selection_change(self, current: QListWidgetItem) -> None:
        recipe_id = self.get_recipe_id(current)
        recipe = self.get_recipe(recipe_id)
        if recipe is None:
            print(f"Error: Recipe ID {recipe_id} does not exist in the current tracker data!")
            return

        self.update_gui_on_recipe_selection(recipe)

    def update_gui_on_recipe_selection(self, recipe: Recipe) -> None:
        """
        Method sets the given Recipe as the currently selected recipe
        and updates all GUI elements to reflect selection.
        """
        print(f"Currently selected recipe changed to {recipe.identifier_string}")
        self.selected_recipe_id = recipe.item_id

        self.update_recipe_identifier(identifier=recipe.identifier_string)
        self.update_recipe_descriptions(description=recipe.additional_data.description)
        self.update_recipe_details(recipe=recipe)
        self.update_calculated_recipe_details(recipe=recipe)
        self.update_adjust_for_evaporation_option(recipe=recipe)
        self.update_relative_inputs(recipe=recipe, ingredient=None)
        self.refresh_ingredients_table()

    def update_gui_on_ingredient_selection(self, ingredient: Ingredient) -> None:
        """
        Method sets the given ingredient as the currently selected ingredient
        and updates all GUI elements to reflect selection.
        """
        ...

    def filter_recipes_list(self, text):
        for index in range(self.recipes_list.count()):
            item = self.recipes_list.item(index)
            item.setHidden(text.lower() not in item.text().lower())

    def row_items_dictionary(self, ingredient: Ingredient) -> dict:
        """
        Returns a dictionary of QTableWidgetItems for adding to the table row.
        """
        nutrition_data = ingredient.get_nutrition_data()

        item_id = new_table_item_ne(value=ingredient.item_id)
        item_name = SearchableComboBox()
        item_name.item_identifier = ingredient.item_id
        item_name.lineEdit().installEventFilter(self.filter)
        item_name.addItems(self.ctr_data.get_all_product_names())
        item_name.setCurrentIndex(ingredient.product.item_id)
        item_name.currentIndexChanged.connect(self.set_ingredient_product_item)
        font = item_name.lineEdit().font()
        font.setBold(True)
        item_name.lineEdit().setFont(font)
        text_color = QColor(255, 255, 255, 255)
        background_color = QColor(0, 0, 139, 100)
        item_name.set_colors(text_color, background_color)
        item_amount = new_table_item(value=ingredient.amount)
        item_amount_unit = new_table_item_ne(value=ingredient.amount_definition_unit_string)
        if ingredient.net_amount_definition is NetAmountDefinition.EQUAL:
            item_net_amount = new_table_item_ne(value=ingredient.get_net_amount())
        else:
            item_net_amount = new_table_item(value=ingredient.get_net_amount())
        item_net_amount_unit = new_table_item_ne(value=ingredient.net_amount_definition_unit_string)
        item_net_mass = new_table_item_ne(value=ingredient.get_net_mass())
        item_price = new_table_item_ne(value=ingredient.get_price())
        item_calories = new_table_item_ne(value=nutrition_data.calories)
        item_fat = new_table_item_ne(value=nutrition_data.fat)
        item_carbs = new_table_item_ne(value=nutrition_data.carbs)
        item_protein = new_table_item_ne(value=nutrition_data.protein)
        item_filler = new_table_item_ne(value="")

        custom_table_dict = {
            self.column.index(TableCol.ID): item_id,
            self.column.index(TableCol.INGREDIENT): item_name,
            self.column.index(TableCol.AMOUNT): item_amount,
            self.column.index(TableCol.AMOUNT_UNIT): item_amount_unit,
            self.column.index(TableCol.NET_AMOUNT): item_net_amount,
            self.column.index(TableCol.NET_AMOUNT_UNIT): item_net_amount_unit,
            self.column.index(TableCol.NET_MASS): item_net_mass,
            self.column.index(TableCol.PRICE): item_price,
            self.column.index(TableCol.CALORIES): item_calories,
            self.column.index(TableCol.FAT): item_fat,
            self.column.index(TableCol.CARBS): item_carbs,
            self.column.index(TableCol.PROTEIN): item_protein,
            self.column.index(TableCol.FILLER): item_filler,
        }

        return custom_table_dict

    def summary_row_items_total(self) -> dict[int, QTableWidgetItem]:
        """
        Returns a dictionary of QTableWidgetItems for adding to the table totals summary row.
        """
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            nutrition_data = NutritionData()
        else:
            nutrition_data = recipe.get_total_nutrition_data()

        item_name = new_table_item_ne(value="Total")
        item_amount = new_table_item_ne(value="-")
        item_amount_unit = new_table_item_ne(value="/")
        item_net_amount = new_table_item_ne(value="-")
        item_net_amount_unit = new_table_item_ne(value="/")
        item_net_mass= new_table_item_ne(value=recipe.get_total_net_mass())
        item_price = new_table_item_ne(value=recipe.get_total_price())
        item_calories = new_table_item_ne(value=nutrition_data.calories)
        item_fat = new_table_item_ne(value=nutrition_data.fat)
        item_carbs = new_table_item_ne(value=nutrition_data.carbs)
        item_protein = new_table_item_ne(value=nutrition_data.protein)

        custom_table_dict = {
            self.column.index(TableCol.INGREDIENT): item_name,
            self.column.index(TableCol.AMOUNT): item_amount,
            self.column.index(TableCol.AMOUNT_UNIT): item_amount_unit,
            self.column.index(TableCol.NET_AMOUNT): item_net_amount,
            self.column.index(TableCol.NET_AMOUNT_UNIT): item_net_amount_unit,
            self.column.index(TableCol.NET_MASS): item_net_mass,
            self.column.index(TableCol.PRICE): item_price,
            self.column.index(TableCol.CALORIES): item_calories,
            self.column.index(TableCol.FAT): item_fat,
            self.column.index(TableCol.CARBS): item_carbs,
            self.column.index(TableCol.PROTEIN): item_protein,
        }

        return custom_table_dict

    def summary_row_items_total_per_100_grams(self) -> dict[int, QTableWidgetItem]:
        """
        Returns a dictionary of QTableWidgetItems for adding to the table totals per 100g summary row.
        """
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            nutrition_data = NutritionData()
        else:
            nutrition_data = recipe.get_total_nutrition_data_per_100g()

        item_name = new_table_item_ne(value="Total per 100g")
        item_amount = new_table_item_ne(value="-")
        item_amount_unit = new_table_item_ne(value="/")
        item_net_amount = new_table_item_ne(value="-")
        item_net_amount_unit = new_table_item_ne(value="/")
        item_net_mass = new_table_item_ne(value=100)
        item_price = new_table_item_ne(value=recipe.get_price_per_100g())
        item_calories = new_table_item_ne(value=nutrition_data.calories)
        item_fat = new_table_item_ne(value=nutrition_data.fat)
        item_carbs = new_table_item_ne(value=nutrition_data.carbs)
        item_protein = new_table_item_ne(value=nutrition_data.protein)

        custom_table_dict = {
            self.column.index(TableCol.INGREDIENT): item_name,
            self.column.index(TableCol.AMOUNT): item_amount,
            self.column.index(TableCol.AMOUNT_UNIT): item_amount_unit,
            self.column.index(TableCol.NET_AMOUNT): item_net_amount,
            self.column.index(TableCol.NET_AMOUNT_UNIT): item_net_amount_unit,
            self.column.index(TableCol.NET_MASS): item_net_mass,
            self.column.index(TableCol.PRICE): item_price,
            self.column.index(TableCol.CALORIES): item_calories,
            self.column.index(TableCol.FAT): item_fat,
            self.column.index(TableCol.CARBS): item_carbs,
            self.column.index(TableCol.PROTEIN): item_protein,
        }

        return custom_table_dict

    def refresh_recipes_list(self) -> None:
        self.recipes_list.blockSignals(True)
        self.recipes_list.clear()

        recipe_ids = list(self.ctr_data.recipes_record.keys())
        if 0 in recipe_ids:
            recipe_ids.pop(recipe_ids.index(0))     # First null recipe removed from the list

        for recipe_id in recipe_ids:
            recipe = self.ctr_data.recipes_record[recipe_id]
            list_item = QListWidgetItem()
            list_item.setFlags(list_item.flags() | Qt.ItemFlag.ItemIsEditable)
            list_item.setData(0, recipe.identifier_string)
            list_item.setData(1, recipe.item_id)
            self.recipes_list.addItem(list_item)

        self.recipes_list.blockSignals(False)

    def refresh_ingredients_table(self) -> None:
        """
        Refreshes the table data from the current tracker data.
        Table itemChanged signal is disconnected for the duration of the data refresh.
        """
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            print("No currently selected recipe to show!")
            return

        start = timer()
        self.table.set_item_changed_signal(connection_status=False, on_changed=self.set_recipe_data)
        self.table.save_scroll_bar_location()
        self.table.clear_table()

        for item in recipe.ingredients.values():
            self.table.add_table_row(row_items=self.row_items_dictionary(item))

        self.table.add_table_row(row_items=self.summary_row_items_total())
        self.table.add_table_row(row_items=self.summary_row_items_total_per_100_grams())

        self.table.restore_scroll_bar_location()
        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_recipe_data)
        end = timer()
        print(f"Recipe ingredients table refreshed for {recipe.identifier_string} in {end - start} s")

    def refresh_ingredients_table_row(self, ingredient: Ingredient, selected_row: int | None = None) -> None:
        """
        Refreshes data in the recipe ingredients table only for the given table row index.
        """
        if selected_row is None:
            selected_row = self.table.currentRow()

        self.table.set_item_changed_signal(connection_status=False, on_changed=self.set_recipe_data)

        self.table.update_table_row(selected_row, self.row_items_dictionary(ingredient))
        self.refresh_summary_total_rows()

        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_recipe_data)

    def refresh_summary_total_rows(self) -> None:
        self.table.update_table_row(row=self.table.rowCount() - 2,
                                    row_items=self.summary_row_items_total())
        self.table.update_table_row(row=self.table.rowCount() - 1,
                                    row_items=self.summary_row_items_total_per_100_grams())
        print(f"Updated summary total rows for rowcount {self.table.rowCount()}")

    def get_selected_item(self, selected_row: int | None = None) -> Recipe | None:
        """
        Method returns the currently selected recipe.
        """
        item_id = self.table.get_current_integer_value(self.column.index(TableCol.ID), selected_row)

        if item_id is None:
            return None

        return self.ctr_data.product_catalogue.get(item_id, None)

    def get_recipe(self, recipe_id: int) -> Recipe | None:
        """
        Method returns the Recipe from the current tracker data.
        """
        if recipe_id in self.ctr_data.recipes_record.keys():
            return self.ctr_data.recipes_record[recipe_id]
        else:
            return None

    def get_selected_ingredient(self, selected_row: int | None = None) -> Ingredient | None:
        """
        Method returns the currently selected recipe ingredient.
        """
        item_id = self.table.get_current_integer_value(self.column.index(TableCol.ID), selected_row)
        if item_id is None:
            return None

        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            return None

        return recipe.get_ingredient(item_id)

    def get_amount_definition(self) -> AmountDefinition:
        cbox: QComboBox = self.main_window.comboBox_ingredient_amount_definition
        return cbox.itemData(cbox.currentIndex())

    def get_amount_relative_ingredient_id(self) -> int | None:
        cbox: QComboBox = self.main_window.comboBox_relative_amount_ingredient
        return cbox.itemData(cbox.currentIndex())

    def get_net_amount_definition(self) -> NetAmountDefinition:
        cbox: QComboBox = self.main_window.comboBox_ingredient_net_amount_definition
        return cbox.itemData(cbox.currentIndex())

    def custom_rmb_action_menu_list(self, event) -> None:
        list_item: QListWidgetItem = self.recipes_list.itemAt(event.pos())

        if list_item is None:
            self.action_menu_list_no_selection()
        else:
            recipe_id = self.get_recipe_id(list_item)
            self.action_menu_list_single_selection(recipe_id)

    def custom_rmb_action_menu_table(self, event) -> None:
        table_item = self.table.itemAt(event.pos())
        if table_item is None:
            if self.selected_recipe_id is None:
                return
            else:
                self.action_menu_table_no_selection()
                return

        # items = self.get_selected_items()

        # if not items or len(items) == 1:
        self.action_menu_table_single_selection(selected_row=table_item.row())
        # else:
        #     # self.action_menu_multiple_selection(selected_items=items)
        #     print("Multiple selection action menu not implemented!")

    def action_menu_list_no_selection(self) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Add New Recipe", self.add_new_recipe)
        menu.addSeparator()
        menu.addAction("Refresh List", self.refresh_recipes_list)

        menu.exec_(QCursor.pos())

    def action_menu_list_single_selection(self, recipe_id: int) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Add New Recipe", self.add_new_recipe)
        menu.addAction("Set ID...", lambda: self.on_set_recipe_id(recipe_id))
        menu.addAction("Remove", lambda: self.on_remove_recipe(recipe_id))
        menu.addSeparator()
        menu.addAction("Refresh List", self.refresh_recipes_list)

        menu.exec_(QCursor.pos())

    def action_menu_table_no_selection(self) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Add New Ingredient", self.add_new_ingredient)
        menu.addAction("Refresh Table", self.refresh_ingredients_table)

        menu.exec_(QCursor.pos())

    def action_menu_table_single_selection(self, selected_row: int) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Add New Ingredient", self.add_new_ingredient)
        menu.addAction("Go To Ingredient Definition", lambda: self.on_go_to_ingredient(selected_row))
        menu.addAction("Set ID...", lambda: self.on_set_ingredient_id(selected_row))
        menu.addAction("Remove", lambda: self.on_remove_recipe_ingredient(selected_row))
        menu.addSeparator()
        menu.addAction("Refresh Table", self.refresh_ingredients_table)

        menu.exec_(QCursor.pos())

    def add_new_recipe(self) -> None:
        new_recipe = self.ctr_data.add_recipe(
            name="New Recipe",
            description="Recipe preparation instructions / Description / Notes"
        )
        self.selected_recipe_id = new_recipe.item_id

        event_manager().emit_data_changed(f"Recipes Page: Added a new recipe ID {new_recipe.item_id} and set as"
                                          f" current recipe ID {self.selected_recipe_id}")

        self.update_gui_on_recipe_selection(new_recipe)
        self.refresh_recipes_list()

    def add_new_ingredient(self) -> None:
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            print("Recipe is None! Can't add a new ingredient")
            return

        product = Product(0, "", ProductCategory.OTHER)
        new_ingredient = Ingredient(item_id=0, product=product)
        new_ingredient = recipe.add_ingredient(new_ingredient)

        event_manager().emit_data_changed(f"Recipes Page: Added a new ingredient for recipe ID "
                                          f"{self.selected_recipe_id}")
        self.refresh_ingredients_table()
        self.update_relative_amount_cbox(recipe, selected_ingredient=new_ingredient)

    def on_go_to_ingredient(self, selected_row: int):
        ingredient: Ingredient = self.get_selected_ingredient(selected_row=selected_row)
        if ingredient is None:
            return

        print(f"Navigating to Product {ingredient.product.identifier_string}... WIP - Not Implemented!")

    def on_rename_recipe(self, list_item: QListWidgetItem) -> None:
        recipe_id = self.get_recipe_id(list_item)

        recipe = self.get_recipe(recipe_id)
        if recipe is None:
            print("Recipe is None! Can't rename it!")
            return

        recipe_name = list_item.text()
        recipe.name = recipe_name
        self.refresh_recipes_list()
        self.update_recipe_identifier(recipe.identifier_string)

        event_manager().emit_data_changed(f"Recipes Page: Renamed recipe ID {recipe_id} to {recipe_name}")

    def on_set_recipe_id(self, recipe_id: int):
        recipe: Recipe = self.get_recipe(recipe_id=recipe_id)
        if recipe is None:
            return

        value, confirmation = QInputDialog.getInt(
            self.mw,
            "Enter New ID",
            f"Enter a new ID for {recipe.name}",
            value=recipe.item_id,
            minValue=1,
            maxValue=len(self.ctr_data.recipes_record) - 1,
            step=1)

        if confirmation:
            self.ctr_data.set_recipe_id(recipe, new_id=value)

            event_manager().emit_data_changed(f"Recipes Page: Changed recipe ID "
                                              f"{recipe.name} to {value}")
            self.refresh_recipes_list()

    def on_set_ingredient_id(self, selected_row: int):
        ingredient: Ingredient = self.get_selected_ingredient(selected_row=selected_row)
        if ingredient is None:
            return

        recipe: Recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            return

        value, confirmation = QInputDialog.getInt(
            self.mw,
            "Enter New ID",
            f"Enter a new ID for {ingredient.product.name}",
            value=ingredient.item_id,
            minValue=1,
            maxValue=len(recipe.ingredients),
            step=1)

        if confirmation:
            recipe.set_ingredient_id(ingredient, new_id=value)

            event_manager().emit_data_changed(f"Recipes Page: Changed recipe ingredient ID "
                                              f"{ingredient.product.name} to {value}")
            self.refresh_ingredients_table()

    def on_remove_recipe(self, recipe_id: int) -> None:
        recipe = self.get_recipe(recipe_id)
        if recipe is None:
            return

        confirmation = self.mw.confirm_action(
            message=f"Action will remove Recipe\n{recipe.identifier_string}",
            accept_label="Remove",
            category=ConfirmationCategory.REMOVE_RECIPE
        )

        if confirmation:
            self.ctr_data.remove_recipe(recipe_id)

            event_manager().emit_data_changed(f"Recipes Page: Removed recipe ID {recipe_id}")
            self.refresh_recipes_list()
            self.refresh_ingredients_table()

    def on_remove_recipe_ingredient(self, selected_row: int) -> None:
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            return

        ingredient_id = self.table.get_current_integer_value(self.column.index(TableCol.ID), selected_row)
        if ingredient_id is None:
            return

        ingredient = recipe.get_ingredient(ingredient_id)
        if ingredient is None:
            return

        confirmation = self.mw.confirm_action(
            message=f"Action will remove Ingredient\n{ingredient.identifier_string}",
            accept_label="Remove",
            category=ConfirmationCategory.REMOVE_RECIPE_INGREDIENT
        )

        if confirmation:
            recipe.remove_ingredient(ingredient_id)
            recipe.renumber_ingredients()

            event_manager().emit_data_changed(f"Recipes Page: Removed recipe {recipe.identifier_string} "
                                              f"ingredient ID {ingredient_id}")
            self.refresh_ingredients_table()
            self.update_relative_inputs(recipe=recipe, ingredient=None)

    def update_recipe_identifier(self, identifier: str) -> None:
        self.main_window.label_selected_recipe_identifier.setText(f"Recipe Details:   {identifier}")

    def update_ingredient_identifier(self, ingredient: Ingredient | None) -> None:
        label = self.main_window.label_selected_ingredient_identifier
        if ingredient is None:
            label.setText("Ingredient:   /")
        else:
            label.setText(f"Ingredient:   {ingredient.identifier_string}")

    def update_recipe_descriptions(self, description: str) -> None:
        self.description_input.blockSignals(True)
        self.description_input.setText(description)
        self.description_input.blockSignals(False)

    def update_recipe_details(self, recipe: Recipe):
        measured_mass_input: QDoubleSpinBox = self.main_window.doubleSpinBox_recipe_measured_mass
        mass_reduction_input: QDoubleSpinBox = self.main_window.doubleSpinBox_mass_reduction

        measured_mass_input.blockSignals(True)
        measured_mass_input.setValue(recipe.net_mass_data.measured_value)
        measured_mass_input.blockSignals(False)

        mass_reduction_input.blockSignals(True)
        mass_reduction_input.setValue(recipe.net_mass_data.reduction)
        mass_reduction_input.blockSignals(False)

    def update_calculated_recipe_details(self, recipe: Recipe):
        self.main_window.doubleSpinBox_net_mass_total.setValue(recipe.get_net_measured_mass())
        self.main_window.doubleSpinBox_mass_ratio.setValue(recipe.get_net_mass_ratio())

    def update_adjust_for_evaporation_option(self, recipe: Recipe):
        if recipe.net_mass_data.adjust_for_evaporation:
            self.main_window.groupBox_measured_mass.blockSignals(True)
            self.main_window.groupBox_measured_mass.setChecked(True)
            self.main_window.groupBox_measured_mass.blockSignals(False)
        else:
            self.main_window.groupBox_measured_mass.blockSignals(True)
            self.main_window.groupBox_measured_mass.setChecked(False)
            self.main_window.groupBox_measured_mass.blockSignals(False)

        self.update_mass_input_field_visibility(visible=recipe.net_mass_data.adjust_for_evaporation)

    def update_mass_input_field_visibility(self, visible: bool):
        inputs_frame = self.main_window.frame_measured_mass_inputs
        inputs_frame.setVisible(visible)
        # for i in range(self.main_window.verticalLayout_groupbox_mass_inputs.count()):
        #     widget = self.main_window.verticalLayout_groupbox_mass_inputs.itemAt(i).widget()
        #     if widget:
        #         widget.setVisible(visible)
        self.main_window.groupBox_measured_mass.adjustSize()

    def update_relative_amount_cbox(self, recipe: Recipe | None, selected_ingredient: Ingredient | None) -> None:
        """
        Updates the ingredients combobox for ingredient amount definition relative to another ingredient.
        Does not allow for an ingredient to reference itself in relative amount definition.
        """
        cbox: QComboBox = self.main_window.comboBox_relative_amount_ingredient

        cbox.blockSignals(True)
        cbox.clear()
        cbox.addItem("None", userData=None)
        if recipe is not None:
            for ingredient in recipe.ingredients.values():
                if ingredient == selected_ingredient:
                    continue
                cbox.addItem(ingredient.identifier_string, userData=ingredient.item_id)
        cbox.blockSignals(False)

        if selected_ingredient is None:
            return

        if selected_ingredient.amount_relative_to is None:
            index = 0
        else:
            index = cbox.findText(selected_ingredient.amount_relative_to.identifier_string)

        cbox.blockSignals(True)
        cbox.setCurrentIndex(index)
        cbox.blockSignals(False)

    def update_amount_definition_cbox(self, ingredient: Ingredient | None):
        """
        Updates the amount definition combobox to display the setting for the currently selected ingredient.
        """
        cbox: QComboBox = self.main_window.comboBox_ingredient_amount_definition
        if ingredient is not None:
            index = cbox.findText(ingredient.amount_definition.value)
        else:
            index = 0

        cbox.blockSignals(True)
        cbox.setCurrentIndex(index)
        cbox.blockSignals(False)

    def update_net_amount_definition_cbox(self, ingredient: Ingredient | None):
        """
        Updates the net amount definition combobox to display the setting for the currently selected ingredient.
        """
        cbox: QComboBox = self.main_window.comboBox_ingredient_net_amount_definition
        if ingredient is not None:
            index = cbox.findText(ingredient.net_amount_definition.value)
        else:
            index = 0

        cbox.blockSignals(True)
        cbox.setCurrentIndex(index)
        cbox.blockSignals(False)

    def update_relative_inputs(self, recipe: Recipe | None, ingredient: Ingredient | None) -> None:
        """
        Updates relative amount inputs based on selected Recipe and Ingredient.
        """
        if recipe is None or ingredient is None:
            self.set_relative_inputs_status(active=False)
        else:
            self.set_relative_inputs_status(active=True)

        self.update_ingredient_identifier(ingredient=ingredient)
        self.update_relative_amount_cbox(recipe=recipe, selected_ingredient=ingredient)
        self.update_amount_definition_cbox(ingredient=ingredient)
        self.update_net_amount_definition_cbox(ingredient=ingredient)

    def set_ingredient_product_item(self, product_index: int) -> None:
        """
        Method sets the Product item of the Ingredient object in the Recipe data based on user selection.
        :param product_index: Index of the Product in the catalogue
        """
        selected_row = self.table.currentRow()

        product = self.ctr_data.product_catalogue.get(product_index, None)
        if product is None:
            return

        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            return None

        ingredient_id = self.table.get_current_integer_value(self.column.index(TableCol.ID))
        ingredient = recipe.get_ingredient(ingredient_id)
        if ingredient is None:
            return

        ingredient.product = product

        event_manager().emit_data_changed(f"Recipes Page: Changed ingredient Product item of recipe ID "
                                          f"{self.selected_recipe_id} at row {selected_row} "
                                          f"to {product.identifier_string}")
        self.refresh_ingredients_table()
        """Setting of current cell after refreshing the table ensures focus on the
           searchable combobox, enabling continuous scrolling to select the desired item,
           in combination with custom wheelEvent filtering based on focus.
           Blocking signals is required due to connected currentItemChanged signal."""
        self.table.blockSignals(True)
        self.table.setCurrentCell(selected_row, self.column.index(TableCol.INGREDIENT))
        self.table.blockSignals(False)

        self.update_relative_inputs(recipe=recipe, ingredient=ingredient)

    def set_recipe_adjust_for_evaporation(self):
        """
        Method sets the optional recipe net nutrition value calculation based on user selection.
        """
        checked = self.main_window.groupBox_measured_mass.isChecked()
        self.update_mass_input_field_visibility(visible=checked)

        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            print("Recipe is None! Can't set recipe mass calc method")
            return

        recipe.net_mass_data.adjust_for_evaporation = checked

        event_manager().emit_data_changed(f"Recipes Page: Changed calculation with water evaporation option "
                                          f"to {checked} for recipe {recipe.identifier_string}")

    def set_recipe_description(self):
        """
        Method sets the recipe description based on user inputs.

        WIP - Requires parsing and removal of forbidden characters (csv savefile delimiters)!
        """
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            print("Recipe is None! Can't set recipe description")
            return
        description = self.description_input.toPlainText()
        recipe.additional_data.description = description

        event_manager().emit_data_changed(f"Recipes Page: Changed description for "
                                          f"recipe {recipe.identifier_string}")

    def set_recipe_measured_mass(self):
        """
        Method sets the recipe measured mass based on user input.
        """
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            print("Recipe is None! Can't set recipe measured mass")
            return

        value = self.main_window.doubleSpinBox_recipe_measured_mass.value()
        recipe.net_mass_data.measured_value = value

        event_manager().emit_data_changed(f"Recipes Page: Changed measured net mass for "
                                          f"recipe {recipe.identifier_string}")
        self.update_calculated_recipe_details(recipe=recipe)
        self.refresh_summary_total_rows()

    def set_recipe_mass_reduction(self):
        """
        Method sets the recipe mass reduction based on user input.
        """
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            print("Recipe is None! Can't set recipe mass reduction")
            return

        value = self.main_window.doubleSpinBox_mass_reduction.value()
        recipe.net_mass_data.reduction = value

        event_manager().emit_data_changed(f"Recipes Page: Changed net mass reduction for "
                                          f"recipe {recipe.identifier_string}")
        self.update_calculated_recipe_details(recipe=recipe)
        self.refresh_summary_total_rows()

    def set_recipe_data(self, changed_item: QTableWidgetItem) -> None:
        """
        Method modifies recipe data (gross and net amount) based on user inputs in the ingredients table.
        """
        row_index = changed_item.row()

        ingredient: Ingredient = self.get_selected_ingredient(selected_row=row_index)
        if ingredient is None:
            return

        ingredient.amount = self.table.get_current_float_value(self.column.index(TableCol.AMOUNT), row_index)
        ingredient.net_amount = self.table.get_current_float_value(self.column.index(TableCol.NET_AMOUNT), row_index)

        event_manager().emit_data_changed(f"Recipes Page: Changed ingredient {ingredient.identifier_string} "
                                          f"amounts of recipe ID {self.selected_recipe_id}")
        self.refresh_ingredients_table_row(ingredient)

    def set_ingredient_amount_definition(self):
        """
        Method sets the currently selected ingredient amount definition attribute based on user selection.
        """
        ingredient: Ingredient = self.get_selected_ingredient()
        if ingredient is None:
            return

        definition = self.get_amount_definition()
        ingredient.amount_definition = definition

        event_manager().emit_data_changed(f"Recipes Page: Changed ingredient {ingredient.identifier_string} "
                                          f"amount definition to {definition.value}")

        selected_row = self.table.currentRow()
        self.refresh_ingredients_table()
        self.table.blockSignals(True)
        self.table.setCurrentCell(selected_row, self.column.index(TableCol.ID))
        self.table.blockSignals(False)
        self.update_relative_inputs(recipe=self.get_recipe(recipe_id=self.selected_recipe_id), ingredient=ingredient)

    def set_ingredient_relative_amount_reference(self):
        """
        Method sets the currently selected ingredient amount relative to the selected other ingredient.
        """
        recipe = self.get_recipe(recipe_id=self.selected_recipe_id)
        if recipe is None:
            print("Recipe is None! Can't set ingredient relative amount reference!")
            return

        ingredient_id = self.table.get_current_integer_value(self.column.index(TableCol.ID))
        curr_ingredient = recipe.get_ingredient(ingredient_id)
        if curr_ingredient is None:
            print("Current ingredient is None! Can't set ingredient relative amount reference!")
            return

        rel_ingredient_id = self.get_amount_relative_ingredient_id()
        rel_ingredient = recipe.get_ingredient(rel_ingredient_id)
        if rel_ingredient is None:
            print("Relative ingredient is None! Can't set ingredient relative amount reference!")
            return

        curr_ingredient.amount_relative_to = rel_ingredient
        circular_references = curr_ingredient.detect_circular_reference()

        if circular_references:
            curr_ingredient.amount_relative_to = None

            QMessageBox.information(
                self.mw,
                "Circular Reference Error",
                f"Detected a circular reference between ingredients "
                f"{curr_ingredient.identifier_string} and {rel_ingredient.identifier_string}!\n"
                f"Undoing relative ingredient definition for {curr_ingredient.identifier_string}."
            )

        else:
            event_manager().emit_data_changed(f"Recipes Page: Changed ingredient {curr_ingredient.identifier_string} "
                                              f"amount relative to {rel_ingredient.identifier_string}")

        selected_row = self.table.currentRow()
        self.refresh_ingredients_table()
        self.table.blockSignals(True)
        self.table.setCurrentCell(selected_row, self.column.index(TableCol.ID))
        self.table.blockSignals(False)
        self.update_relative_inputs(recipe=recipe, ingredient=curr_ingredient)

    def set_ingredient_net_amount_definition(self):
        """
        Method sets the currently selected ingredient net amount definition attribute based on user selection.
        """
        ingredient: Ingredient = self.get_selected_ingredient()
        if ingredient is None:
            return

        definition = self.get_net_amount_definition()
        ingredient.net_amount_definition = definition

        event_manager().emit_data_changed(f"Recipes Page: Changed ingredient {ingredient.identifier_string} "
                                          f"net amount definition to {definition.value}")

        selected_row = self.table.currentRow()
        self.refresh_ingredients_table()
        self.table.blockSignals(True)
        self.table.setCurrentCell(selected_row, self.column.index(TableCol.ID))
        self.table.blockSignals(False)
        self.update_relative_inputs(recipe=self.get_recipe(recipe_id=self.selected_recipe_id), ingredient=ingredient)

