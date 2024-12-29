from PySide6.QtCore import Qt, Slot, Signal, QPoint
from PySide6.QtGui import QTextCursor, QClipboard, QTextDocument
from PySide6.QtWidgets import QApplication, QMdiSubWindow, QPushButton, QCheckBox, QAbstractSlider, QTabWidget
from typing import List
from multiserialviewer.text_highlighter.textHighlighter import TextHighlighter, TextHighlighterConfig
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui.serialViewerTextEdit import SerialViewerTextEdit
from multiserialviewer.gui.searchWidget import SearchWidget
from multiserialviewer.gui.statisticsWidget import StatisticsWidget

from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.gui.animatedScrollBarMover import AnimatedScrollBarMover


class SerialViewerWindow(QMdiSubWindow):
    signal_closed = Signal()
    signal_clearPressed = Signal()
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

        self.textEdit.selectionChanged.connect(self.handleTextSelectionChange)

        self.textEdit.signal_mousePressed.connect(self.handleMousePress)
        self.textEdit.verticalScrollBar().sliderPressed.connect(self.handleSliderPress)
        self.textEdit.verticalScrollBar().actionTriggered.connect(self.handleSliderAction)

        self.highlighter = TextHighlighter()
        self.highlighter.setDocument(self.textEdit.document())

        pb_clear: QPushButton = widget.findChild(QPushButton, 'pb_clear')
        pb_clear.pressed.connect(self.clear)
        pb_clear.pressed.connect(self.signal_clearPressed)

        pb_copy: QPushButton = widget.findChild(QPushButton, 'pb_copy')
        pb_copy.pressed.connect(self.copy)

        self.checkBox_autoscrollActive: QCheckBox = self.widget().findChild(QCheckBox, 'checkBox_autoscrollActive')
        self.checkBox_autoscrollActive.checkStateChanged.connect(self.autoscrollStateChanged)
        self.animatedScrollBarMover: AnimatedScrollBarMover = AnimatedScrollBarMover(self.textEdit.verticalScrollBar())

        self._initTabWidget(widget.findChild(QTabWidget, 'tabWidget'))



    def _initTabWidget(self, tab_widget: QTabWidget):
        self.searchWidget: SearchWidget = SearchWidget(self)
        self.statisticsWidget: StatisticsWidget = StatisticsWidget(self)
        
        self.searchWidget.signal_searchString.connect(self.searchString)
        self.searchWidget.signal_previousClicked.connect(self.searchPrevious)
        self.searchWidget.signal_nextClicked.connect(self.searchNext)

        tab_widget.addTab(self.searchWidget, "Search")
        tab_widget.addTab(self.statisticsWidget, "Statistics")
        # tab_widget.addTab(QWidget(), "Watches")
        # tab_widget.addTab(QWidget(), "Counter")

        # tab_widget.updateGeometry()
        # super().updateGeometry()
        # self.adjustSize()

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

    def deactivateAutoscroll(self):
        if self.checkBox_autoscrollActive.isChecked():
            self.checkBox_autoscrollActive.setCheckState(Qt.CheckState.Unchecked)

    @Slot(QPoint)
    def handleMousePress(self, position: QPoint):
        self.deactivateAutoscroll()

    @Slot()
    def handleSliderPress(self):
        self.deactivateAutoscroll()

    @Slot()
    def handleSliderAction(self, action: QAbstractSlider.SliderAction):
        if action in [QAbstractSlider.SliderAction.SliderPageStepAdd.value,
                      QAbstractSlider.SliderAction.SliderPageStepSub.value,
                      QAbstractSlider.SliderAction.SliderSingleStepAdd.value,
                      QAbstractSlider.SliderAction.SliderSingleStepSub.value]:
            self.deactivateAutoscroll()

    @Slot()
    def autoscrollStateChanged(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            # retrieving start and end value here, because inside scroll
            # function, scroll bar returns wrong values... not sure why.
            start = self.textEdit.verticalScrollBar().value()
            end = self.textEdit.verticalScrollBar().maximum()
            self.animatedScrollBarMover.scroll(start, end)
        elif state == Qt.CheckState.Unchecked:
            if self.animatedScrollBarMover.isRunning():
                self.animatedScrollBarMover.stop()

    @Slot(str, bool)
    def searchString(self, text: str, backward_search: bool):
        if self.textEdit.textCursor().selectedText() != text:
            self.textEdit.textCursor().clearSelection()
        self.textEdit.find(text, QTextDocument.FindFlag.FindBackward if backward_search else QTextDocument.FindFlag(0))

    @Slot()
    def searchPrevious(self):
        self.textEdit.find(self.textEdit.textCursor().selectedText(), QTextDocument.FindFlag.FindBackward)

    @Slot()
    def searchNext(self):
        self.textEdit.find(self.textEdit.textCursor().selectedText(), QTextDocument.FindFlag(0))

    @Slot()
    def handleTextSelectionChange(self):
        has_selected_text = len(self.textEdit.textCursor().selectedText()) > 0
        self.searchWidget.widget.pb_previous.setEnabled(has_selected_text)
        self.searchWidget.widget.pb_next.setEnabled(has_selected_text)
