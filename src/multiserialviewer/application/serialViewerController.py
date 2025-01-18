from PySide6.QtCore import QObject, Slot, Signal, QThread
from datetime import datetime

from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings
from multiserialviewer.gui_viewer.serialViewerWindow import SerialViewerWindow
from multiserialviewer.serial_data.serialDataReceiver import SerialDataReceiver
from multiserialviewer.serial_data.serialDataProcessor import SerialDataProcessor
from multiserialviewer.application.counterHandler import CounterHandler


class SerialViewerController(QObject):
    signal_deleteController: Signal = Signal(str)

    def __init__(self, settings: SerialViewerSettings, view: SerialViewerWindow):
        super(SerialViewerController, self).__init__()

        self.receiver: SerialDataReceiver = SerialDataReceiver(settings.connection)
        self.receiverThread: QThread = QThread(self)
        self.receiverThread.setObjectName('SerialDataReceiver thread')
        self.receiver.moveToThread(self.receiverThread)
        self.receiverThread.start()

        self.processor: SerialDataProcessor = SerialDataProcessor()
        self.processor.setConvertNonPrintableCharsToHex(settings.showNonPrintableCharsAsHex)
        self.processorThread: QThread = QThread(self)
        self.processorThread.setObjectName('SerialDataProcessor thread')
        self.processor.moveToThread(self.processorThread)
        self.processorThread.start()

        self.counterHandler: CounterHandler = CounterHandler(settings.counters, self.processor)

        self.view: SerialViewerWindow = view
        self.view.counterWidget.setCounterTableModel(self.counterHandler.counterTableModel)
        self.view.textEdit.signal_createCounter.connect(self.view.setCounterPatternToCreate)
        self.view.counterWidget.signal_createCounter.connect(self.counterHandler.createCounter)
        self.view.counterWidget.signal_removeCounter.connect(self.counterHandler.removeCounter)
        self.view.signal_settingConvertNonPrintableCharsToHexChanged.connect(self.processor.setConvertNonPrintableCharsToHex)

        self.processor.signal_asciiDataAvailable.connect(self.view.appendData)
        self.receiver.signal_rawDataAvailable.connect(self.processor.handleRawData)
        self.view.signal_closed.connect(self.onViewClosed)

    def getPortName(self) -> str:
        return self.receiver.getSettings().portName

    def startCapture(self) -> bool:
        opened, msg = self.receiver.openPort()
        if opened:
            self.show_message(f'Opened {self.receiver.getSettings().portName}')
            return True
        else:
            self.show_error(f'Failed to open {self.receiver.getSettings().portName} ({msg})')
            return False

    def stopCapture(self):
        self.receiver.closePort()
        self.show_message(f'Closed {self.receiver.getSettings().portName}')

    def clearAll(self):
        self.view.clear()
        self.counterHandler.clear()

    def show_message(self, text):
        self.view.appendData(f'\n[MSG: {datetime.now().strftime("%Y/%b/%d %H:%M:%S")}: {text} :MSG]\n')

    def show_error(self, text):
        self.view.appendData(f'\n[ERR: {datetime.now().strftime("%Y/%b/%d %H:%M:%S")}: {text} :ERR]\n')

    def destruct(self):
        self.receiver.closePort()

        if self.receiverThread.isRunning():
            self.receiverThread.quit()
            self.receiverThread.wait()
        if self.processorThread.isRunning():
            self.processorThread.quit()
            self.processorThread.wait()

    @Slot()
    def onViewClosed(self):
        # view is already closed
        self.signal_deleteController.emit(self.receiver.getSettings().portName)
