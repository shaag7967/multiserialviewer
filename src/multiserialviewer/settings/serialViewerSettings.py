from typing import Optional, List
from PySide6.QtCore import QSize, QPoint, QByteArray

from multiserialviewer.settings.serialConnectionSettings import SerialConnectionSettings
from multiserialviewer.settings.counterSettings import CounterSettings


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
        self.connection: SerialConnectionSettings = SerialConnectionSettings('')
