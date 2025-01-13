from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHeaderView
from PySide6.QtCore import Slot, Qt, QModelIndex
from typing import List

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.settings.textHighlighterSettings import TextHighlighterSettings
from multiserialviewer.text_highlighter.textHighlighterTableModel import TextHighlighterTableModel
from multiserialviewer.text_highlighter.colorSelectorItemDelegate import ColorSelectorItemDelegate


class TextHighlighterSettingsDialog(QDialog):
    __defaultPattern_MSG: str = r'\[MSG: .* :MSG\]'
    __defaultPattern_ERR: str = r'\[ERR: .* :ERR\]'
    __defaultPattern_HEX: str = r'\[[0-9A-F]{2}\]'

    def __init__(self, parent, settings: List[TextHighlighterSettings]):
        super().__init__(parent)

        self.setWindowTitle("Text Highlighter Settings")
        self.widget = createWidgetFromUiFile("textHighlighterSettingsDialog.ui")
        QVBoxLayout(self).addWidget(self.widget)

        self.tableModel = TextHighlighterTableModel(settings)
        self.widget.tableView.setModel(self.tableModel)
        self.widget.tableView.setItemDelegateForColumn(1, ColorSelectorItemDelegate(self.widget.tableView))
        self.widget.tableView.setItemDelegateForColumn(2, ColorSelectorItemDelegate(self.widget.tableView))

        # QTableView Headers
        self.horizontal_header = self.widget.tableView.horizontalHeader()
        self.vertical_header = self.widget.tableView.verticalHeader()

        # size
        self.horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.horizontal_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.horizontal_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.horizontal_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # buttons
        self.widget.buttonBox.accepted.connect(self.accept)
        self.widget.buttonBox.rejected.connect(self.reject)
        self.widget.pb_add.clicked.connect(self.addSetting)
        self.widget.pb_delete.clicked.connect(self.deleteSetting)
        self.widget.pb_applyDefaults.clicked.connect(self.applyDefaults)


    @Slot()
    def addSetting(self):
        self.tableModel.insertRows(self.tableModel.rowCount(), 1)

    @Slot()
    def deleteSetting(self):
        selected_model_indices = [modelIndex.row() for modelIndex in self.widget.tableView.selectionModel().selectedRows()]

        for index in sorted(selected_model_indices, reverse=True):
            self.tableModel.removeRows(index, 1)

    @staticmethod
    def getDefaultHighlighting_MSG() -> TextHighlighterSettings:
        cfg = TextHighlighterSettings()
        cfg.pattern = TextHighlighterSettingsDialog.__defaultPattern_MSG
        cfg.color_foreground = 'darkgreen'
        cfg.color_background = 'transparent'
        cfg.italic = False
        cfg.bold = True
        cfg.font_size = QApplication.font().pointSize()
        return cfg

    @staticmethod
    def getDefaultHighlighting_ERR() -> TextHighlighterSettings:
        cfg = TextHighlighterSettings()
        cfg.pattern = TextHighlighterSettingsDialog.__defaultPattern_ERR
        cfg.color_foreground = 'darkred'
        cfg.color_background = 'transparent'
        cfg.italic = False
        cfg.bold = True
        cfg.font_size = QApplication.font().pointSize()
        return cfg

    @staticmethod
    def getDefaultHighlighting_HEX() -> TextHighlighterSettings:
        cfg = TextHighlighterSettings()
        cfg.pattern = TextHighlighterSettingsDialog.__defaultPattern_HEX
        cfg.color_foreground = 'mediumblue'
        cfg.color_background = 'transparent'
        cfg.italic = False
        cfg.bold = False
        cfg.font_size = QApplication.font().pointSize()
        return cfg

    @Slot()
    def applyDefaults(self):
        defaultSettings: List[TextHighlighterSettings] = [TextHighlighterSettingsDialog.getDefaultHighlighting_MSG(),
                                                          TextHighlighterSettingsDialog.getDefaultHighlighting_ERR(),
                                                          TextHighlighterSettingsDialog.getDefaultHighlighting_HEX()]

        for setting in defaultSettings:
            entriesFound: List[QModelIndex] = self.tableModel.match(self.tableModel.index(0, 0),
                                                                    Qt.ItemDataRole.DisplayRole,
                                                                    setting.pattern,
                                                                    hits=1,
                                                                    flags=Qt.MatchFlag.MatchFixedString)
            if len(entriesFound) > 0:
                self.tableModel.replaceRow(entriesFound[0].row(), setting)
            else:
                self.tableModel.insertRows(0, 1)
                self.tableModel.replaceRow(0, setting)
