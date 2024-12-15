from PySide6.QtWidgets import QMdiArea, QMainWindow, QPushButton
from PySide6.QtCore import QSize, Signal

from typing import List

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.serial_data.serialConnectionSettings import SerialConnectionSettings
from multiserialviewer.gui.serialViewerWindow import SerialViewerWindow
from multiserialviewer.gui.serialViewerCreateDialog import SerialViewerCreateDialog
from multiserialviewer.gui.textHighlighterSettingsDialog import TextHighlighterSettingsDialog
from multiserialviewer.text_highlighter.textHighlighter import TextHighlighterConfig


class MainWindow(QMainWindow):
    signal_showSerialViewerCreateDialog = Signal()
    signal_createSerialViewer = Signal(str, SerialConnectionSettings)
    signal_clearAll = Signal()
    signal_connectionStateChanged = Signal(bool)
    signal_aboutToBeClosed = Signal()
    signal_editHighlighterSettings = Signal()
    signal_applyHighlighterSettings = Signal(object)

    def __init__(self, title: str):
        super(MainWindow, self).__init__()
        self.setWindowTitle(title)

        widget = createWidgetFromUiFile("mainWindow.ui")

        self.mdiArea = widget.findChild(QMdiArea, 'mdiArea')
        self.pb_changeConnectionState: QPushButton = widget.findChild(QPushButton, 'pb_changeConnectionState')

        self.setCentralWidget(widget)
        self.setConnectionState(False)

        # connections
        widget.pb_create.clicked.connect(self.signal_showSerialViewerCreateDialog)
        widget.pb_clear.clicked.connect(self.signal_clearAll)
        widget.pb_changeConnectionState.clicked.connect(self.signal_connectionStateChanged)
        widget.pb_highlighter.clicked.connect(self.signal_editHighlighterSettings)

    def showSerialViewerCreateDialog(self, disabled_ports: list):
        dialog = SerialViewerCreateDialog(self)
        dialog.disablePorts(disabled_ports)
        if dialog.exec():
            port_name = dialog.getPortName()
            if len(port_name) > 0:
                settings = SerialConnectionSettings(port_name)
                settings.baudrate = dialog.getBaudrate()
                settings.bytesize = dialog.getDataBits()
                settings.parity = dialog.getParity()
                settings.stopbits = dialog.getStopBits()

                self.signal_createSerialViewer.emit(dialog.getName(), settings)

    def createSerialViewerWindow(self, viewTitle: str, size: QSize = None):
        view = SerialViewerWindow(viewTitle)
        if size:
            view.resize(size)
        self.mdiArea.addSubWindow(view)
        view.show()
        return view

    def showHighlighterSettingsDialog(self, settings: List[TextHighlighterConfig]):
        dialog = TextHighlighterSettingsDialog(self, settings)
        if dialog.exec():
            self.signal_applyHighlighterSettings.emit(dialog.table_model.settings)

    def getConnectionState(self):
        return self.pb_changeConnectionState.isChecked()

    def setConnectionState(self, state):
        self.pb_changeConnectionState.setChecked(state)
        if state:
            self.pb_changeConnectionState.setText('Stop')
        else:
            self.pb_changeConnectionState.setText('Start')

    def closeEvent(self, event):
        self.signal_aboutToBeClosed.emit()
        event.accept()
