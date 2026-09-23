from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from localization.manager import LanguageManager


class LangSwitch(QWidget):
    def __init__(self):
        super().__init__()
        self.lang = LanguageManager.instance()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.ru_btn = QPushButton("РУС")
        self.kz_btn = QPushButton("QAZ")
        for btn, code in ((self.ru_btn, "ru"), (self.kz_btn, "kz")):
            btn.setObjectName("LangSwitchButton")
            btn.setCheckable(True)
            btn.setFixedSize(52, 26)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, c=code: self.lang.set_language(c))
            layout.addWidget(btn)

        self.lang.language_changed.connect(self._sync)
        self._sync()

    def _sync(self, *_):
        self.ru_btn.setChecked(self.lang.current_lang == "ru")
        self.kz_btn.setChecked(self.lang.current_lang == "kz")
        