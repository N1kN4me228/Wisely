from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QButtonGroup
from PyQt6.QtCore import pyqtSignal, Qt
from localization.manager import LanguageManager
from widgets.icon_utils import safe_icon

NAV_ITEMS = [
    ("nav_dashboard", 0, "icon_dashboard.png"),
    ("nav_subjects", 1, "icon_subjects.png"),
    ("nav_homework", 2, "icon_homework.png"),
    ("nav_progress", 3, "icon_progress.png"),
]


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
            btn.setIcon(safe_icon(icon))
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
            