from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from core.repository import Repository
from core.config import DEMO_USER_ID
from ai_engine import get_recommendation
from localization.manager import LanguageManager
from localization.content import localize_content


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(16)

        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)

        self.rec_label = QLabel()
        self.rec_label.setObjectName("RecommendationCard")
        self.rec_label.setWordWrap(True)
        layout.addWidget(self.rec_label)

        layout.addStretch()
        self.retranslate_ui()

    def retranslate_ui(self):
        self.title.setText(self.lang.tr("dashboard_welcome_back"))
        progress = self.repo.get_progress(DEMO_USER_ID)
        rec = get_recommendation(progress)
        self.rec_label.setText(self._format_recommendation(rec))

    def _format_recommendation(self, rec: dict) -> str:
        if rec["action"] == "start":
            return self.lang.tr("rec_start")
        topic_name = localize_content(rec.get("topic"), self.lang.current_lang)
        if rec["action"] == "repeat":
            return self.lang.tr("rec_repeat", topic=topic_name)
        if rec["action"] == "practice":
            return self.lang.tr("rec_practice", topic=topic_name)
        return self.lang.tr("rec_next")
