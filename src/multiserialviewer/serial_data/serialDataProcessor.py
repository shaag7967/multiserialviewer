from PySide6.QtCore import Signal, Slot, QObject, QThread, QByteArray, Qt


class Processor(QObject):
    asciiData = Signal(str)

    Slot(QByteArray)
    def handleRawData(self, rawData: QByteArray):
        data : bytearray = bytearray(rawData) 

        if len(data) > 0:
            self.asciiData.emit(data.decode(encoding='ascii', errors='ignore'))


class SerialDataProcessor(QObject):
    asciiData: Signal = Signal(str)
    __rawData: Signal = Signal(QByteArray)

    def __init__(self):
        super(SerialDataProcessor, self).__init__()
        self.__worker: Processor = Processor()
        self.__thread: QThread = QThread()
        self.__worker.moveToThread(self.__thread)
        self.__rawData.connect(self.__worker.handleRawData, Qt.ConnectionType.QueuedConnection)
        self.__worker.asciiData.connect(self.__handleAsciiData, Qt.ConnectionType.QueuedConnection)

    def start(self):
        self.__thread.start()

    def stop(self):
        self.__thread.quit()
        self.__thread.wait()

    Slot(QByteArray)
    def handleRawData(self, rawData: QByteArray):
        self.__rawData.emit(rawData)

    Slot(str)
    def __handleAsciiData(self, asciiData: str):
        self.asciiData.emit(asciiData)
