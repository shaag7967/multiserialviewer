from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Slot, Signal
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile


class StatisticsWidget(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.widget = createWidgetFromUiFile("statisticsWidget.ui")
        self.widget.setParent(self)

        self.pbar_curUsage: QProgressBar = self.widget.findChild(QProgressBar, 'pbar_curUsage')
        self.pbar_maxUsage: QProgressBar = self.widget.findChild(QProgressBar, 'pbar_maxUsage')
        self.la_bytes: QLabel = self.widget.findChild(QLabel, 'la_bytes')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

    @Slot(int)
    def handleCurUsageChanged(self, value: int):
        self.pbar_curUsage.setValue(value)

    @Slot(int)
    def handleMaxUsageChanged(self, value: int):
        self.pbar_maxUsage.setValue(value)

    @Slot(int)
    def handleReceivedBytesIncremented(self, value: int):
        self.la_bytes.setText(str(value))
