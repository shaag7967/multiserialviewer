from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QHeaderView, QDialogButtonBox
from PySide6.QtCore import Slot, Qt, QModelIndex, QUrl, QItemSelectionModel, QItemSelection
from PySide6.QtGui import QDesktopServices
from typing import List
import copy

from multiserialviewer.ui_files.uiFileHelper import createWidgetFromUiFile
from multiserialviewer.icons.iconSet import IconSet
from multiserialviewer.settings.settings import Settings, TextHighlighterSettings
from multiserialviewer.text_highlighter.textHighlighterTableModel import TextHighlighterTableModel
from multiserialviewer.text_highlighter.colorSelectorItemDelegate import ColorSelectorItemDelegate


class SettingsDialog(QDialog):

    def __init__(self, parent, settings: Settings, iconSet: IconSet):
        super().__init__(parent)

        self.setWindowTitle("Settings")
        self.widget = createWidgetFromUiFile("settingsDialog.ui")
        QVBoxLayout(self).addWidget(self.widget)

        self.settingsBackup = copy.deepcopy(settings)
        self.settings = settings
        self.__init(self.settings)

        #
        # text highlighter
        #
        self.widget.tableView.setModel(self.tableModel)
        self.widget.tableView.setItemDelegateForColumn(1, ColorSelectorItemDelegate(self.widget.tableView))
        self.widget.tableView.setItemDelegateForColumn(2, ColorSelectorItemDelegate(self.widget.tableView))

        self.widget.pb_delete.setEnabled(False)
        selectionModel: QItemSelectionModel = self.widget.tableView.selectionModel()
        selectionModel.selectionChanged.connect(self.updateEnableState_buttonDelete)

        horizontal_header = self.widget.tableView.horizontalHeader()
        horizontal_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        horizontal_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.widget.tableView.setColumnWidth(1, 170)
        horizontal_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.widget.tableView.setColumnWidth(2, 170)
        horizontal_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        horizontal_header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        horizontal_header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.widget.pb_add.clicked.connect(self.addHighlighterSetting)
        self.widget.pb_delete.clicked.connect(self.deleteHighlighterSetting)
        self.widget.pb_applyHighlighterRecommendations.clicked.connect(self.applyHighlighterRecommendations)

        #
        # advanced
        #
        self.widget.pb_openSettingsDir.setIcon(iconSet.getDirectoryIcon())
        self.widget.pb_openSettingsDir.clicked.connect(self.openSettingsDirectoryInFileBrowser)

        #
        # buttonBox
        #
        buttonBox: QDialogButtonBox = self.widget.buttonBox
        buttonBox.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(self.applyChanges)
        buttonBox.rejected.connect(self.reject)
        buttonBox.button(QDialogButtonBox.StandardButton.Reset).clicked.connect(self.resetChanges)

    def __init(self, settings: Settings):
        self.widget.cb_restoreCaptureState.setCheckState(
            Qt.CheckState.Checked if settings.application.restoreCaptureState else Qt.CheckState.Unchecked)
        self.tableModel = TextHighlighterTableModel(settings.textHighlighter.entries)
        self.widget.tableView.setModel(self.tableModel)
        selectionModel: QItemSelectionModel = self.widget.tableView.selectionModel()
        selectionModel.selectionChanged.connect(self.updateEnableState_buttonDelete)

    @Slot(str)
    def updateEnableState_buttonDelete(self, selected: QItemSelection, deselected: QItemSelection):
        self.widget.pb_delete.setEnabled(selected.count() > 0)

    @Slot()
    def openSettingsDirectoryInFileBrowser(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.settings.settingsDir))

    @Slot()
    def applyChanges(self):
        self.settings.application.restoreCaptureState = self.widget.cb_restoreCaptureState.checkState() == Qt.CheckState.Checked
        self.settings.textHighlighter.entries = self.tableModel.settings
        self.accept()

    @Slot()
    def resetChanges(self):
        self.settings = copy.deepcopy(self.settingsBackup)
        self.__init(self.settings)

    @Slot()
    def addHighlighterSetting(self):
        self.tableModel.insertRows(self.tableModel.rowCount(), 1)

    @Slot()
    def deleteHighlighterSetting(self):
        selected_model_indices = [modelIndex.row() for modelIndex in self.widget.tableView.selectionModel().selectedRows()]

        for index in sorted(selected_model_indices, reverse=True):
            self.tableModel.removeRows(index, 1)

    @staticmethod
    def getDefaultHighlighting_HEX() -> TextHighlighterSettings:
        cfg = TextHighlighterSettings()
        cfg.pattern = r'\[[0-9A-F]{2}\]'
        cfg.color_foreground = 'darkred'
        cfg.color_background = 'transparent'
        cfg.italic = False
        cfg.bold = False
        cfg.font_size = QApplication.font().pointSize()
        return cfg

    @Slot()
    def applyHighlighterRecommendations(self):
        defaultSettings: List[TextHighlighterSettings] = [SettingsDialog.getDefaultHighlighting_HEX()]

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
