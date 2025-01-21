import re

from PySide6.QtCore import QObject, Slot

from multiserialviewer.settings.watchSettings import WatchSettings
from multiserialviewer.serial_data.streamingTextExtractor import StreamingTextExtractor
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.application.watchTableModel import WatchTableModel, WatchEntryNumber, WatchEntryWord


class WatchHandler(QObject):
    def __init__(self, settings: list[WatchSettings], dataSource: SerialDataProcessor):
        super().__init__()
        self.dataSource: SerialDataProcessor = dataSource
        self.textExtractors: list[StreamingTextExtractor] = []
        self.watchTableModel: WatchTableModel = WatchTableModel()

        for watchSettings in settings:
            self.createWatch(watchSettings.name, watchSettings.description, watchSettings.variableType.name, watchSettings.pattern)

    def getSettings(self) -> list[WatchSettings]:
        assert len(self.textExtractors) == len(self.watchTableModel.entries)

        settings: list[WatchSettings] = []
        for index, entry in enumerate(self.watchTableModel.entries):
            assert isinstance(entry, (WatchEntryNumber, WatchEntryWord))
            assert entry.name == self.textExtractors[index].name

            if isinstance(self.watchTableModel.entries[index], WatchEntryNumber):
                settings.append(WatchSettings(entry.name, '', WatchSettings.VariableType.number, entry.pattern))
            elif isinstance(self.watchTableModel.entries[index], WatchEntryWord):
                settings.append(WatchSettings(entry.name, entry.description, WatchSettings.VariableType.word, entry.pattern))

        return settings

    def clear(self):
        self.watchTableModel.reset()

    @staticmethod
    def __createWatchPattern(variableName: str, pattern: str) -> str:
        return re.escape(variableName) + r"[\s:=]+" + pattern

    @Slot(str)
    def createWatch(self, variableName: str, description: str, variableType: str, pattern: str):
        varTypeSettings = WatchSettings.VariableType[variableType]

        self.removeWatchByVariableName(variableName)

        idx = -1
        if varTypeSettings == WatchSettings.VariableType.number:
            entry = WatchEntryNumber(variableName, pattern)
            idx = self.watchTableModel.addWatchEntry(entry)
        elif varTypeSettings == WatchSettings.VariableType.word:
            entry = WatchEntryWord(variableName, description, pattern)
            idx = self.watchTableModel.addWatchEntry(entry)

        if idx >= 0:
            watchPattern = self.__createWatchPattern(variableName, pattern)
            textExtractor = StreamingTextExtractor(variableName, watchPattern)
            self.dataSource.signal_asciiDataAvailable.connect(textExtractor.processBytesFromStream)
            textExtractor.signal_textExtracted.connect(self.watchTableModel.setWatchValue)
            self.textExtractors.append(textExtractor)

    def removeWatchByVariableName(self, variableName: str):
        index = self.watchTableModel.getWatchIndex(variableName)
        if index >= 0:
            self.removeWatchByIndex(index)

    @Slot(int)
    def removeWatchByIndex(self, index: int):
        if self.watchTableModel.removeWatchEntry(index):
            textExtractor = self.textExtractors[index]
            self.dataSource.signal_asciiDataAvailable.disconnect(textExtractor.processBytesFromStream)
            textExtractor.signal_textExtracted.disconnect(self.watchTableModel.setWatchValue)
            del self.textExtractors[index]
