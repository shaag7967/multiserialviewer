from PySide6.QtWidgets import QScrollBar
from PySide6.QtCore import Slot, QVariantAnimation, QEasingCurve


class AnimatedScrollBarMover(QVariantAnimation):
    def __init__(self, scroll_bar: QScrollBar):
        QVariantAnimation.__init__(self)
        self._scroll_bar: QScrollBar = scroll_bar

    def updateCurrentValue(self, value: int):
        self._scroll_bar.setValue(value)

    def isRunning(self) -> bool:
        return self.state() == QVariantAnimation.State.Running

    def scroll(self, start: int, end: int, duration: int = 1000):
        self.stop()
        self.setDuration(duration)  # ms
        self.setEasingCurve(QEasingCurve.Type.InOutQuart)

        # value() returns wrong position if used like this. Not sure why.
        # self.setStartValue(self._scroll_bar.value())
        # self.setEndValue(self._scroll_bar.maximum())
        self.setStartValue(start)
        self.setEndValue(end)
        self.start()
