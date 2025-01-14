"""
CTR - Calorie Tracker & Recipes

Main CTR Python module

    "Why buy something when
     you can make it yourself,
     exactly the way you need"

"""

from GUI.MainWindow.main_window import *
import sys

debug_mode = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window_theme = setup_initial_theme(app=app, theme=WindowTheme.DARK)

    mw = CTRMainWindow(app, window_theme)


    def load_test_savefiles(
            test_catalogue: bool = True,
            test_recipes: bool = True,
            test_daily_intake: bool = True
    ):
        if test_catalogue:
            mw.import_catalogue(filepath=f"{desktop_path}Default Catalogue.ctc")
        if test_recipes:
            mw.import_recipes(filepath=f"{desktop_path}Default Recipes.ctr")
        if test_daily_intake:
            mw.import_daily_intake(filepath=f"{desktop_path}CTR Daily Intake.ctd")

    def load_test_ctr_savefile():
        mw.ctr_data = CTRDataModel(filepath=f"{desktop_path}CTR Savefile.ct").read_savefile()
        mw.setup_on_ctr_data_open()

    if debug_mode:
        mw.setup_test_button()
        # load_test_savefiles()
        load_test_ctr_savefile()

    app.exec()
