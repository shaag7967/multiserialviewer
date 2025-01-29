from PySide6.QtWidgets import QTextEdit, QMenu, QWidget
from PySide6.QtGui import QContextMenuEvent, QAction, QMouseEvent, QWheelEvent, QTextCursor
from PySide6.QtCore import Signal, Slot, QPoint
import typing
from datetime import datetime

from multiserialviewer.icons.iconSet import IconSet


class SerialViewerTextEdit(QTextEdit):
    signal_createTextHighlightEntry: Signal = Signal(str)
    signal_createWatchFromSelectedText: Signal = Signal(str)
    signal_createCounterFromSelectedText: Signal = Signal(str)
    signal_mousePressed: Signal = Signal(QPoint)
    signal_wheelEvent: Signal = Signal(QPoint)

    def __init__(self, parent: QWidget):
        super(SerialViewerTextEdit, self).__init__(parent)
        self.iconSet: typing.Optional[IconSet] = None

    def __getHtmlMessage(self, imagePath: str, message: str) -> str:
        return ('<table border=0 cellspacing=10><tr>'
                f'<td align=left valign=middle><img src="{imagePath}" width=24 height=24></td>'
                f'<td align=left valign=middle>{datetime.now().strftime("%Y/%b/%d %H:%M:%S")}:</td>'
                f'<td align=left valign=middle><b>{message}</b></td></tr></table>')

    def __getHtmlErrorMessage(self, message: str) -> str:
        return '<font color=darkred>' + self.__getHtmlMessage(self.iconSet.getErrorIconPath(), message) + '</font>'
    def __getHtmlStartMessage(self, message: str) -> str:
        return self.__getHtmlMessage(self.iconSet.getCaptureStartIconPath(), message)
    def __getHtmlStopMessage(self, message: str) -> str:
        return self.__getHtmlMessage(self.iconSet.getCaptureStopIconPath(), message)

    def appendData(self, data: str, scrollToBottom: bool):
        cursor: QTextCursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(data)

        if scrollToBottom:
            self.scrollToBottom()

    def appendErrorMessage(self, message: str, scrollToBottom: bool):
        cursor: QTextCursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(self.__getHtmlErrorMessage(message))

        if scrollToBottom:
            self.scrollToBottom()

    def appendStartMessage(self, message: str, scrollToBottom: bool):
        cursor: QTextCursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(self.__getHtmlStartMessage(message))

        if scrollToBottom:
            self.scrollToBottom()

    def appendStopMessage(self, message: str, scrollToBottom: bool):
        cursor: QTextCursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertHtml(self.__getHtmlStopMessage(message))

        if scrollToBottom:
            self.scrollToBottom()

    def scrollToBottom(self):
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def setIconSet(self, iconSet: IconSet):
        self.iconSet = iconSet

    def contextMenuEvent(self, event: QContextMenuEvent):
        assert self.iconSet is not None

        menu: QMenu = self.createStandardContextMenu()

        action_highlight: QAction = QAction(icon=self.iconSet.getHighlighterIcon(), text="Highlight selected text", parent=menu)
        action_highlight.setEnabled(len(self.textCursor().selectedText()) > 0)
        action_highlight.triggered.connect(self.action_triggeredHighlight)

        action_createWatch: QAction = QAction(icon=self.iconSet.getWatchIcon(), text="Create watch", parent=menu)
        action_createWatch.setEnabled(len(self.textCursor().selectedText()) > 0)
        action_createWatch.triggered.connect(self.action_triggeredCreateWatch)

        action_createCounter: QAction = QAction(icon=self.iconSet.getCounterIcon(), text="Create counter", parent=menu)
        action_createCounter.setEnabled(len(self.textCursor().selectedText()) > 0)
        action_createCounter.triggered.connect(self.action_triggeredCreateCounter)

        menu.insertAction(menu.actions()[0], action_highlight)
        menu.insertAction(menu.actions()[0], action_createCounter)
        menu.insertAction(menu.actions()[0], action_createWatch)
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
    def action_triggeredCreateWatch(self):
        selected_text = self.textCursor().selectedText()
        assert len(selected_text) > 0
        self.signal_createWatchFromSelectedText.emit(selected_text)

    @Slot()
    def action_triggeredCreateCounter(self):
        selected_text = self.textCursor().selectedText()
        assert len(selected_text) > 0
        self.signal_createCounterFromSelectedText.emit(selected_text)



