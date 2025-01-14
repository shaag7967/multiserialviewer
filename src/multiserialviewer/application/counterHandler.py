from PySide6.QtCore import QObject, Slot

from multiserialviewer.settings.counterSettings import CounterSettings
from multiserialviewer.serial_data.streamingTextExtractor import StreamingTextExtractor
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.application.counterTableModel import CounterTableModel


class CounterHandler(QObject):
    def __init__(self, settings: list[CounterSettings], dataSource: SerialDataProcessor):
        super().__init__()
        self.dataSource: SerialDataProcessor = dataSource
        self.textExtractors: list[StreamingTextExtractor] = []
        self.counterTableModel: CounterTableModel = CounterTableModel()

        for counterSettings in settings:
            self.createCounter(counterSettings.pattern)

    def getSettings(self) -> list[CounterSettings]:
        return self.counterTableModel.settings

    def clear(self):
        self.counterTableModel.resetCounters()

    @Slot(str)
    def createCounter(self, pattern: str):
        idx = self.counterTableModel.addCounterEntry(pattern)
        if idx >= 0:
            textExtractor = StreamingTextExtractor(pattern, pattern)
            self.dataSource.signal_asciiDataAvailable.connect(textExtractor.processBytesFromStream)
            textExtractor.signal_textExtracted.connect(self.counterTableModel.incrementCounterValue)
            self.textExtractors.append(textExtractor)

    @Slot(int)
    def removeCounter(self, index: int):
        if self.counterTableModel.removeCounterEntry(index):
            textExtractor = self.textExtractors[index]
            self.dataSource.signal_asciiDataAvailable.disconnect(textExtractor.processBytesFromStream)
            textExtractor.signal_textExtracted.disconnect(self.counterTableModel.incrementCounterValue)
            del self.textExtractors[index]
