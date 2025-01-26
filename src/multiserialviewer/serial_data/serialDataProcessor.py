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

    @staticmethod
    def __charIsPrintable(b: int) -> bool:
        return b == 0x0D or b == 0x0A or 32 <= b <= 126

    @staticmethod
    def __getPrintableReplacement(b: int) -> str:
        return f'[{b:02X}]'

    @Slot(QByteArray, QByteArray)
    def handleRawData(self, timestampData: QByteArray, rawData: QByteArray):
        if rawData.size() > 0:
            nonPrintableCharsCount = 0
            asciiData: str = ''

            for b in rawData.data():
                if SerialDataProcessor.__charIsPrintable(b):
                    asciiData += chr(b)
                elif self.__convertNonPrintableCharsToHex:
                    nonPrintableCharsCount += 1
                    asciiData += SerialDataProcessor.__getPrintableReplacement(b)

            self.signal_asciiDataAvailable.emit(asciiData)
            if nonPrintableCharsCount > 0:
                self.signal_numberOfNonPrintableChars.emit(nonPrintableCharsCount)
