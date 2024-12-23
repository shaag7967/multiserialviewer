from .serialConnectionSettings import SerialConnectionSettings
from threading import Thread, Event, Lock
from PySide6.QtCore import Signal, QObject
import time
import typing
import serial

class SerialDataStatistics(QObject):
    utilizationInPercentage = Signal(int)

    def __init__(self, settings: SerialConnectionSettings):
        super(SerialDataStatistics, self).__init__()

        STARTBIT = 1        
        parityBits = 0

        if (settings.parity != serial.PARITY_NONE):
            parityBits = 1

        self.__bitsPerFrame = STARTBIT + settings.bytesize + settings.stopbits + parityBits
        self.__thread: typing.Optional[Thread] = None
        self.__terminateEvent = Event()
        self.__lock = Lock()
        self.__baudrate = settings.baudrate
        self.__framesPerPeriod = int ( 0 )

    def start(self):
        if self.__thread is None:
            self.__thread = Thread(target=self.__process, args=[self.__terminateEvent])
            self.__thread.start()

    def stop(self):
        if self.__thread and self.__thread.is_alive():
            self.__terminateEvent.set()
            self.__thread.join()
            self.__thread = None
            self.__terminateEvent.clear()

    def reset(self):
        # Nothing to reset yet
        pass

    def incrementFrameCount(self, count: int = 1):
        self.__lock.acquire()
        self.__framesPerPeriod += count
        self.__lock.release()

    def __process(self, terminateEvent):

        STATISTICS_UPDATE_PERIOD_S = 0.2
        PERCENTAGE = 100

        while not terminateEvent.is_set():

            self.__lock.acquire()
            framesPerPeriodCached = self.__framesPerPeriod
            self.__framesPerPeriod = 0
            self.__lock.release()

            bitsPerPeriod = framesPerPeriodCached * self.__bitsPerFrame
            maxBitsPerPeriod = int(self.__baudrate) * STATISTICS_UPDATE_PERIOD_S
            
            self.utilizationInPercentage.emit(int( round(( bitsPerPeriod / maxBitsPerPeriod) * PERCENTAGE) ))

            time.sleep(STATISTICS_UPDATE_PERIOD_S)
        
        self.terminateEvent.clear()