from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile


def createWidgetFromUiFile(ui_file_name):
    ui_file = QFile(ui_file_name)
    if not ui_file.open(QFile.ReadOnly):
        raise Exception(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
    loader = QUiLoader()
    widget = loader.load(ui_file)
    ui_file.close()
    if not widget:
        raise Exception(loader.errorString())
    return widget
