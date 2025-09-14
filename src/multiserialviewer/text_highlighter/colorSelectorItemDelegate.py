from PySide6.QtWidgets import QStyledItemDelegate, QAbstractItemDelegate, QAbstractItemView, QComboBox
from PySide6.QtCore import Qt

from multiserialviewer.text_highlighter.textHighlighterTableModel import TextHighlighterTableModel


class ColorSelectorItemDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        combobox = QComboBox(parent)

        colors = index.data(TextHighlighterTableModel.AllColorsRole)
        for color in colors:
            combobox.insertItem(color[0], color[1])
            combobox.setItemData(color[0], color[2], Qt.ItemDataRole.DecorationRole)

        model = index.model()
        row, col = index.row(), index.column()
        combobox.currentIndexChanged.connect(
            lambda ix, m=model, r=row, c=col: m.setData(m.index(r, c), ix, TextHighlighterTableModel.SelectedColorRole)
        )
        return combobox

    def setEditorData(self, editor, index):
        if isinstance(editor, QComboBox):
            ix = index.data(TextHighlighterTableModel.SelectedColorRole)
            if ix is not None:
                editor.setCurrentIndex(ix)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            ix = editor.currentIndex()
            model.setData(index, ix, TextHighlighterTableModel.SelectedColorRole)
        else:
            super().setModelData(editor, model, index)

