from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import pyqtSignal
from widgets.subject_card import SubjectCard
from core.repository import Repository
from localization.manager import LanguageManager
from localization.content import localize_content

DEMO_USER_ID = 1


class SubjectsPage(QWidget):
    subject_opened = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self._retranslate_ui)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)

        grid = QGridLayout()
        grid.setSpacing(16)

        subjects = self.repo.get_subjects()
        progress_rows = {p["topic_id"]: p["score"] for p in self.repo.get_user_progress(DEMO_USER_ID)}

        for i, subject in enumerate(subjects):
            topics = self.repo.get_topics(subject_id=subject["id"])
            scores = [progress_rows.get(t["id"], 0) for t in topics]
            avg_progress = round(sum(scores) / len(scores)) if scores else 0

            display_name = localize_content(subject["name"], self.lang.current_lang)
            card = SubjectCard(subject["id"], display_name, avg_progress)
            card.clicked.connect(lambda sid, name=display_name: self.subject_opened.emit(sid, name))
            grid.addWidget(card, i // 4, i % 4)

        layout.addLayout(grid)
        layout.addStretch()
        self._retranslate_ui()

    def _retranslate_ui(self, *_):
        self.title.setText(self.lang.tr("nav_subjects"))
