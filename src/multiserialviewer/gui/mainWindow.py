from PySide6.QtWidgets import QMdiArea, QMainWindow, QPushButton
from PySide6.QtCore import QSize, QPoint, Signal
from PySide6.QtGui import QAction
from typing import List

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui.serialViewerWindow import SerialViewerWindow
from multiserialviewer.gui.serialViewerCreateDialog import SerialViewerCreateDialog
from multiserialviewer.gui.textHighlighterSettingsDialog import TextHighlighterSettingsDialog
from multiserialviewer.text_highlighter.textHighlighter import TextHighlighterSettings
from multiserialviewer.application.serialViewerSettings import SerialViewerSettings
from multiserialviewer.icons.iconSet import IconSet


class MainWindow(QMainWindow):
    signal_showSerialViewerCreateDialog: Signal = Signal()
    signal_createSerialViewer: Signal = Signal(SerialViewerSettings)
    signal_clearAll: Signal = Signal()
    signal_connectionStateChanged: Signal = Signal(bool)
    signal_aboutToBeClosed: Signal = Signal()
    signal_editHighlighterSettings: Signal = Signal()
    signal_applyHighlighterSettings: Signal = Signal(object)
    signal_createTextHighlightEntry: Signal = Signal(str)
    signal_openSettingsDirectory: Signal = Signal()

    def __init__(self, title: str, icon_set: IconSet):
        super(MainWindow, self).__init__()
        self.icon_set = icon_set

        self.populateMenuBar()
        widget = createWidgetFromUiFile("mainWindow.ui")

        self.setWindowTitle(title)
        self.setCentralWidget(widget)
        self.mdiArea = widget.findChild(QMdiArea, 'mdiArea')
        self.pb_changeConnectionState: QPushButton = widget.findChild(QPushButton, 'pb_changeConnectionState')
        self.setConnectionState(False)

        # icons
        self.setWindowIcon(icon_set.getAppIcon())
        self.pb_changeConnectionState.setIcon(self.icon_set.getCaptureStartIcon())
        widget.pb_create.setIcon(self.icon_set.getSerialViewerIcon())
        widget.pb_clear.setIcon(self.icon_set.getClearContentIcon())

        # connections
        widget.pb_create.clicked.connect(self.signal_showSerialViewerCreateDialog)
        widget.pb_clear.clicked.connect(self.signal_clearAll)
        widget.pb_changeConnectionState.clicked.connect(self.signal_connectionStateChanged)

    def populateMenuBar(self):
        # settings
        fileMenu = self.menuBar().addMenu("&Settings")

        action_textHighlighterSettings: QAction = QAction(icon=self.icon_set.getHighlighterIcon(), text="Text Highlighter",  parent=fileMenu)
        action_textHighlighterSettings.triggered.connect(self.signal_editHighlighterSettings)
        fileMenu.addAction(action_textHighlighterSettings)

        fileMenu.addSeparator()

        action_openSettingsDirectory: QAction = QAction(text="Open settings directory",  parent=fileMenu)
        action_openSettingsDirectory.triggered.connect(self.signal_openSettingsDirectory)
        fileMenu.addAction(action_openSettingsDirectory)

    def showSerialViewerCreateDialog(self, disabled_ports: list):
        dialog = SerialViewerCreateDialog(self)
        dialog.disablePorts(disabled_ports)
        if dialog.exec():
            self.signal_createSerialViewer.emit(dialog.getSerialViewerSettings())

    def createSerialViewerWindow(self, view_title: str, size: QSize = None, position: QPoint = None):
        view = SerialViewerWindow(view_title, self.icon_set)
        if size:
            view.resize(size)
        if position:
            view.move(position)
        self.mdiArea.addSubWindow(view)
        view.signal_createTextHighlightEntry.connect(self.signal_createTextHighlightEntry)
        view.show()
        return view

    def showHighlighterSettingsDialog(self, settings: List[TextHighlighterSettings]):
        dialog = TextHighlighterSettingsDialog(self, settings)
        if dialog.exec():
            self.signal_applyHighlighterSettings.emit(dialog.tableModel.settings)

    def getConnectionState(self):
        return self.pb_changeConnectionState.isChecked()

    def setConnectionState(self, state):
        self.pb_changeConnectionState.setChecked(state)
        if state:
            self.pb_changeConnectionState.setIcon(self.icon_set.getCaptureStopIcon())
            self.pb_changeConnectionState.setText('Stop capture')
        else:
            self.pb_changeConnectionState.setIcon(self.icon_set.getCaptureStartIcon())
            self.pb_changeConnectionState.setText('Start capture')

    def closeEvent(self, event):
        self.signal_aboutToBeClosed.emit()
        event.accept()
