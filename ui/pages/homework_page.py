from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QProgressBar, QVBoxLayout, QWidget

from core.config import DEMO_USER_ID
from core.repository import Repository
from localization.content import localize_content
from localization.manager import LanguageManager
from widgets.mascot_widget import MascotWidget


class HomeworkPage(QWidget):
    """Practice queue built from the seeded tasks until a teacher assignment model exists."""

    topic_requested = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)
        self._cards = []

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 32)
        root.setSpacing(16)

        hero = QHBoxLayout()
        copy = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("PageSubtitle")
        self.subtitle.setWordWrap(True)
        copy.addWidget(self.title)
        copy.addWidget(self.subtitle)
        hero.addLayout(copy, 1)
        hero.addWidget(MascotWidget("reading", 104))
        root.addLayout(hero)

        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(10)
        root.addLayout(self.list_layout)
        root.addStretch()
        self.retranslate_ui()
        self._reload()

    def retranslate_ui(self, *_):
        self.title.setText(self.lang.tr("homework_title"))
        self.subtitle.setText(self.lang.tr("homework_subtitle"))
        for card in self._cards:
            card.retranslate(self.lang)

    def _reload(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._cards.clear()
        for topic in self.repo.get_topics():
            tasks = self.repo.get_tasks(topic_id=topic["id"], kind="practice")
            if not tasks:
                continue
            progress = {p["topic_id"]: p for p in self.repo.get_user_progress(DEMO_USER_ID)}.get(topic["id"])
            card = HomeworkCard(
                topic_id=topic["id"],
                topic_name=localize_content(topic["name"], self.lang.current_lang),
                task_count=len(tasks),
                score=progress["score"] if progress else 0,
                lang=self.lang,
            )
            card.open_requested.connect(lambda tid, name=topic["name"]: self.topic_requested.emit(tid, name))
            self._cards.append(card)
            self.list_layout.addWidget(card)


class HomeworkCard(QFrame):
    open_requested = pyqtSignal(int)

    def __init__(self, topic_id, topic_name, task_count, score, lang):
        super().__init__()
        self.topic_id = topic_id
        self.topic_name = topic_name
        self.task_count = task_count
        self.score = score
        self.lang = lang
        self.setObjectName("HomeworkCard")

        row = QHBoxLayout(self)
        row.setContentsMargins(18, 14, 18, 14)
        text = QVBoxLayout()
        self.name = QLabel()
        self.name.setObjectName("CardTitle")
        self.detail = QLabel()
        self.detail.setObjectName("MutedLabel")
        text.addWidget(self.name)
        text.addWidget(self.detail)
        row.addLayout(text, 1)
        self.progress = QProgressBar()
        self.progress.setObjectName("HomeworkProgress")
        self.progress.setFixedWidth(150)
        self.progress.setValue(score)
        row.addWidget(self.progress)
        self.button = QPushButton()
        self.button.setObjectName("PrimaryButton")
        self.button.clicked.connect(lambda: self.open_requested.emit(self.topic_id))
        row.addWidget(self.button)
        self.retranslate(lang)

    def retranslate(self, lang):
        self.name.setText(self.topic_name)
        self.detail.setText(lang.tr("homework_tasks", count=self.task_count))
        self.button.setText(lang.tr("homework_open"))
