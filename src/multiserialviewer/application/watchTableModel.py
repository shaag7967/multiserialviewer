from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Slot
from typing import Optional


class WatchEntryNumber:
    def __init__(self, variableName: str, pattern: str):
        self.name: str = variableName
        self.pattern: str = pattern
        self.value: Optional[float | None] = None
        self.minValue: Optional[float | None] = None
        self.maxValue: Optional[float | None] = None
        self.updateCount: int = 0

    def setValue(self, value: str):
        try:
            self.value = float(value)
        except ValueError:
            pass
        else:
            self.minValue = self.value if self.minValue is None else min(self.minValue, self.value)
            self.maxValue = self.value if self.maxValue is None else max(self.maxValue, self.value)
            self.updateCount += 1

    def getValue(self):
        return '' if self.value is None else str(self.value)

    def reset(self):
        self.value = None
        self.minValue = None
        self.maxValue = None
        self.updateCount = 0

    def getTooltipPrimary(self):
        if self.updateCount > 0:
            return f"Received {str(self.updateCount)} time{'s' if self.updateCount != 1 else ''}"
        else:
            return ""

    def getTooltipSecondary(self):
        toolTips = []
        if self.minValue is not None:
            toolTips.append(f"Min: {str(self.minValue)}")
        if self.maxValue is not None:
            toolTips.append(f"Max: {str(self.maxValue)}")
        return '\n'.join(toolTips)


class WatchEntryWord:
    def __init__(self, variableName: str, description: str, pattern: str):
        self.name: str = variableName
        self.description: str = description
        self.pattern: str = pattern
        self.value: Optional[str | None] = None
        self.receivedWords: list[str] = []
        self.updateCount: int = 0

    def setValue(self, value: str):
        self.value = value
        if value not in self.receivedWords:
            self.receivedWords.append(value)
        self.updateCount += 1

    def getValue(self):
        return '' if self.value is None else self.value

    def reset(self):
        self.value = None
        self.receivedWords = []
        self.updateCount = 0

    def getTooltipPrimary(self):
        hint = f"Recognized words: {self.description}"
        if self.updateCount > 0:
            return f"Received {str(self.updateCount)} time{'s' if self.updateCount != 1 else ''}\n{hint}"
        else:
            return hint

    def getTooltipSecondary(self):
        if len(self.receivedWords) > 0:
            words = ', '.join(self.receivedWords)
            return f"Received words '{words}'"
        else:
            return ""

class WatchTableModel(QAbstractTableModel):
    def __init__(self):
        QAbstractTableModel.__init__(self)

        self.entries: list[WatchEntryNumber | WatchEntryWord] = []
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
            return ("Name of variable", "Value")[section]
        else:  # vertical
            return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return self.entries[row].name
            elif column == 1:
                return self.entries[row].getValue()

        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 0:
                return self.entries[row].getTooltipPrimary()
            elif column == 1:
                return self.entries[row].getTooltipSecondary()
        return None

    def reset(self):
        for idx, entry in enumerate(self.entries):
            entry.reset()
        self.dataChanged.emit(self.index(0, 1), self.index(len(self.entries)-1, 1))

    def addWatchEntry(self, entry: WatchEntryNumber | WatchEntryWord) -> int:
        rowIdx = -1

        if entry.name not in self.nameToIndex.keys():
            rowIdx = len(self.entries)
            self.beginInsertRows(QModelIndex(), rowIdx, rowIdx)
            self.nameToIndex[entry.name] = rowIdx
            self.entries.append(entry)
            self.endInsertRows()

        return rowIdx

    def getWatchIndex(self, variableName: str) -> int:
        if variableName in self.nameToIndex.keys():
            return self.nameToIndex[variableName]
        else:
            return -1

    def removeWatchEntry(self, index: int) -> bool:
        if index < len(self.entries):
            self.beginRemoveRows(QModelIndex(), index, index)
            del self.nameToIndex[self.entries[index].name]
            del self.entries[index]
            self.endRemoveRows()
            return True
        else:
            return False
