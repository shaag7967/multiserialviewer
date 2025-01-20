from time import sleep

from PySide6.QtCore import QObject, Qt, Signal, Slot, QMetaObject, QCoreApplication, QCommandLineParser, QThread, QByteArray
from PySide6.QtSerialPort import QSerialPort
import sys
import typing
import numpy as np



class Writer(QObject):
    signal_writerFinished: Signal= Signal()
    # TEXT_TO_WRITE: str = "\nabcdefghijk"
    TEXT_TO_WRITE: str = "test\nnumber: 123\nzaehler=zwei"

    def __init__(self, portName: str, baudrate: int):
        super(Writer, self).__init__()

        self.__serialPort: QSerialPort = QSerialPort(self)
        self.__serialPort.setPortName(portName)
        self.__serialPort.setBaudRate(baudrate)
        self.__serialPort.setParity(QSerialPort.Parity.NoParity)
        self.__serialPort.setStopBits(QSerialPort.StopBits.OneStop)
        self.__serialPort.setDataBits(QSerialPort.DataBits.Data8)
        if not self.__serialPort.open(QSerialPort.OpenModeFlag.WriteOnly):
            raise Exception(self.__serialPort.error().name)

        self.__serialPort.bytesWritten.connect(self.write)
        self.__maxWriteCount = 100     # <<<=== change here number of writes
        self.__writeCounter = 0

        self.__printCnt_col = 0
        self.__printCnt_row = 0

        # self.__data: QByteArray = QByteArray.fromStdString(Writer.TEXT_TO_WRITE)
        # self.__data += '\x00'

        self.__data: QByteArray = QByteArray()
        length = np.pi * 2
        sineWave = np.sin(np.arange(0, length, length / 20))
        for val in sineWave:
            self.__data += QByteArray.fromStdString(f'\nmyValue: {val}')

    @Slot()
    def write(self):
        if self.__writeCounter < self.__maxWriteCount:
            self.__writeCounter += 1
            self.__printCnt_col += 1
            if self.__printCnt_col == 100:
                print('.', end='', flush=True)
                self.__printCnt_col = 0
                self.__printCnt_row += 1
                if self.__printCnt_row == 100:
                    print('')
                    self.__printCnt_row = 0

            result = self.__serialPort.write(self.__data)
            if result != self.__data.size():
                print(self.__writeCounter)
        else:
            sleep(1)
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
