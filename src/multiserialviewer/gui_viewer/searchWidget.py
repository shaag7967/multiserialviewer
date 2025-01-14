from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Slot, Signal
from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile


class SearchWidget(QWidget):
    signal_searchString = Signal(str, bool)
    signal_previousClicked = Signal()
    signal_nextClicked = Signal()

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.widget = createWidgetFromUiFile("searchWidget.ui")
        self.widget.setParent(self)

        self.widget.pb_search.setEnabled(False)
        self.widget.cb_backwardsSearch.setCheckState(Qt.CheckState.Checked)

        self.widget.pb_previous.setEnabled(False)
        self.widget.pb_next.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.widget)

        self.widget.ed_search.textChanged.connect(self.handleSearchStringChange)
        self.widget.ed_search.returnPressed.connect(self.handleSearchButtonClick)
        self.widget.pb_search.clicked.connect(self.handleSearchButtonClick)
        self.widget.pb_previous.clicked.connect(self.signal_previousClicked)
        self.widget.pb_next.clicked.connect(self.signal_nextClicked)

    @Slot(str)
    def handleSearchStringChange(self, search_string: str):
        self.widget.pb_search.setEnabled(len(search_string) > 0)

    @Slot()
    def handleSearchButtonClick(self):
        text: str = self.widget.ed_search.text()
        if len(text):
            backwards: bool = self.widget.cb_backwardsSearch.isChecked()
            self.signal_searchString.emit(text, backwards)
