from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
from PySide6.QtCore import Signal, Slot, QObject, QByteArray, QTimer, Qt, QMetaObject
from PySide6.QtSerialPort import QSerialPort


class Translator:
    @staticmethod
    def parityToBits(parity: QSerialPort.Parity) -> int:
        lookup_parityBits = {QSerialPort.Parity.NoParity: 0, 
                             QSerialPort.Parity.EvenParity: 1, 
                             QSerialPort.Parity.OddParity: 1,
                             QSerialPort.Parity.SpaceParity: 1,
                             QSerialPort.Parity.MarkParity: 1}

        return lookup_parityBits[parity]
    
    @staticmethod
    def stopsToBits(stopbits: QSerialPort.StopBits) -> float:
        lookup_StopBits = {QSerialPort.StopBits.OneStop: 1, 
                           QSerialPort.StopBits.OneAndHalfStop: 1.5, 
                           QSerialPort.StopBits.TwoStop: 2}

        return lookup_StopBits[stopbits]

    @staticmethod
    def datasToBits(dataBits: QSerialPort.DataBits) -> int:
        lookup_dataBits = {QSerialPort.DataBits.Data5: 5, 
                           QSerialPort.DataBits.Data6: 6, 
                           QSerialPort.DataBits.Data7: 7, 
                           QSerialPort.DataBits.Data8: 8}

        return lookup_dataBits[dataBits]


class SerialDataStatistics(QObject):
    signal_curUsageChanged = Signal(int)
    signal_maxUsageChanged = Signal(int)
    signal_receivedBytesIncremented = Signal(int)

    def __init__(self, settings: SerialConnectionSettings):
        super(SerialDataStatistics, self).__init__()

        self.__bitsPerFrame: float = Translator.datasToBits(settings.dataBits) + \
                                     Translator.stopsToBits(settings.stopBits) + \
                                     Translator.parityToBits(settings.parity)
        self.__period: float = round(10000.0 / settings.baudrate, 5)

        self.__maxBytesPerPeriod: int = round((settings.baudrate * self.__period) / self.__bitsPerFrame)
        self.__receivedBytesPerPeriod: int = 0
        self.__overallReceivedBytes: int = 0
        self.__maxUsage: int = 0

        self.__refreshSignalsTimer = QTimer(self)
        self.__refreshSignalsTimer.setTimerType(Qt.TimerType.PreciseTimer)
        self.__refreshSignalsTimer.setInterval(int(self.__period * 1000))
        self.__refreshSignalsTimer.setSingleShot(False)
        self.__refreshSignalsTimer.timeout.connect(self.__handleTimeoutRefreshSignals)

        self.__refreshSignalsTimer.start()

    @Slot(QByteArray, QByteArray)
    def handleRawData(self, timestampData: QByteArray, rawData: QByteArray):
        self.__receivedBytesPerPeriod += rawData.size()
        self.__overallReceivedBytes += rawData.size()

    def reset(self):
        QMetaObject.invokeMethod(self, '__handleReset', Qt.ConnectionType.QueuedConnection)

    @Slot()
    def __handleReset(self):
        self.__overallReceivedBytes = 0
        self.__maxUsage = 0

    @Slot()
    def __handleTimeoutRefreshSignals(self):
        curUtilization: int = int(round((self.__receivedBytesPerPeriod / self.__maxBytesPerPeriod) * 100))

        # curUtilization is not very accurate for two reasons:
        # 1. QTimer has a jitter
        # 2. We receive multiple bytes at once which could (partly) belong to the previous period.
        #    That's why we calculate sometimes a utilization > 100%. On the other side, we could get a
        #    utilization which is too small, because the received bytes are not processed/forwarded yet.
        curUtilization = min(curUtilization, 100)
        self.signal_curUsageChanged.emit(curUtilization)
        self.signal_receivedBytesIncremented.emit(self.__overallReceivedBytes)

        if curUtilization > self.__maxUsage:
            self.__maxUsage = curUtilization
            self.signal_maxUsageChanged.emit(self.__maxUsage)

        self.__receivedBytesPerPeriod = 0
