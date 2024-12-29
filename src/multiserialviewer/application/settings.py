from PySide6.QtCore import QSettings, QSize, QPoint, Qt
from PySide6.QtWidgets import QApplication
from typing import Optional, List
from pathlib import PurePath

from multiserialviewer.serial_data.serialConnectionSettings import SerialConnectionSettings, QSerialPort
from multiserialviewer.text_highlighter.textHighlighterConfig import TextHighlighterConfig


class Settings:
    settingsFileName_main = 'multiserialviewer2.ini'
    settingsFileName_highlighter = 'highlighter.ini'

    def __init__(self, configDir: str):
        self.__configDir = configDir
        self.__mainSettingsFilePath = PurePath(self.__configDir, Settings.settingsFileName_main)
        # highlighter settings are stored in a separate file, because then it can be copied separately to another PC
        self.__highlighterSettingsFilePath = PurePath(self.__configDir, Settings.settingsFileName_highlighter)

        self.mainWindow: Settings.MainWindow = Settings.MainWindow()
        self.serialViewerList: Settings.SerialViewerArray = Settings.SerialViewerArray()

        self.restoreDefaultValues()

    def restoreDefaultValues(self):
        self.mainWindow.restoreDefaultValues()
        self.serialViewerList.restoreDefaultValues()

    def loadFromDisk(self):
        self.restoreDefaultValues()

        settings = QSettings(str(self.__mainSettingsFilePath), QSettings.Format.IniFormat)

        self.mainWindow.loadSettings(settings)
        self.serialViewerList.loadSettings(settings)

    def saveToDisk(self):
        settings = QSettings(str(self.__mainSettingsFilePath), QSettings.Format.IniFormat)

        self.mainWindow.saveSettings(settings)
        self.serialViewerList.saveSettings(settings)

    class MainWindow:
        SettingsName_v1: str = "MainWindow"

        def __init__(self):
            self.size: QSize = QSize()
            self.restoreDefaultValues()

        def restoreDefaultValues(self):
            self.size = QSize(800, 800)

        def loadSettings(self, settings: QSettings):
            self.restoreDefaultValues()

            if Settings.MainWindow.SettingsName_v1 in settings.childGroups():
                self.loadSettings_V1(settings)

        def loadSettings_V1(self, settings: QSettings):
            settings.beginGroup(self.SettingsName_v1)
            if settings.contains("size"):
                self.size = settings.value("size")
            settings.endGroup()

        def saveSettings(self, settings: QSettings):
            """ Writes settings to disk. We always use the latest version."""
            settings.beginGroup(self.SettingsName_v1)
            settings.setValue("size", self.size)
            settings.endGroup()

    class SerialViewerArray:
        ArrayName_v1: str = "SerialViewer"

        def __init__(self):
            self.__index: int = 0
            self.serialViewer: List[Settings.SerialViewer] = []

        def __iter__(self):
            self.__index = 0
            return self

        def __next__(self):
            if self.__index < len(self.serialViewer):
                self.__index += 1
                return self.serialViewer[self.__index - 1]
            raise StopIteration

        def clear(self):
            self.serialViewer.clear()

        def append(self, item):
            self.serialViewer.append(item)

        def restoreDefaultValues(self):
            self.serialViewer = []

        def loadSettings(self, settings: QSettings):
            self.restoreDefaultValues()

            numberOfSerialViewers = settings.beginReadArray(self.ArrayName_v1)
            for index in range(numberOfSerialViewers):
                settings.setArrayIndex(index)

                viewer: Settings.SerialViewer = Settings.SerialViewer()
                viewer.loadSettings(settings)
                self.serialViewer.append(viewer)
            settings.endArray()

        def saveSettings(self, settings: QSettings):
            settings.beginWriteArray(self.ArrayName_v1)
            settings.remove("")  # remove all existing connections

            for index, serialViewer in enumerate(self.serialViewer):
                settings.setArrayIndex(index)

                serialViewer.saveSettings(settings)
            settings.endArray()


    class SerialViewer:
        def __init__(self):
            self.title: str = ''
            self.size: Optional[QSize] = None
            self.position: Optional[QPoint] = None
            self.connection: SerialConnectionSettings = SerialConnectionSettings('')

        def restoreDefaultValues(self):
            self.title = 'Unnamed'
            self.size = None
            self.position = None
            self.connection = SerialConnectionSettings('')

        def loadSettings(self, settings: QSettings):
            self.restoreDefaultValues()

            if settings.contains("view/title"):
                self.title = settings.value("view/title")
            if settings.contains("view/size"):
                self.size = settings.value("view/size")
            if settings.contains("view/pos"):
                self.position = settings.value("view/pos")

            # load serial connection settings
            if settings.contains("connection/portName"):
                self.connection.portName = str(settings.value("connection/portName"))
            if settings.contains("connection/baudrate"):
                self.connection.baudrate = int(settings.value("connection/baudrate"))
            if settings.contains("connection/dataBits"):
                self.connection.dataBits = QSerialPort.DataBits(int(settings.value("connection/dataBits")))
            if settings.contains("connection/parity"):
                self.connection.parity = QSerialPort.Parity(int(settings.value("connection/parity")))
            if settings.contains("connection/stopBits"):
                self.connection.stopBits = QSerialPort.StopBits(int(settings.value("connection/stopBits")))

        def saveSettings(self, settings: QSettings):
            settings.setValue("view/title", self.title)
            settings.setValue("view/size", self.size)
            settings.setValue("view/pos", self.position)

            settings.setValue("connection/portName", self.connection.portName)
            settings.setValue("connection/baudrate", self.connection.baudrate)
            settings.setValue("connection/dataBits", self.connection.dataBits.value)
            settings.setValue("connection/parity", self.connection.parity.value)
            settings.setValue("connection/stopBits", self.connection.stopBits.value)

