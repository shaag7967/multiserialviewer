

class TextHighlighterSettings:
    numberOfAttributes = 6

    def __init__(self):
        self.pattern = r"some text"
        self.color_foreground = 'red'
        self.color_background = 'transparent'
        self.italic = False
        self.bold = False
        self.font_size = 9

    def __str__(self):
        return (f"{self.pattern}: "
                f"  front {self.color_foreground} | back {self.color_background}"
                f"{' | italic' if self.italic is True else ''}{' | bold' if self.bold is True else ''}"
                f" | font size {self.font_size}")

