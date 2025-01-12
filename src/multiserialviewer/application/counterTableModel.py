from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot
from multiserialviewer.settings.counterSettings import CounterSettings


class CounterTableModel(QAbstractTableModel):
    class CounterEntry:
        def __init__(self, regex: str, initialValue: int = 0):
            self.regex: str = regex
            self.value: int = initialValue

        def increment(self):
            self.value += 1

    def __init__(self):
        QAbstractTableModel.__init__(self)

        self.settings: list[CounterSettings] = []
        self.entries: list[CounterTableModel.CounterEntry] = []
        self.regexToIndex: dict[str, int] = {}

    @Slot()
    def incrementCounterValue(self, regex: str, unused: object):
        if regex in self.regexToIndex:
            rowIndex = self.regexToIndex[regex]
            self.entries[rowIndex].increment()
            self.dataChanged.emit(self.index(rowIndex, 1), self.index(rowIndex, 1))

    def rowCount(self, parent=QModelIndex()):
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 2  # pattern and value

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return ("Text/Pattern", "Counted")[section]
        else:  # vertical
            return f"{section}"

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if column == 0:
                return self.entries[row].regex
            elif column == 1:
                return str(self.entries[row].value)
        return None

    def resetCounters(self):
        for idx, entry in enumerate(self.entries):
            entry.value = 0
            self.dataChanged.emit(self.index(idx, 1), self.index(idx, 1))

    def addCounterEntry(self, pattern) -> int:
        rowIdx = -1
        if pattern not in self.regexToIndex.keys():
            rowIdx = len(self.settings)
            self.beginInsertRows(QModelIndex(), rowIdx, rowIdx)
            self.regexToIndex[pattern] = rowIdx
            self.settings.append(CounterSettings(pattern))
            self.entries.append(CounterTableModel.CounterEntry(pattern))
            self.endInsertRows()

            assert len(self.entries) == len(self.settings)
        return rowIdx

    def removeCounterEntry(self, index: int) -> bool:
        assert len(self.entries) == len(self.settings)

        if index < len(self.settings):
            self.beginRemoveRows(QModelIndex(), index, index)
            del self.settings[index]
            del self.regexToIndex[self.entries[index].regex]
            del self.entries[index]
            self.endRemoveRows()
            return True
        else:
            return False
