from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat
from PySide6.QtGui import QColor
import re
from typing import List

from multiserialviewer.settings.textHighlighterSettings import TextHighlighterSettings


class TextHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        QSyntaxHighlighter.__init__(self, parent)
        self._settings: List[TextHighlighterSettings] = []

    def setSettings(self, settings: List[TextHighlighterSettings]):
        self._settings = settings

    def highlightBlock(self, text):
        if len(text) < 1:
            return

        for setting in self._settings:
            for match in re.finditer(setting.pattern, text):
                text_format = QTextCharFormat()
                text_format.setFontItalic(bool(setting.italic))
                if setting.bold:
                    text_format.setFontWeight(700)
                text_format.setFontPointSize(int(setting.font_size))
                text_format.setForeground(QColor(setting.color_foreground))
                text_format.setBackground(QColor(setting.color_background))

                start, end = match.span()
                self.setFormat(start, end - start, text_format)
