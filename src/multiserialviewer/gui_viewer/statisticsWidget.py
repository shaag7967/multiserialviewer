from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QTableView, QHeaderView, QGroupBox
from PySide6.QtCore import Slot, Signal, QItemSelectionModel, QItemSelection
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile


class StatisticsWidget(QWidget):

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.widget = createWidgetFromUiFile("statisticsWidget.ui")

        self.pbar_curUsage: QProgressBar = self.widget.findChild(QProgressBar, 'pbar_curUsage')
        self.pbar_maxUsage: QProgressBar = self.widget.findChild(QProgressBar, 'pbar_maxUsage')
        self.la_bytes: QLabel = self.widget.findChild(QLabel, 'la_bytes')

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

    def __minimizeHeightOfTableView(self):
        tableView: QTableView = self.widget.tableView
        tableView.resizeRowsToContents()

        totalHeight = 0
        for row in range(tableView.model().rowCount()):
            totalHeight += tableView.rowHeight(row)

        totalHeight += tableView.horizontalHeader().height()
        totalHeight += tableView.contentsMargins().top() + tableView.contentsMargins().bottom()
        tableView.setMaximumHeight(totalHeight)

        groupBox: QGroupBox = self.widget.findChild(QGroupBox, 'gb_stats')
        groupBox.setMaximumHeight(totalHeight + groupBox.contentsMargins().top() + groupBox.contentsMargins().bottom())

    def setStatisticsTableModel(self, model):
        tableView: QTableView = self.widget.tableView
        tableView.setModel(model)

        tableView.resizeColumnsToContents()
        horizontal_header = tableView.horizontalHeader()
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.__minimizeHeightOfTableView()

    @Slot(int)
    def handleCurUsageChanged(self, value: int):
        self.pbar_curUsage.setValue(value)

    @Slot(int)
    def handleMaxUsageChanged(self, value: int):
        self.pbar_maxUsage.setValue(value)

    @Slot(int)
    def handleReceivedBytesIncremented(self, value: int):
        self.la_bytes.setText(str(value))
