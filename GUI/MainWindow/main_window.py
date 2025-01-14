"""
CTR - Calorie Tracker & Recipes

Module for the main window user interface

"""


from PySide6.QtCore import QEvent

from GUI.Common.event_manager import event_manager
from GUI.Common.dialogs import open_file_dialog, save_file_dialog
from GUI.Common.gui_util_functions import update_tooltip_style
from GUI.Dialogs.confirmation import DialogConfirmation
from GUI.Dialogs.save_before_close import DialogSaveBeforeClose
from Settings.app_env import Program_Version, get_light_icon, get_dark_icon, desktop_path, get_window_icon, WindowTheme
from Core.ctr_data import CTRData, SavefileExtension
from Core.csv_data_models import (CTRDataModel, DailyIntakeDataModel, CatalogueDataModel, RecipesDataModel,
                                  InformationDataModel)
from GUI.MainWindow.page_daily_intake import PageDailyIntake
from GUI.MainWindow.page_catalogue import PageCatalogue
from GUI.MainWindow.page_recipes import PageRecipes
from GUI.Icons import resources     # noqa: F401
from GUI.UiFiles.PYUI.MainWindow import Ui_MainWindow

import os
import qdarktheme
from enum import Enum
from typing import Any
from timeit import default_timer as timer
from PySide6.QtCore import Qt
from PySide6.QtGui import QActionGroup, QAction
from PySide6.QtWidgets import QMainWindow, QApplication, QStackedWidget, QToolBar, QDialog, QMessageBox

from Settings.config_enums import ConfirmationCategory, DialogWindow


class MainWindowDisplay(Enum):
    DISPLAY_DAILY_INTAKE = "Daily Intake"
    DISPLAY_CATALOGUE = "Catalogue"
    DISPLAY_RECIPES = "Recipes"


