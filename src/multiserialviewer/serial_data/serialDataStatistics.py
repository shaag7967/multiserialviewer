from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
from PySide6.QtCore import Signal, Slot, QObject, QByteArray, QTimer, Qt
from PySide6.QtSerialPort import QSerialPort

import time


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
        self.__maxBytesPerPeriod: float = (self.__baudrate * __REFRESH_SIGNALS_PERIOD_S) / self.__bitsPerFrame
        self.__receivedBytesPerPeriod: int = 0
        self.__overallReceivedBytes: int = 0
        self.__maxUsage: int = 0

        self.__refreshSignalsTimer = QTimer(self)
        self.__refreshSignalsTimer.setTimerType(Qt.TimerType.PreciseTimer)
        self.__refreshSignalsTimer.setInterval(int(__REFRESH_SIGNALS_PERIOD_S * 1000))
        self.__refreshSignalsTimer.setSingleShot(False)
        self.__refreshSignalsTimer.timeout.connect(self.__handleTimeoutRefreshSignals)

        self.__refreshSignalsTimer.start()
        self.lastTimestamp = 0

    @Slot(QByteArray, QByteArray)
    def handleRawData(self, timestampData: QByteArray, rawData: QByteArray):
        # timestamp: int = int.from_bytes(timestampData.data(), byteorder='big', signed=False)

        self.__receivedBytesPerPeriod += rawData.size()
        self.__overallReceivedBytes += rawData.size()

    @Slot()
    def handleReset(self):
        self.__overallReceivedBytes = 0
        self.__maxUsage = 0

    @Slot()
    def __handleTimeoutRefreshSignals(self):
        timestamp = time.perf_counter_ns()
        # print(timestamp - self.lastTimestamp)
        self.lastTimestamp = timestamp

        curUtilization: int = int(round((self.__receivedBytesPerPeriod / self.__maxBytesPerPeriod) * 100))
        self.signal_curUsageChanged.emit(curUtilization)
        self.signal_receivedBytesIncremented.emit(self.__overallReceivedBytes)

        if curUtilization > self.__maxUsage:
            self.__maxUsage = curUtilization
            self.signal_maxUsageChanged.emit(self.__maxUsage)

        self.__receivedBytesPerPeriod = 0
