
from Core.daily_intake import DailyIntake
from Core.serving import Serving
from Core.product import NutritionData
from Core.enums import ServingType
from GUI.MainWindow.page_base import MainWindowPage
from GUI.MainWindow.chart_widget import DailyIntakeWidget, DonutChartTargetWidget
from GUI.Common.event_manager import event_manager
from GUI.Common.custom_widgets import (CustomDataTable, CustomTableWidgetItem, SearchableComboBox,
                                       DoubleSpinBoxDelegate, new_table_item_ne, new_table_item,
                                       CustomCalendarWidget)
from Settings.app_env import get_dark_icon, get_light_icon
from Settings.config_enums import ConfirmationCategory

from enum import Enum, auto
# from timeit import default_timer as timer
from PySide6.QtCore import Qt, QSize, QDate, QPoint
from PySide6.QtGui import QTextCharFormat, QBrush, QColor, QCursor, QIcon
from PySide6.QtWidgets import (QLayout, QHeaderView, QTableWidgetItem, QSplitter, QMenu, QMessageBox, QLabel,
                               QVBoxLayout, QWidget, QSpinBox, QAbstractSpinBox, QHBoxLayout)


class NutritionTargetInput(Enum):
    CALORIES = "Calories"
    FAT = "Fat"
    CARBS = "Carbs"
    PROTEIN = "Protein"


class TableCol(Enum):
    STAR = auto()
    NAME = auto()
    PORTION = auto()
    CALORIES = auto()
    FAT = auto()
    CARBS = auto()
    PROTEIN = auto()
    FILLER = auto()


