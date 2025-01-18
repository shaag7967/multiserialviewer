from PySide6.QtSerialPort import QSerialPort
from PySide6.QtCore import Slot, Signal, QObject, QByteArray
from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings


class SerialDataReceiver(QObject):
    signal_rawDataAvailable: Signal = Signal(QByteArray)

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

    def getSettings(self) -> SerialConnectionSettings:
        return self.__settings

    @Slot()
    def __handleData(self):
        receivedData : QByteArray = self.__serialPort.readAll()
        size = len(receivedData)
        if size > 0:
            print(size)
            self.signal_rawDataAvailable.emit(receivedData)
