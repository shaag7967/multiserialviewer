from PySide6.QtCore import QSettings, QSize
from PySide6.QtSerialPort import QSerialPort
from typing import List
from pathlib import PurePath

from multiserialviewer.application.serialViewerSettings import SerialViewerSettings
from multiserialviewer.text_highlighter.textHighlighterSettings import TextHighlighterSettings


class Settings:
    settingsFileName_main = 'multiserialviewer.ini'
    settingsFileName_highlighter = 'highlighter.ini'

    def __init__(self, settingsDir: str):
        self.__settingsDir = settingsDir
        self.__mainSettingsFilePath = PurePath(self.__settingsDir, Settings.settingsFileName_main)
        # highlighter settings are stored in a separate file, because then e.g. it can be copied separately to another PC
        self.__highlighterSettingsFilePath = PurePath(self.__settingsDir, Settings.settingsFileName_highlighter)

        self.mainWindow: Settings.MainWindow = Settings.MainWindow()
        self.serialViewer: Settings.SerialViewer = Settings.SerialViewer()
        self.textHighlighter: Settings.TextHighlighter = Settings.TextHighlighter()

        self.restoreDefaultValues()

    def restoreDefaultValues(self):
        self.mainWindow.restoreDefaultValues()
        self.serialViewer.restoreDefaultValues()
        self.textHighlighter.restoreDefaultValues()

    def loadFromDisk(self):
        self.restoreDefaultValues()

        settings = QSettings(str(self.__mainSettingsFilePath), QSettings.Format.IniFormat)
        self.mainWindow.loadSettings(settings)
        self.serialViewer.loadSettings(settings)

        settings = QSettings(str(self.__highlighterSettingsFilePath), QSettings.Format.IniFormat)
        self.textHighlighter.loadSettings(settings)

    def saveToDisk(self):
        settings = QSettings(str(self.__mainSettingsFilePath), QSettings.Format.IniFormat)
        self.mainWindow.saveSettings(settings)
        self.serialViewer.saveSettings(settings)

        settings = QSettings(str(self.__highlighterSettingsFilePath), QSettings.Format.IniFormat)
        self.textHighlighter.saveSettings(settings)

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

    class SerialViewer:
        ArrayName_v1: str = "SerialViewer"

        def __init__(self):
            self.entries: List[SerialViewerSettings] = []

        def restoreDefaultValues(self):
            self.entries = []

        def loadSettings(self, settings: QSettings):
            self.restoreDefaultValues()

            numberOfSerialViewers = settings.beginReadArray(self.ArrayName_v1)
            for index in range(numberOfSerialViewers):
                settings.setArrayIndex(index)

                entry = SerialViewerSettings()
                # settings of window
                if settings.contains("view/title"):
                    entry.title = settings.value("view/title")
                if settings.contains("view/size"):
                    entry.size = settings.value("view/size")
                if settings.contains("view/pos"):
                    entry.position = settings.value("view/pos")
                # serial connection settings
                if settings.contains("connection/portName"):
                    entry.connection.portName = settings.value("connection/portName")
                if settings.contains("connection/baudrate"):
                    entry.connection.baudrate = int(settings.value("connection/baudrate"))
                if settings.contains("connection/dataBits"):
                    entry.connection.dataBits = QSerialPort.DataBits(settings.value("connection/dataBits", type=int))
                if settings.contains("connection/parity"):
                    entry.connection.parity = QSerialPort.Parity(settings.value("connection/parity", type=int))
                if settings.contains("connection/stopBits"):
                    entry.connection.stopBits = QSerialPort.StopBits(settings.value("connection/stopBits", type=int))

                self.entries.append(entry)
            settings.endArray()

        def saveSettings(self, settings: QSettings):
            settings.beginWriteArray(self.ArrayName_v1)
            settings.remove("")  # remove all existing entries

            for index, entry in enumerate(self.entries):
                settings.setArrayIndex(index)

                settings.setValue("view/title", entry.title)
                settings.setValue("view/size", entry.size)
                settings.setValue("view/pos", entry.position)

                settings.setValue("connection/portName", entry.connection.portName)
                settings.setValue("connection/baudrate", entry.connection.baudrate)
                settings.setValue("connection/dataBits", entry.connection.dataBits.value)
                settings.setValue("connection/parity", entry.connection.parity.value)
                settings.setValue("connection/stopBits", entry.connection.stopBits.value)
            settings.endArray()


    class TextHighlighter:
        ArrayName_v1: str = "TextHighlighter"

        def __init__(self):
            self.entries: List[TextHighlighterSettings] = []

        def restoreDefaultValues(self):
            self.entries = []

        def loadSettings(self, settings: QSettings):
            self.restoreDefaultValues()

            numberOfEntries = settings.beginReadArray(self.ArrayName_v1)
            for index in range(numberOfEntries):
                settings.setArrayIndex(index)

                entry = TextHighlighterSettings()
                if settings.contains("pattern"):
                    entry.pattern = settings.value("pattern")
                if settings.contains("color_foreground"):
                    entry.color_foreground = settings.value("color_foreground")
                if settings.contains("color_background"):
                    entry.color_background = settings.value("color_background")
                if settings.contains("italic"):
                    entry.italic = settings.value("italic", type=bool)
                if settings.contains("bold"):
                    entry.bold = settings.value("bold", type=bool)
                if settings.contains("font_size"):
                    entry.font_size = settings.value("font_size", type=int)

                self.entries.append(entry)
            settings.endArray()

        def saveSettings(self, settings: QSettings):
            settings.beginWriteArray(self.ArrayName_v1)
            settings.remove("")  # remove all existing entries

            for index, entry in enumerate(self.entries):
                settings.setArrayIndex(index)

                settings.setValue("pattern", entry.pattern)
                settings.setValue("color_foreground", entry.color_foreground)
                settings.setValue("color_background", entry.color_background)
                settings.setValue("italic", entry.italic)
                settings.setValue("bold", entry.bold)
                settings.setValue("font_size", entry.font_size)

            settings.endArray()
