import time
import typing
from threading import Thread, Event
from queue import Queue, Empty
from PySide6.QtCore import Signal, QObject


class SerialDataProcessor(QObject):
    dataAvailable = Signal(str)

    def __init__(self, raw_data_queue: Queue):
        super(SerialDataProcessor, self).__init__()
        self.lastEmitTimestamp = self.getTimestamp()
        self._terminateEvent = Event()
        self._rawDataQueue = raw_data_queue
        self._thread: typing.Optional[Thread] = None

    def start(self):
        if self._thread is None:
            self._thread = Thread(target=self.processData, args=(self._rawDataQueue, self._terminateEvent))
            self._thread.start()

    def stop(self):
        if self._thread and self._thread.is_alive():
            self._terminateEvent.set()
            self._thread.join()
            self._thread = None
            self._terminateEvent.clear()

    def getTimestamp(self):
        return int(round(time.time() * 1000))

    def timeDiffSinceLastEmit(self):
        return self.getTimestamp() - self.lastEmitTimestamp

    def processData(self, queue, terminate_event):
        data = bytearray()

        while not terminate_event.is_set():
            try:
                rx_bytes = queue.get(timeout=0.2)
                data.extend(rx_bytes)
            except Empty:
                pass
            finally:
                if len(data) > 0:
                    try:
                        self.dataAvailable.emit(data.decode("ascii"))
                        queue.task_done()
                    except:
                        pass
                    data = bytearray()
