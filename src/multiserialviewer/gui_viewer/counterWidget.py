from PySide6.QtWidgets import QWidget, QVBoxLayout, QHeaderView
from PySide6.QtCore import Qt, Slot, Signal, QItemSelectionModel, QItemSelection
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile


class CounterWidget(QWidget):
    signal_createCounter: Signal = Signal(str)
    signal_removeCounter: Signal = Signal(int)

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.widget = createWidgetFromUiFile("counterWidget.ui")
        self.widget.setParent(self)

        self.widget.pb_create.setEnabled(False)
        self.widget.pb_deleteSelected.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

        self.widget.ed_textToCount.textChanged.connect(self.updateEnableState_buttonCreate)
        self.widget.pb_create.clicked.connect(self.handleCreateButtonClick)
        self.widget.pb_deleteSelected.clicked.connect(self.handleDeleteSelectedButtonClick)

    def setCounterTableModel(self, model):
        self.widget.tableView.setModel(model)

        selectionModel: QItemSelectionModel = self.widget.tableView.selectionModel()
        selectionModel.selectionChanged.connect(self.updateEnableState_buttonDeleteSelected)

        horizontal_header = self.widget.tableView.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    @Slot(str)
    def updateEnableState_buttonCreate(self, text):
        self.widget.pb_create.setEnabled(len(self.widget.ed_textToCount.text()) > 0)

    @Slot(str)
    def updateEnableState_buttonDeleteSelected(self, selected: QItemSelection, deselected: QItemSelection):
        self.widget.pb_deleteSelected.setEnabled(selected.count() > 0)

    @Slot()
    def handleCreateButtonClick(self):
        self.signal_createCounter.emit(self.widget.ed_textToCount.text())

    @Slot()
    def handleDeleteSelectedButtonClick(self):
        selected_model_indices = [modelIndex.row() for modelIndex in self.widget.tableView.selectionModel().selectedRows()]

        for index in sorted(selected_model_indices, reverse=True):
            self.signal_removeCounter.emit(index)
