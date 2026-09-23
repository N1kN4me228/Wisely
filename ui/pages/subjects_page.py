from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PyQt6.QtCore import pyqtSignal
from widgets.subject_card import SubjectCard
from core.repository import Repository

DEMO_USER_ID = 1


class SubjectsPage(QWidget):
    subject_opened = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.repo = Repository()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        title = QLabel("Мои предметы")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(16)

        subjects = self.repo.get_subjects()
        progress_rows = {p["topic_id"]: p["score"] for p in self.repo.get_user_progress(DEMO_USER_ID)}

        for i, subject in enumerate(subjects):
            topics = self.repo.get_topics(subject_id=subject["id"])
            scores = [progress_rows.get(t["id"], 0) for t in topics]
            avg_progress = round(sum(scores) / len(scores)) if scores else 0

            card = SubjectCard(subject["id"], subject["name"], avg_progress)
            card.clicked.connect(lambda sid, name=subject["name"]: self.subject_opened.emit(sid, name))
            grid.addWidget(card, i // 4, i % 4)

        layout.addLayout(grid)
        layout.addStretch()
