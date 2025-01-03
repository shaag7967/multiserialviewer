from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMdiSubWindow, QTabWidget, QScrollArea, QFrame
from typing import List

from multiserialviewer.text_highlighter.textHighlighter import TextHighlighter, TextHighlighterSettings
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui.serialViewerTextEdit import SerialViewerTextEdit
from multiserialviewer.gui.searchWidget import SearchWidget
from multiserialviewer.gui.serialViewerSettingsWidget import SerialViewerSettingsWidget
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.application.serialViewerSettings import SerialViewerSettings
from multiserialviewer.gui.autoscrollHandler import AutoscrollHandler
from multiserialviewer.gui.searchHandler import SearchHandler


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
        self.__createTabWidget(widget.findChild(QTabWidget, 'tabWidget'))

        self.textEdit: SerialViewerTextEdit = widget.findChild(SerialViewerTextEdit, 'textEdit')
        self.textEdit.setIconSet(icon_set)
        self.autoscroll: AutoscrollHandler = AutoscrollHandler(self.textEdit,
                                                             self.settingsWidget.widget.cb_autoscrollActive,
                                                             self.settingsWidget.widget.cb_autoscrollReactivate)
        self.search: SearchHandler = SearchHandler(self.textEdit, self.searchWidget)
        self.highlighter = TextHighlighter()
        self.highlighter.setDocument(self.textEdit.document())

        # connections
        self.textEdit.signal_createTextHighlightEntry.connect(self.signal_createTextHighlightEntry)
        self.search.signal_foundString.connect(self.autoscroll.deactivateAutoscroll)
        self.settingsWidget.widget.ed_name.textChanged.connect(self.setWindowName)

    def __createTabWidget(self, tab_widget: QTabWidget):
        # search
        self.searchScrollArea = QScrollArea(tab_widget)
        self.searchScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.searchWidget: SearchWidget = SearchWidget(self.searchScrollArea)
        self.searchScrollArea.setWidget(self.searchWidget)
        tab_widget.addTab(self.searchScrollArea, "Search")

        # settings
        self.settingsScrollArea = QScrollArea(tab_widget)
        self.settingsScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.settingsWidget: SerialViewerSettingsWidget = SerialViewerSettingsWidget(self.settingsScrollArea, readOnly=True)
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

        if self.autoscroll.autoscrollIsActive():
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
            self.textEdit.ensureCursorVisible()

    @Slot()
    def setWindowName(self, name: str):
        self.setWindowTitle(name)


