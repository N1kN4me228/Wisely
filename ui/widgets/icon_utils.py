import os
from PyQt6.QtGui import QIcon


ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")


def safe_icon(filename: str) -> QIcon:
    path = os.path.join(ICONS_DIR, filename)

    if os.path.exists(path):
        return QIcon(path)
    
    return QIcon()
