from PySide6.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QComboBox
from PySide6.QtCore import Qt, Slot, Signal, QItemSelectionModel, QItemSelection
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
import re


class WatchWidget(QWidget):
    signal_createWatch: Signal = Signal(str, str)
    signal_removeWatch: Signal = Signal(int)

    CB_TEXT_NUMBER = 'Number'
    CB_TEXT_WORDS = 'Set of words'

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.widget = createWidgetFromUiFile("watchWidget.ui")
        self.widget.setParent(self)

        self.widget.pb_create.setEnabled(False)
        self.widget.pb_deleteSelected.setEnabled(False)

        self.widget.cb_type.currentTextChanged.connect(self.handleTypeChanged)
        self.widget.cb_type.addItem(WatchWidget.CB_TEXT_NUMBER)
        self.widget.cb_type.addItem(WatchWidget.CB_TEXT_WORDS)
        self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_NUMBER)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

        self.widget.ed_name.textChanged.connect(self.updateEnableState_buttonCreate)
        self.widget.cb_type.currentTextChanged.connect(self.updateEnableState_buttonCreate)
        self.widget.ed_setOfWords.textChanged.connect(self.updateEnableState_buttonCreate)
        self.widget.ed_textToWatch.textChanged.connect(self.updateEnableState_buttonCreate)

        self.widget.ed_textToWatch.returnPressed.connect(self.handleCreateButtonClick)
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
        pattern = r'^(\w+)[\s:=]*([-+]?(?:\d*[.])?\d+(?:[eE][-+]?\d+)?)$'
        m = re.match(pattern, text)
        if m:
            self.widget.ed_name.setText(m.group(1))
            self.widget.ed_textToWatch.setText(m.group(1))
            self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_NUMBER)
            return

        # set of words
        pattern = r'^(\w+)[\s:=]+(\w+)$'
        m = re.match(pattern, text)
        if m:
            self.widget.ed_name.setText(m.group(1))
            self.widget.ed_textToWatch.setText(m.group(1))
            self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_WORDS)
            self.widget.ed_setOfWords.setText(m.group(2))
            return

        # nothing matched
        self.widget.ed_name.setText(text)
        self.widget.ed_textToWatch.setText(re.escape(text))
        self.widget.cb_type.setCurrentText(WatchWidget.CB_TEXT_NUMBER)

    @Slot(str)
    def handleTypeChanged(self, typeText: str):
        visible = typeText == WatchWidget.CB_TEXT_WORDS
        self.widget.lb_setOfWords.setVisible(visible)
        self.widget.ed_setOfWords.setVisible(visible)

    @Slot(str)
    def updateEnableState_buttonCreate(self, text):
        enabled = (len(self.widget.ed_name.text()) > 0
                   and len(self.widget.ed_textToWatch.text()) > 0
                   and (self.widget.cb_type.currentText() != WatchWidget.CB_TEXT_WORDS or len(self.widget.ed_setOfWords.text()) > 0))
        print(enabled)
        self.widget.pb_create.setEnabled(enabled)

    @Slot(str)
    def updateEnableState_buttonDeleteSelected(self, selected: QItemSelection, deselected: QItemSelection):
        selectionModel: QItemSelectionModel = self.widget.tableView.selectionModel()
        self.widget.pb_deleteSelected.setEnabled(selectionModel.hasSelection())

    @Slot()
    def handleCreateButtonClick(self):
        name = self.widget.ed_name.text()
        text = self.widget.ed_textToWatch.text()
        if len(name) > 0 and len(text) > 0:

            if self.widget.cb_type.currentText() == WatchWidget.CB_TEXT_NUMBER:
                pattern = text + r'[\s:=]*' + r'([-+]?(?:\d*[.])?\d+(?:[eE][-+]?\d+)?)'
                self.signal_createWatch.emit(name, pattern)
            elif self.widget.cb_type.currentText() == WatchWidget.CB_TEXT_WORDS:
                setOfWords = re.split(r'\s+|;|,|/', self.widget.ed_setOfWords.text())
                words = [re.escape(w) for w in setOfWords if len(w) > 0]
                words = list(set(words)) # remove duplicates
                pattern = text + r'[\s:=]*' + f'({"|".join(words)})'
                self.signal_createWatch.emit(name, pattern)

            self.widget.ed_name.setText('')
            self.widget.ed_textToWatch.setText('')
            self.widget.ed_setOfWords.setText('')

    @Slot()
    def handleDeleteSelectedButtonClick(self):
        selected_model_indices = [modelIndex.row() for modelIndex in self.widget.tableView.selectionModel().selectedRows()]

        for index in sorted(selected_model_indices, reverse=True):
            self.signal_removeWatch.emit(index)
