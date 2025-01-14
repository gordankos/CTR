
from Settings.app_env import desktop_path

from PySide6.QtCore import QUrl, QSettings
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFileDialog, QColorDialog, QDialog


_SETTINGS = QSettings("GK", "CTR")


def _restore_sidebar_urls(file_dialog: QFileDialog):
    """
    Function restores QFileDialog sidebar URLs.
    On Windows, settings are stored in the registry under HKEY_CURRENT_USER\Software\GK\CTRT
    """
    sidebar_urls: list = _SETTINGS.value("sidebarUrls", [])     # noqa
    if sidebar_urls:
        file_dialog.setSidebarUrls([QUrl.fromLocalFile(url) for url in sidebar_urls])
    else:
        file_dialog.setSidebarUrls([QUrl.fromLocalFile(desktop_path)])


def _save_sidebar_urls(file_dialog: QFileDialog):
    """
    Function saves QFileDialog sidebar URLs.
    On Windows, settings are stored in the registry under HKEY_CURRENT_USER\Software\GK\CCTR
    """
    urls = [url.toLocalFile() for url in file_dialog.sidebarUrls()]
    _SETTINGS.setValue("sidebarUrls", urls)


def _get_file_dialog(
        parent,
        window_title: str,
        name_filter: str | list[str] | None = None,
        export_dir: str | None = None
) -> QFileDialog:
    """
    Function creates a new QFileDialog instance with common settings for all open and save file dialogs.

    :param parent: Parent window for the dialog.
    :param window_title: Dialog window title.
    :param name_filter: Name filter for displaying only files of the given type in the file dialog.
    :param export_dir: Default export directory. Uses the desktop path if None.
    """
    file_dialog = QFileDialog(parent)
    file_dialog.setWindowTitle(window_title)
    file_dialog.setViewMode(QFileDialog.ViewMode.Detail)
    file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)

    file_dialog.show()

    if name_filter is not None:
        if type(name_filter) is list:
            file_dialog.setNameFilters(name_filter)
        else:
            file_dialog.setNameFilter(name_filter)

    if export_dir is None:
        file_dialog.setDirectory(desktop_path)
    else:
        file_dialog.setDirectory(export_dir)

    _restore_sidebar_urls(file_dialog)

    return file_dialog


def open_file_dialog(
        parent,
        window_title: str,
        name_filter: str | list[str] | None = None,
        export_dir: str | None = None
) -> str | bool:
    """
    Opens an open / import file dialog.

    :param parent: Parent window for the dialog.
    :param window_title: Dialog window title.
    :param name_filter: Name filter for displaying only files of the given type in the file dialog.
    :param export_dir: Default export directory. Uses the desktop path if None.
    :return: Selected file path if accepted. False if not accepted.
    """
    file_dialog = _get_file_dialog(parent, window_title, name_filter, export_dir)

    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

    if file_dialog.exec_() == QFileDialog.DialogCode.Accepted:
        selected_file = file_dialog.selectedFiles()[0]

        _save_sidebar_urls(file_dialog)
        return selected_file

    else:
        # _save_sidebar_urls(file_dialog)
        return False


def open_files_dialog(
        parent,
        window_title: str,
        name_filter: str | list[str] | None = None,
        export_dir: str | None = None
) -> list[str] | bool:
    """
    Opens an open / import file dialog for opening multiple selected files.

    :param parent: Parent window for the dialog.
    :param window_title: Dialog window title.
    :param name_filter: Name filter for displaying only files of the given type in the file dialog.
    :param export_dir: Default export directory. Uses the desktop path if None.
    :return: Selected file path if accepted. False if not accepted.
    """
    file_dialog = _get_file_dialog(parent, window_title, name_filter, export_dir)

    file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

    if file_dialog.exec_() == QFileDialog.DialogCode.Accepted:
        selected_files = file_dialog.selectedFiles()

        _save_sidebar_urls(file_dialog)
        return selected_files

    else:
        return False


def save_file_dialog(
        parent,
        window_title: str,
        filename: str,
        name_filter: str | list[str] | None = None,
        export_dir: str | None = None
) -> str | bool:
    """
    Opens a save / export file dialog.

    :param parent: Parent window for the dialog.
    :param window_title: Dialog window title.
    :param filename: Default filename to be input in the file name field.
    :param name_filter: Name filter for displaying only files of the given type in the file dialog.
        Example: "Standard Triangle Language (*.stl)"
    :param export_dir: Default export directory. Uses the desktop path if None.
    :return: Selected file path if accepted. False if not accepted.
    """
    file_dialog = _get_file_dialog(parent, window_title, name_filter, export_dir)

    file_dialog.setFileMode(QFileDialog.FileMode.AnyFile)
    file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    file_dialog.selectFile(filename)

    if file_dialog.exec_() == QFileDialog.DialogCode.Accepted:
        selected_name_filter = file_dialog.selectedNameFilter()
        extension = selected_name_filter.split("(*")[-1].strip(")")
        selected_file = file_dialog.selectedFiles()[0]

        if not selected_file.endswith(extension):
            selected_file += extension

        _save_sidebar_urls(file_dialog)
        return selected_file

    else:
        return False


def directory_file_dialog(
        parent,
        window_title: str,
        current_dir: str | None = None
) -> str | bool:
    """
    Opens a save file dialog for selecting the output directory.

    :param parent: Parent window for the dialog.
    :param window_title: Dialog window title.
    :param current_dir: Default directory. Uses the desktop path if None.
    :return: Selected file path if accepted. False if not accepted.
    """
    file_dialog = _get_file_dialog(parent, window_title, None, current_dir)

    file_dialog.setFileMode(QFileDialog.FileMode.Directory)

    if file_dialog.exec_() == QFileDialog.DialogCode.Accepted:
        selected_directory = file_dialog.selectedFiles()[0] + "/"

        _save_sidebar_urls(file_dialog)
        return selected_directory

    else:
        return False


def color_picker_gui(
        parent,
        current_color: QColor | None = None
) -> QColor | None:
    """
    Function opens a color picker GUI.

    :param parent: Parent window for the dialog.
    :param current_color: Current color to be set in the picker.
    """
    dialog = QColorDialog(parent)
    dialog.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel, on=True)
    dialog.setWindowTitle("Color Picker")

    if hasattr(parent, "windowIcon"):
        dialog.setWindowIcon(parent.windowIcon())

    if current_color is not None:
        dialog.setCurrentColor(current_color)

    if dialog.exec_() == QDialog.DialogCode.Accepted:
        color = dialog.selectedColor()
        if color.isValid():
            # return color.name()  # hex
            return color  # RGBA
        else:
            return None
    else:
        return None
