from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
from PySide6.QtCore import Signal, Slot, QObject, QByteArray, QMetaObject, QTimer, Qt
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

        __REFRESH_SIGNALS_PERIOD_S = 0.1
        __USAGE_SETTLED_TIME_S = 0.25

        self.__bitsPerFrame: float = Translator.datasToBits(settings.dataBits) + \
                                     Translator.stopsToBits(settings.stopBits) + \
                                     Translator.parityToBits(settings.parity)
        self.__baudrate: int = settings.baudrate
        self.__maxBitsPerPeriod: float = self.__baudrate * __REFRESH_SIGNALS_PERIOD_S
        self.__bitsPerPeriod: float = 0
        self.__overallReceivedBytes: int = 0
        self.__maxUsage: int = 0

        self.__refreshSignalsTimer = QTimer(self)
        self.__refreshSignalsTimer.setTimerType(Qt.TimerType.PreciseTimer)
        self.__refreshSignalsTimer.setInterval(int(__REFRESH_SIGNALS_PERIOD_S * 1000))
        self.__refreshSignalsTimer.setSingleShot(False)
        self.__refreshSignalsTimer.timeout.connect(self.__handleTimeoutRefreshSignals)

        self.__settledUsageTimer = QTimer(self)
        self.__settledUsageTimer.setTimerType(Qt.TimerType.PreciseTimer)
        self.__settledUsageTimer.setInterval(int(__USAGE_SETTLED_TIME_S * 1000))
        self.__settledUsageTimer.setSingleShot(True)
        self.__settledUsageTimer.timeout.connect(self.__handleTimeoutUsageSettled)

        self.__usageSettled = False

        self.__refreshSignalsTimer.start()

    def __del__(self):
        self.__refreshSignalsTimer.stop()

    @Slot()
    def start(self):
        QMetaObject.invokeMethod(self.__settledUsageTimer, 'start', Qt.ConnectionType.QueuedConnection)

    @Slot()
    def stop(self):
        QMetaObject.invokeMethod(self, '__handleStop', Qt.ConnectionType.QueuedConnection)

    @Slot(QByteArray)
    def handleRawData(self, rawData: QByteArray):
        if self.__usageSettled:
            self.__bitsPerPeriod += (rawData.size() * self.__bitsPerFrame)
        else:
            self.__bitsPerPeriod = 0

        self.__overallReceivedBytes += rawData.size()

    @Slot()
    def handleReset(self):
        self.__overallReceivedBytes = 0
        self.__maxUsage = 0

    @Slot()
    def __handleTimeoutRefreshSignals(self):
        curUtilization: int = int( round(( self.__bitsPerPeriod / self.__maxBitsPerPeriod) * 100) )
        curUtilization = min(curUtilization, 100)
        self.__maxUsage = max(curUtilization, self.__maxUsage)
        self.__bitsPerPeriod = 0

        self.signal_curUsageChanged.emit(curUtilization)
        self.signal_maxUsageChanged.emit(self.__maxUsage)
        self.signal_receivedBytesIncremented.emit(self.__overallReceivedBytes)

    @Slot()
    def __handleTimeoutUsageSettled(self):
        self.__usageSettled = True 

    @Slot()
    def __handleStop(self):
        self.__usageSettled = False    

