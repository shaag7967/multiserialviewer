from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot, Qt
from PySide6.QtGui import QGuiApplication
from platformdirs import user_config_dir
import copy

from multiserialviewer.application.serialViewerController import SerialViewerController
from multiserialviewer.application.proxyStyle import ProxyStyle
from multiserialviewer.gui_main.mainWindow import MainWindow
from multiserialviewer.application.serialViewerControllerPool import SerialViewerControllerPool
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.settings.settings import Settings
from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
from multiserialviewer.settings.textHighlighterSettings import TextHighlighterSettings
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings


class Application(QApplication):
    NAME = 'MultiSerialViewer'

    def __init__(self, version: str, arguments):
        super().__init__(arguments)

        self.configDir = user_config_dir(appname=Application.NAME, roaming=False, ensure_exists=True, appauthor=False)
        self.settings: Settings = Settings(self.configDir)
        self.settings.loadSettings()

        self.captureActive: bool = False
        self.controllerPool: SerialViewerControllerPool = SerialViewerControllerPool()

        colorScheme: Qt.ColorScheme = QGuiApplication.styleHints().colorScheme()
        if colorScheme == Qt.ColorScheme.Dark:
            self.icon_set = IconSet('google', 'CCCCCC')
        else:
            self.icon_set = IconSet('google', '434343')

        self.mainWindow = MainWindow(f'{Application.NAME} {version}', self.icon_set)
        self.mainWindow.updateCaptureButton(self.captureActive)

        self.mainWindow.signal_showSerialViewerCreateDialog.connect(self.showSerialViewerCreateDialog)
        self.mainWindow.signal_createSerialViewer.connect(self.createSerialViewer)
        self.mainWindow.signal_clearAll.connect(self.clearAll)
        self.mainWindow.signal_toggleCaptureState.connect(self.toggleCaptureState)
        self.mainWindow.signal_aboutToBeClosed.connect(self.onAboutToBeClosed)
        self.mainWindow.signal_editSettings.connect(self.showSettingsDialog)
        self.mainWindow.signal_applySettings.connect(self.applyModifiedSettings)
        self.mainWindow.signal_createTextHighlightEntry.connect(self.createTextHighlightEntry)

        self.applySettings()
        self.setStyle(ProxyStyle())
        self.mainWindow.show()

        if self.controllerPool.count() == 0:
            self.showSerialViewerCreateDialog()

    @Slot(str)
    def createTextHighlightEntry(self, text_to_highlight: str):
        highlighterSettings = TextHighlighterSettings()
        highlighterSettings.pattern = text_to_highlight

        settings = copy.deepcopy(self.settings)
        settings.textHighlighter.entries.append(highlighterSettings)
        self.mainWindow.showSettingsDialog(settings)

    @Slot()
    def showSerialViewerCreateDialog(self):
        alreadyUsedPorts = self.controllerPool.getUsedPorts()
        self.mainWindow.showSerialViewerCreateDialog(alreadyUsedPorts)

    @Slot()
    def showSettingsDialog(self):
        self.mainWindow.showSettingsDialog(copy.deepcopy(self.settings))

    @Slot()
    def applyModifiedSettings(self, modifiedSettings: Settings):
        # this could cause some bugs if new values are added to Settings, but not here... -> refactor it
        self.settings.application = modifiedSettings.application
        self.settings.textHighlighter = modifiedSettings.textHighlighter
        self.controllerPool.setHighlighterSettings(self.settings.textHighlighter.entries)

    @Slot(SerialViewerSettings)
    def createSerialViewer(self, settings: SerialViewerSettings):
        if settings.connection.portName in self.controllerPool.getUsedPorts():
            raise Exception(f"{settings.connection.portName} exists already")

        view = self.mainWindow.createSerialViewerWindow(settings.title,
                                                        self.settings.textHighlighter.entries,
                                                        size=settings.size,
                                                        position=settings.position,
                                                        splitterState=settings.splitterState,
                                                        currentTabName=settings.currentTabName)
        view.setSerialViewerSettings(settings)

        ctrl = SerialViewerController(settings, view)
        ctrl.signal_deleteController.connect(self.controllerPool.deleteController, type=Qt.ConnectionType.QueuedConnection)
        self.controllerPool.add(ctrl)

        if self.captureActive:
            if not ctrl.startCapture():
                self.stopCapture()

    @Slot()
    def clearAll(self):
        self.controllerPool.resetReceivedData()

    @Slot(bool)
    def toggleCaptureState(self):
        if self.captureActive:
            self.stopCapture()
        elif self.controllerPool.count() > 0:
            self.startCapture()

    def startCapture(self):
        if self.controllerPool.startCapture():
            self.captureActive = True
            self.mainWindow.updateCaptureButton(self.captureActive)
        else:
            self.stopCapture()

    @Slot()
    def stopCapture(self):
        self.controllerPool.stopCapture()
        self.captureActive = False
        self.mainWindow.updateCaptureButton(self.captureActive)

    def applySettings(self):
        self.mainWindow.resize(self.settings.mainWindow.size)
        self.mainWindow.addToolBar(self.settings.mainWindow.toolBarArea, self.mainWindow.toolBar)

        for serialViewerSetting in self.settings.serialViewer.entries:
            self.createSerialViewer(serialViewerSetting)
        # note: highlighter settings do not need to be applied here, because this is
        #       done inside function createSerialViewer

        if self.settings.application.restoreCaptureState:
            if self.settings.application.captureActive:
                self.startCapture()

    def persistCurrentSettings(self):
        self.settings.application.captureActive = self.captureActive

        self.settings.mainWindow.size = self.mainWindow.size()
        self.settings.mainWindow.toolBarArea = self.mainWindow.toolBarArea(self.mainWindow.toolBar)

        self.settings.serialViewer.entries.clear()

        ctrl: SerialViewerController
        for ctrl in self.controllerPool.entries():
            settings = SerialViewerSettings()
            settings.title = ctrl.view.windowTitle()
            settings.size = ctrl.view.size()
            settings.position = ctrl.view.pos()
            settings.splitterState = ctrl.view.splitter.saveState()
            settings.currentTabName = ctrl.view.getCurrentTab()
            settings.showNonPrintableCharsAsHex = ctrl.view.getSettingConvertNonPrintableCharsToHex()

            settings.autoscrollActive = ctrl.view.autoscroll.autoscrollIsActive()
            settings.autoscrollReactivate = ctrl.view.autoscroll.autoReactivateIsActive()

            settings.counters = ctrl.counterHandler.getSettings()
            settings.watches = ctrl.watchHandler.getSettings()

            connection: SerialConnectionSettings = ctrl.receiver.getSettings()
            settings.connection.portName = connection.portName
            settings.connection.baudrate = connection.baudrate
            settings.connection.dataBits = connection.dataBits
            settings.connection.parity = connection.parity
            settings.connection.stopBits = connection.stopBits

            self.settings.serialViewer.entries.append(settings)

        self.settings.saveSettings()

    def onAboutToBeClosed(self):
        self.persistCurrentSettings()
        self.stopCapture()
        self.controllerPool.deleteAll()
