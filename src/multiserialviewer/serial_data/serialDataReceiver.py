from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import Slot, Signal, QObject, QByteArray
from .serialConnectionSettings import SerialConnectionSettings


class SerialDataReceiver(QObject):
    signal_rawDataAvailable: Signal = Signal(QByteArray)

    def __init__(self, settings: SerialConnectionSettings):
        super(SerialDataReceiver, self).__init__()
        self.__serialPort: QSerialPort = QSerialPort(settings.portName)
        self.__serialPort.setBaudRate(settings.baudrate)
        self.__serialPort.setParity(settings.parity)
        self.__serialPort.setStopBits(settings.stopbits)
        self.__serialPort.setDataBits(settings.dataBits)
        self.__settings = settings

        self.__serialPort.readyRead.connect(self.__handleReadableData)

    def openPort(self) -> bool:
        if not self.__serialPort.isOpen():
            return self.__serialPort.open(QSerialPort.OpenModeFlag.ReadOnly)
        else:
            return False

    def closePort(self) -> bool:
        if self.__serialPort.isOpen():
            self.__serialPort.close()
            return True
        else:
            return False

    def getSettings(self) -> SerialConnectionSettings:
        return self.__settings
   
    @Slot()
    def __handleReadableData(self):
        received_data : QByteArray = self.__serialPort.readAll()
        if len(received_data) > 0:
            self.signal_rawDataAvailable.emit(received_data)

