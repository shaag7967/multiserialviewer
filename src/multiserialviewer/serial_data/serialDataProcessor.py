from PySide6.QtCore import Signal, Slot, QObject, QThread, QByteArray


class SerialDataProcessor(QObject):
    signal_asciiDataAvailable: Signal = Signal(str)

    def __init__(self):
        super(SerialDataProcessor, self).__init__()
        self.__thread: QThread = QThread()
        self.moveToThread(self.__thread)

        self.__thread.start()

    def __del__(self):
        self.__thread.quit()
        self.__thread.wait()

    @Slot(QByteArray)
    def handleRawData(self, rawData: QByteArray):
        data : bytearray = bytearray(rawData) 

        if len(data) > 0:
            self.signal_asciiDataAvailable.emit(data.decode(encoding='ascii', errors='ignore'))

