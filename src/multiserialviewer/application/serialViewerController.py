from PySide6.QtCore import QObject, Slot, Signal

from multiserialviewer.gui.serialViewerWindow import SerialViewerWindow
from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.serial_data.serialDataStatistics import SerialDataStatistics


class SerialViewerController(QObject):
    terminated = Signal(str)

    def __init__(self, receiver: SerialDataReceiver, processor: SerialDataProcessor, statistics: SerialDataStatistics, view: SerialViewerWindow):
        super().__init__()

        self.receiver: SerialDataReceiver = receiver
        self.processor: SerialDataProcessor = processor
        self.statistics: SerialDataStatistics = statistics
        self.view: SerialViewerWindow = view

        self.view.signal_closed.connect(self.terminate)

        self.statistics.signal_curUsageChanged.connect(self.view.statisticsWidget.handleCurUsageChanged)
        self.statistics.signal_maxUsageChanged.connect(self.view.statisticsWidget.handleMaxUsageChanged)
        self.statistics.signal_receivedBytesIncremented.connect(self.view.statisticsWidget.handleReceivedBytesIncremented)
        self.view.signal_clearPressed.connect(self.statistics.handleReset)

        self.receiver.signal_rawDataAvailable.connect(self.statistics.handleRawData)
        self.receiver.signal_rawDataAvailable.connect(self.processor.handleRawData)

        self.processor.signal_asciiDataAvailable.connect(self.view.appendData)

    def start(self) -> bool:
        if self.receiver.openPort():
            self.statistics.start()
            self.show_message(f'Opened {self.receiver.getSettings().portName}')
            return True
        else:
            self.show_error(f'Failed to open {self.receiver.getSettings().portName}')
            return False

    def stop(self):
        if self.receiver.closePort():
            self.statistics.stop()
            self.show_message(f'Closed {self.receiver.getSettings().portName}')

    def show_message(self, text):
        self.view.appendData(f'\n[MSG: {text} :MSG]\n')

    def show_error(self, text):
        self.view.appendData(f'\n[ERR: {text} :ERR]\n')

    @Slot()
    def terminate(self):
        # view is already closed
        self.receiver.closePort()
        portName: str = self.receiver.getSettings().portName

        del self.receiver
        del self.statistics
        del self.processor

        self.terminated.emit(portName)
