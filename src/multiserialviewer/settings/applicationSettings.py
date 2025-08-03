
class ApplicationSettings:
    DEFAULT_TIMESTAMP_FORMAT = '[%H:%M:%S.%f] '

    def __init__(self):
        self.restoreCaptureState: bool = False
        self.showNonPrintableCharsAsHex: bool = False
        self.showTimestamp: bool = False
        self.timestampFormat: str = ""
