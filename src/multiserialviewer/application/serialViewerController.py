from PySide6.QtCore import QObject, Slot, Signal

from multiserialviewer.gui.serialViewerWindow import SerialViewerWindow
from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.serial_data.serialDataStatistics import SerialDataStatistics


class SerialViewerController(QObject):
    terminated = Signal(str)

    def __init__(self, receiver: SerialDataReceiver, statistics: SerialDataStatistics, processor: SerialDataProcessor, view: SerialViewerWindow):
        super().__init__()

        self.receiver = receiver
        self.statistics = statistics
        self.processor = processor
        self.view = view

        self.view.closed.connect(self.terminate)
        self.processor.dataAvailable.connect(self.view.appendData)
        self.statistics.utilizationInPercentage.connect(self.view.setUtilizationInPercentage)

    def start(self) -> bool:
        if self.receiver.open_port():
            self.processor.start()
            self.statistics.start()
            self.receiver.start()
            self.show_message(f'Opened {self.receiver.settings.portName}')
            return True
        else:
            self.show_error(f'Failed to open {self.receiver.settings.portName}')
            return False

    def stop(self):
        if self.receiver.isReceiving():
            self.receiver.stop()
            self.receiver.close_port()
            self.statistics.stop()
            self.processor.stop()
            self.show_message(f'Closed {self.receiver.settings.portName}')

    def show_message(self, text):
        self.view.appendData(f'\n[MSG: {text} :MSG]\n', True)

    def show_error(self, text):
        self.view.appendData(f'\n[ERR: {text} :ERR]\n', True)

    @Slot()
    def terminate(self):
        # view is already closed
        self.receiver.stop()
        self.receiver.close_port()
        self.statistics.stop()
        self.processor.stop()
        self.terminated.emit(self.receiver.settings.portName)
