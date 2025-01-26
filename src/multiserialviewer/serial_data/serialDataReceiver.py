from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import Slot, Signal, QObject, QByteArray
from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
import time, sys


class SerialDataReceiver(QObject):
    signal_rawDataAvailable: Signal = Signal(QByteArray, QByteArray)

    def __init__(self, settings: SerialConnectionSettings):
        super(SerialDataReceiver, self).__init__()

        self.__serialPort: QSerialPort = QSerialPort(self)
        self.__serialPort.setPortName(settings.portName)
        self.__serialPort.setBaudRate(settings.baudrate)
        self.__serialPort.setParity(settings.parity)
        self.__serialPort.setStopBits(settings.stopBits)
        self.__serialPort.setDataBits(settings.dataBits)
        self.__settings = settings

        self.__serialPort.readyRead.connect(self.__handleData)

    def openPort(self) -> tuple[bool, str]:
        if not self.__serialPort.isOpen():
            self.__serialPort.clear(QSerialPort.Direction.AllDirections)
            self.__serialPort.clearError()

            openedSuccessfully = self.__serialPort.open(QSerialPort.OpenModeFlag.ReadOnly)
            return openedSuccessfully, self.__serialPort.error().name
        else:
            return True, QSerialPort.SerialPortError.NoError.name

    def closePort(self):
        if self.__serialPort.isOpen():
            self.__serialPort.close()

    def portIsOpen(self):
        return self.__serialPort.isOpen()

    def getSettings(self) -> SerialConnectionSettings:
        return self.__settings

    @Slot()
    def __handleData(self):
        timestamp: int = time.perf_counter_ns()
        # timestamp is an 32 byte integer and cannot be emitted directly as an int type
        # Therefore we pack it into a QByteArray, which has to be unpacked with int.from_bytes on the other side
        timestampData: QByteArray = QByteArray(timestamp.to_bytes(sys.getsizeof(timestamp),
                                               byteorder='big',
                                               signed=False))

        receivedData: QByteArray = self.__serialPort.readAll()
        if receivedData.size() > 0:
            self.signal_rawDataAvailable.emit(timestampData, receivedData)
