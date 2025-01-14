
from Core.ctr_data import CTRData
from GUI.UiFiles.PYUI.MainWindow import Ui_MainWindow


class MainWindowPage:
    def __init__(self, mw):
        self.mw = mw   # CTR Main window

    @property
    def main_window(self) -> Ui_MainWindow:
        if hasattr(self.mw, "main_window"):
            return self.mw.main_window
        else:
            raise AttributeError()

    @property
    def ctr_data(self) -> CTRData:
        if hasattr(self.mw, "ctr_data"):
            return self.mw.ctr_data
        else:
            raise AttributeError()

