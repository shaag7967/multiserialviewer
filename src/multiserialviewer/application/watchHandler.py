from PySide6.QtCore import QObject, Slot

from multiserialviewer.settings.watchSettings import WatchSettings
from multiserialviewer.serial_data.streamingTextExtractor import StreamingTextExtractor
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.application.watchTableModel import WatchTableModel


class WatchHandler(QObject):
    def __init__(self, settings: list[WatchSettings], dataSource: SerialDataProcessor):
        super().__init__()
        self.dataSource: SerialDataProcessor = dataSource
        self.textExtractors: list[StreamingTextExtractor] = []
        self.watchTableModel: WatchTableModel = WatchTableModel()

        for watchSettings in settings:
            self.createWatch(watchSettings.name, watchSettings.pattern)

    def getSettings(self) -> list[WatchSettings]:
        return self.watchTableModel.settings

    def clear(self):
        self.watchTableModel.reset()

    @Slot(str)
    def createWatch(self, name: str, pattern: str):
        idx = self.watchTableModel.addWatchEntry(name, pattern)
        if idx >= 0:
            textExtractor = StreamingTextExtractor(name, pattern)
            self.dataSource.signal_asciiDataAvailable.connect(textExtractor.processBytesFromStream)
            textExtractor.signal_textExtracted.connect(self.watchTableModel.setWatchValue)
            self.textExtractors.append(textExtractor)

    @Slot(int)
    def removeWatch(self, index: int):
        if self.watchTableModel.removeWatchEntry(index):
            textExtractor = self.textExtractors[index]
            self.dataSource.signal_asciiDataAvailable.disconnect(textExtractor.processBytesFromStream)
            textExtractor.signal_textExtracted.disconnect(self.watchTableModel.setWatchValue)
            del self.textExtractors[index]
