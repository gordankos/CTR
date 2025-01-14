
from PySide6.QtCore import QSize

from Core.ctr_data import SavefileExtension
from GUI.UiFiles.PYUI import SaveBeforeCloseDialog
from GUI.Common.dialogs import save_file_dialog
from Settings.app_env import get_light_icon, get_dark_icon, WindowTheme, get_window_icon, desktop_path

from PySide6.QtWidgets import QDialog, QMainWindow


class DialogSaveBeforeClose(QDialog):
    def __init__(
            self,
            mw: QMainWindow,
            filepath: str = "",
            file_extension: SavefileExtension = SavefileExtension.CTR_DATA,
            parent=None):
        super().__init__(parent)
        self.mw = mw
        self.filepath = filepath
        self.file_extension = file_extension

        self.window = SaveBeforeCloseDialog.Ui_Dialog()
        self.window.setupUi(self)

        self.setWindowTitle(" ")
        self.setWindowIcon(get_window_icon())

        self.selected_path = filepath

        self.setup_ui()

    def setup_ui(self):
        self.setup_push_buttons()
        self.setup_path_input()
        self.update_icon_theme()
        self.set_initial_path()
        self.set_button_focus()

    def setup_push_buttons(self):
        self.window.pushButton_directory_browser.clicked.connect(self.set_savefile_path)
        self.window.pushButton_save.clicked.connect(lambda: self.done(1))       # Return 1 for Save
        self.window.pushButton_dont_save.clicked.connect(lambda: self.done(2))  # Return 2 for Don't Save
        self.window.pushButton_cancel.clicked.connect(lambda: self.done(3))     # Return 3 for Cancel

    def setup_path_input(self):
        self.window.lineEdit_filepath.setReadOnly(True)

    def update_icon_theme(self) -> None:
        if hasattr(self.mw, "window_theme"):
            theme = self.mw.window_theme
            if theme is WindowTheme.DARK:
                self.set_dark_theme_icons()
            else:
                self.set_light_theme_icons()

    def set_initial_path(self):
        self.window.lineEdit_filepath.setText(self.filepath)

    def set_button_focus(self):
        self.window.pushButton_save.setFocus()

    def set_savefile_path(self):
        file = save_file_dialog(
            parent=self,
            window_title="Save Tracker Data",
            filename=self.filepath,
            name_filter=f"Calorie Tracker (*{self.file_extension.value})",
            export_dir=desktop_path)

        if file:
            self.selected_path = file
            self.done(1)

    def set_light_theme_icons(self):
        self.window.pushButton_directory_browser.setIcon(get_light_icon("open_file.png"))
        self.window.pushButton_directory_browser.setIconSize(QSize(20, 20))

    def set_dark_theme_icons(self):
        self.window.pushButton_directory_browser.setIcon(get_dark_icon("open_file_dark.png"))
        self.window.pushButton_directory_browser.setIconSize(QSize(20, 20))
