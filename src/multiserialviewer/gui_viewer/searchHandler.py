from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QTextDocument

from multiserialviewer.gui_viewer.serialViewerTextEdit import SerialViewerTextEdit
from multiserialviewer.gui_viewer.searchWidget import SearchWidget


class SearchHandler(QObject):
    signal_foundString: Signal = Signal(str)

    def __init__(self, textEdit: SerialViewerTextEdit, searchWidget: SearchWidget):
        super(SearchHandler, self).__init__()

        self.__textEdit = textEdit
        self.__searchWidget = searchWidget

        self.__textEdit.selectionChanged.connect(self.handleTextSelectionChange)
        self.__searchWidget.signal_searchString.connect(self.searchString)
        self.__searchWidget.signal_previousClicked.connect(self.searchPrevious)
        self.__searchWidget.signal_nextClicked.connect(self.searchNext)

    @Slot(str, bool)
    def searchString(self, text: str, backward_search: bool):
        if self.__textEdit.textCursor().selectedText() != text:
            self.__textEdit.textCursor().clearSelection()
        found = self.__textEdit.find(text, QTextDocument.FindFlag.FindBackward if backward_search else QTextDocument.FindFlag(0))
        if found:
            self.signal_foundString.emit(text)

    @Slot()
    def searchPrevious(self):
        selectedText = self.__textEdit.textCursor().selectedText()
        self.__textEdit.find(selectedText, QTextDocument.FindFlag.FindBackward)

    @Slot()
    def searchNext(self):
        selectedText = self.__textEdit.textCursor().selectedText()
        self.__textEdit.find(selectedText, QTextDocument.FindFlag(0))

    @Slot()
    def handleTextSelectionChange(self):
        hasSelectedText = len(self.__textEdit.textCursor().selectedText()) > 0
        self.__searchWidget.widget.pb_previous.setEnabled(hasSelectedText)
        self.__searchWidget.widget.pb_next.setEnabled(hasSelectedText)

