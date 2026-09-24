from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from localization.manager import LanguageManager


class TopicPage(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)
        layout = QVBoxLayout(self)
        self.label = QLabel()
        layout.addWidget(self.label)
        self.retranslate_ui()

    def retranslate_ui(self, *_):
        self.label.setText(self.lang.tr("topic_todo"))
