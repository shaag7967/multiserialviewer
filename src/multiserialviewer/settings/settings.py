from PySide6.QtCore import Qt, QSettings, QSize
from PySide6.QtSerialPort import QSerialPort
from typing import List, Any
from pathlib import PurePath

from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings, CounterSettings
from multiserialviewer.settings.textHighlighterSettings import TextHighlighterSettings


class MandatorySettingsValueNotFound(Exception):
    """Exception raised if a mandatory settings value does not exist.

    Attributes:
        context -- name of settings
        key -- key of settings value
    """

    def __init__(self, context: str, key: str):
        self.key = key
        self.context = context
        super().__init__(f"Invalid settings: {key} missing in {context}")


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

    @staticmethod
    def loadMandatoryValue(settings: QSettings, key: str) -> Any:
        if settings.contains(key):
            return settings.value(key)
        else:
            raise MandatorySettingsValueNotFound(settings.group(), key)

    class MainWindow:
        SettingsName_v1: str = "MainWindow"

        def __init__(self):
            self.size: QSize = QSize()
            self.toolBarArea: Qt.ToolBarArea = Qt.ToolBarArea.TopToolBarArea
            self.restoreDefaultValues()

        def restoreDefaultValues(self):
            self.size = QSize(800, 800)
            self.toolBarArea = Qt.ToolBarArea.LeftToolBarArea

        def loadSettings(self, settings: QSettings):
            self.restoreDefaultValues()

            if Settings.MainWindow.SettingsName_v1 in settings.childGroups():
                self.loadSettings_V1(settings)

        def loadSettings_V1(self, settings: QSettings):
            settings.beginGroup(self.SettingsName_v1)
            if settings.contains("size"):
                self.size = settings.value("size")
            if settings.contains("toolBarArea"):
                self.toolBarArea = Qt.ToolBarArea(int(settings.value("toolBarArea")))
            settings.endGroup()

        def saveSettings(self, settings: QSettings):
            """ Writes settings to disk. We always use the latest version."""
            settings.beginGroup(self.SettingsName_v1)
            settings.setValue("size", self.size)
            settings.setValue("toolBarArea", self.toolBarArea.value)
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

                settings.beginGroup('view')
                entry = SerialViewerSettings()
                # settings of window
                if settings.contains("title"):
                    entry.title = settings.value("title")
                if settings.contains("size"):
                    entry.size = settings.value("size")
                if settings.contains("position"):
                    entry.position = settings.value("position")
                if settings.contains("autoscrollActive"):
                    entry.autoscrollActive = settings.value("autoscrollActive", type=bool)
                if settings.contains("autoscrollReactivate"):
                    entry.autoscrollReactivate = settings.value("autoscrollReactivate", type=bool)
                if settings.contains("splitterState"):
                    entry.splitterState = settings.value("splitterState")
                if settings.contains("currentTabName"):
                    entry.currentTabName = settings.value("currentTabName")
                settings.endGroup()

                numberOfCounters = settings.beginReadArray('counter')
                for counterIndex in range(numberOfCounters):
                    settings.setArrayIndex(counterIndex)
                    counterSettings = CounterSettings(settings.value("regex"))
                    entry.counters.append(counterSettings)
                settings.endArray()

                # serial connection settings (mandatory)
                settings.beginGroup('connection')
                try:
                    entry.connection.portName = Settings.loadMandatoryValue(settings, "portName")
                    entry.connection.baudrate = int(Settings.loadMandatoryValue(settings, "baudrate"))
                    entry.connection.dataBits = QSerialPort.DataBits(int(Settings.loadMandatoryValue(settings, "dataBits")))
                    entry.connection.parity = QSerialPort.Parity(int(Settings.loadMandatoryValue(settings, "parity")))
                    entry.connection.stopBits = QSerialPort.StopBits(int(Settings.loadMandatoryValue(settings, "stopBits")))

                    self.entries.append(entry)
                except MandatorySettingsValueNotFound as e:
                    # we do not add this entry because at least one important parameter is missing
                    print(e)
                settings.endGroup()

            settings.endArray()

        def saveSettings(self, settings: QSettings):
            settings.beginWriteArray(self.ArrayName_v1)
            settings.remove("")  # remove all existing entries

            for index, entry in enumerate(self.entries):
                settings.setArrayIndex(index)

                settings.beginGroup('view')
                settings.setValue("title", entry.title)
                settings.setValue("size", entry.size)
                settings.setValue("position", entry.position)
                settings.setValue("autoscrollActive", entry.autoscrollActive)
                settings.setValue("autoscrollReactivate", entry.autoscrollReactivate)
                settings.setValue("splitterState", entry.splitterState)
                settings.setValue("currentTabName", entry.currentTabName)
                settings.endGroup()

                settings.beginWriteArray('counter')
                settings.remove("")  # remove all existing entries

                for counterIndex, counter in enumerate(entry.counters):
                    settings.setArrayIndex(counterIndex)
                    settings.setValue('regex', counter.regex)
                settings.endArray()

                settings.beginGroup('connection')
                settings.setValue("portName", entry.connection.portName)
                settings.setValue("baudrate", entry.connection.baudrate)
                settings.setValue("dataBits", entry.connection.dataBits.value)
                settings.setValue("parity", entry.connection.parity.value)
                settings.setValue("stopBits", entry.connection.stopBits.value)
                settings.endGroup()
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
