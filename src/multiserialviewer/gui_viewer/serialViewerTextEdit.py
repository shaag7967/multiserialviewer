from PySide6.QtWidgets import QTextEdit, QMenu, QWidget
from PySide6.QtGui import QContextMenuEvent, QAction, QMouseEvent, QWheelEvent
from PySide6.QtCore import Signal, Slot, QPoint
import typing

from multiserialviewer.icons.iconSet import IconSet


class SerialViewerTextEdit(QTextEdit):
    signal_createTextHighlightEntry: Signal = Signal(str)
    signal_createCounter: Signal = Signal(str)
    signal_mousePressed: Signal = Signal(QPoint)
    signal_wheelEvent: Signal = Signal(QPoint)

    def __init__(self, parent: QWidget):
        super(SerialViewerTextEdit, self).__init__(parent)
        self.icon_set: typing.Optional[IconSet] = None

    def setIconSet(self, icon_set: IconSet):
        self.icon_set = icon_set

    def contextMenuEvent(self, event: QContextMenuEvent):
        assert self.icon_set is not None

        menu: QMenu = self.createStandardContextMenu()

        action_highlight: QAction = QAction(icon=self.icon_set.getHighlighterIcon(), text="Highlight selected text",  parent=menu)
        action_highlight.setEnabled(len(self.textCursor().selectedText()) > 0)
        action_highlight.triggered.connect(self.action_triggeredHighlight)

        action_createCounter: QAction = QAction(icon=self.icon_set.getCounterIcon(), text="Create counter using selected text",  parent=menu)
        action_createCounter.setEnabled(len(self.textCursor().selectedText()) > 0)
        action_createCounter.triggered.connect(self.action_triggeredCreateCounter)

        menu.insertAction(menu.actions()[0], action_highlight)
        menu.insertAction(menu.actions()[0], action_createCounter)
        menu.insertSeparator(menu.actions()[2])
        menu.exec(event.globalPos())
        del menu

    def wheelEvent(self, event: QWheelEvent):
        super(SerialViewerTextEdit, self).wheelEvent(event)
        self.signal_wheelEvent.emit(event.angleDelta())

    def mousePressEvent(self, event: QMouseEvent):
        super(SerialViewerTextEdit, self).mousePressEvent(event)
        self.signal_mousePressed.emit(event.localPos())

    @Slot()
    def action_triggeredHighlight(self):
        selected_text = self.textCursor().selectedText()
        assert len(selected_text) > 0
        self.signal_createTextHighlightEntry.emit(selected_text)

    @Slot()
    def action_triggeredCreateCounter(self):
        selected_text = self.textCursor().selectedText()
        assert len(selected_text) > 0
        self.signal_createCounter.emit(selected_text)



