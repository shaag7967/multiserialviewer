from PySide6.QtCore import QObject, Qt, Signal, Slot, QMetaObject, QCoreApplication, QCommandLineParser, QThread
from PySide6.QtSerialPort import QSerialPort
import sys
import typing



class Writer(QObject):
    signal_writerFinished: Signal= Signal()
    TEXT_TO_WRITE: bytes = b"test\ntest2"

    def __init__(self, portName: str, baudrate: int):
        super(Writer, self).__init__()

        self.__serialPort: QSerialPort = QSerialPort(self)
        self.__serialPort.setPortName(portName)
        self.__serialPort.setBaudRate(baudrate)
        self.__serialPort.setParity(QSerialPort.Parity.NoParity)
        self.__serialPort.setStopBits(QSerialPort.StopBits.OneStop)
        self.__serialPort.setDataBits(QSerialPort.DataBits.Data8)
        self.__serialPort.open(QSerialPort.OpenModeFlag.WriteOnly)

        self.__serialPort.bytesWritten.connect(self.write)
        self.__maxWriteCount = 100
        self.__writeCounter = 0

    @Slot()
    def write(self):
        if self.__writeCounter < self.__maxWriteCount:
            self.__serialPort.write(Writer.TEXT_TO_WRITE)
            self.__writeCounter += 1
        else:
            self.signal_writerFinished.emit()


def main() -> int:
    app = QCoreApplication(sys.argv)

    parser = QCommandLineParser()
    parser.setApplicationDescription("Writes predefined data to a serial port")
    parser.addPositionalArgument("port", "Name of port, e.g. 'COM1'")
    parser.addPositionalArgument("baudrate", "Baudrate, e.g. 115200")
    parser.process(app)
    args: typing.List[str] = parser.positionalArguments()

    writer: Writer = Writer(args[0], int(args[1]))
    writer.signal_writerFinished.connect(app.quit)

    writerThread: QThread = QThread()
    writer.moveToThread(writerThread)

    QMetaObject.invokeMethod(writer, 'write', Qt.ConnectionType.QueuedConnection)

    writerThread.start()
    app.exec()
    writerThread.quit()
    writerThread.wait()

    return 1


if __name__ == '__main__':
    sys.exit(main())
