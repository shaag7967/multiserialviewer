from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QColor
from typing import List
from collections import OrderedDict

from multiserialviewer.text_highlighter.textHighlighterConfig import TextHighlighterConfig


class TextHighlighterTableModel(QAbstractTableModel):
    AllColorsRole = Qt.UserRole + 1
    SelectedColorRole = Qt.UserRole + 2

    def __init__(self, settings: List[TextHighlighterConfig]):
        QAbstractTableModel.__init__(self)
        self.settings = settings

        self.color_map = OrderedDict()
        for i, name in enumerate(QColor.colorNames()):
            self.color_map[name] = (i, name, QColor(name))

    def rowCount(self, parent=QModelIndex()):
        return len(self.settings)

    def columnCount(self, parent=QModelIndex()):
        return TextHighlighterConfig.number_of_attributes

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return ("Text/Pattern", "Foreground", "Background", "Italic", "Bold", "Font Size")[section]
        else:  # vertical
            return f"{section}"

    def setData(self, index, value, role=Qt.EditRole):
        if role not in [Qt.EditRole, Qt.CheckStateRole, TextHighlighterTableModel.SelectedColorRole]:
            return False

        column = index.column()
        row = index.row()
        if row >= len(self.settings):
            return False
        if column >= TextHighlighterConfig.number_of_attributes:
            return False

        if column == 0:
            self.settings[row].pattern = value
        elif column == 1:
            self.settings[row].color_foreground = list(self.color_map.values())[value][1]  # color by index
        elif column == 2:
            self.settings[row].color_background = list(self.color_map.values())[value][1]  # color by index
        elif column == 3:
            if role == Qt.CheckStateRole:
                self.settings[row].italic = bool(value)
        elif column == 4:
            if role == Qt.CheckStateRole:
                self.settings[row].bold = bool(value)
        elif column == 5:
            self.settings[row].font_size = int(value)

        self.dataChanged.emit(index, index)
        return True

    def flags(self, index):
        f = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() in [0, 1, 2, 5]:
            f |= Qt.ItemIsEditable
        elif index.column() == 3 or index.column() == 4:
            f |= Qt.ItemIsUserCheckable
        return f

    def data(self, index, role=Qt.DisplayRole):
        column = index.column()
        row = index.row()

        if role == TextHighlighterTableModel.AllColorsRole:
            return self.color_map.values()

        if role == TextHighlighterTableModel.SelectedColorRole:
            if column == 1:
                return self.color_map[self.settings[row].color_foreground][0]  # return index of color in color_map
            elif column == 2:
                return self.color_map[self.settings[row].color_background][0]

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if column == 0:
                return self.settings[row].pattern
            elif column == 5:
                return self.settings[row].font_size
        elif role == Qt.CheckStateRole:
            if column == 3:
                value = self.settings[row].italic
            elif column == 4:
                value = self.settings[row].bold
            else:
                return None
            return Qt.Checked if value else Qt.Unchecked
        elif role == Qt.BackgroundRole:
            if column == 0:
                return self.color_map[self.settings[row].color_background][2]
        elif role == Qt.ForegroundRole:
            if column == 0:
                return self.color_map[self.settings[row].color_foreground][2]
        elif role == Qt.TextAlignmentRole:
            if column == 0:
                return Qt.AlignRight
        return None

    def insertRows(self, row, count, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)
        for i in range(count):
            self.settings.insert(row+i, TextHighlighterConfig())
        self.endInsertRows()

    def removeRows(self, row, count, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)
        for i in range(count):
            del self.settings[row]
        self.endRemoveRows()
        return True
