from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QIcon
from localization.manager import LanguageManager
from widgets.icon_utils import EMOTIONS_DIR
import os

# Sidebar icons reuse Okto's emotion set instead of the icon_dashboard.png /
# icon_subjects.png / icon_homework.png / icon_progress.png files this used
# to reference — those were never part of ui/resources/icons, so every nav
# button silently rendered with no icon at all (safe_icon() falls back to a
# blank QIcon when the file is missing). Okto is already the mascot used
# everywhere else in the app, so this also keeps the nav visually consistent
# with the rest of the UI instead of introducing a second icon set.
NAV_ITEMS = [
    ("nav_dashboard", 0, "happy.png"),
    ("nav_subjects", 1, "reading.png"),
    ("nav_homework", 2, "thinking.png"),
    ("nav_progress", 3, "teaching.png"),
]


def _nav_icon(filename: str) -> QIcon:
    path = os.path.join(EMOTIONS_DIR, filename)
    return QIcon(path) if os.path.exists(path) else QIcon()


class Sidebar(QWidget):
    page_selected = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.setObjectName("Sidebar")
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        self.group = QButtonGroup(self)
        self.group.setExclusive(True)
        self.buttons = {}

        for key, index, icon in NAV_ITEMS:
            btn = QPushButton()
            btn.setObjectName("SidebarButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setIcon(_nav_icon(icon))
            btn.setIconSize(QSize(22, 22))
            btn.clicked.connect(lambda _, i=index: self.page_selected.emit(i))
            self.group.addButton(btn, index)
            self.buttons[key] = btn
            layout.addWidget(btn)

        self.buttons["nav_dashboard"].setChecked(True)
        layout.addStretch()
        self.retranslate_ui()

    def retranslate_ui(self):
        for key, btn in self.buttons.items():
            btn.setText("  " + self.lang.tr(key))
