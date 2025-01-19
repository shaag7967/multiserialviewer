from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot
from multiserialviewer.settings.watchSettings import WatchSettings

class WatchTableModel(QAbstractTableModel):
    class WatchEntry:
        def __init__(self, name: str, pattern: str, initialValue: str = ''):
            self.name: str = name
            self.pattern: str = pattern
            self.value: str = initialValue

        def setValue(self, value: str):
            self.value = value

    def __init__(self):
        QAbstractTableModel.__init__(self)

        self.settings: list[WatchSettings] = []
        self.entries: list[WatchTableModel.WatchEntry] = []
        self.nameToIndex: dict[str, int] = {}

    @Slot()
    def setWatchValue(self, name: str, value: list[str]):
        if name in self.nameToIndex:
            rowIndex = self.nameToIndex[name]
            self.entries[rowIndex].setValue(value[0])
            self.dataChanged.emit(self.index(rowIndex, 1), self.index(rowIndex, 1))

    def rowCount(self, parent=QModelIndex()):
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 2  # name and value

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return ("Name", "Value")[section]
        else:  # vertical
            return f"{section}"

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if column == 0:
                return self.entries[row].name
            elif column == 1:
                return str(self.entries[row].value)
        return None

    def reset(self):
        for idx, entry in enumerate(self.entries):
            entry.value = ''
            self.dataChanged.emit(self.index(idx, 1), self.index(idx, 1))

    def addWatchEntry(self, name: str, pattern) -> int:
        rowIdx = -1
        if name not in self.nameToIndex.keys():
            rowIdx = len(self.settings)
            self.beginInsertRows(QModelIndex(), rowIdx, rowIdx)
            self.nameToIndex[name] = rowIdx
            self.settings.append(WatchSettings(name, pattern))
            self.entries.append(WatchTableModel.WatchEntry(name, pattern))
            self.endInsertRows()

            assert len(self.entries) == len(self.settings)
        return rowIdx

    def removeWatchEntry(self, index: int) -> bool:
        assert len(self.entries) == len(self.settings)

        if index < len(self.settings):
            self.beginRemoveRows(QModelIndex(), index, index)
            del self.settings[index]
            del self.nameToIndex[self.entries[index].name]
            del self.entries[index]
            self.endRemoveRows()
            return True
        else:
            return False
