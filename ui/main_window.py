from PyQt6.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QSizeGrip, QMessageBox,
)
from PyQt6.QtCore import Qt

from localization.manager import LanguageManager
from settings.app_settings import AppSettings
from pages.role_select_page import RoleSelectPage
from pages.subject_preference_page import SubjectPreferencePage
from widgets.lang_switch import LangSwitch


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setMinimumSize(900, 600)

        screen = self.screen().availableGeometry()
        self.resize(int(screen.width() * 0.75), int(screen.height() * 0.8))
        self.move(screen.center() - self.rect().center())

        self.settings = AppSettings()
        self.lang = LanguageManager.instance()

        saved_lang = self.settings.get_language()
        if saved_lang:
            self.lang.current_lang = saved_lang
        self.lang.language_changed.connect(self.settings.set_language)

        # --- корневой контейнер: шапка сверху + контент снизу ---
        outer = QWidget()
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        outer_layout.addWidget(self._build_title_bar())

        self.root_stack = QStackedWidget()
        outer_layout.addWidget(self.root_stack)

        grip_row = QHBoxLayout()
        grip_row.addStretch()
        grip_row.addWidget(QSizeGrip(outer))
        outer_layout.addLayout(grip_row)

        self.setCentralWidget(outer)

        self._drag_pos = None

        self.current_role = self.settings.get_role()
        self.selected_subjects = self.settings.get_subjects()

        if self.settings.is_onboarding_done():
            self._enter_main_app()
        else:
            self._start_onboarding()

    # ---------- Кастомная шапка (заменяет системную рамку) ----------
    def _build_title_bar(self) -> QWidget:
        self.title_bar = QWidget()
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(40)
        self.title_bar.installEventFilter(self)

        layout = QHBoxLayout(self.title_bar)
        layout.setContentsMargins(16, 0, 8, 0)

        title_label = QLabel("WISELY")
        title_label.setObjectName("TitleBarLabel")

        self.logout_btn = QPushButton()
        self.logout_btn.setObjectName("LogoutButton")
        self.logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.logout_btn.clicked.connect(self._logout)
        self.lang.language_changed.connect(self._retranslate_title_bar)
        self._retranslate_title_bar()

        close_btn = QPushButton("✕")
        close_btn.setObjectName("CloseButton")
        close_btn.setFixedSize(32, 32)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close)

        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.logout_btn)
        layout.addWidget(LangSwitch())
        layout.addWidget(close_btn)
        return self.title_bar

    def _retranslate_title_bar(self):
        self.logout_btn.setText(self.lang.tr("logout_btn"))

    def _logout(self):
        reply = QMessageBox.question(
            self,
            self.lang.tr("logout_confirm_title"),
            self.lang.tr("logout_confirm_text"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        from core.content import seed
        seed()  # чистит attempts/progress/tasks/topics/subjects/users и пересевает демо-данные + DEMO_USER_ID заново

        self.settings.reset()             # роль, предметы, онбординг, язык
        self.current_role = None
        self.selected_subjects = []

        if hasattr(self, "app_widget"):
            self.root_stack.removeWidget(self.app_widget)
            self.app_widget.deleteLater()
            del self.app_widget

        self._start_onboarding()          # обратно на RoleSelectPage

    def eventFilter(self, obj, event):
        if obj == self.title_bar:
            if event.type() == event.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self._drag_pos = event.globalPosition().toPoint() - self.pos()
                return True
            elif event.type() == event.Type.MouseMove and self._drag_pos is not None:
                self.move(event.globalPosition().toPoint() - self._drag_pos)
                return True
            elif event.type() == event.Type.MouseButtonRelease:
                self._drag_pos = None
                return True
        return super().eventFilter(obj, event)

    # ---------- Онбординг (без изменений) ----------
    def _start_onboarding(self):
        self.role_page = RoleSelectPage()
        self.role_page.role_selected.connect(self._on_role_selected)
        self.root_stack.addWidget(self.role_page)
        self.root_stack.setCurrentWidget(self.role_page)

    def _on_role_selected(self, role: str):
        self.current_role = role
        self.settings.set_role(role)
        if role == "student":
            self.subjects_page = SubjectPreferencePage()
            self.subjects_page.finished.connect(self._on_subjects_selected)
            self.root_stack.addWidget(self.subjects_page)
            self.root_stack.setCurrentWidget(self.subjects_page)
        else:
            self._finish_onboarding()

    def _on_subjects_selected(self, subjects: list):
        self.selected_subjects = subjects
        self.settings.set_subjects(subjects)
        self._finish_onboarding()

    def _finish_onboarding(self):
        self.settings.set_onboarding_done(True)
        self._enter_main_app()

    def _enter_main_app(self):
        self.app_widget = self._build_main_app()
        self.root_stack.addWidget(self.app_widget)
        self.root_stack.setCurrentWidget(self.app_widget)

    def _build_main_app(self) -> QWidget:
        from main_app import MainAppWidget
        return MainAppWidget(role=self.current_role)
    