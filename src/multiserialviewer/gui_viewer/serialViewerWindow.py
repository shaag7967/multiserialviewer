from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QMdiSubWindow, QTabWidget, QScrollArea, QFrame, QSplitter, QTabBar
from typing import List

from multiserialviewer.text_highlighter.textHighlighter import TextHighlighter, TextHighlighterSettings
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.gui_viewer.serialViewerTextEdit import SerialViewerTextEdit
from multiserialviewer.gui_viewer.searchWidget import SearchWidget
from multiserialviewer.gui_viewer.counterWidget import CounterWidget
from multiserialviewer.gui_viewer.watchWidget import WatchWidget
from multiserialviewer.gui_viewer.statisticsWidget import StatisticsWidget
from multiserialviewer.gui_viewer.serialViewerSettingsWidget import SerialViewerSettingsWidget
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.settings.serialViewerSettings import SerialViewerSettings
from multiserialviewer.gui_viewer.autoscrollHandler import AutoscrollHandler
from multiserialviewer.gui_viewer.searchHandler import SearchHandler


class SerialViewerWindow(QMdiSubWindow):
    signal_closed = Signal()
    signal_createTextHighlightEntry = Signal(str)
    signal_createWatchFromSelectedText = Signal(str)
    signal_createCounter = Signal(str)
    signal_settingConvertNonPrintableCharsToHexChanged = Signal(bool)

    def __init__(self, windowTitle: str, iconSet: IconSet):
        super().__init__()

        self.iconSet = iconSet
        widget = createWidgetFromUiFile("serialViewerWindow.ui")

        self.setWidget(widget)
        self.setWindowTitle(windowTitle)
        self.setWindowIcon(iconSet.getSerialViewerIcon())
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.tabWidget: QTabWidget = widget.findChild(QTabWidget, 'tabWidget')
        self.__populateTabWidget(self.tabWidget)

        self.splitter: QSplitter = widget.findChild(QSplitter, 'splitter')

        self.textEdit: SerialViewerTextEdit = widget.findChild(SerialViewerTextEdit, 'textEdit')
        self.textEdit.setIconSet(iconSet)
        self.autoscroll: AutoscrollHandler = AutoscrollHandler(self.textEdit,
                                                             self.settingsWidget.widget.cb_autoscrollActive,
                                                             self.settingsWidget.widget.cb_autoscrollReactivate)
        self.search: SearchHandler = SearchHandler(self.textEdit, self.searchWidget)
        self.highlighter = TextHighlighter()
        self.highlighter.setDocument(self.textEdit.document())

        # connections
        self.textEdit.signal_createTextHighlightEntry.connect(self.signal_createTextHighlightEntry)
        self.textEdit.signal_createWatchFromSelectedText.connect(self.signal_createWatchFromSelectedText)
        self.textEdit.signal_createCounterFromSelectedText.connect(self.signal_createCounter)
        self.search.signal_foundString.connect(self.autoscroll.deactivateAutoscroll)
        self.settingsWidget.widget.ed_name.textChanged.connect(self.setWindowName)
        self.settingsWidget.signal_showNonPrintableAsHex.connect(self.handleSettingShowNonPrintableAsHexChanged)


    def __populateTabWidget(self, tabWidget: QTabWidget):
        widgetMinimumWidth = 400

        # search
        self.searchScrollArea = QScrollArea(tabWidget)
        self.searchScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.searchScrollArea.setWidgetResizable(True)

        self.searchWidget: SearchWidget = SearchWidget(self.searchScrollArea)
        self.searchWidget.setMinimumWidth(widgetMinimumWidth)
        self.searchScrollArea.setWidget(self.searchWidget)
        tabWidget.addTab(self.searchScrollArea, self.iconSet.getSearchIcon(), "Search")

        # watches
        self.watchScrollArea = QScrollArea(None)
        self.watchScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.watchScrollArea.setWidgetResizable(True)

        self.watchWidget: WatchWidget = WatchWidget(self.watchScrollArea)
        self.watchWidget.setMinimumWidth(widgetMinimumWidth)
        self.watchScrollArea.setWidget(self.watchWidget)
        tabWidget.addTab(self.watchScrollArea, self.iconSet.getWatchIcon(), "Watch")

        # counter
        self.counterScrollArea = QScrollArea(None)
        self.counterScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.counterScrollArea.setWidgetResizable(True)

        self.counterWidget: CounterWidget = CounterWidget(self.counterScrollArea)
        self.counterWidget.setMinimumWidth(widgetMinimumWidth)
        self.counterScrollArea.setWidget(self.counterWidget)
        tabWidget.addTab(self.counterScrollArea, self.iconSet.getCounterIcon(), "Count")

        # statistics
        self.statisticsScrollArea = QScrollArea(None)
        self.statisticsScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.statisticsScrollArea.setWidgetResizable(True)

        self.statisticsWidget: StatisticsWidget = StatisticsWidget(self.statisticsScrollArea)
        self.statisticsWidget.setMinimumWidth(widgetMinimumWidth)
        self.statisticsScrollArea.setWidget(self.statisticsWidget)
        tabWidget.addTab(self.statisticsScrollArea, self.iconSet.getStatsIcon(), "Statistics")

        # settings
        self.settingsScrollArea = QScrollArea(None)
        self.settingsScrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.settingsScrollArea.setWidgetResizable(True)

        self.settingsWidget: SerialViewerSettingsWidget = SerialViewerSettingsWidget(self.settingsScrollArea, readOnly=True)
        self.settingsWidget.setMinimumWidth(widgetMinimumWidth)
        self.settingsScrollArea.setWidget(self.settingsWidget)
        tabWidget.addTab(self.settingsScrollArea, self.iconSet.getSettingsIcon(), "Settings")


    def __scrollToBottom(self):
        self.textEdit.moveCursor(QTextCursor.MoveOperation.End)
        self.textEdit.ensureCursorVisible()

    def getCurrentTab(self) -> str:
        name = self.tabWidget.tabText(self.tabWidget.currentIndex())
        return name

    def setCurrentTab(self, name: str):
        tabBar: QTabBar = self.tabWidget.tabBar()
        for index in range(tabBar.count()):
            if tabBar.tabText(index) == name:
                self.tabWidget.setCurrentIndex(index)
                break

    @Slot(str)
    def createWatchFromText(self, text: str):
        self.selectTab_Watch()
        self.watchScrollArea.verticalScrollBar().setValue(self.watchScrollArea.verticalScrollBar().maximum())
        self.watchWidget.setTextForWatchCreation(text)

    @Slot()
    def setCounterPatternToCreate(self, pattern: str):
        self.selectTab_Count()
        self.counterScrollArea.verticalScrollBar().setValue(self.counterScrollArea.verticalScrollBar().maximum())
        self.counterWidget.setPatternToCreate(pattern)

    def closeEvent(self, event):
        # is not called when mainwindow is closed
        event.accept()
        self.signal_closed.emit()

    @Slot()
    def clear(self):
        self.textEdit.clear()

    @Slot()
    def selectTab_Watch(self):
        self.setCurrentTab('Watch')

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
        self.textEdit.appendData(data, self.autoscroll.autoscrollIsActive())

    @Slot()
    def appendErrorMessage(self, message: str):
        self.textEdit.appendErrorMessage(message, self.autoscroll.autoscrollIsActive())

    @Slot()
    def appendStartMessage(self, message: str):
        self.textEdit.appendStartMessage(message, self.autoscroll.autoscrollIsActive())

    @Slot()
    def appendStopMessage(self, message: str):
        self.textEdit.appendStopMessage(message, self.autoscroll.autoscrollIsActive())

    @Slot()
    def setWindowName(self, name: str):
        self.setWindowTitle(name)

    @Slot()
    def handleSettingShowNonPrintableAsHexChanged(self, state: Qt.CheckState):
        self.signal_settingConvertNonPrintableCharsToHexChanged.emit(state == Qt.CheckState.Checked)

    def getSettingConvertNonPrintableCharsToHex(self) -> bool:
        return self.settingsWidget.getSettingShowNonPrintableAsHex()

