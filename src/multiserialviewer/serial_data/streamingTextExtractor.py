from PySide6.QtCore import Signal, Slot, QObject, QTimer
import re


class StreamingTextExtractor(QObject):
    signal_textExtracted: Signal = Signal(str, object)

    def __init__(self, name: str, pattern: str):
        super(StreamingTextExtractor, self).__init__()

        self.name = name
        self.regex = re.compile(pattern)
        self.buffer: str = ''

        self.delayedProcessing: QTimer = QTimer(self)
        self.delayedProcessing.setInterval(200)
        self.delayedProcessing.setSingleShot(True)
        self.delayedProcessing.timeout.connect(self.processTimeout)

    @Slot(str)
    def processBytesFromStream(self, asciiString: str):
        self.delayedProcessing.stop()
        self.alreadyProcessed = True

        self.buffer += asciiString

        lastPos = 0
        for match in self.regex.finditer(self.buffer):
            if match.end(0) != len(self.buffer):
                # a match is only processed if not at the end of the buffer, because
                # there could be coming more bytes, that belong to this pattern,
                # and we don't want to miss them. E.g. an integer matches after the first
                # number (char), but we want to be greedy and get all numbers (which could
                # arrive some time later).
                self.signal_textExtracted.emit(self.name, [*match.groups()])
                lastPos = match.end(0)
            else:
                # wait some time to get all bytes that belong to this pattern
                self.alreadyProcessed = False
                self.delayedProcessing.start()
                break
        if lastPos > 0:
            self.buffer = self.buffer[lastPos:]

        if len(self.buffer) > 5000:
            self.buffer = self.buffer[2000:]

    @Slot()
    def processTimeout(self):
        if self.alreadyProcessed == True:
            # processBytesFromStream was called in the meantime (event queue...)
            return

        # no more data was received for this pattern, so let's assume it is complete
        lastPos = 0
        for match in self.regex.finditer(self.buffer):
            self.signal_textExtracted.emit(self.name, [*match.groups()])
            lastPos = match.end(0)
        if lastPos > 0:
            self.buffer = self.buffer[lastPos:]


