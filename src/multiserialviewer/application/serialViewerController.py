from PySide6.QtCore import QObject, Slot, Signal
from datetime import datetime

from multiserialviewer.gui_viewer.serialViewerWindow import SerialViewerWindow
from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor


class SerialViewerController(QObject):
    terminated = Signal(str)

    def __init__(self, receiver: SerialDataReceiver, processor: SerialDataProcessor, view: SerialViewerWindow):
        super().__init__()

        self.receiver: SerialDataReceiver = receiver
        self.processor: SerialDataProcessor = processor
        self.view: SerialViewerWindow = view

        self.view.signal_closed.connect(self.terminate)
        self.receiver.signal_rawDataAvailable.connect(self.processor.handleRawData)

    def start(self) -> bool:
        if self.receiver.openPort():
            self.processor.start()
            self.receiver.start()

            self.show_message(f'Opened {self.receiver.getSettings().portName}')
            self.processor.signal_asciiDataAvailable.connect(self.view.appendData)
            return True
        else:
            self.show_error(f'Failed to open {self.receiver.getSettings().portName}')
            return False

    def stop(self):
        if self.receiver.isReceiving():
            self.receiver.stop()
            self.receiver.closePort()
            self.processor.stop()
            self.processor.signal_asciiDataAvailable.disconnect(self.view.appendData)
            self.show_message(f'Closed {self.receiver.getSettings().portName}')

    def show_message(self, text):
        self.view.appendData(f'\n[MSG: {datetime.now().strftime("%Y/%b/%d %H:%M:%S")}: {text} :MSG]\n')

    def show_error(self, text):
        self.view.appendData(f'\n[ERR: {datetime.now().strftime("%Y/%b/%d %H:%M:%S")}: {text} :ERR]\n')

    @Slot()
    def terminate(self):
        # view is already closed
        self.receiver.stop()
        self.receiver.closePort()
        self.processor.stop()
        self.terminated.emit(self.receiver.getSettings().portName)
