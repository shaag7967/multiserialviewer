import serial
import typing
from threading import Thread, Event
from queue import Queue
from .serialConnectionSettings import SerialConnectionSettings
from .serialDataStatistics import SerialDataStatistics

class SerialDataReceiver:
    def __init__(self, settings: SerialConnectionSettings, statistics: SerialDataStatistics):
        self._terminateEvent = Event()
        self._thread: typing.Optional[Thread] = None
        self._serialPort: typing.Optional[serial.Serial] = None
        self.settings = settings
        self.rxQueue = Queue()
        self._statistics = statistics

    def open_port(self) -> bool:
        if self._serialPort:
            self._serialPort.close()

        self._serialPort = serial.Serial()
        self._serialPort.port = self.settings.portName
        self._serialPort.baudrate = self.settings.baudrate
        self._serialPort.bytesize = self.settings.bytesize
        self._serialPort.parity = self.settings.parity
        self._serialPort.stopbits = self.settings.stopbits
        self._serialPort.timeout = self.settings.timeout

        try:
            self._serialPort.open()
        except serial.SerialException:
            return False
        return True

    def close_port(self):
        if self._serialPort:
            self._serialPort.close()
            self._serialPort = None

    def start(self):
        if self._thread is None:
            self._thread = Thread(target=self.receiveData, args=(self.rxQueue, self._terminateEvent))
            self._thread.start()

    def stop(self):
        if self._thread:
            self._terminateEvent.set()
            self._thread.join()
            self._thread = None
            self._terminateEvent.clear()

    def isReceiving(self):
        return self._thread and self._thread.is_alive()

    def receiveData(self, queue, terminate_event):
        self._serialPort.reset_input_buffer()

        while not terminate_event.is_set():
            received_data = self._serialPort.read(1)

            count = len(received_data)
            if count > 0:
                queue.put(received_data)
                self._statistics.incrementFrameCount(count)

        self._terminateEvent.clear()

