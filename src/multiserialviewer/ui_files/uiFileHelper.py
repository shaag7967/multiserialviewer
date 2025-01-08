from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import pathlib

from multiserialviewer.gui_viewer.serialViewerTextEdit import SerialViewerTextEdit


def createWidgetFromUiFile(ui_file_name):
    ui_file_path_file_name = pathlib.Path(__file__).parent.joinpath(ui_file_name).resolve()

    ui_file = QFile(ui_file_path_file_name)
    if not ui_file.open(QFile.ReadOnly):
        raise Exception(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
    loader = QUiLoader()

    # cutom widgets
    loader.registerCustomWidget(SerialViewerTextEdit)

    widget = loader.load(ui_file)
    ui_file.close()
    if not widget:
        raise Exception(loader.errorString())
    return widget
