from PySide6.QtWidgets import QMdiArea, QMainWindow, QToolBar, QMenu, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QSize, QPoint, Signal
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
    signal_toggleCaptureState: Signal = Signal()
    signal_aboutToBeClosed: Signal = Signal()
    signal_editHighlighterSettings: Signal = Signal()
    signal_applyHighlighterSettings: Signal = Signal(object)
    signal_createTextHighlightEntry: Signal = Signal(str)
    signal_openSettingsDirectory: Signal = Signal()

    def __init__(self, title: str, icon_set: IconSet):
        super(MainWindow, self).__init__()
        self.icon_set = icon_set
        self.actions = self.__createActions()
        self.__connectActions()
        self.toolBar: QToolBar = self.__createToolBar()

        widget = createWidgetFromUiFile("mainWindow.ui")

        self.setWindowTitle(title)
        self.setWindowIcon(icon_set.getAppIcon())
        self.setCentralWidget(widget)
        self.mdiArea = widget.findChild(QMdiArea, 'mdiArea')
        self.updateCaptureButton(False)


    def __createActions(self):
        actions = {}

        action: QAction = QAction(icon=self.icon_set.getHighlighterIcon(), text="Text Highlighter",  parent=self)
        action.setToolTip("Modify Text Highlighter settings")
        actions['textHighlighterSettings'] = action

        action: QAction = QAction(icon=self.icon_set.getDirectoryIcon(), text="Open settings directory",  parent=self)
        actions['openSettingsDir'] = action

        action: QAction = QAction(icon=self.icon_set.getAddIcon(), text="Create SerialViewer",  parent=self)
        actions['createSerialViewer'] = action

        action: QAction = QAction(icon=self.icon_set.getClearContentIcon(), text="Clear content",  parent=self)
        actions['clearContent'] = action

        action: QAction = QAction(icon=self.icon_set.getCaptureStartIcon(), text="Start capture",  parent=self)
        actions['capture'] = action

        return actions

    def __connectActions(self):
        self.actions['textHighlighterSettings'].triggered.connect(self.signal_editHighlighterSettings)
        self.actions['openSettingsDir'].triggered.connect(self.signal_openSettingsDirectory)
        self.actions['createSerialViewer'].triggered.connect(self.signal_showSerialViewerCreateDialog)
        self.actions['clearContent'].triggered.connect(self.signal_clearAll)
        self.actions['capture'].triggered.connect(self.signal_toggleCaptureState)

    def __createToolBar(self) -> QToolBar:
        toolBar: QToolBar = QToolBar(self)
        toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        toolBar.addAction(self.actions['createSerialViewer'])
        toolBar.addAction(self.actions['capture'])
        toolBar.addAction(self.actions['clearContent'])

        # expanding space
        space = QWidget()
        space.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolBar.addWidget(space)

        # settings
        settingsMenu: QMenu = QMenu(toolBar)
        settingsMenu.addAction(self.actions['openSettingsDir'])
        self.actions['textHighlighterSettings'].setMenu(settingsMenu)
        toolBar.addAction(self.actions['textHighlighterSettings'])

        return toolBar

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

    def updateCaptureButton(self, captureState):
        if captureState:
            self.actions['capture'].setIcon(self.icon_set.getCaptureStopIcon())
            self.actions['capture'].setText('Stop capture')
        else:
            self.actions['capture'].setIcon(self.icon_set.getCaptureStartIcon())
            self.actions['capture'].setText('Start capture')

    def closeEvent(self, event):
        self.signal_aboutToBeClosed.emit()
        event.accept()
