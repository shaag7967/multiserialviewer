from PySide6.QtCore import Qt, Slot, Signal, QPoint
from PySide6.QtGui import QTextCursor, QClipboard
from PySide6.QtWidgets import QApplication, QMdiSubWindow, QPushButton, QCheckBox
from typing import List
from multiserialviewer.text_highlighter.textHighlighter import TextHighlighter, TextHighlighterConfig
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui.serialViewerTextEdit import SerialViewerTextEdit
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.gui.animatedScrollBarMover import AnimatedScrollBarMover


class SerialViewerWindow(QMdiSubWindow):
    signal_closed = Signal()
    signal_createTextHighlightEntry = Signal(str)

    def __init__(self, window_title: str, icon_set: IconSet):
        super().__init__()

        widget = createWidgetFromUiFile("serialViewerWindow.ui")

        self.setWidget(widget)
        self.setWindowTitle(window_title)
        self.setWindowIcon(icon_set.getSerialViewerIcon())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.textEdit: SerialViewerTextEdit = widget.findChild(SerialViewerTextEdit, 'textEdit')
        self.textEdit.setIconSet(icon_set)
        self.textEdit.signal_createTextHighlightEntry.connect(self.signal_createTextHighlightEntry)
        self.textEdit.signal_mousePressed.connect(self.handleMousePress)

        self.highlighter = TextHighlighter()
        self.highlighter.setDocument(self.textEdit.document())

        pb_clear: QPushButton = widget.findChild(QPushButton, 'pb_clear')
        pb_clear.pressed.connect(self.clear)

        pb_copy: QPushButton = widget.findChild(QPushButton, 'pb_copy')
        pb_copy.pressed.connect(self.copy)

        self.checkBox_autoscrollActive: QCheckBox = self.widget().findChild(QCheckBox, 'checkBox_autoscrollActive')
        self.checkBox_autoscrollActive.checkStateChanged.connect(self.autoscrollStateChanged)
        self.animatedScrollBarMover: AnimatedScrollBarMover = AnimatedScrollBarMover(self.textEdit.verticalScrollBar())

    def closeEvent(self, event):
        # is not called when mainwindow is closed
        event.accept()
        self.signal_closed.emit()

    @Slot()
    def clear(self):
        self.textEdit.clear()

    def setHighlighterSettings(self, settings: List[TextHighlighterConfig]):
        self.highlighter.setSettings(settings)
        self.highlighter.rehighlight()

    @Slot()
    def copy(self):
        clipboard: QClipboard = QApplication.clipboard()
        cursor = self.textEdit.textCursor()

        if cursor.selection().isEmpty():
            text = self.textEdit.toPlainText()
        else:
            text = cursor.selection().toPlainText()

        if len(text) > 0:
            clipboard.setText(text)

    @Slot()
    def appendData(self, data):
        cursor: QTextCursor = QTextCursor(self.textEdit.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(data)

        if self.checkBox_autoscrollActive.isChecked() and not self.animatedScrollBarMover.isRunning():
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
            self.textEdit.ensureCursorVisible()

    @Slot()
    def handleMousePress(self, position: QPoint):
        if self.checkBox_autoscrollActive.isChecked():
            self.checkBox_autoscrollActive.setCheckState(Qt.CheckState.Unchecked)

    @Slot()
    def autoscrollStateChanged(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            # retrieving start and end value here, because inside scroll
            # function, scroll bar returns wrong values... not sure why.
            start = self.textEdit.verticalScrollBar().value()
            end = self.textEdit.verticalScrollBar().maximum()
            self.animatedScrollBarMover.scroll(start, end)
