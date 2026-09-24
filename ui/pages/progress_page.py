from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout, QWidget

from core.config import DEMO_USER_ID
from core.activity import last_days
from core.repository import Repository
from localization.content import localize_content
from localization.manager import LanguageManager
from widgets.mascot_widget import MascotWidget


class ProgressPage(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)
        self._topic_cards = []

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 32)
        root.setSpacing(16)
        hero = QHBoxLayout()
        text = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("PageSubtitle")
        self.subtitle.setWordWrap(True)
        text.addWidget(self.title)
        text.addWidget(self.subtitle)
        hero.addLayout(text, 1)
        hero.addWidget(MascotWidget("teaching", 104))
        root.addLayout(hero)

        self.summary = QFrame()
        self.summary.setObjectName("SummaryCard")
        summary_row = QHBoxLayout(self.summary)
        self.average_label = QLabel()
        self.average_label.setObjectName("MetricValue")
        self.completed_label = QLabel()
        self.completed_label.setObjectName("MetricValue")
        self.mistakes_label = QLabel()
        self.mistakes_label.setObjectName("MetricValue")
        for label in (self.average_label, self.completed_label, self.mistakes_label):
            summary_row.addWidget(label, 1)
        root.addWidget(self.summary)

        self.activity_card = QFrame()
        self.activity_card.setObjectName("ActivityCard")
        activity_layout = QVBoxLayout(self.activity_card)
        activity_header = QHBoxLayout()
        self.activity_title = QLabel()
        self.activity_title.setObjectName("SectionTitle")
        self.streak_label = QLabel()
        self.streak_label.setObjectName("StreakValue")
        activity_header.addWidget(self.activity_title)
        activity_header.addStretch()
        activity_header.addWidget(self.streak_label)
        activity_layout.addLayout(activity_header)
        self.activity_days = QHBoxLayout()
        self.activity_days.setSpacing(8)
        activity_layout.addLayout(self.activity_days)
        root.addWidget(self.activity_card)

        self.grid = QGridLayout()
        self.grid.setSpacing(12)
        root.addLayout(self.grid)
        root.addStretch()
        self._reload()
        self.retranslate_ui()

    def _reload(self):
        activity = self.repo.get_activity_summary(DEMO_USER_ID)
        self.streak_label.setText(
            self.lang.tr(
                "streak_current",
                days=activity["current_streak"],
                best=activity["best_streak"],
            )
        )
        while self.activity_days.count():
            item = self.activity_days.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        weekday_keys = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for day, active in last_days(activity["days"]):
            label = QLabel()
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setObjectName("ActivityDayActive" if active else "ActivityDay")
            label.setText(f"{self.lang.tr(weekday_keys[day.weekday()])}\n{day.day}")
            self.activity_days.addWidget(label)

        progress = {p["topic_id"]: p for p in self.repo.get_user_progress(DEMO_USER_ID)}
        topics = self.repo.get_topics()
        scores = [progress[t["id"]]["score"] for t in topics if t["id"] in progress]
        completed = sum(1 for p in progress.values() if p["completed"])
        mistakes = sum(p["mistakes"] for p in progress.values())
        average = round(sum(scores) / len(scores)) if scores else 0
        self.average_label.setText(f"{average}%\n{self.lang.tr('progress_average')}")
        self.completed_label.setText(f"{completed}/{len(topics)}\n{self.lang.tr('progress_completed')}")
        self.mistakes_label.setText(f"{mistakes}\n{self.lang.tr('progress_mistakes')}")

        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._topic_cards.clear()
        for index, topic in enumerate(topics):
            entry = progress.get(topic["id"], {"score": 0, "completed": False})
            card = TopicProgressCard(
                localize_content(topic["name"], self.lang.current_lang),
                entry["score"],
                bool(entry["completed"]),
                self.lang,
            )
            self._topic_cards.append(card)
            self.grid.addWidget(card, index // 2, index % 2)

    def retranslate_ui(self, *_):
        self.title.setText(self.lang.tr("progress_title"))
        self.subtitle.setText(self.lang.tr("progress_subtitle"))
        self.activity_title.setText(self.lang.tr("activity_title"))
        self._reload()
        for card in self._topic_cards:
            card.retranslate(self.lang)


class TopicProgressCard(QFrame):
    def __init__(self, name, score, completed, lang):
        super().__init__()
        self.name_text = name
        self.score = score
        self.completed = completed
        self.setObjectName("ProgressTopicCard")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        self.name = QLabel()
        self.name.setObjectName("CardTitle")
        self.status = QLabel()
        self.status.setObjectName("MutedLabel")
        self.bar = QProgressBar()
        self.bar.setObjectName("ProgressBar")
        self.bar.setValue(score)
        layout.addWidget(self.name)
        layout.addWidget(self.status)
        layout.addWidget(self.bar)
        self.retranslate(lang)

    def retranslate(self, lang):
        self.name.setText(self.name_text)
        self.status.setText(lang.tr("progress_done") if self.completed else lang.tr("progress_in_progress"))
