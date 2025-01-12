from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QGuiApplication
from typing import List
from platformdirs import user_config_dir
import copy

from multiserialviewer.gui_main.mainWindow import MainWindow
from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
from multiserialviewer.settings.textHighlighterSettings import TextHighlighterSettings
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings, CounterSettings
from multiserialviewer.application.serialViewerController import SerialViewerController
from multiserialviewer.application.proxyStyle import ProxyStyle
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.settings.settings import Settings


class Application(QApplication):
    NAME = 'MultiSerialViewer'

    def __init__(self, version: str, arguments):
        super().__init__(arguments)

        self.configDir = user_config_dir(appname=Application.NAME, roaming=False, ensure_exists=True, appauthor=False)
        self.settings: Settings = Settings(self.configDir)
        self.settings.loadFromDisk()

        self.captureActive: bool = False
        self.controller = {}

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
        self.mainWindow.signal_aboutToBeClosed.connect(self.persistCurrentSettings)
        self.mainWindow.signal_aboutToBeClosed.connect(self.stopAllSerialViewer)
        self.mainWindow.signal_editHighlighterSettings.connect(self.showHighlighterSettingsDialog)
        self.mainWindow.signal_applyHighlighterSettings.connect(self.setHighlighterSettings)
        self.mainWindow.signal_createTextHighlightEntry.connect(self.createTextHighlightEntry)
        self.mainWindow.signal_openSettingsDirectory.connect(self.openSettingsDirectoryInFileBrowser)

        self.applySettings()
        self.setStyle(ProxyStyle())
        self.mainWindow.show()

        if len(self.controller) == 0:
            self.showSerialViewerCreateDialog()

    @Slot(object)
    def setHighlighterSettings(self, settings: List[TextHighlighterSettings]):
        self.settings.textHighlighter.entries = settings
        for ctrl in self.controller.values():
            ctrl.view.setHighlighterSettings(self.settings.textHighlighter.entries)

    @Slot(str)
    def createTextHighlightEntry(self, text_to_highlight: str):
        settings = TextHighlighterSettings()
        settings.pattern = text_to_highlight

        highlighter_settings = copy.deepcopy(self.settings.textHighlighter.entries)
        highlighter_settings.append(settings)
        self.mainWindow.showHighlighterSettingsDialog(highlighter_settings)

    @Slot()
    def showSerialViewerCreateDialog(self):
        already_used_ports = list(self.controller.keys())
        self.mainWindow.showSerialViewerCreateDialog(already_used_ports)

    @Slot()
    def showHighlighterSettingsDialog(self):
        self.mainWindow.showHighlighterSettingsDialog(copy.deepcopy(self.settings.textHighlighter.entries))

    @Slot()
    def openSettingsDirectoryInFileBrowser(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.configDir))

    @Slot(str, SerialConnectionSettings)
    def createSerialViewer(self, settings: SerialViewerSettings):
        if settings.connection.portName in self.controller:
            raise Exception(f"{settings.connection.portName} exists already")

        view = self.mainWindow.createSerialViewerWindow(settings.title,
                                                        size=settings.size,
                                                        position=settings.position,
                                                        splitterState=settings.splitterState,
                                                        currentTabName=settings.currentTabName)
        view.setHighlighterSettings(self.settings.textHighlighter.entries)
        view.setSerialViewerSettings(settings)
        ctrl = SerialViewerController(settings, view)

        ctrl.terminated.connect(self.deleteSerialViewer, type=Qt.ConnectionType.QueuedConnection)
        self.controller[settings.connection.portName] = ctrl

        if self.captureActive:
            if not ctrl.start():
                self.stopAllSerialViewer()

    @Slot()
    def deleteSerialViewer(self, portName):
        if portName in self.controller:
            del self.controller[portName]
        else:
            raise Exception("Controller to remove does not exist in list")

    @Slot()
    def clearAll(self):
        for ctrl in self.controller.values():
            ctrl.clearAll()

    @Slot(bool)
    def toggleCaptureState(self):
        if self.captureActive:
            self.stopAllSerialViewer()
        elif len(self.controller.values()) > 0:
            self.startAllSerialViewer()

    def startAllSerialViewer(self):
        controller_started_count = 0
        for ctrl in self.controller.values():
            if ctrl.start():
                controller_started_count += 1

        if controller_started_count == len(self.controller):
            self.captureActive = True
            self.mainWindow.updateCaptureButton(self.captureActive)
        else:
            self.stopAllSerialViewer()

    @Slot()
    def stopAllSerialViewer(self):
        for ctrl in self.controller.values():
            ctrl.stop()
        self.captureActive = False
        self.mainWindow.updateCaptureButton(self.captureActive)

    def applySettings(self):
        self.mainWindow.resize(self.settings.mainWindow.size)
        self.mainWindow.addToolBar(self.settings.mainWindow.toolBarArea, self.mainWindow.toolBar)

        for serialViewerSetting in self.settings.serialViewer.entries:
            self.createSerialViewer(serialViewerSetting)
        # note: highlighter settings do not need to be applied here, because this is
        #       done inside function createSerialViewer

    def persistCurrentSettings(self):
        self.settings.mainWindow.size = self.mainWindow.size()
        self.settings.mainWindow.toolBarArea = self.mainWindow.toolBarArea(self.mainWindow.toolBar)

        self.settings.serialViewer.entries.clear()
        for ctrl in self.controller.values():
            settings = SerialViewerSettings()
            settings.title = ctrl.view.windowTitle()
            settings.size = ctrl.view.size()
            settings.position = ctrl.view.pos()
            settings.splitterState = ctrl.view.splitter.saveState()
            settings.currentTabName = ctrl.view.getCurrentTab()

            settings.autoscrollActive = ctrl.view.autoscroll.autoscrollIsActive()
            settings.autoscrollReactivate = ctrl.view.autoscroll.autoReactivateIsActive()

            settings.counters = ctrl.counterHandler.getSettings()

            connection: SerialConnectionSettings = ctrl.receiver.getSettings()
            settings.connection.portName = connection.portName
            settings.connection.baudrate = connection.baudrate
            settings.connection.dataBits = connection.dataBits
            settings.connection.parity = connection.parity
            settings.connection.stopBits = connection.stopBits

            self.settings.serialViewer.entries.append(settings)

        self.settings.saveToDisk()
