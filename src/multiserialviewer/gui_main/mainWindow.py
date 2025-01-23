from PySide6.QtWidgets import QMdiArea, QMainWindow, QToolBar, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QSize, QPoint, Signal, Slot, QByteArray
from PySide6.QtGui import QAction
from typing import List

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui_viewer.serialViewerWindow import SerialViewerWindow
from multiserialviewer.gui_viewer.serialViewerCreateDialog import SerialViewerCreateDialog
from multiserialviewer.gui_main.settingsDialog import SettingsDialog
from multiserialviewer.settings.settings import Settings
from multiserialviewer.settings.textHighlighterSettings import TextHighlighterSettings
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings
from multiserialviewer.icons.iconSet import IconSet


class MainWindow(QMainWindow):
    signal_showSerialViewerCreateDialog: Signal = Signal()
    signal_createSerialViewer: Signal = Signal(SerialViewerSettings)
    signal_clearAll: Signal = Signal()
    signal_toggleCaptureState: Signal = Signal()
    signal_aboutToBeClosed: Signal = Signal()
    signal_editSettings: Signal = Signal()
    signal_applySettings: Signal = Signal(object)
    signal_createTextHighlightEntry: Signal = Signal(str)
    signal_openSettingsDirectory: Signal = Signal()

    def __init__(self, title: str, iconSet: IconSet):
        super(MainWindow, self).__init__()
        self.iconSet = iconSet
        self.actions = self.__createActions()
        self.__connectActions()
        self.toolBar: QToolBar = self.__createToolBar()

        widget = createWidgetFromUiFile("mainWindow.ui")

        self.setWindowTitle(title)
        self.setWindowIcon(iconSet.getAppIcon())
        self.setCentralWidget(widget)
        self.mdiArea: QMdiArea = widget.findChild(QMdiArea, 'mdiArea')
        self.updateCaptureButton(False)


    def __createActions(self):
        actions = {}

        action: QAction = QAction(icon=self.iconSet.getSettingsIcon(), text="Settings", parent=self)
        action.setToolTip("Edit settings")
        actions['openSettingsDialog'] = action

        action: QAction = QAction(icon=self.iconSet.getAddIcon(), text="Create Viewer", parent=self)
        action.setToolTip("Create additional SerialViewer window")
        actions['createSerialViewer'] = action

        action: QAction = QAction(icon=self.iconSet.getClearContentIcon(), text="Clear Content", parent=self)
        action.setToolTip("Remove received serial data")
        actions['clearContent'] = action

        action: QAction = QAction(icon=self.iconSet.getCaptureStartIcon(), text="Start Capture", parent=self)
        action.setToolTip("Start/stop receiving serial data")
        actions['capture'] = action

        action: QAction = QAction(icon=self.iconSet.getTileIcon(), text="Arrange", parent=self)
        action.setToolTip("Automatically arrange all SerialViewer windows side by side")
        actions['arrangeSerialViewerWindows'] = action

        return actions

    def __connectActions(self):
        self.actions['openSettingsDialog'].triggered.connect(self.signal_editSettings)
        self.actions['createSerialViewer'].triggered.connect(self.signal_showSerialViewerCreateDialog)
        self.actions['clearContent'].triggered.connect(self.signal_clearAll)
        self.actions['capture'].triggered.connect(self.signal_toggleCaptureState)
        self.actions['arrangeSerialViewerWindows'].triggered.connect(self.arrangeWindowsInTile)

    def __createToolBar(self) -> QToolBar:
        toolBar: QToolBar = QToolBar(self)
        toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        toolBar.setIconSize(QSize(32, 32))

        toolBar.addAction(self.actions['createSerialViewer'])
        toolBar.addAction(self.actions['capture'])
        toolBar.addAction(self.actions['clearContent'])

        # expanding space
        space = QWidget()
        space.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolBar.addWidget(space)

        toolBar.addSeparator()
        toolBar.addAction(self.actions['arrangeSerialViewerWindows'])
        toolBar.addSeparator()

        toolBar.addAction(self.actions['openSettingsDialog'])
        return toolBar

    def showSerialViewerCreateDialog(self, disabled_ports: list):
        dialog = SerialViewerCreateDialog(self)
        dialog.disablePorts(disabled_ports)
        if dialog.exec():
            self.signal_createSerialViewer.emit(dialog.getSerialViewerSettings())

    def createSerialViewerWindow(self,
                                 view_title: str,
                                 highlighterSettings: List[TextHighlighterSettings],
                                 size: QSize = None,
                                 position: QPoint = None,
                                 splitterState: QByteArray = None,
                                 currentTabName: str = None):
        view = SerialViewerWindow(view_title, self.iconSet)
        view.setHighlighterSettings(highlighterSettings)
        if size:
            view.resize(size)
        if position:
            view.move(position)
        if splitterState:
            view.splitter.restoreState(splitterState)
        if currentTabName:
            view.setCurrentTab(currentTabName)

        self.mdiArea.addSubWindow(view)
        view.signal_createTextHighlightEntry.connect(self.signal_createTextHighlightEntry)
        view.show()
        return view

    def showSettingsDialog(self, settings: Settings):
        dialog = SettingsDialog(self, settings, self.iconSet)
        dialog.resize(800, 600)
        if dialog.exec():
            self.signal_applySettings.emit(dialog.settings)

    def updateCaptureButton(self, captureState):
        if captureState:
            self.actions['capture'].setIcon(self.iconSet.getCaptureStopIcon())
            self.actions['capture'].setText('Stop Capture')
        else:
            self.actions['capture'].setIcon(self.iconSet.getCaptureStartIcon())
            self.actions['capture'].setText('Start Capture')

    def closeEvent(self, event):
        self.signal_aboutToBeClosed.emit()
        event.accept()

    @Slot()
    def arrangeWindowsInTile(self):
        self.mdiArea.tileSubWindows()
