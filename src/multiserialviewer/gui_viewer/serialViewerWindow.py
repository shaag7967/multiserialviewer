from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMdiSubWindow, QTabWidget, QScrollArea, QFrame, QSplitter, QTabBar
from typing import List

from multiserialviewer.text_highlighter.textHighlighter import TextHighlighter, TextHighlighterSettings
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui_viewer.serialViewerTextEdit import SerialViewerTextEdit
from multiserialviewer.gui_viewer.searchWidget import SearchWidget
from multiserialviewer.gui_viewer.counterWidget import CounterWidget
from multiserialviewer.gui_viewer.serialViewerSettingsWidget import SerialViewerSettingsWidget
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings
from multiserialviewer.gui_viewer.autoscrollHandler import AutoscrollHandler
from multiserialviewer.gui_viewer.searchHandler import SearchHandler


class SerialViewerWindow(QMdiSubWindow):
    signal_closed = Signal()
    signal_createTextHighlightEntry = Signal(str)
    signal_createCounter = Signal(str)

    def __init__(self, window_title: str, icon_set: IconSet):
        super().__init__()

        widget = createWidgetFromUiFile("serialViewerWindow.ui")

        self.setWidget(widget)
        self.setWindowTitle(window_title)
        self.setWindowIcon(icon_set.getSerialViewerIcon())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.tabWidget: QTabWidget = widget.findChild(QTabWidget, 'tabWidget')
        self.__populateTabWidget(self.tabWidget)

        self.splitter: QSplitter = widget.findChild(QSplitter, 'splitter')

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
        self.textEdit.signal_createCounter.connect(self.signal_createCounter)
        self.search.signal_foundString.connect(self.autoscroll.deactivateAutoscroll)
        self.settingsWidget.widget.ed_name.textChanged.connect(self.setWindowName)

    def __populateTabWidget(self, tabWidget: QTabWidget):
        widgetMinimumWidth = 390

        # search
        self.searchScrollArea = QScrollArea(tabWidget)
        self.searchScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.searchWidget: SearchWidget = SearchWidget(self.searchScrollArea)
        self.searchWidget.setMinimumWidth(widgetMinimumWidth)
        self.searchScrollArea.setWidget(self.searchWidget)
        tabWidget.addTab(self.searchScrollArea, "Search")

        # counter
        self.counterScrollArea = QScrollArea(tabWidget)
        self.counterScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.counterWidget: CounterWidget = CounterWidget(self.counterScrollArea)
        self.counterWidget.setMinimumWidth(widgetMinimumWidth)
        self.counterScrollArea.setWidget(self.counterWidget)
        tabWidget.addTab(self.counterScrollArea, "Count")

        # settings
        self.settingsScrollArea = QScrollArea(tabWidget)
        self.settingsScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.settingsWidget: SerialViewerSettingsWidget = SerialViewerSettingsWidget(self.settingsScrollArea, readOnly=True)
        self.settingsWidget.setMinimumWidth(widgetMinimumWidth)
        self.settingsScrollArea.setWidget(self.settingsWidget)
        tabWidget.addTab(self.settingsScrollArea, "Settings")

    def getCurrentTab(self) -> str:
        name = self.tabWidget.tabText(self.tabWidget.currentIndex())
        return name

    def setCurrentTab(self, name: str):
        tabBar: QTabBar = self.tabWidget.tabBar()
        for index in range(tabBar.count()):
            if tabBar.tabText(index) == name:
                self.tabWidget.setCurrentIndex(index)
                break

    def closeEvent(self, event):
        # is not called when mainwindow is closed
        event.accept()
        self.signal_closed.emit()

    @Slot()
    def clear(self):
        self.textEdit.clear()

    @Slot()
    def selectTab_Count(self):
        self.setCurrentTab('Count')

    def setHighlighterSettings(self, settings: List[TextHighlighterSettings]):
        self.highlighter.setSettings(settings)
        self.highlighter.rehighlight()

    def setSerialViewerSettings(self, settings: SerialViewerSettings):
        self.settingsWidget.setSerialViewerSettings(settings)

    @Slot()
    def appendData(self, data: str):
        cursor: QTextCursor = QTextCursor(self.textEdit.document())
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(data)

        if self.autoscroll.autoscrollIsActive():
            self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
            self.textEdit.ensureCursorVisible()

    @Slot()
    def setWindowName(self, name: str):
        self.setWindowTitle(name)


