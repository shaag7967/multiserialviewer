from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex


class StatisticsTableModel(QAbstractTableModel):
    class DataEntry:
        def __init__(self, name: str):
            self.name: str = name
            self.value: int = 0


    def __init__(self):
        QAbstractTableModel.__init__(self)

        self.entries: list[StatisticsTableModel.DataEntry] = []
        self.entries.append(StatisticsTableModel.DataEntry('Current bandwidth usage'))
        self.entries.append(StatisticsTableModel.DataEntry('Max bandwidth usage'))
        self.entries.append(StatisticsTableModel.DataEntry('Bytes received'))
        self.entries.append(StatisticsTableModel.DataEntry('Non-printable bytes'))

    def setCurrentUsage(self, usage: int):
        self.entries[0].value = usage
        self.dataChanged.emit(self.index(0, 1), self.index(0, 1))

    def setMaxUsage(self, usage: int):
        self.entries[1].value = usage
        self.dataChanged.emit(self.index(1, 1), self.index(1, 1))

    def setReceivedByteCount(self, count: int):
        self.entries[2].value = count
        self.dataChanged.emit(self.index(2, 1), self.index(2, 1))

    def handleInvalidByteCount(self, count: int):
        self.entries[3].value += count
        self.dataChanged.emit(self.index(3, 1), self.index(3, 1))

    def rowCount(self, parent=QModelIndex()):
        return len(self.entries)

    def columnCount(self, parent=QModelIndex()):
        return 2  # name and value

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        column = index.column()
        row = index.row()

        if role == Qt.ItemDataRole.DisplayRole:
            if column == 0:
                return self.entries[row].name
            elif column == 1:
                if row < 2:
                    return str(self.entries[row].value) + ' %'
                else:
                    return str(self.entries[row].value)
        return None

    def reset(self):
        for idx, entry in enumerate(self.entries):
            entry.value = 0
        self.dataChanged.emit(self.index(0, 1), self.index(len(self.entries) - 1, 1))
