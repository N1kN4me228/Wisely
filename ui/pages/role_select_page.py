from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtCore import Qt, pyqtSignal
from localization.manager import LanguageManager

class RoleSelectPage(QWidget):
    role_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setObjectName("RoleSelectPage")
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.setSpacing(24)

        self.title = QLabel("WISELY")
        self.title.setObjectName("RoleTitle")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subtitle = QLabel()
        self.subtitle.setObjectName("RoleSubtitle")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_row.setSpacing(16)

        self.student_btn = QPushButton()
        self.teacher_btn = QPushButton()
        for btn, role in ((self.student_btn, "student"), (self.teacher_btn, "teacher")):
            btn.setObjectName("RoleButton")
            btn.setFixedSize(220, 130)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, r=role: self.role_selected.emit(r))
            btn_row.addWidget(btn)

        # переключатель языка
        lang_row = QHBoxLayout()
        lang_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lang_row.setSpacing(8)

        self.ru_btn = QPushButton("РУС")
        self.kz_btn = QPushButton("QAZ")
        for btn, code in ((self.ru_btn, "ru"), (self.kz_btn, "kz")):
            btn.setObjectName("LangButton")
            btn.setCheckable(True)
            btn.setFixedSize(70, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, c=code: self.lang.set_language(c))
            lang_row.addWidget(btn)

        root.addWidget(self.title)
        root.addWidget(self.subtitle)
        root.addLayout(btn_row)
        root.addSpacing(20)
        root.addLayout(lang_row)

        self.retranslate_ui()
        self._sync_lang_buttons()

    def retranslate_ui(self):
        self.subtitle.setText(self.lang.tr("role_question"))
        self.student_btn.setText(self.lang.tr("role_student"))
        self.teacher_btn.setText(self.lang.tr("role_teacher"))
        self._sync_lang_buttons()

    def _sync_lang_buttons(self):
        self.ru_btn.setChecked(self.lang.current_lang == "ru")
        self.kz_btn.setChecked(self.lang.current_lang == "kz")
