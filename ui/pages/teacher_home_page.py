from PyQt6.QtWidgets import QFrame, QGridLayout, QLabel, QProgressBar, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

from core.config import DEMO_USER_ID
from core.database import get_connection
from core.repository import Repository
from localization.manager import LanguageManager
from localization.content import localize_content
from widgets.mascot_widget import MascotWidget


class TeacherHomePage(QWidget):
    """A useful teacher overview for the demo, backed by the same SQLite data."""

    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)
        self._topic_rows = []

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 32)
        root.setSpacing(16)
        hero = QGridLayout()
        text = QVBoxLayout()
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        self.subtitle = QLabel()
        self.subtitle.setObjectName("PageSubtitle")
        self.subtitle.setWordWrap(True)
        text.addWidget(self.title)
        text.addWidget(self.subtitle)
        hero.addLayout(text, 0, 0)
        hero.addWidget(MascotWidget("teaching", 118), 0, 1)
        root.addLayout(hero)

        self.stats = QFrame()
        self.stats.setObjectName("SummaryCard")
        stats = QGridLayout(self.stats)
        self.students = QLabel()
        self.attempts = QLabel()
        self.average = QLabel()
        stats.addWidget(self.students, 0, 0)
        stats.addWidget(self.attempts, 0, 1)
        stats.addWidget(self.average, 0, 2)
        root.addWidget(self.stats)

        self.section = QLabel()
        self.section.setObjectName("SectionTitle")
        root.addWidget(self.section)
        self.learners_section = QLabel()
        self.learners_section.setObjectName("SectionTitle")
        root.addWidget(self.learners_section)
        self.learners_list = QVBoxLayout()
        self.learners_list.setSpacing(8)
        root.addLayout(self.learners_list)
        self.topic_list = QVBoxLayout()
        self.topic_list.setSpacing(8)
        root.addLayout(self.topic_list)
        root.addStretch()
        self.retranslate_ui()

    def _summary(self):
        conn = get_connection()
        attempts = conn.execute("SELECT COUNT(*) AS c, COALESCE(AVG(score), 0) AS avg FROM attempts").fetchone()
        users = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
        topic_rows = conn.execute(
            """SELECT t.name, COALESCE(AVG(a.score), 0) AS score, COUNT(a.id) AS attempts
               FROM topics t LEFT JOIN tasks k ON k.topic_id = t.id
               LEFT JOIN attempts a ON a.task_id = k.id
               GROUP BY t.id ORDER BY t.order_index, t.id"""
        ).fetchall()
        conn.close()
        return users, attempts["c"], round(attempts["avg"]), topic_rows

    def retranslate_ui(self, *_):
        self.title.setText(self.lang.tr("teacher_title"))
        self.subtitle.setText(self.lang.tr("teacher_subtitle"))
        self.section.setText(self.lang.tr("teacher_topics"))
        self.learners_section.setText(self.lang.tr("teacher_learners"))
        users, attempts, average, topic_rows = self._summary()
        self.students.setText(f"{users}\n{self.lang.tr('teacher_students')}")
        self.attempts.setText(f"{attempts}\n{self.lang.tr('teacher_attempts')}")
        self.average.setText(f"{average}%\n{self.lang.tr('teacher_average')}")
        while self.learners_list.count():
            item = self.learners_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for learner in self.repo.get_teacher_learners():
            card = QFrame()
            card.setObjectName("TeacherLearnerRow")
            layout = QGridLayout(card)
            name = QLabel(f"{learner['name']} · {learner['class_number']} {self.lang.tr('teacher_grade')}")
            name.setObjectName("CardTitle")
            details = QLabel(self.lang.tr("teacher_learner_detail", attempts=learner["attempts"], average=learner["average"]))
            details.setObjectName("MutedLabel")
            streak = QLabel(self.lang.tr("teacher_streak", days=learner["current_streak"], best=learner["best_streak"]))
            streak.setObjectName("StreakValue")
            layout.addWidget(name, 0, 0)
            layout.addWidget(details, 1, 0)
            layout.addWidget(streak, 0, 1, 2, 1)
            self.learners_list.addWidget(card)
        while self.topic_list.count():
            item = self.topic_list.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for row in topic_rows:
            card = QFrame()
            card.setObjectName("TeacherTopicRow")
            layout = QGridLayout(card)
            name = QLabel(localize_content(row["name"], self.lang.current_lang))
            name.setObjectName("CardTitle")
            bar = QProgressBar()
            bar.setObjectName("ProgressBar")
            bar.setValue(round(row["score"]))
            details = QLabel(self.lang.tr("teacher_topic_detail", attempts=row["attempts"]))
            details.setObjectName("MutedLabel")
            layout.addWidget(name, 0, 0)
            layout.addWidget(details, 1, 0)
            layout.addWidget(bar, 0, 1, 2, 1)
            self.topic_list.addWidget(card)
