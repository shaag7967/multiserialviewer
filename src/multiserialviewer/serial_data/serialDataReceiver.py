import serial
import typing
from threading import Thread, Event
from queue import Queue
from .serialConnectionSettings import SerialConnectionSettings



class SerialDataReceiver:
    def __init__(self, settings: SerialConnectionSettings):
        self.terminateEvent = Event()
        self.rxQueue = Queue()
        self.thread: typing.Optional[Thread] = None
        self.serialPort: typing.Optional[serial.Serial] = None
        self.settings = settings

    def open_port(self) -> bool:
        if self.serialPort:
            self.serialPort.close()

        self.serialPort = serial.Serial()
        self.serialPort.port = self.settings.portName
        self.serialPort.baudrate = self.settings.baudrate
        self.serialPort.bytesize = self.settings.bytesize
        self.serialPort.parity = self.settings.parity
        self.serialPort.stopbits = self.settings.stopbits
        self.serialPort.timeout = self.settings.timeout

        try:
            self.serialPort.open()
        except serial.SerialException:
            return False
        return True

    def close_port(self):
        if self.serialPort:
            self.serialPort.close()
            self.serialPort = None

    def start(self):
        if self.thread is None:
            self.thread = Thread(target=self.receiveData, args=(self.rxQueue, self.terminateEvent))
            self.thread.start()

    def stop(self):
        if self.thread:
            self.terminateEvent.set()
            self.thread.join()
            self.thread = None
            self.terminateEvent.clear()

    def isReceiving(self):
        return self.thread and self.thread.is_alive()

    def receiveData(self, queue, terminate_event):
        self.serialPort.reset_input_buffer()

        while not terminate_event.is_set():
            received_data = self.serialPort.read(1)
            if len(received_data) > 0:
                queue.put(received_data)

        self.terminateEvent.clear()

