from typing import Optional, List
from PySide6.QtCore import QSize, QPoint

from multiserialviewer.serial_data.serialConnectionSettings import SerialConnectionSettings

class CounterSettings:
    def __init__(self, name: str = '', regex: str = ''):
        self.name: str = name
        self.regex: str = regex

class SerialViewerSettings:
    def __init__(self):
        self.title: str = ''
        self.size: Optional[QSize] = None
        self.position: Optional[QPoint] = None
        self.autoscrollActive: bool = True
        self.autoscrollReactivate: bool = True
        self.counters: List[CounterSettings] = []
        self.connection: SerialConnectionSettings = SerialConnectionSettings('')
