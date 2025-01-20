from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot
from multiserialviewer.settings.watchSettings import WatchSettings
from typing import Optional


class WatchTableModel(QAbstractTableModel):
    class WatchEntry:
        def __init__(self, name: str, pattern: str):
            self.name: str = name
            self.pattern: str = pattern
            self.value: str = ''
            self.minValue: Optional[float | None] = None
            self.maxValue: Optional[float | None] = None
            self.updateCount: int = 0

        def setValue(self, value: str):
            self.value = value
            self.__updateMinMaxValues(value)
            self.updateCount += 1

        def __updateMinMaxValues(self, value: str):
            try:
                # is it a number?
                number = float(value)
            except:
                pass
            else:
                self.minValue = number if self.minValue is None else min(self.minValue, number)
                self.maxValue = number if self.maxValue is None else max(self.maxValue, number)

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

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return self.entries[row].name
            elif column == 1:
                return self.entries[row].value

        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 0:
                return f"Received {str(self.entries[row].updateCount)} value{'s' if self.entries[row].updateCount != 1 else ''}"
            elif column == 1:
                toolTips = []
                if self.entries[row].minValue is not None:
                    toolTips.append(f"Min: {str(self.entries[row].minValue)}")
                if self.entries[row].maxValue is not None:
                    toolTips.append(f"Max: {str(self.entries[row].maxValue)}")
                return '\n'.join(toolTips)
        return None

    def reset(self):
        for idx, entry in enumerate(self.entries):
            entry.value = ''
            entry.minValue = None
            entry.maxValue = None
            entry.updateCount = 0
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
