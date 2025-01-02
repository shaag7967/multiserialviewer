from PySide6.QtCore import Qt, Slot, Signal, QPoint
from PySide6.QtGui import QTextCursor, QClipboard, QTextDocument
from PySide6.QtWidgets import QApplication, QMdiSubWindow, QPushButton, QCheckBox, QAbstractSlider, \
    QTabWidget, QScrollArea, QDialogButtonBox, QFrame, QWidget, QVBoxLayout
from typing import List
from multiserialviewer.text_highlighter.textHighlighter import TextHighlighter, TextHighlighterSettings
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui.serialViewerTextEdit import SerialViewerTextEdit
from multiserialviewer.gui.searchWidget import SearchWidget
from multiserialviewer.gui.serialViewerSettingsWidget import SerialViewerSettingsWidget
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.application.serialViewerSettings import SerialViewerSettings


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

        self.textEdit.selectionChanged.connect(self.handleTextSelectionChange)

        self.textEdit.signal_mousePressed.connect(self.handleMousePress)
        self.textEdit.signal_wheelEvent.connect(self.handleWheelEvent)
        self.textEdit.verticalScrollBar().sliderPressed.connect(self.handleSliderPress)
        self.textEdit.verticalScrollBar().actionTriggered.connect(self.handleSliderAction)

        self.highlighter = TextHighlighter()
        self.highlighter.setDocument(self.textEdit.document())

        self._initTabWidget(widget.findChild(QTabWidget, 'tabWidget'))

    def _initTabWidget(self, tab_widget: QTabWidget):
        # search
        self.searchScrollArea = QScrollArea(tab_widget)
        self.searchScrollArea.setFrameShape(QFrame.Shape.NoFrame)

        self.searchWidget: SearchWidget = SearchWidget(self.searchScrollArea)
        self.searchWidget.signal_searchString.connect(self.searchString)
        self.searchWidget.signal_previousClicked.connect(self.searchPrevious)
        self.searchWidget.signal_nextClicked.connect(self.searchNext)

        self.searchScrollArea.setWidget(self.searchWidget)
        tab_widget.addTab(self.searchScrollArea, "Search")

        # settings
        self.settingsScrollArea = QScrollArea(tab_widget)
        self.settingsScrollArea.setFrameShape(QFrame.Shape.NoFrame)

        self.settingsWidget: SerialViewerSettingsWidget = SerialViewerSettingsWidget(self.settingsScrollArea, readOnly=True)
        self.settingsWidget.widget.cb_autoscrollActive.checkStateChanged.connect(self.autoscrollStateChanged)
        self.settingsWidget.widget.ed_name.textChanged.connect(self.nameChanged)

        self.settingsScrollArea.setWidget(self.settingsWidget)
        tab_widget.addTab(self.settingsScrollArea, "Settings")

    def closeEvent(self, event):
        # is not called when mainwindow is closed
        event.accept()
        self.signal_closed.emit()

    @Slot()
    def clear(self):
        self.textEdit.clear()

    def setHighlighterSettings(self, settings: List[TextHighlighterSettings]):
        self.highlighter.setSettings(settings)
        self.highlighter.rehighlight()

    def setSerialViewerSettings(self, settings: SerialViewerSettings):
        self.settingsWidget.setSerialViewerSettings(settings)

    @Slot()
    def appendData(self, data):
        cursor: QTextCursor = QTextCursor(self.textEdit.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(data)

        if self.autoscrollIsActive():
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
            self.textEdit.ensureCursorVisible()

    def autoscrollIsActive(self) -> bool:
        return self.settingsWidget.widget.cb_autoscrollActive.isChecked()
    def autoscrollReactivateIsActive(self) -> bool:
        return self.settingsWidget.widget.cb_autoscrollReactivate.isChecked()

    def activateAutoscroll(self):
        if not self.autoscrollIsActive():
            self.settingsWidget.widget.cb_autoscrollActive.setCheckState(Qt.CheckState.Checked)

    def deactivateAutoscroll(self):
        if self.autoscrollIsActive():
            self.settingsWidget.widget.cb_autoscrollActive.setCheckState(Qt.CheckState.Unchecked)

    @Slot(QPoint)
    def handleMousePress(self, position: QPoint):
        self.deactivateAutoscroll()

    @Slot()
    def handleWheelEvent(self, angleDelta: QPoint):
        scrollingDownwards = angleDelta.y() < 0
        bottomOfScrollBarReached = self.textEdit.verticalScrollBar().value() == self.textEdit.verticalScrollBar().maximum()

        if scrollingDownwards and bottomOfScrollBarReached:
            if self.autoscrollReactivateIsActive():
                self.activateAutoscroll()
        else:
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
    def checkIfScrolledToBottom(self, value: int):
        if value == self.textEdit.verticalScrollBar().maximum():
            if self.autoscrollReactivateIsActive():
                self.activateAutoscroll()

    @Slot()
    def autoscrollStateChanged(self, state: Qt.CheckState):
        if state == Qt.CheckState.Checked:
            self.textEdit.verticalScrollBar().valueChanged.disconnect(self.checkIfScrolledToBottom)
        elif state == Qt.CheckState.Unchecked:
            self.textEdit.verticalScrollBar().valueChanged.connect(self.checkIfScrolledToBottom)

    @Slot()
    def nameChanged(self, name: str):
        self.setWindowTitle(name)

    @Slot(str, bool)
    def searchString(self, text: str, backward_search: bool):
        if self.textEdit.textCursor().selectedText() != text:
            self.textEdit.textCursor().clearSelection()
        found = self.textEdit.find(text, QTextDocument.FindFlag.FindBackward if backward_search else QTextDocument.FindFlag(0))
        if found:
            self.deactivateAutoscroll()

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
