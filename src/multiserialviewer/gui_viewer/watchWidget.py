from PySide6.QtWidgets import QWidget, QVBoxLayout, QHeaderView
from PySide6.QtCore import Slot, Signal, QItemSelectionModel, QItemSelection
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
import re


class WatchWidget(QWidget):
    signal_createWatch: Signal = Signal(str, str, str, str)
    signal_removeWatch: Signal = Signal(int)

    CB_TEXT_NUMBER = 'Number'
    CB_TEXT_WORDS = 'Set of words'

    def __init__(self, parent: QWidget | None):
        super().__init__(parent)
        self.widget = createWidgetFromUiFile("watchWidget.ui")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

        self.widget.pb_create.setEnabled(False)
        self.widget.pb_deleteSelected.setEnabled(False)

        self.widget.cb_type.currentTextChanged.connect(self.handleTypeChanged)
        self.widget.cb_type.addItem(WatchWidget.CB_TEXT_NUMBER)
        self.widget.cb_type.addItem(WatchWidget.CB_TEXT_WORDS)
        self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_NUMBER)

        self.widget.cb_type.currentTextChanged.connect(self.updateEnableState_buttonCreate)
        self.widget.ed_setOfWords.textChanged.connect(self.updateEnableState_buttonCreate)
        self.widget.ed_variableName.textChanged.connect(self.updateEnableState_buttonCreate)

        self.widget.ed_variableName.returnPressed.connect(self.handleCreateButtonClick)
        self.widget.pb_create.clicked.connect(self.handleCreateButtonClick)
        self.widget.pb_deleteSelected.clicked.connect(self.handleDeleteSelectedButtonClick)

    def setWatchTableModel(self, model):
        self.widget.tableView.setModel(model)

        selectionModel: QItemSelectionModel = self.widget.tableView.selectionModel()
        selectionModel.selectionChanged.connect(self.updateEnableState_buttonDeleteSelected)

        horizontal_header = self.widget.tableView.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def setTextForWatchCreation(self, text: str):
        text = text.strip()

        # number
        pattern = r'^((?:[\w\-\_]+\s*)+)[\s:=]+([-+]?(?:\d*[.])?\d+(?:[eE][-+]?\d+)?)$'
        m = re.match(pattern, text)
        if m:
            self.widget.ed_variableName.setText(m.group(1))
            self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_NUMBER)
            return

        # set of words
        pattern = r'^((?:[\w\-\_]+\s*)+)[\s:=]+(\w+)$'
        m = re.match(pattern, text)
        if m:
            self.widget.ed_variableName.setText(m.group(1))
            self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_WORDS)
            self.widget.ed_setOfWords.setText(m.group(2))
            return

        # nothing matched
        self.widget.ed_variableName.setText(text)
        self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_NUMBER)

    @Slot(str)
    def handleTypeChanged(self, typeText: str):
        visible = typeText == WatchWidget.CB_TEXT_WORDS
        self.widget.lb_setOfWords.setVisible(visible)
        self.widget.ed_setOfWords.setVisible(visible)

    @Slot(str)
    def updateEnableState_buttonCreate(self, text):
        enabled = (len(self.widget.ed_variableName.text()) > 0
                   and (self.widget.cb_type.currentText() != WatchWidget.CB_TEXT_WORDS or len(self.widget.ed_setOfWords.text()) > 0))
        self.widget.pb_create.setEnabled(enabled)

    @Slot(str)
    def updateEnableState_buttonDeleteSelected(self, selected: QItemSelection, deselected: QItemSelection):
        selectionModel: QItemSelectionModel = self.widget.tableView.selectionModel()
        self.widget.pb_deleteSelected.setEnabled(selectionModel.hasSelection())

    @Slot()
    def handleCreateButtonClick(self):
        variableName = self.widget.ed_variableName.text()
        if len(variableName) > 0:
            if self.widget.cb_type.currentText() == WatchWidget.CB_TEXT_NUMBER:
                pattern = r'([-+]?(?:\d*[.])?\d+(?:[eE][-+]?\d+)?)'
                self.signal_createWatch.emit(variableName, '', 'number', pattern)
            elif self.widget.cb_type.currentText() == WatchWidget.CB_TEXT_WORDS:
                setOfWords = re.split(r'\s+|;|,|/', self.widget.ed_setOfWords.text())
                words = list(set([re.escape(w) for w in setOfWords if len(w) > 0]))
                pattern = f'({"|".join(words)})'
                self.signal_createWatch.emit(variableName, ', '.join(words), 'word', pattern)

            self.widget.ed_variableName.setText('')
            self.widget.ed_setOfWords.setText('')

    @Slot()
    def handleDeleteSelectedButtonClick(self):
        selected_model_indices = [modelIndex.row() for modelIndex in self.widget.tableView.selectionModel().selectedRows()]

        for index in sorted(selected_model_indices, reverse=True):
            self.signal_removeWatch.emit(index)
