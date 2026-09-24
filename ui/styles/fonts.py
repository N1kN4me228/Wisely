from PyQt6.QtGui import QFont


FORMULA_FONT = QFont("Consolas", 14)


def bold_font(family: str, size: int = 10) -> QFont:
    font = QFont(family, size)
    font.setBold(True)
    return font


def medium_font(family: str, size: int = 10) -> QFont:
    font = QFont(family, size)
    font.setWeight(QFont.Weight.Medium)
    return font
