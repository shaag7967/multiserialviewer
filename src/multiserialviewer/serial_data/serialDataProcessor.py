from PySide6.QtCore import Signal, Slot, QObject, QByteArray
from datetime import datetime


class SerialDataProcessor(QObject):
    signal_asciiDataAvailable: Signal = Signal(str)
    signal_deleteLine: Signal = Signal()
    signal_numberOfNonPrintableChars: Signal = Signal(int)

    def __init__(self):
        super(SerialDataProcessor, self).__init__()
        self.__convertNonPrintableCharsToHex: bool = False
        self.__backspaceDeletesLastLine: bool = False
        self.__insertTimestampAtLineStart: bool = True
        self.__timestampFormat: str = ""

        self.__lastReceivedChar: int | None = None

    @Slot()
    def setConvertNonPrintableCharsToHex(self, state: bool):
        self.__convertNonPrintableCharsToHex = state

    @Slot()
    def setBackspaceDeletesLastLine(self, state: bool):
        self.__backspaceDeletesLastLine = state

    @Slot()
    def setShowTimestampAtLineStart(self, state: bool, strFormat: str):
        self.__insertTimestampAtLineStart = state
        self.__timestampFormat = strFormat
        self.clear()

    def clear(self):
        self.__lastReceivedChar = None

    @staticmethod
    def __charIsLinebreak(b: int) -> bool:
        return b is not None and (b == 0x0D or b == 0x0A)  # '\r' or '\n'

    @staticmethod
    def __charIsDeleteLine(b: int) -> bool:
        return b is not None and b == 0x08  # '\b'

    @staticmethod
    def __charIsPrintable(b: int) -> bool:
        return 32 <= b <= 126

    @staticmethod
    def __getPrintableReplacement(b: int) -> str:
        return f'[{b:02X}]'

    @Slot(datetime, QByteArray)
    def handleRawData(self, rxTime: datetime, rawData: QByteArray):
        if rawData.size() > 0:
            nonPrintableCharsCount = 0
            asciiData: str = ''

            for b in rawData.data():
                if self.__insertTimestampAtLineStart:
                    if self.__charIsLinebreak(self.__lastReceivedChar):
                        asciiData += rxTime.strftime(self.__timestampFormat)
                    self.__lastReceivedChar = b

                if SerialDataProcessor.__charIsPrintable(b) or SerialDataProcessor.__charIsLinebreak(b):
                    asciiData += chr(b)
                elif self.__backspaceDeletesLastLine and SerialDataProcessor.__charIsDeleteLine(b):
                    if len(asciiData) > 0:
                        self.signal_asciiDataAvailable.emit(asciiData)
                        asciiData = ''
                    self.signal_deleteLine.emit()
                elif self.__convertNonPrintableCharsToHex:
                    nonPrintableCharsCount += 1
                    asciiData += SerialDataProcessor.__getPrintableReplacement(b)

            if len(asciiData) > 0:
                self.signal_asciiDataAvailable.emit(asciiData)
            if nonPrintableCharsCount > 0:
                self.signal_numberOfNonPrintableChars.emit(nonPrintableCharsCount)