class PageDailyIntake(MainWindowPage):
    def __init__(self, mw):
        super().__init__(mw)
        self.mw = mw

        self.table = CustomDataTable(self.mw)
        self.layout: QLayout = self.main_window.verticalLayout_frame_dashboard_right
        self.layout.addWidget(self.table)

        self.chart_widget = DailyIntakeWidget(self.mw)

        self.nutrition_target_inputs: dict[NutritionTargetInput, QSpinBox] = {}

        self.calorie_target_widget = DonutChartTargetWidget(self.mw, unit_label="kcal")
        self.fat_target_widget = DonutChartTargetWidget(self.mw, unit_label="g")
        self.carbs_target_widget = DonutChartTargetWidget(self.mw, unit_label="g")
        self.protein_target_widget = DonutChartTargetWidget(self.mw, unit_label="g")

        self.calendar = CustomCalendarWidget()

        self.column: list[TableCol] = [
            TableCol.STAR,
            TableCol.NAME,
            TableCol.PORTION,
            TableCol.CALORIES,
            TableCol.FAT,
            TableCol.CARBS,
            TableCol.PROTEIN,
            TableCol.FILLER,
        ]

        self.icon_star_full: QIcon = get_light_icon("star_full.png")
        self.icon_star_empty: QIcon = get_light_icon("star_empty.png")

        self.selected_date: QDate = QDate.currentDate()

        self.setup_page()

    @property
    def current_date_string(self) -> str:
        return self.selected_date.toString(Qt.DateFormat.ISODate)

    @staticmethod
    def get_date_from_string(date: str) -> QDate:
        return QDate.fromString(date, format=Qt.DateFormat.ISODate)

    def setup_page(self):
        self.setup_daily_intake_table()
        self.setup_custom_spinbox_delegate()
        self.setup_splitter()
        self.setup_buttons()
        self.setup_tooltips()
        self.set_current_date()
        self.setup_chart_widget()
        self.setup_nutrition_target_widgets()
        self.setup_calendar_widget()
        self.update_calendar_display()
        self.table.set_lmb_action_method(self.toggle_favorite_selection)
        self.table.set_rmb_action_method(self.custom_rmb_action_menu)

    def setup_daily_intake_table(self) -> None:
        headers = [
            ("", 25, self.column.index(TableCol.STAR)),
            ("Serving Item", 180, self.column.index(TableCol.NAME)),
            ("Portion\n[g]", 60, self.column.index(TableCol.PORTION)),
            ("Calories\n[kcal]", 60, self.column.index(TableCol.CALORIES)),
            ("Fat\n[g]", 60, self.column.index(TableCol.FAT)),
            ("Carbs\n[g]", 60, self.column.index(TableCol.CARBS)),
            ("Protein\n[g]", 60, self.column.index(TableCol.PROTEIN)),
            ("", 1, self.column.index(TableCol.FILLER))
        ]

        self.table.set_headers_specified(headers)
        self.table.set_header_settings(height=40)

        self.table.horizontalHeader().setSectionResizeMode(self.column.index(TableCol.FILLER),
                                                           QHeaderView.ResizeMode.Stretch)
        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_daily_intake_data)
        # self.table.setSortingEnabled(True)

    def setup_custom_spinbox_delegate(self) -> None:
        portion_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=9999.0, min_val=0.0, decimals=1, decimals_display=0, val_step=5.0)
        nutrition_value_delegate = DoubleSpinBoxDelegate(
            self.table, max_val=9999.0, min_val=0.0, decimals=1, decimals_display=1)

        self.table.setItemDelegateForColumn(self.column.index(TableCol.PORTION), portion_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.CALORIES), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.FAT), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.CARBS), nutrition_value_delegate)
        self.table.setItemDelegateForColumn(self.column.index(TableCol.PROTEIN), nutrition_value_delegate)

    def setup_splitter(self) -> None:
        v_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_window.horizontalLayout_dashboard.addWidget(v_splitter)
        v_splitter.addWidget(self.main_window.frame_dashboard_left)
        v_splitter.addWidget(self.main_window.frame_dashboard_right)
        v_splitter.setSizes([700, 550])

    def setup_buttons(self) -> None:
        self.main_window.pushButton_add_catalogue_item.clicked.connect(self.add_new_product)
        self.main_window.pushButton_add_recipe_item.clicked.connect(self.add_new_recipe)
        self.main_window.pushButton_previous_date.clicked.connect(self.set_previous_date)
        self.main_window.pushButton_next_date.clicked.connect(self.set_next_date)
        self.main_window.pushButton_calendar_toggle.clicked.connect(self.update_calendar_display)

    def setup_tooltips(self) -> None:
        self.main_window.pushButton_add_catalogue_item.setToolTip(
            "Add a new product to the daily intake table.")
        self.main_window.pushButton_add_recipe_item.setToolTip(
            "Add a new recipe to the daily intake table.")
        self.main_window.pushButton_previous_date.setToolTip(
            "Switch to previous calendar day.")
        self.main_window.pushButton_next_date.setToolTip(
            "Switch to next calendar day.")
        self.main_window.pushButton_calendar_toggle.setToolTip(
            "Calendar display toggle.")

    def row_items_dictionary(self, index: int, serving: Serving) -> dict[int, QTableWidgetItem | SearchableComboBox]:
        """
        Returns a dictionary of QTableWidgetItems for adding to the table row.
        """
        nutrition_data = serving.get_consumed_nutrition_values()
        item_type = serving.item_type

        item_star = QTableWidgetItem()
        if self.ctr_data.serving_in_favorites(serving=serving):
            item_star.setIcon(self.icon_star_full)
        else:
            item_star.setIcon(self.icon_star_empty)
        item_star.setFlags(Qt.ItemFlag.ItemIsEnabled |
                           Qt.ItemFlag.ItemIsSelectable)
        item_name = SearchableComboBox()
        text_color = QColor(255, 255, 255, 255)
        background_color = QColor(255, 255, 255, 255)
        if item_type is ServingType.PRODUCT:
            background_color = QColor(0, 0, 139, 100)
            item_name.addItems(self.ctr_data.get_all_product_names())
            item_index = item_name.findText(serving.item_name)
            item_name.setCurrentIndex(item_index)
            item_name.currentIndexChanged.connect(self.set_product_item)

        elif item_type is ServingType.RECIPE:
            background_color = QColor(155, 155, 155, 100)
            item_name.addItems(self.ctr_data.get_all_recipe_names())
            item_index = item_name.findText(serving.item_name)
            item_name.setCurrentIndex(item_index)
            item_name.currentIndexChanged.connect(self.set_recipe_item)

        font = item_name.lineEdit().font()
        font.setBold(True)
        item_name.lineEdit().setFont(font)
        item_name.set_colors(text_color, background_color)
        item_portion = new_table_item(value=serving.portion,
                                      identifier_id=index,
                                      identifier_type=item_type)
        item_calories = new_table_item_ne(value=nutrition_data.calories)
        item_fat = new_table_item_ne(value=nutrition_data.fat)
        item_carbs = new_table_item_ne(value=nutrition_data.carbs)
        item_protein = new_table_item_ne(value=nutrition_data.protein)

        custom_table_dict = {
            self.column.index(TableCol.STAR): item_star,
            self.column.index(TableCol.NAME): item_name,
            self.column.index(TableCol.PORTION): item_portion,
            self.column.index(TableCol.CALORIES): item_calories,
            self.column.index(TableCol.FAT): item_fat,
            self.column.index(TableCol.CARBS): item_carbs,
            self.column.index(TableCol.PROTEIN): item_protein,
        }

        return custom_table_dict

    def summary_row_items_dictionary(self) -> dict[int, QTableWidgetItem]:
        """
        Returns a dictionary of QTableWidgetItems for adding to the table summary row.
        """
        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            nutrition_data = NutritionData()
        else:
            nutrition_data = intake_data.get_total_consumed_nutrition_data()

        self.chart_widget.update_data(data=nutrition_data)
        self.update_intake_target_charts(data=nutrition_data)

        item_name = new_table_item_ne(value="Total")
        item_portion = new_table_item_ne(value="-")
        item_calories = new_table_item_ne(value=nutrition_data.calories)
        item_fat = new_table_item_ne(value=nutrition_data.fat)
        item_carbs = new_table_item_ne(value=nutrition_data.carbs)
        item_protein = new_table_item_ne(value=nutrition_data.protein)

        custom_table_dict = {
            self.column.index(TableCol.NAME): item_name,
            self.column.index(TableCol.PORTION): item_portion,
            self.column.index(TableCol.CALORIES): item_calories,
            self.column.index(TableCol.FAT): item_fat,
            self.column.index(TableCol.CARBS): item_carbs,
            self.column.index(TableCol.PROTEIN): item_protein,
        }

        return custom_table_dict

    def get_intake_data(self, date: str) -> DailyIntake | None:
        if date in self.ctr_data.daily_intake_record.keys():
            return self.ctr_data.daily_intake_record[date]
        else:
            return None

    def refresh_table(self) -> None:
        """
        Refreshes the table data from the current tracker data.
        Table itemChanged signal is disconnected for the duration of the data refresh.
        """
        self.table.set_item_changed_signal(connection_status=False, on_changed=self.set_daily_intake_data)
        self.table.save_scroll_bar_location()
        self.table.clear_table()

        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is not None:
            for product_index, item in enumerate(intake_data.consumed_products):
                self.table.add_table_row(self.row_items_dictionary(product_index, item))
            for recipe_index, item in enumerate(intake_data.consumed_recipes):
                self.table.add_table_row(self.row_items_dictionary(recipe_index, item))
        else:
            print(f"No daily intake data for calendar date {self.current_date_string}")

        self.add_summary_row()
        self.table.restore_scroll_bar_location()
        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_daily_intake_data)

    def refresh_table_row(self, serving: Serving, serving_index: int, selected_row: int) -> None:
        """
        Refreshes data in the daily intake table only for the given table row index.
        """
        self.table.set_item_changed_signal(connection_status=False, on_changed=self.set_daily_intake_data)

        self.table.update_table_row(selected_row, self.row_items_dictionary(serving_index, serving))
        self.refresh_summary_row()

        self.table.set_item_changed_signal(connection_status=True, on_changed=self.set_daily_intake_data)

    def add_summary_row(self) -> None:
        self.table.add_table_row(self.summary_row_items_dictionary())

    def refresh_summary_row(self) -> None:
        self.table.update_table_row(row=self.table.rowCount() - 1, row_items=self.summary_row_items_dictionary())

    def set_current_date(self) -> None:
        self.main_window.dateEdit_daily_intake_date.setDate(self.selected_date)

    def setup_chart_widget(self):
        self.main_window.verticalLayout_frame_totals_diagram.addWidget(self.chart_widget)
        self.main_window.verticalLayout_frame_totals_diagram.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.chart_widget.setMaximumWidth(400)
        self.chart_widget.setMinimumSize(QSize(400, 250))

    def get_spinbox(self, name: str) -> QSpinBox:
        return self.mw.findChild(QSpinBox, name)  # noqa

    def setup_nutrition_target_widgets(self):
        def group_donut_chart_w_label(widget: DonutChartTargetWidget,
                                      target_input: NutritionTargetInput,
                                      unit: str = "") -> QWidget:
            text_label = target_input.value
            label = QLabel(text_label)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            unit_label = QLabel(f"[{unit}]")
            unit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            spinbox = QSpinBox()
            spinbox.setObjectName(f"spinBox_nutrition_target_{text_label}")
            spinbox.setMaximumSize(QSize(60, 30))
            spinbox.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            spinbox.setMaximum(9999)
            spinbox.setSingleStep(0)
            spinbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
            spinbox.editingFinished.connect(self.on_intake_target_data_change)

            spinbox_layout = QHBoxLayout()
            spinbox_layout.addWidget(spinbox)

            layout = QVBoxLayout()
            layout.addWidget(widget)
            layout.addWidget(label)
            layout.addWidget(unit_label)
            layout.addLayout(spinbox_layout)

            container = QWidget()
            container.setLayout(layout)

            self.nutrition_target_inputs[target_input] = spinbox

            return container

        self.main_window.horizontalLayout_frame_intake_target.addWidget(
            group_donut_chart_w_label(self.calorie_target_widget,
                                      target_input=NutritionTargetInput.CALORIES,
                                      unit="kcal")
        )
        self.main_window.horizontalLayout_frame_intake_target.addWidget(
            group_donut_chart_w_label(self.fat_target_widget,
                                      target_input=NutritionTargetInput.FAT,
                                      unit="g")
        )
        self.main_window.horizontalLayout_frame_intake_target.addWidget(
            group_donut_chart_w_label(self.carbs_target_widget,
                                      target_input=NutritionTargetInput.CARBS,
                                      unit="g")
        )
        self.main_window.horizontalLayout_frame_intake_target.addWidget(
            group_donut_chart_w_label(self.protein_target_widget,
                                      target_input=NutritionTargetInput.PROTEIN,
                                      unit="g")
        )

        self.main_window.horizontalLayout_frame_intake_target.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def setup_calendar_widget(self):
        # collapsable_widget = CollapsibleSectionWidget(title="Calendar")
        self.main_window.verticalLayout_frame_calendar.addWidget(self.calendar)
        self.main_window.frame_calendar.setMinimumHeight(200)
        self.main_window.frame_calendar.setMaximumHeight(200)
        self.main_window.verticalLayout_frame_calendar.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.calendar.set_rmb_action_method(self.action_menu_calendar_selection)

    def on_intake_target_data_change(self) -> None:
        """
        Updates daily nutrition intake target values and visualization charts
        based on user inputs in the daily target spinboxes.
        """
        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            nutrition_data = NutritionData()
        else:
            nutrition_data = intake_data.get_total_consumed_nutrition_data()

        calorie_target = self.nutrition_target_inputs[NutritionTargetInput.CALORIES].value()
        fat_target = self.nutrition_target_inputs[NutritionTargetInput.FAT].value()
        carbs_target = self.nutrition_target_inputs[NutritionTargetInput.CARBS].value()
        protein_target = self.nutrition_target_inputs[NutritionTargetInput.PROTEIN].value()

        target_data = NutritionData(
            calories=calorie_target,
            fat=fat_target,
            carbs=carbs_target,
            protein=protein_target)

        self.ctr_data.nutrition_targets = target_data
        event_manager().emit_data_changed(f"Daily Intake Page: Changed daily intake nutrition targets")

        self.update_intake_target_charts(data=nutrition_data)

    def update_intake_target_charts(self, data: NutritionData) -> None:
        """
        Updates daily nutrition intake target charts based on user inputs.
        """
        target = self.ctr_data.nutrition_targets

        self.calorie_target_widget.set_values(current=data.calories, target=target.calories)
        self.fat_target_widget.set_values(current=data.fat, target=target.fat)
        self.carbs_target_widget.set_values(current=data.carbs, target=target.carbs)
        self.protein_target_widget.set_values(current=data.protein, target=target.protein)

    def update_intake_target_inputs(self):
        """
        Updates daily nutrition intake targets to reflect current CTR data.
        """
        target = self.ctr_data.nutrition_targets

        def set_input_value(input_spinbox: QSpinBox, value: float):
            input_spinbox.blockSignals(True)
            input_spinbox.setValue(int(value))
            input_spinbox.blockSignals(False)

        set_input_value(
            input_spinbox=self.nutrition_target_inputs[NutritionTargetInput.CALORIES],
            value=target.calories)

        set_input_value(
            input_spinbox=self.nutrition_target_inputs[NutritionTargetInput.FAT],
            value=target.fat)

        set_input_value(
            input_spinbox=self.nutrition_target_inputs[NutritionTargetInput.CARBS],
            value=target.carbs)

        set_input_value(
            input_spinbox=self.nutrition_target_inputs[NutritionTargetInput.PROTEIN],
            value=target.protein)

    def update_calendar_display(self):
        if self.main_window.pushButton_calendar_toggle.isChecked():
            # self.animation.stop()
            # self.animation.setStartValue(self.options_area.maximumHeight())
            # self.animation.setEndValue(self.options_area.sizeHint().height())
            # self.animation.start()
            print("Setting calendar visible...")
            self.main_window.frame_calendar.setVisible(True)
        else:
            # self.animation.stop()
            # self.animation.setStartValue(self.options_area.maximumHeight())
            # self.animation.setEndValue(0)
            # self.animation.start()
            # self.animation.finished.connect(self.on_animation_finished)
            print("Hiding calendar...")
            self.main_window.frame_calendar.setVisible(False)

    def set_dark_theme(self) -> None:
        self.set_dark_theme_button_icons()
        self.chart_widget.update_theme_colors(theme=self.mw.window_theme)
        self.calorie_target_widget.update_theme_colors(theme=self.mw.window_theme)
        self.fat_target_widget.update_theme_colors(theme=self.mw.window_theme)
        self.carbs_target_widget.update_theme_colors(theme=self.mw.window_theme)
        self.protein_target_widget.update_theme_colors(theme=self.mw.window_theme)

    def set_light_theme(self) -> None:
        self.set_light_theme_button_icons()
        self.chart_widget.update_theme_colors(theme=self.mw.window_theme)
        self.calorie_target_widget.update_theme_colors(theme=self.mw.window_theme)
        self.fat_target_widget.update_theme_colors(theme=self.mw.window_theme)
        self.carbs_target_widget.update_theme_colors(theme=self.mw.window_theme)
        self.protein_target_widget.update_theme_colors(theme=self.mw.window_theme)

    def set_dark_theme_button_icons(self) -> None:
        icons = {
            "catalogue_dark.png": self.main_window.pushButton_add_catalogue_item,
            "recipe_dark.png": self.main_window.pushButton_add_recipe_item,
            "left_arrow_dark.png": self.main_window.pushButton_previous_date,
            "right_arrow_dark.png": self.main_window.pushButton_next_date,
            "calendar_dark.png": self.main_window.pushButton_calendar_toggle,
        }

        for icon, button in icons.items():
            button.setIcon(get_dark_icon(icon))
            button.setIconSize(QSize(24, 24))

        self.icon_star_full: QIcon = get_dark_icon("star_full_dark.png")
        self.icon_star_empty: QIcon = get_dark_icon("star_empty_dark.png")

    def set_light_theme_button_icons(self) -> None:
        icons = {
            "catalogue.png": self.main_window.pushButton_add_catalogue_item,
            "recipe.png": self.main_window.pushButton_add_recipe_item,
            "left_arrow.png": self.main_window.pushButton_previous_date,
            "right_arrow.png": self.main_window.pushButton_next_date,
            "calendar.png": self.main_window.pushButton_calendar_toggle,
        }

        for icon, button in icons.items():
            button.setIcon(get_light_icon(icon))
            button.setIconSize(QSize(24, 24))

        self.icon_star_full: QIcon = get_light_icon("star_full.png")
        self.icon_star_empty: QIcon = get_light_icon("star_empty.png")

    def get_selected_serving_data(self, selected_row: int | None = None) -> tuple | None:
        """
        Method returns the currently selected serving (Product or Recipe) data.
        """
        if selected_row is None:
            selected_row = self.table.currentRow()
        item = self.table.item(selected_row, self.column.index(TableCol.PORTION))
        if not isinstance(item, CustomTableWidgetItem):
            print(f"Item is not an instance of CustomTableWidgetItem at row {selected_row}! {item = }")
            return None

        item_index = item.identifier_id
        item_type = item.identifier_type

        return item_index, item_type

    def get_selected_serving(self, selected_row: int | None = None) -> Serving | None:
        """
        Method returns the currently selected serving (Product or Recipe).
        """
        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}")
            return None

        serving_data = self.get_selected_serving_data(selected_row)
        if serving_data is None:
            return None
        item_index, item_type = serving_data

        # print(f"Returning item type {item_type} at index {item_index}")
        if item_type is ServingType.PRODUCT:
            return intake_data.consumed_products[item_index]
        elif item_type is ServingType.RECIPE:
            return intake_data.consumed_recipes[item_index]
        else:
            return None

    def get_selected_servings(self, selected_table_rows: list[int]) -> list[Serving]:
        """
        Returns all selected servings in the table based on selected table rows.
        """
        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}, "
                  f"unable to get all selected servings.")
            return []

        selected_servings: list[Serving] = []

        for row in selected_table_rows:
            item = self.table.item(row, self.column.index(TableCol.PORTION))
            if not isinstance(item, CustomTableWidgetItem):
                continue

            item_index = item.identifier_id
            item_type = item.identifier_type

            if item_type is ServingType.PRODUCT:
                selected_servings.append(intake_data.consumed_products[item_index])
            elif item_type is ServingType.RECIPE:
                selected_servings.append(intake_data.consumed_recipes[item_index])

        return selected_servings

    def custom_rmb_action_menu(self, event) -> None:
        table_item = self.table.itemAt(event.pos())
        if table_item is None:
            self.action_menu_no_selection()
            return

        selected_table_rows = self.table.get_selected_rows()
        if len(selected_table_rows) == 0:
            self.action_menu_no_selection()
            return

        elif len(selected_table_rows) == 1:
            selected_serving: Serving = self.get_selected_serving(selected_row=table_item.row())
            if selected_serving is None:
                self.action_menu_no_selection()
                return
            if selected_serving.item_type is ServingType.PRODUCT:
                self.action_menu_single_product_selection(serving=selected_serving)
            elif selected_serving.item_type is ServingType.RECIPE:
                self.action_menu_single_recipe_selection(serving=selected_serving)
        else:
            selected_servings = self.get_selected_servings(selected_table_rows)
            self.action_menu_multiple_selection(servings=selected_servings)

    def action_menu_calendar_selection(self, position: QPoint, date_string: str) -> None:
        menu = QMenu(self.mw)
        menu.addAction("View Details", lambda: self.on_view_daily_intake_details(date_string))
        menu.addAction("Remove Record", lambda: self.on_remove_daily_intake_record(date_string))
        menu.exec(position)

    def action_menu_no_selection(self) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Add New Product", self.add_new_product)
        menu.addAction("Add New Recipe", self.add_new_recipe)
        menu.addSeparator()
        menu.addAction("Duplicate Previous", self.duplicate_previous_date_record)
        menu.addAction("Refresh Table", self.refresh_table)

        menu.exec_(QCursor.pos())

    def action_menu_single_product_selection(self, serving: Serving) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Remove", lambda: self.on_remove_product_item(serving))
        menu.addSeparator()
        menu.addAction("Go To Product Definition", lambda: self.on_go_to_product(serving))
        menu.addSeparator()
        menu.addAction("Add New Product", self.add_new_product)
        menu.addAction("Add New Recipe", self.add_new_recipe)
        menu.addAction("Refresh Table", self.refresh_table)

        menu.exec_(QCursor.pos())

    def action_menu_single_recipe_selection(self, serving: Serving) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Remove", lambda: self.on_remove_recipe_item(serving))
        menu.addSeparator()
        menu.addAction("Go To Recipe Definition", lambda: self.on_go_to_recipe(serving))
        menu.addSeparator()
        menu.addAction("Add New Product", self.add_new_product)
        menu.addAction("Add New Recipe", self.add_new_recipe)
        menu.addAction("Refresh Table", self.refresh_table)

        menu.exec_(QCursor.pos())

    def action_menu_multiple_selection(self, servings: list[Serving]) -> None:
        menu = QMenu(self.mw)
        menu.addAction("Remove All", lambda: self.on_remove_multiple_servings(servings))
        menu.addSeparator()
        menu.addAction("Add New Product", self.add_new_product)
        menu.addAction("Add New Recipe", self.add_new_recipe)
        menu.addAction("Refresh Table", self.refresh_table)

        menu.exec_(QCursor.pos())

    def highlight_dates_with_data(self, dates: list[QDate]) -> None:
        format_highlight = QTextCharFormat()
        format_highlight.setBackground(QBrush(QColor("green")))

        for entry in dates:
            self.calendar.setDateTextFormat(entry, format_highlight)

    def highlight_all_dates_with_data(self):
        all_dates_w_data = [QDate.fromString(date, format=Qt.DateFormat.ISODate)
                            for date in self.ctr_data.daily_intake_record.keys()]

        self.highlight_dates_with_data(all_dates_w_data)

    def clear_all_date_formats(self):
        formatted_dates = self.calendar.dateTextFormat()
        for date in formatted_dates.keys():
            self.calendar.setDateTextFormat(date, QTextCharFormat())

    def add_new_product(self) -> None:
        date = self.current_date_string
        intake_data = self.get_intake_data(date)

        if intake_data is None:
            intake_data = self.ctr_data.add_daily_intake(date=date)
            event_manager().emit_data_changed(f"Daily Intake Page: Added a new daily intake record for date {date}")

        serving = Serving(item_type=ServingType.PRODUCT)
        intake_data.add_consumed_product(serving)

        event_manager().emit_data_changed(f"Daily Intake Page: Added a new Product to daily intake for {date}")

        self.refresh_table()

    def add_new_recipe(self) -> None:
        date = self.current_date_string
        intake_data = self.get_intake_data(date)

        if intake_data is None:
            intake_data = self.ctr_data.add_daily_intake(date=date)
            event_manager().emit_data_changed(f"Daily Intake Page: Added a new daily intake record for date {date}")

        serving = Serving(item_type=ServingType.RECIPE)
        intake_data.add_consumed_recipe(serving)

        event_manager().emit_data_changed(f"Daily Intake Page: Added a new recipe to daily intake for {date}")

        self.refresh_table()

    def duplicate_previous_date_record(self) -> None:
        """
        Duplicates the previous calendar day intake data and adds it to the currently selected date.
        """
        previous_date = self.selected_date.addDays(-1)
        previous_date_string = previous_date.toString(Qt.DateFormat.ISODate)

        if previous_date_string not in self.ctr_data.daily_intake_record.keys():
            QMessageBox.information(
                self.mw,
                "Daily Intake Data Not Found",
                f"Daily intake data for previous date {previous_date_string} does not exist!\n"
                f"Unable to duplicate daily intake of the previous calendar day."
            )
            return

        if not self.ctr_data.daily_intake_record[previous_date_string].has_data:
            QMessageBox.information(
                self.mw,
                "Daily Intake Data Not Found",
                f"Daily intake data for previous date {previous_date_string} has no data!\n"
                f"Unable to duplicate daily intake of the previous calendar day."
            )
            return

        confirmation = self.mw.confirm_action(
            message=f"Action will override all intake entries\nfor calendar day {self.current_date_string}. Continue?",
            accept_label="Override",
            category=ConfirmationCategory.OVERRIDE_DAILY_INTAKE
        )

        if confirmation:
            self.ctr_data.duplicate_daily_intake(date_string=previous_date_string,
                                                 override_date_string=self.current_date_string)
            event_manager().emit_data_changed(f"Daily Intake Page: Overridden daily intake record of date "
                                              f"{self.current_date_string} with data from {previous_date_string}")

            self.refresh_table()

    def set_previous_date(self) -> None:
        """
        Sets the previous calendar day in the daily intake table.
        """
        self.selected_date = self.selected_date.addDays(-1)
        self.main_window.dateEdit_daily_intake_date.setDate(self.selected_date)
        self.refresh_table()

    def set_next_date(self) -> None:
        """
        Sets the next calendar day in the daily intake table.

        Automatically duplicates todays' daily intake record in its entirety for the next calendar day,
        if a daily intake record has not been created for tomorrows' date.
        """
        self.selected_date = self.selected_date.addDays(1)
        self.main_window.dateEdit_daily_intake_date.setDate(self.selected_date)

        tomorrows_date: QDate = QDate.currentDate().addDays(1)
        tomorrows_date_string = tomorrows_date.toString(Qt.DateFormat.ISODate)

        if self.selected_date == tomorrows_date:
            current_date: QDate = QDate.currentDate()
            current_date_string = current_date.toString(Qt.DateFormat.ISODate)

            if current_date_string not in self.ctr_data.daily_intake_record.keys():
                print(f"Current date {current_date_string} does not exist in CTR data! Unable to duplicate "
                      f"todays daily intake for the next calendar day {tomorrows_date_string}.")
                self.refresh_table()
                return

            if not self.ctr_data.daily_intake_record[current_date_string].has_data:
                print(f"Current date {current_date_string} has no associated data! Unable to duplicate "
                      f"todays daily intake for the next calendar day {tomorrows_date_string}.")
                self.refresh_table()
                return

            if tomorrows_date_string not in self.ctr_data.daily_intake_record.keys():
                self.ctr_data.duplicate_todays_daily_intake(date_string=tomorrows_date_string)
                event_manager().emit_data_changed(f"Daily Intake Page: Added a new daily intake record for "
                                                  f"tomorrows' date ({tomorrows_date_string}) by duplicating todays record.")
            else:
                print(f"Tomorrows date {tomorrows_date_string} already exists in CTR data. "
                      f"Skipping daily intake record duplication.")
        else:
            # print(f"Selected date {self.selected_date.toString(Qt.DateFormat.ISODate)} "
            #       f"is not tomorrows date {tomorrows_date_string}.")
            ...

        self.refresh_table()

    def set_product_item(self, product_index: int) -> None:
        """
        Method sets the Product item of the serving in the daily calorie
        intake table based on user selection in the combobox.
        :param product_index: Index of the Product in the catalogue
        """
        selected_row = self.table.currentRow()

        item = self.table.item(selected_row, self.column.index(TableCol.PORTION))
        if not isinstance(item, CustomTableWidgetItem):
            print(f"Item is not an instance of CustomTableWidgetItem at row {selected_row}! {item = }")
            return None

        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}")
            return None

        item_index = item.identifier_id     # index in the consumed Products list
        serving = intake_data.consumed_products[item_index]

        if serving is None:
            return

        product = self.ctr_data.product_catalogue.get(product_index, None)
        if product is None:
            return

        event_manager().emit_data_changed(f"Daily Intake Page: Setting Product item in row {selected_row} to "
                                          f"{product.identifier_string} for daily intake {intake_data.date}")

        serving.update_item(item=product,
                            new_item_id=product.item_id,
                            new_item_name=product.name,
                            new_item_type=product.item_type)

        self.refresh_table()
        """Setting of current cell after refreshing the table ensures focus on the
           searchable combobox, enabling continuous scrolling to select the desired item,
           in combination with custom wheelEvent filtering based on focus"""
        self.table.setCurrentCell(selected_row, self.column.index(TableCol.NAME))

    def set_recipe_item(self, recipe_id: int) -> None:
        """
        Method sets the recipe of the consumable object in the daily calorie
        intake table based on user selection in the combobox.
        :param recipe_id: Recipe ID.
        """
        selected_row = self.table.currentRow()

        item = self.table.item(selected_row, self.column.index(TableCol.PORTION))
        if not isinstance(item, CustomTableWidgetItem):
            print(f"Item is not an instance of CustomTableWidgetItem at row {selected_row}! {item = }")
            return None

        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}")
            return None

        item_index = item.identifier_id     # index in the consumed recipes list
        serving = intake_data.consumed_recipes[item_index]

        if serving is None:
            return

        recipe = self.ctr_data.recipes_record.get(recipe_id, None)
        if recipe is None:
            return

        event_manager().emit_data_changed(f"Daily Intake Page: Setting Recipe item in row {selected_row} to "
                                          f"{recipe.identifier_string} for daily intake {intake_data.date}")

        serving.update_item(item=recipe,
                            new_item_id=recipe.item_id,
                            new_item_name=recipe.name,
                            new_item_type=recipe.item_type)

        self.refresh_table()
        """Setting of current cell after refreshing the table ensures focus on the
           searchable combobox, enabling continuous scrolling to select the desired item,
           in combination with custom wheelEvent filtering based on focus"""
        self.table.setCurrentCell(selected_row, self.column.index(TableCol.NAME))

    def toggle_favorite_selection(self, event) -> None:
        index = self.table.indexAt(event.pos())
        if not index.isValid():
            return

        column = index.column()
        if column != 0:
            return

        row = index.row()
        serving = self.get_selected_serving(row)
        if serving is None:
            print(f"Error, no serving at row {row}")
            return

        # start = timer()
        favorite_status = self.ctr_data.toggle_favorite_serving(serving=serving)
        # end = timer()
        # print(f"Favorite status for {serving.identifier_string} set in {end - start} s")

        event_manager().emit_data_changed(f"Daily Intake Page: Toggled serving favorite status "
                                          f"for {serving.identifier_string} to {favorite_status}")

        self.refresh_table()

    def set_daily_intake_data(self, changed_item: QTableWidgetItem) -> None:
        """
        Modifies daily intake data based on the changed QTableWidgetItem.
        """
        row = changed_item.row()

        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}")
            return None

        serving_data = self.get_selected_serving_data(row)
        if serving_data is None:
            return None
        item_index, item_type = serving_data

        if item_type is ServingType.PRODUCT:
            serving = intake_data.consumed_products[item_index]
        elif item_type is ServingType.RECIPE:
            serving =  intake_data.consumed_recipes[item_index]
        else:
            serving = None

        if serving is None:
            print(f"Error, changed serving at row {row} column {changed_item.column()} is None!")
            return

        serving.portion = self.table.get_current_float_value(self.column.index(TableCol.PORTION), row)

        event_manager().emit_data_changed(f"Daily Intake Page: Changed serving portion size "
                                          f"for {serving.identifier_string}")
        self.refresh_table_row(serving, serving_index=item_index, selected_row=row)

    def on_go_to_product(self, serving: Serving) -> None:
        print(f"Navigating to Product {serving.item_name}... WIP - Not Implemented!")

    def on_go_to_recipe(self, serving: Serving) -> None:
        print(f"Navigating to Recipe {serving.item_name}... WIP - Not Implemented!")

    def on_remove_product_item(self, serving: Serving) -> None:
        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}")
            return None

        if serving not in intake_data.consumed_products:
            print(f"Serving {serving.identifier_string} not found in daily intake "
                  f"consumed products for {self.current_date_string}")
            return None

        confirmation = self.mw.confirm_action(
            message=f"Action will remove Serving\n{serving.item_name}",
            accept_label="Remove",
            category=ConfirmationCategory.REMOVE_SERVING
        )

        if confirmation:
            index = intake_data.consumed_products.index(serving)
            intake_data.consumed_products.pop(index)

            event_manager().emit_data_changed(f"Daily Intake Page: Removed serving {serving.item_name} at "
                                              f"index {index} from consumed products list.")
            self.refresh_table()

    def on_remove_recipe_item(self, serving):
        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}")
            return None

        if serving not in intake_data.consumed_recipes:
            print(f"Serving {serving.identifier_string} not found in daily intake "
                  f"consumed recipes for {self.current_date_string}")
            return None

        confirmation = self.mw.confirm_action(
            message=f"Action will remove Serving\n{serving.item_name}",
            accept_label="Remove",
            category=ConfirmationCategory.REMOVE_SERVING
        )

        if confirmation:
            index = intake_data.consumed_recipes.index(serving)
            intake_data.consumed_recipes.pop(index)

            event_manager().emit_data_changed(f"Daily Intake Page: Removed serving {serving.item_name} at "
                                              f"index {index} from consumed recipes list.")
            self.refresh_table()

    def on_remove_multiple_servings(self, servings: list[Serving]) -> None:
        intake_data = self.get_intake_data(date=self.current_date_string)
        if intake_data is None:
            print(f"No daily intake data for calendar date {self.current_date_string}")
            return None

        confirmation = self.mw.confirm_action(
            message=f"Action will remove all {len(servings)} Servings!",
            accept_label="Remove",
            category=ConfirmationCategory.REMOVE_SERVING
        )

        if confirmation:
            for serving in servings:
                if serving.item_type is ServingType.PRODUCT and serving in intake_data.consumed_products:
                    index = intake_data.consumed_products.index(serving)
                    intake_data.consumed_products.pop(index)
                elif serving.item_type is ServingType.RECIPE and serving in intake_data.consumed_recipes:
                    index = intake_data.consumed_recipes.index(serving)
                    intake_data.consumed_recipes.pop(index)

            event_manager().emit_data_changed(f"Daily Intake Page: Removed {len(servings)} from "
                                              f"{self.current_date_string} daily intake record.")
            self.refresh_table()

    def on_remove_daily_intake_record(self, date_string: str):
        confirmation = self.mw.confirm_action(
            message=f"Action will remove daily intake record\nfor calendar day {date_string}. Continue?",
            accept_label="Remove",
            category=ConfirmationCategory.REMOVE_DAILY_INTAKE
        )

        if confirmation:
            print(f"Removing daily intake record for date {date_string}... WIP - Not Implemented")

    def on_view_daily_intake_details(self, date_string: str):
        QMessageBox.information(
            self.mw,
            "Daily Intake Details",
            f"Daily intake details for date {date_string}:\n"
            f"WIP - Not Implemented."
        )
