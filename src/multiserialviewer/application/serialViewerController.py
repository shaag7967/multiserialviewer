from PySide6.QtCore import QObject, Slot, Signal, QThread

from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings
from multiserialviewer.settings.applicationSettings import ApplicationSettings
from multiserialviewer.gui_viewer.serialViewerWindow import SerialViewerWindow
from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.serial_data.serialDataStatistics import SerialDataStatistics
from multiserialviewer.application.counterHandler import CounterHandler
from multiserialviewer.application.watchHandler import WatchHandler
from multiserialviewer.application.statisticsHandler import StatisticsHandler


class SerialViewerController(QObject):
    signal_deleteController: Signal = Signal(str)

    def __init__(self, settings: SerialViewerSettings, settingsApplication: ApplicationSettings, view: SerialViewerWindow):
        super(SerialViewerController, self).__init__()

        self.dataProcessingThread: QThread = QThread(self)
        self.dataProcessingThread.setObjectName('SerialData thread')
        self.statsThread: QThread = QThread(self)
        self.statsThread.setObjectName('statsThread thread')

        self.receiver: SerialDataReceiver = SerialDataReceiver(settings.connection)
        self.processor: SerialDataProcessor = SerialDataProcessor()
        self.processor.setConvertNonPrintableCharsToHex(settingsApplication.showNonPrintableCharsAsHex)
        self.processor.setBackspaceDeletesLastLine(settingsApplication.backspaceDeletesLastLine)
        self.processor.setShowTimestampAtLineStart(settingsApplication.showTimestamp, settingsApplication.timestampFormat)
        self.statistics: SerialDataStatistics = SerialDataStatistics(settings.connection)

        self.counterHandler: CounterHandler = CounterHandler(settings.counters, self.processor)
        self.watchHandler: WatchHandler = WatchHandler(settings.watches, self.processor)
        self.statisticsHandler: StatisticsHandler = StatisticsHandler(self.statistics)

        self.processor.moveToThread(self.dataProcessingThread)
        self.statistics.moveToThread(self.statsThread)
        self.counterHandler.moveToThread(self.dataProcessingThread)
        self.watchHandler.moveToThread(self.dataProcessingThread)
        self.statisticsHandler.moveToThread(self.statsThread)

        self.dataProcessingThread.start()
        self.dataProcessingThread.setPriority(QThread.Priority.NormalPriority)
        self.statsThread.start()
        self.statsThread.setPriority(QThread.Priority.TimeCriticalPriority)

        self.view: SerialViewerWindow = view
        # counter
        self.view.counterWidget.setCounterTableModel(self.counterHandler.counterTableModel)
        self.view.counterWidget.signal_createCounter.connect(self.counterHandler.createCounter)
        self.view.counterWidget.signal_removeCounter.connect(self.counterHandler.removeCounter)
        # watch
        self.view.watchWidget.setWatchTableModel(self.watchHandler.watchTableModel)
        self.view.watchWidget.signal_createWatch.connect(self.watchHandler.createWatch)
        self.view.watchWidget.signal_removeWatch.connect(self.watchHandler.removeWatchByIndex)
        # stats
        self.view.statisticsWidget.setStatisticsTableModel(self.statisticsHandler.statisticsTableModel)

        self.view.textEdit.signal_createCounterFromSelectedText.connect(self.view.setCounterPatternToCreate)
        self.view.textEdit.signal_createWatchFromSelectedText.connect(self.view.createWatchFromText)
        self.view.signal_closed.connect(self.onViewClosed)

        self.processor.signal_asciiDataAvailable.connect(self.view.appendData)
        self.processor.signal_deleteLine.connect(self.view.deleteLastLine)
        self.processor.signal_numberOfNonPrintableChars.connect(self.statisticsHandler.handleInvalidByteCounter)
        self.receiver.signal_rawDataAvailable.connect(self.processor.handleRawData)
        self.receiver.signal_rawDataAvailable.connect(self.statistics.handleRawData)

    def getPortName(self) -> str:
        return self.receiver.getSettings().portName

    def startCapture(self) -> bool:
        opened, msg = self.receiver.openPort()
        if opened:
            self.showStartMessage(f'Opened {self.receiver.getSettings().portName}')
            return True
        else:
            self.showErrorMessage(f'Failed to open {self.receiver.getSettings().portName} ({msg})')
            return False

    def stopCapture(self):
        if self.receiver.portIsOpen():
            self.receiver.closePort()
            self.showStopMessage(f'Closed {self.receiver.getSettings().portName}')

    def clearAll(self):
        self.processor.clear()
        self.view.clear()
        self.counterHandler.clear()
        self.watchHandler.clear()
        self.statisticsHandler.clear()
        self.statistics.reset()

    def showErrorMessage(self, text):
        self.view.appendErrorMessage(text)

    def showStartMessage(self, text):
        self.view.appendStartMessage(text)

    def showStopMessage(self, text):
        self.view.appendStopMessage(text)

    def destruct(self):
        self.receiver.closePort()

        if self.dataProcessingThread.isRunning():
            self.dataProcessingThread.quit()
            self.dataProcessingThread.wait()
        if self.statsThread.isRunning():
            self.statsThread.quit()
            self.statsThread.wait()

        self.statistics.deleteLater()

    @Slot()
    def onViewClosed(self):
        # view is already closed
        self.signal_deleteController.emit(self.receiver.getSettings().portName)
