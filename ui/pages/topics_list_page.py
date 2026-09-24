from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from core.repository import Repository
from widgets.icon_utils import subject_icon_pixmap
from localization.manager import LanguageManager
from localization.content import localize_content


DEMO_USER_ID = 1


class TopicsListPage(QWidget):
    topic_opened = pyqtSignal(int, str)
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)

        self.layout_ = QVBoxLayout(self)
        self.layout_.setContentsMargins(32, 24, 32, 32)
        self.layout_.setSpacing(12)

        header = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setObjectName("BackButton")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn)
        header.addStretch()
        self.layout_.addLayout(header)

        title_row = QHBoxLayout()
        self.subject_icon_label = QLabel()
        self.subject_icon_label.setPixmap(subject_icon_pixmap("", 40))
        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        title_row.addWidget(self.subject_icon_label)
        title_row.addWidget(self.title)
        title_row.addStretch()
        self.layout_.addLayout(title_row)

        self.list_container = QVBoxLayout()
        self.list_container.setSpacing(10)
        self.layout_.addLayout(self.list_container)
        self.layout_.addStretch()
        self.retranslate_ui()

    def retranslate_ui(self, *_):
        self.back_btn.setText(self.lang.tr("back_short"))

    def load_subject(self, subject_id: int, subject_name: str):
        self.title.setText(subject_name)
        self.subject_icon_label.setPixmap(subject_icon_pixmap(subject_name, 40))

        while self.list_container.count():
            item = self.list_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        topics = self.repo.get_topics(subject_id=subject_id)
        progress = {p["topic_id"]: p for p in self.repo.get_user_progress(DEMO_USER_ID)}

        for topic in topics:
            row = QPushButton()
            row.setObjectName("TopicRow")
            row.setCursor(Qt.CursorShape.PointingHandCursor)
            row.setMinimumHeight(64)

            p = progress.get(topic["id"])
            score_text = f"{p['score']}%" if p else "0%"
            status = "✓ " if p and p["completed"] else ""

            topic_name = localize_content(topic["name"], self.lang.current_lang)
            row.setText(f"{status}{topic_name}   —   {score_text}")
            row.clicked.connect(lambda _, t=topic, name=topic_name: self.topic_opened.emit(t["id"], name))
            self.list_container.addWidget(row)
