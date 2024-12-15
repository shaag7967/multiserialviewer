import time
from threading import Thread, Event
from queue import Empty
from PySide6.QtCore import Signal, QObject


class SerialDataProcessor(QObject):
    dataAvailable = Signal(str)

    def __init__(self, raw_data_queue):
        super(SerialDataProcessor, self).__init__()
        self.lastEmitTimestamp = self.getTimestamp()
        self.terminateEvent = Event()
        self.rawDataQueue = raw_data_queue
        self.thread = None

    def start(self):
        if self.thread is None:
            self.thread = Thread(target=self.processData, args=(self.rawDataQueue, self.terminateEvent))
            self.thread.start()

    def stop(self):
        if self.thread and self.thread.is_alive():
            self.terminateEvent.set()
            self.thread.join()
            self.thread = None
            self.terminateEvent.clear()

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
                # queue.task_done()
            except Empty:
                pass
            finally:
                if len(data) > 0:
                    try:
                        self.dataAvailable.emit(data.decode("ascii"))
                    except:
                        pass
                    data = bytearray()
