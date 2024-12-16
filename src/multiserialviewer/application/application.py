from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings, QSize, Slot
from typing import List
from platformdirs import user_config_dir
import pathlib
import copy

from multiserialviewer.gui.mainWindow import MainWindow
from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.serial_data.serialConnectionSettings import SerialConnectionSettings
from multiserialviewer.text_highlighter.textHighlighterConfig import TextHighlighterConfig
from multiserialviewer.application.serialViewerController import SerialViewerController
from multiserialviewer.application.proxyStyle import ProxyStyle




class Application(QApplication):
    NAME = 'MultiSerialViewer'

    def __init__(self, version: str, arguments):
        super().__init__(arguments)

        self.config_dir = user_config_dir(appname=Application.NAME, roaming=False, ensure_exists=True, appauthor=False)
        self.main_config_file_path = str(pathlib.PurePath(self.config_dir, 'multiserialviewer.ini'))
        self.highlighter_config_file_path = str(pathlib.PurePath(self.config_dir, 'highlighter.ini'))

        self.controller = {}
        self.highlighterSettings: List[TextHighlighterConfig] = []

        self.mainWindow = MainWindow(f'{Application.NAME} {version}')
        self.mainWindow.signal_showSerialViewerCreateDialog.connect(self.showSerialViewerCreateDialog)
        self.mainWindow.signal_createSerialViewer.connect(self.createSerialViewer)
        self.mainWindow.signal_clearAll.connect(self.clearAll)
        self.mainWindow.signal_connectionStateChanged.connect(self.changeConnectionState)
        self.mainWindow.signal_aboutToBeClosed.connect(self.saveSettings)
        self.mainWindow.signal_aboutToBeClosed.connect(self.saveSerialViewerSettings)
        self.mainWindow.signal_aboutToBeClosed.connect(self.saveHighlighterSettings)
        self.mainWindow.signal_aboutToBeClosed.connect(self.stopAllSerialViewer)
        self.mainWindow.signal_editHighlighterSettings.connect(self.showHighlighterSettingsDialog)
        self.mainWindow.signal_applyHighlighterSettings.connect(self.setHighlighterSettings)

        self.loadSettings()
        self.loadHighlighterSettings()
        self.loadSerialViewerSettings()

        self.setStyle(ProxyStyle())
        self.mainWindow.show()

    def initDefaultHighlighterSettings(self):
        self.highlighterSettings = []

        cfg = TextHighlighterConfig()
        cfg.pattern = r'\[MSG: .* :MSG\]'
        cfg.color_foreground = 'darkgreen'
        cfg.color_background = 'transparent'
        cfg.italic = False
        cfg.bold = True
        cfg.font_size = QApplication.font().pointSize()
        self.highlighterSettings.append(cfg)

        cfg = TextHighlighterConfig()
        cfg.pattern = r'\[ERR: .* :ERR\]'
        cfg.color_foreground = 'darkred'
        cfg.color_background = 'transparent'
        cfg.italic = False
        cfg.bold = True
        cfg.font_size = QApplication.font().pointSize()
        self.highlighterSettings.append(cfg)

    @Slot(object)
    def setHighlighterSettings(self, settings: List[TextHighlighterConfig]):
        self.highlighterSettings = settings
        for ctrl in self.controller.values():
            ctrl.view.setHighlighterSettings(self.highlighterSettings)

    @Slot()
    def showSerialViewerCreateDialog(self):
        already_used_ports = list(self.controller.keys())
        self.mainWindow.showSerialViewerCreateDialog(already_used_ports)

    @Slot(str, SerialConnectionSettings)
    def createSerialViewer(self, window_title: str, settings: SerialConnectionSettings, size: QSize = None):
        if settings.portName in self.controller:
            raise Exception(f"{settings.portName} exists already")

        receiver = SerialDataReceiver(settings)
        processor = SerialDataProcessor(receiver.rxQueue)
        view = self.mainWindow.createSerialViewerWindow(window_title, size)
        view.setHighlighterSettings(self.highlighterSettings)
        ctrl = SerialViewerController(receiver, processor, view)

        ctrl.terminated.connect(self.deleteSerialViewer)
        self.controller[settings.portName] = ctrl

        if self.mainWindow.getConnectionState():
            ctrl.start()

    @Slot()
    def deleteSerialViewer(self, portName):
        if portName in self.controller:
            del self.controller[portName]
        else:
            raise Exception("Controller to remove does not exist in list")

    @Slot()
    def clearAll(self):
        for ctrl in self.controller.values():
            ctrl.view.clear()

    @Slot(bool)
    def changeConnectionState(self, state):
        if len(self.controller.values()) > 0:
            if state:
                failed_to_connect = False

                # try to connect all ports
                for ctrl in self.controller.values():
                    if not ctrl.start():
                        failed_to_connect = True

                if failed_to_connect:
                    # cleanup if connect failed
                    for ctrl in self.controller.values():
                        ctrl.stop()
                    self.mainWindow.setConnectionState(False)
                else:
                    self.mainWindow.setConnectionState(True)
            else:
                for ctrl in self.controller.values():
                    ctrl.stop()
                self.mainWindow.setConnectionState(False)
        else:
            self.mainWindow.setConnectionState(False)

    def loadSettings(self):
        settings = QSettings(self.main_config_file_path, QSettings.Format.IniFormat)

        settings.beginGroup("MainWindow")
        self.mainWindow.resize(settings.value("size", QSize(800, 800)))
        settings.endGroup()

    def saveSettings(self):
        settings = QSettings(self.main_config_file_path, QSettings.Format.IniFormat)

        settings.beginGroup("MainWindow")
        settings.setValue("size", self.mainWindow.size())
        settings.endGroup()

    def loadSerialViewerSettings(self):
        settings = QSettings(self.main_config_file_path, QSettings.Format.IniFormat)

        number_of_connections = settings.beginReadArray("connections")
        for i in range(number_of_connections):
            settings.setArrayIndex(i)

            # check if all needed keys exist
            if all(elem in settings.allKeys() for elem in ['serialViewer', 'view/size', 'view/title']):
                self.createSerialViewer(settings.value("view/title"), settings.value("serialViewer"),
                                        settings.value("view/size"))
        settings.endArray()

    @Slot()
    def saveSerialViewerSettings(self):
        settings = QSettings(self.main_config_file_path, QSettings.Format.IniFormat)

        settings.beginWriteArray("connections")
        settings.remove("")  # remove all existing connections

        for i, ctrl in enumerate(self.controller.values()):
            settings.setArrayIndex(i)
            settings.setValue("serialViewer", ctrl.receiver.settings)
            settings.setValue("view/title", ctrl.view.windowTitle())
            settings.setValue("view/size", ctrl.view.size())

        settings.endArray()

    def loadHighlighterSettings(self):
        settings = QSettings(self.highlighter_config_file_path, QSettings.Format.IniFormat)

        number_of_settings = settings.beginReadArray("settings")
        if number_of_settings > 0:
            self.highlighterSettings = []

            for i in range(number_of_settings):
                settings.setArrayIndex(i)

                # check if all needed keys exist
                if all(elem in settings.allKeys() for elem in ['pattern', 'color_foreground', 'color_background', 'italic', 'bold']):
                    cfg = TextHighlighterConfig()
                    cfg.pattern = settings.value("pattern")
                    cfg.color_foreground = settings.value("color_foreground")
                    cfg.color_background = settings.value("color_background")
                    cfg.italic = settings.value("italic", type=bool)
                    cfg.bold = settings.value("bold", type=bool)
                    cfg.font_size = settings.value("font_size", type=int)
                    self.highlighterSettings.append(cfg)
            settings.endArray()
        else:
            self.initDefaultHighlighterSettings()

    @Slot()
    def saveHighlighterSettings(self):
        settings = QSettings(self.highlighter_config_file_path, QSettings.Format.IniFormat)

        settings.beginWriteArray("settings")
        settings.remove("")  # remove all existing settings

        for i, cfg in enumerate(self.highlighterSettings):
            settings.setArrayIndex(i)
            settings.setValue("pattern", cfg.pattern)
            settings.setValue("color_foreground", cfg.color_foreground)
            settings.setValue("color_background", cfg.color_background)
            settings.setValue("italic", cfg.italic)
            settings.setValue("bold", cfg.bold)
            settings.setValue("font_size", cfg.font_size)
        settings.endArray()

    @Slot()
    def stopAllSerialViewer(self):
        for ctrl in self.controller.values():
            ctrl.stop()

    @Slot()
    def showHighlighterSettingsDialog(self):
        self.mainWindow.showHighlighterSettingsDialog(copy.deepcopy(self.highlighterSettings))