class CTRMainWindow(QMainWindow):
    def __init__(
            self,
            app: QApplication,
            window_theme: WindowTheme = WindowTheme.FUSION
    ):
        super().__init__()
        self.app = app
        self.window_theme = window_theme

        self.gui_window_title = f"CTR |  Calorie Tracking & Recipes |  Version {Program_Version}"
        self.window_icon = get_window_icon()

        self.main_window = Ui_MainWindow()
        self.main_window.setupUi(self)

        self.setWindowTitle(self.gui_window_title)
        self.setWindowIcon(self.window_icon)

        self.actiongroup_display = QActionGroup(self)

        self.dont_ask_for_confirmation: list[ConfirmationCategory] = []

        self.ctr_data = CTRData(filename="CTR Savefile")
        self._unsaved_data: bool = False
        self.working_directory: str = desktop_path

        self.page_daily_intake = PageDailyIntake(self)
        self.page_catalogue = PageCatalogue(self)
        self.page_recipes = PageRecipes(self)

        self.dialogs: dict[DialogWindow, Any] = {}

        self.setup_ui()

        self.show()

    def setup_ui(self):
        self.setup_initial_theme()
        self.setup_dialogs_dictionary()
        self.setup_main_window_display_toggles()
        self.setup_menubar_buttons()
        self.setup_menubar_actions()
        self.setup_toolbar()
        self.setup_toolbar_actions()
        self.enable_event_filters()
        self.connect_main_window_signals()
        self.resize(1250, 600)

    def setup_initial_theme(self):
        if self.window_theme is WindowTheme.DARK:
            self.set_dark_theme_icons()
            self.page_daily_intake.set_dark_theme()
            self.page_catalogue.set_dark_theme_button_icons()
            self.page_recipes.set_dark_theme_button_icons()
        else:
            self.set_light_theme_icons()
            self.page_daily_intake.set_light_theme()
            self.page_catalogue.set_light_theme_button_icons()
            self.page_recipes.set_light_theme_button_icons()

        update_tooltip_style(self.window_theme, self)

    def setup_dialogs_dictionary(self):
        for dialog_enum in DialogWindow:
            self.dialogs[dialog_enum] = None

    def setup_main_window_display_toggles(self):
        buttons: dict[QAction, MainWindowDisplay] = {
            self.main_window.action_daily_intake: MainWindowDisplay.DISPLAY_DAILY_INTAKE,
            self.main_window.action_catalogue: MainWindowDisplay.DISPLAY_CATALOGUE,
            self.main_window.action_recipes: MainWindowDisplay.DISPLAY_RECIPES}

        for action, data in buttons.items():
            action.setData(data)
            self.actiongroup_display.addAction(action)

        self.main_window.action_daily_intake.setChecked(True)

        self.main_window.action_daily_intake.triggered.connect(self.switch_main_window_display)
        self.main_window.action_catalogue.triggered.connect(self.switch_main_window_display)
        self.main_window.action_recipes.triggered.connect(self.switch_main_window_display)

    def setup_menubar_buttons(self):
        self.main_window.action_theme_fusion.triggered.connect(self.setup_fusion_theme)
        self.main_window.action_theme_light.triggered.connect(self.setup_light_theme)
        self.main_window.action_theme_dark.triggered.connect(self.setup_dark_theme)

    def setup_menubar_actions(self):
        # File menu
        self.main_window.action_menubar_open.triggered.connect(self.dialog_open_data_tracker_savefile)
        self.main_window.action_menubar_save.triggered.connect(self.dialog_save_data_tracker_savefile)
        self.main_window.action_menubar_save_as.triggered.connect(self.dialog_save_data_tracker_savefile)
        self.main_window.action_menubar_quit.triggered.connect(self.close)

        # Export sub-menu
        self.main_window.action_export_daily_intake.triggered.connect(self.dialog_export_daily_intake)
        self.main_window.action_export_catalogue.triggered.connect(self.dialog_export_catalogue)
        self.main_window.action_export_recipes.triggered.connect(self.dialog_export_recipes)

        # Import sub-menu
        self.main_window.action_import_daily_intake.triggered.connect(self.dialog_import_daily_intake)
        self.main_window.action_import_catalogue.triggered.connect(self.dialog_import_catalogue)
        self.main_window.action_import_recipes.triggered.connect(self.dialog_import_recipes)

    def setup_toolbar(self):
        self.main_window.toolBar_navigation.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

    def setup_toolbar_actions(self):
        self.main_window.actionOpen.triggered.connect(self.dialog_open_data_tracker_savefile)
        self.main_window.actionSave.triggered.connect(self.dialog_save_data_tracker_savefile)

    def enable_event_filters(self):
        self.installEventFilter(self)

    def connect_main_window_signals(self):
        event_manager().on_data_changed.connect(self._set_unsaved_data)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Close:
            self.close_windows()
            event.ignore()
            return True

        else:
            return super().eventFilter(source, event)

    def _set_unsaved_data(self, msg: str | None = None) -> None:
        print(f"Data change event;  EventManager ID {id(event_manager())};  Msg: '{msg}'")

        if self._unsaved_data:
            pass
        else:
            self._unsaved_data = True
            self.update_window_title(show_data_name=True)

    def reset_unsaved_data_flag(self):
        self._unsaved_data = False
        self.update_window_title(show_data_name=True)

    def update_window_title(self, show_data_name: bool = True):
        """
        Updates the Main window title with an additional title containing data filename.
        """
        if show_data_name:
            if self._unsaved_data:
                self.setWindowTitle(
                    f"{self.gui_window_title} |  *{self.ctr_data.filename}{SavefileExtension.CTR_DATA.value}")
            else:
                self.setWindowTitle(
                    f"{self.gui_window_title} |  {self.ctr_data.filename}{SavefileExtension.CTR_DATA.value}")
        else:
            self.setWindowTitle(self.gui_window_title)

    def switch_main_window_display(self):
        checked_action: QAction = self.actiongroup_display.checkedAction()
        window_display = checked_action.data()

        display_stacked_widget: QStackedWidget = self.main_window.stackedWidget_main

        if window_display is MainWindowDisplay.DISPLAY_DAILY_INTAKE:
            display_stacked_widget.setCurrentIndex(0)

        elif window_display is MainWindowDisplay.DISPLAY_CATALOGUE:
            display_stacked_widget.setCurrentIndex(1)

        elif window_display is MainWindowDisplay.DISPLAY_RECIPES:
            display_stacked_widget.setCurrentIndex(2)

    def set_dark_theme_icons(self):
        icons = {
            "save_dark.png": self.main_window.actionSave,
            "open_file_dark.png": self.main_window.actionOpen,
            "dashboard_dark.png": self.main_window.action_daily_intake,
            "catalogue_dark.png": self.main_window.action_catalogue,
            "recipe_dark.png": self.main_window.action_recipes,
        }

        for icon, button in icons.items():
            button.setIcon(get_dark_icon(icon))

    def set_light_theme_icons(self):
        icons = {
            "save.png": self.main_window.actionSave,
            "open_file.png": self.main_window.actionOpen,
            "dashboard.png": self.main_window.action_daily_intake,
            "catalogue.png": self.main_window.action_catalogue,
            "recipe.png": self.main_window.action_recipes,
        }

        for icon, button in icons.items():
            button.setIcon(get_light_icon(icon))

    def setup_dark_theme(self):
        """
        Sets dark theme to all windows and updates tooltip background / text color
        of the main window and all open dialog windows.
        """
        qdarktheme.setup_theme(theme="dark")
        self.window_theme = WindowTheme.DARK

        self.set_dark_theme_icons()
        self.page_daily_intake.set_dark_theme()
        self.page_catalogue.set_dark_theme_button_icons()
        self.page_recipes.set_dark_theme_button_icons()
        update_tooltip_style(self.window_theme, self)

        for dialog in self.dialogs.values():
            if dialog is not None:
                update_tooltip_style(self.window_theme, dialog)
                if hasattr(dialog, "update_icon_theme"):
                    dialog.update_icon_theme()

    def setup_light_theme(self):
        """
        Sets light theme to all windows and updates tooltip background / text color
        of the main window and all open dialog windows.

        The dialog has to implement a update_icon_theme function to enable icon
        update on change in the selected theme.
        """
        qdarktheme.setup_theme(theme="light")
        self.window_theme = WindowTheme.LIGHT

        self.set_light_theme_icons()
        self.page_daily_intake.set_light_theme()
        self.page_catalogue.set_light_theme_button_icons()
        self.page_recipes.set_light_theme_button_icons()
        update_tooltip_style(self.window_theme, self)

        for dialog in self.dialogs.values():
            if dialog is not None:
                update_tooltip_style(self.window_theme, dialog)
                if hasattr(dialog, "update_icon_theme"):
                    dialog.update_icon_theme()

    def setup_fusion_theme(self):
        """
        Sets the default Windows system theme to all windows and updates tooltip background / text color
        of the main window and all open dialog windows.
        """
        qdarktheme.setup_theme(theme="auto")
        self.set_light_theme_icons()
        self.window_theme = WindowTheme.FUSION

        self.app.setStyleSheet("")
        self.app.setStyle("Fusion")
        update_tooltip_style(self.window_theme, self)

    def setup_on_ctr_data_open(self):
        """
        Method executes setup of the Main window on opening of a CTR Data savefile.
        """
        self.page_daily_intake.refresh_table()
        self.page_daily_intake.update_intake_target_inputs()
        self.page_catalogue.refresh_table()
        self.page_recipes.refresh_recipes_list()
        self.page_recipes.refresh_ingredients_table()

    def import_daily_intake(self, filepath: str):
        DailyIntakeDataModel(filepath=filepath).read_savefile(self.ctr_data)
        self.page_daily_intake.refresh_table()

    def import_catalogue(self, filepath: str):
        CatalogueDataModel(filepath=filepath).read_savefile(self.ctr_data)
        self.page_catalogue.refresh_table()

    def import_recipes(self, filepath: str):
        RecipesDataModel(filepath=filepath).read_savefile(self.ctr_data)
        self.page_recipes.refresh_recipes_list()

    def dialog_open_data_tracker_savefile(self):
        file = open_file_dialog(
            parent=self,
            window_title="Open CTR Data",
            name_filter=f"CTR (*{SavefileExtension.CTR_DATA.value})",
            export_dir=desktop_path)

        if file:
            self.ctr_data = CTRDataModel(filepath=file).read_savefile()
            self.setup_on_ctr_data_open()

    def dialog_save_data_tracker_savefile(self):
        file = save_file_dialog(
            parent=self,
            window_title="Save CTR Data",
            filename=f"CTR Savefile{SavefileExtension.CTR_DATA.value}",
            name_filter=f"CTR (*{SavefileExtension.CTR_DATA.value})",
            export_dir=desktop_path)

        if file:
            CTRDataModel(filepath=file).write_savefile(self.ctr_data)
            self.reset_unsaved_data_flag()

    def dialog_import_daily_intake(self):
        file = open_file_dialog(
            parent=self,
            window_title="Import Daily Intake Data",
            name_filter=f"CTR Daily Intake (*{SavefileExtension.DAILY_INTAKE.value})",
            export_dir=desktop_path)

        if file:
            self.import_daily_intake(filepath=file)

    def dialog_import_catalogue(self):
        file = open_file_dialog(
            parent=self,
            window_title="Import Catalogue",
            name_filter=f"CTR Catalogue (*{SavefileExtension.CATALOGUE.value})",
            export_dir=desktop_path)

        if file:
            self.import_catalogue(filepath=file)

    def dialog_import_recipes(self):
        file = open_file_dialog(
            parent=self,
            window_title="Import Recipes",
            name_filter=f"CTR Recipes (*{SavefileExtension.RECIPES.value})",
            export_dir=desktop_path)

        if file:
            self.import_recipes(filepath=file)

    def dialog_export_daily_intake(self):
        file = save_file_dialog(
            parent=self,
            window_title="Export Daily Intake Data",
            filename=f"CTR Daily Intake{SavefileExtension.DAILY_INTAKE.value}",
            name_filter=f"CTR Daily Intake (*{SavefileExtension.DAILY_INTAKE.value})",
            export_dir=desktop_path)

        if file:
            DailyIntakeDataModel(filepath=file).write_savefile(self.ctr_data)

    def dialog_export_catalogue(self):
        file = save_file_dialog(
            parent=self,
            window_title="Export Catalogue Data",
            filename=f"CTR Catalogue{SavefileExtension.CATALOGUE.value}",
            name_filter=f"CTR Catalogue (*{SavefileExtension.CATALOGUE.value})",
            export_dir=desktop_path)

        if file:
            CatalogueDataModel(filepath=file).write_savefile(self.ctr_data)

    def dialog_export_recipes(self):
        file = save_file_dialog(
            parent=self,
            window_title="Export Recipes Data",
            filename=f"CTR Recipes{SavefileExtension.RECIPES.value}",
            name_filter=f"CTR Recipes (*{SavefileExtension.RECIPES.value})",
            export_dir=desktop_path)

        if file:
            RecipesDataModel(filepath=file).write_savefile(self.ctr_data)

    def confirm_close(self) -> int:
        if self.dialogs[DialogWindow.CONFIRM_QUIT] is not None:
            self.dialogs[DialogWindow.CONFIRM_QUIT].close()

        filepath = f"{self.working_directory}{self.ctr_data.filename}{SavefileExtension.CTR_DATA.value}"

        dialog: QDialog = DialogSaveBeforeClose(self, filepath)
        self.dialogs[DialogWindow.CONFIRM_QUIT] = dialog
        return dialog.exec()

    def confirm_action(self, message: str, window_title: str = "Confirm Action",
                       accept_label: str = "OK", reject_label: str = "Cancel",
                       category: ConfirmationCategory = ConfirmationCategory.OTHER,
                       do_not_ask_enabled: bool = True) -> bool:
        """
        Opens a custom confirmation dialog window to confirm the selected action.
        :param message: Message to be displayed in the dialog window.
        :param window_title: Dialog window title.
        :param accept_label: Label for the accept button.
        :param reject_label: Label for the reject button.
        :param category: Confirmation category for tracking selection of bug me not checkbox.
        :param do_not_ask_enabled: Enable "Do not ask me again" checkbox.
        :return: Boolean, is the action accepted or not.
        """
        if category in self.dont_ask_for_confirmation:
            return True

        if self.dialogs[DialogWindow.CONFIRM_ACTION] is not None:
            self.dialogs[DialogWindow.CONFIRM_ACTION].close()

        dialog: QDialog = DialogConfirmation(self, message, window_title, accept_label, reject_label,
                                             category, do_not_ask_enabled)
        dialog.accepted.connect(self.close_confirmation_dialog)
        dialog.rejected.connect(self.close_confirmation_dialog)

        self.dialogs[DialogWindow.CONFIRM_ACTION] = dialog
        dialog.exec_()

        if dialog.result():
            return True
        else:
            return False

    def add_to_dont_ask_confirmation(self, category: ConfirmationCategory):
        if category not in self.dont_ask_for_confirmation:
            self.dont_ask_for_confirmation.append(category)

    def remove_from_dont_ask_confirmation(self, category: ConfirmationCategory):
        if category in self.dont_ask_for_confirmation:
            index = self.dont_ask_for_confirmation.index(category)
            self.dont_ask_for_confirmation.pop(index)

    def close_confirmation_dialog(self):
        self.dialogs[DialogWindow.CONFIRM_ACTION].close()

    def close_windows(self):
        if self._unsaved_data:
            response = self.confirm_close()

            if response == 1:
                dialog = self.dialogs.get(DialogWindow.CONFIRM_QUIT, None)
                if dialog is None or not isinstance(dialog, DialogSaveBeforeClose):
                    raise KeyError("Error: DialogSaveBeforeClose has already been destroyed!")

                filepath = dialog.selected_path
                file_directory = os.path.dirname(filepath)
                if not os.path.exists(file_directory):
                    QMessageBox.information(
                        self, "Error", "Unable to save CTR Data. Selected directory does not exist!")
                    return

                try:
                    CTRDataModel(filepath=filepath).write_savefile(self.ctr_data)
                    print(f"Saving before closing to filepath {filepath}")
                    self.close_app()
                except PermissionError as err:
                    print(err)
                    QMessageBox.information(
                        self, "Error", "Unable to save CTR Data. "
                                       "Selected file is already used by another program!")

            elif response == 2:
                print("Not Saving before closing...")
                self.close_app()
            elif response == 3:
                print("Cancelling closing...")
        else:
            self.close_app()

    def close_app(self):
        for window in self.app.topLevelWidgets():
            window.close()
        self.app.quit()

    def setup_test_button(self):
        test_action: QAction = QAction(self)
        toolbar: QToolBar = self.main_window.toolBar_file
        toolbar.addAction(test_action)

        test_action.setIcon(get_light_icon("test_button.png"))
        test_action.setToolTip("Test Button")

        test_action.triggered.connect(self.TEST_FUNCTION)

    def TEST_FUNCTION(self):
        start = timer()

        def test_calendar_highlight():  # noqa
            self.page_daily_intake.highlight_all_dates_with_data()

        def test_write_ctr_info_savefile():  # noqa
            file = save_file_dialog(
                parent=self,
                window_title="Export CTR Info",
                filename=f"CTR Info{SavefileExtension.INFORMATION.value}",
                name_filter=f"CTR Info (*{SavefileExtension.INFORMATION.value})",
                export_dir=desktop_path)

            if file:
                InformationDataModel(filepath=file).write_savefile(self.ctr_data)

        def test_read_ctr_info_savefile():  # noqa
            file = open_file_dialog(
                parent=self,
                window_title="Import CTR Info",
                name_filter=f"CTR Info (*{SavefileExtension.INFORMATION.value})",
                export_dir=desktop_path)

            if file:
                InformationDataModel(filepath=file).read_savefile(self.ctr_data)

        test_calendar_highlight()
        # self.update_window_title(show_data_name=True)
        # test_write_ctr_info_savefile()
        # test_read_ctr_info_savefile()

        end = timer()
        print("Test complete in", end - start, "s")


def setup_initial_theme(
        app: QApplication,
        theme: WindowTheme = WindowTheme.DARK
) -> WindowTheme:
    if theme is WindowTheme.LIGHT:
        qdarktheme.setup_theme(theme="light")
    elif theme is WindowTheme.DARK:
        qdarktheme.setup_theme(theme="dark")
    else:
        app.setStyle("Fusion")

    return theme
