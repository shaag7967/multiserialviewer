from PySide6.QtCore import Signal, Slot, QObject, QByteArray


class SerialDataProcessor(QObject):
    signal_asciiDataAvailable: Signal = Signal(str)
    signal_numberOfNonPrintableChars: Signal = Signal(int)

    def __init__(self):
        super(SerialDataProcessor, self).__init__()
        self.__convertNonPrintableCharsToHex: bool = False

    @Slot()
    def setConvertNonPrintableCharsToHex(self, state: bool):
        self.__convertNonPrintableCharsToHex = state

    def __printableChar(self, b: int) -> bool:
        return b == 0x0D or b == 0x0A or 32 <= b <= 126

    def __getPrintableReplacement(self, b: int) -> str:
        return f'[{b:02X}]'

    @Slot(QByteArray)
    def handleRawData(self, rawData: QByteArray):
        data : bytearray = bytearray(rawData)

        if len(data) > 0:
            nonPrintableCharsCount = 0
            asciiData: str = ''
            for b in data:
                if self.__printableChar(b):
                    asciiData += chr(b)
                elif self.__convertNonPrintableCharsToHex:
                    nonPrintableCharsCount += 1
                    asciiData += self.__getPrintableReplacement(b)

            self.signal_asciiDataAvailable.emit(asciiData)
            if nonPrintableCharsCount > 0:
                self.signal_numberOfNonPrintableChars.emit(nonPrintableCharsCount)
