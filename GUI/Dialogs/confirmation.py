
from PySide6.QtWidgets import QDialog, QLabel, QCheckBox, QPushButton, QMainWindow

from GUI.UiFiles.PYUI import ConfirmationDialog
from Settings.app_env import get_window_icon
from Settings.config_enums import ConfirmationCategory


class DialogConfirmation(QDialog):
    def __init__(
            self,
            mw: QMainWindow,
            message: str = "",
            window_title: str = "Confirm Action",
            accept_label: str = "OK",
            reject_label: str = "Cancel",
            category: ConfirmationCategory = ConfirmationCategory.OTHER,
            do_not_ask_enabled: bool = True,
            parent=None):
        super().__init__(parent)
        self.mw = mw
        self.message = message
        self.window_title = window_title
        self.accept_label = accept_label
        self.reject_label = reject_label
        self.category = category
        self.do_not_ask_enabled = do_not_ask_enabled

        self.window = ConfirmationDialog.Ui_Dialog()
        self.window.setupUi(self)

        self.setWindowTitle(self.window_title)
        self.setWindowIcon(get_window_icon())

        self.label: QLabel = self.window.label_message

        self.setup_ui()

    def setup_ui(self):
        self.setup_message()
        self.setup_checkbox()
        self.setup_push_buttons()

        if self.category is ConfirmationCategory.OTHER:
            self.window.checkBox_dont_ask_again.hide()

        self.adjustSize()

    def setup_message(self):
        self.label.setText(self.message)
        # self.label.setWordWrap(True)

    def setup_checkbox(self):
        cbox: QCheckBox = self.window.checkBox_dont_ask_again

        if self.do_not_ask_enabled:
            cbox.stateChanged.connect(self.dont_ask_again)
        else:
            self.window.checkBox_dont_ask_again.hide()

    def dont_ask_again(self):
        checked = self.window.checkBox_dont_ask_again.isChecked()
        if checked:
            if hasattr(self.mw, "add_to_dont_ask_confirmation"):
                self.mw.add_to_dont_ask_confirmation(self.category)
        else:
            if hasattr(self.mw, "remove_from_dont_ask_confirmation"):
                self.mw.remove_from_dont_ask_confirmation(self.category)

    def setup_push_buttons(self):
        accept_button: QPushButton = self.window.pushButton_confirm_action
        reject_button: QPushButton = self.window.pushButton_cancel_action

        accept_button.setText(self.accept_label)
        reject_button.setText(self.reject_label)

        reject_button.clicked.connect(self.reject)
        accept_button.clicked.connect(self.accept)
