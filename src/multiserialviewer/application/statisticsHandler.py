from PySide6.QtCore import QObject, Slot

from multiserialviewer.serial_data.serialDataStatistics import SerialDataStatistics
from multiserialviewer.application.statisticsTableModel import StatisticsTableModel


class StatisticsHandler(QObject):
    def __init__(self, statisticsSource: SerialDataStatistics):
        super().__init__()
        self.statisticsSource: SerialDataStatistics = statisticsSource
        self.statisticsTableModel: StatisticsTableModel = StatisticsTableModel()


        self.statisticsSource.signal_curUsageChanged.connect(self.handleCurUsageChanged)
        self.statisticsSource.signal_maxUsageChanged.connect(self.handleMaxUsageChanged)
        self.statisticsSource.signal_receivedBytesIncremented.connect(self.handleReceivedBytesIncremented)

    def clear(self):
        self.statisticsTableModel.reset()

    @Slot(int)
    def handleCurUsageChanged(self, usageInPercent: int):
        self.statisticsTableModel.setCurrentUsage(usageInPercent)

    @Slot(int)
    def handleMaxUsageChanged(self, usageInPercent: int):
        self.statisticsTableModel.setMaxUsage(usageInPercent)

    @Slot(int)
    def handleReceivedBytesIncremented(self, count: int):
        self.statisticsTableModel.setReceivedByteCount(count)

    @Slot(int)
    def handleInvalidByteCounter(self, count: int):
        self.statisticsTableModel.handleInvalidByteCount(count)

