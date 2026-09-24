from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from localization.manager import LanguageManager
from widgets.icon_utils import subject_icon


SUBJECT_KEYS = [
    "subject_algebra",
    "subject_geometry",
    "subject_law",
    "subject_physics",
    "subject_chemistry",
    "subject_biology",
]


class SubjectPreferencePage(QWidget):
    finished = pyqtSignal(list)  # список выбранных ключей предметов

    def __init__(self):
        super().__init__()
        self.setObjectName("SubjectPreferencePage")
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)
        self.selected: set[str] = set()
        self.subject_buttons: dict[str, QPushButton] = {}

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(16)
        root.setContentsMargins(40, 40, 40, 40)

        self.title = QLabel()
        self.title.setObjectName("SubjectsPrefTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setWordWrap(True)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("SubjectsPrefSubtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grid = QGridLayout()
        grid.setSpacing(12)
        for i, key in enumerate(SUBJECT_KEYS):
            btn = QPushButton()
            btn.setObjectName("SubjectChip")
            btn.setIcon(subject_icon(key))
            btn.setCheckable(True)
            btn.setMinimumSize(180, 60)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, k=key: self._toggle(k, checked))
            self.subject_buttons[key] = btn
            grid.addWidget(btn, i // 3, i % 3)

        self.continue_btn = QPushButton()
        self.continue_btn.setObjectName("PrimaryButton")
        self.continue_btn.setFixedSize(200, 48)
        self.continue_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.continue_btn.clicked.connect(self._on_continue)

        root.addWidget(self.title)
        root.addWidget(self.subtitle)
        root.addSpacing(12)
        root.addLayout(grid)
        root.addSpacing(24)
        root.addWidget(self.continue_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.retranslate_ui()

    def _toggle(self, key: str, checked: bool):
        if checked:
            self.selected.add(key)
        else:
            self.selected.discard(key)

    def _on_continue(self):
        self.finished.emit(list(self.selected))

    def retranslate_ui(self):
        self.title.setText(self.lang.tr("subjects_title"))
        self.subtitle.setText(self.lang.tr("subjects_subtitle"))
        for key, btn in self.subject_buttons.items():
            btn.setText(self.lang.tr(key))
        self.continue_btn.setText(self.lang.tr("continue_btn"))
