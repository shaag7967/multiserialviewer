from PySide6.QtWidgets import QDialog, QVBoxLayout, QHeaderView
from typing import List

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.text_highlighter.textHighlighterConfig import TextHighlighterConfig
from multiserialviewer.text_highlighter.textHighlighterTableModel import TextHighlighterTableModel
from multiserialviewer.text_highlighter.colorSelectorItemDelegate import ColorSelectorItemDelegate


class TextHighlighterSettingsDialog(QDialog):
    def __init__(self, parent, settings: List[TextHighlighterConfig]):
        super().__init__(parent)

        self.setWindowTitle("Text Highlighter Settings")
        self.widget = createWidgetFromUiFile("textHighlighterSettingsDialog.ui")

        self.table_model = TextHighlighterTableModel(settings)
        self.widget.tableView.setModel(self.table_model)
        self.widget.tableView.setItemDelegateForColumn(1, ColorSelectorItemDelegate(self.widget.tableView))
        self.widget.tableView.setItemDelegateForColumn(2, ColorSelectorItemDelegate(self.widget.tableView))

        # QTableView Headers
        self.horizontal_header = self.widget.tableView.horizontalHeader()
        self.vertical_header = self.widget.tableView.verticalHeader()

        # size
        self.horizontal_header.setSectionResizeMode(QHeaderView.Stretch)
        self.horizontal_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.horizontal_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        # buttons
        self.widget.buttonBox.accepted.connect(self.accept)
        self.widget.buttonBox.rejected.connect(self.reject)
        self.widget.pb_add.clicked.connect(self.addSetting)
        self.widget.pb_delete.clicked.connect(self.deleteSetting)

        QVBoxLayout(self).addWidget(self.widget)

    def addSetting(self):
        self.table_model.insertRows(self.table_model.rowCount(), 1)

    def deleteSetting(self):
        selected_model_indices = [modelIndex.row() for modelIndex in self.widget.tableView.selectionModel().selectedRows()]

        for index in sorted(selected_model_indices, reverse=True):
            self.table_model.removeRows(index, 1)
