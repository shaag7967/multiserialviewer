from typing import Optional, List
from PySide6.QtCore import QSize, QPoint, QByteArray

from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
from multiserialviewer.settings.counterSettings import CounterSettings
from multiserialviewer.settings.watchSettings import WatchSettings


class SerialViewerSettings:
    def __init__(self):
        self.title: str = ''
        self.size: Optional[QSize] = None
        self.position: Optional[QPoint] = None
        self.splitterState: Optional[QByteArray] = None
        self.currentTabName: Optional[str] = None
        self.autoscrollActive: bool = True
        self.autoscrollReactivate: bool = True
        self.counters: List[CounterSettings] = []
        self.watches: List[WatchSettings] = []
        self.connection: SerialConnectionSettings = SerialConnectionSettings('')
        self.showNonPrintableCharsAsHex = True
