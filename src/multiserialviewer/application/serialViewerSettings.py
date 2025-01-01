from typing import Optional
from PySide6.QtCore import QSize, QPoint

from multiserialviewer.serial_data.serialConnectionSettings import SerialConnectionSettings


class SerialViewerSettings:
    def __init__(self):
        self.title: str = ''
        self.size: Optional[QSize] = None
        self.position: Optional[QPoint] = None
        self.autoscrollActive: bool = True
        self.autoscrollReactivate: bool = True
        self.connection: SerialConnectionSettings = SerialConnectionSettings('')
