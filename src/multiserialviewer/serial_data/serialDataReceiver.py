from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import Slot, QObject
from queue import Queue
from .serialConnectionSettings import SerialConnectionSettings


class SerialDataReceiver(QObject):
    def __init__(self, settings: SerialConnectionSettings):
        super(SerialDataReceiver, self).__init__()
        self.__serialPort: QSerialPort = QSerialPort(settings.portName)
        self.__serialPort.setBaudRate(int(settings.baudrate))
        self.__serialPort.setParity(settings.parity)
        self.__serialPort.setStopBits(settings.stopbits)
        self.__serialPort.setDataBits(settings.dataBits)
        self.__settings = settings
        self.rxQueue = Queue()

    def openPort(self) -> bool:
        if not self.__serialPort.isOpen():
            return self.__serialPort.open(QSerialPort.OpenModeFlag.ReadOnly)
        else:
            return False

    def closePort(self):
        if self.__serialPort.isOpen():
            self.__serialPort.close()

    def start(self):
        self.__serialPort.readyRead.connect(self.__handleReadableData)

    def stop(self):
        if self.__isSignalConnected():
            self.__serialPort.readyRead.disconnect(self.__handleReadableData)

    def getSettings(self) -> SerialConnectionSettings:
        return self.__settings

    def isReceiving(self) -> bool:
        return (self.__serialPort.isOpen() and self.__isSignalConnected())
    
    def __isSignalConnected(self) -> bool:
        meta = self.__serialPort.metaObject()
        return self.__serialPort.isSignalConnected(meta.method(meta.indexOfSignal('readyRead()')))

    @Slot()
    def __handleReadableData(self):
        received_data = self.__serialPort.readAll()
        if len(received_data) > 0:
            self.rxQueue.put(received_data)

