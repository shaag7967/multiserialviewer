from PySide6.QtWidgets import QStyledItemDelegate, QAbstractItemDelegate, QAbstractItemView, QComboBox
from PySide6.QtCore import Qt

from multiserialviewer.text_highlighter.textHighlighterTableModel import TextHighlighterTableModel


class ColorSelectorItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if isinstance(self.parent(), QAbstractItemView):
            self.parent().openPersistentEditor(index)
        QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        combobox = QComboBox(parent)

        colors = index.data(TextHighlighterTableModel.AllColorsRole)
        for color in colors:
            combobox.insertItem(color[0], color[1])
            combobox.setItemData(color[0], color[2], Qt.DecorationRole)

        combobox.currentIndexChanged.connect(self.onCurrentIndexChanged)
        return combobox

    def onCurrentIndexChanged(self, ix):
        editor = self.sender()
        self.commitData.emit(editor)
        self.closeEditor.emit(editor, QAbstractItemDelegate.NoHint)

    def setEditorData(self, editor, index):
        ix = index.data(TextHighlighterTableModel.SelectedColorRole)
        editor.setCurrentIndex(ix)

    def setModelData(self, editor, model, index):
        ix = editor.currentIndex()
        model.setData(index, ix, TextHighlighterTableModel.SelectedColorRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def sizeHint(self, option, index):
        return super().sizeHint(option, index)
