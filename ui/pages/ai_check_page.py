import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QMovie
from core.repository import Repository
from core.config import DEMO_USER_ID
from ai_check_thread import SolutionCheckThread
from localization.manager import LanguageManager
from widgets.icon_utils import emotion_pixmap, ICONS_DIR

PRELOADER_GIF = os.path.join(os.path.dirname(ICONS_DIR), "preloader.gif")

MISTAKE_KEYS = {
    "calculation": "mistake_calculation", "formula": "mistake_formula",
    "concept": "mistake_concept", "formatting": "mistake_formatting",
}


class AICheckPage(QWidget):
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)
        self.task = None
        self.image_path = None
        self.thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(16)
        header = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setObjectName("BackButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn)
        header.addStretch()
        layout.addLayout(header)

        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)
        self.okto_label = QLabel()
        self.okto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.okto_label.setToolTip("Окто")
        layout.addWidget(self.okto_label)
        self.preview_label = QLabel()
        self.preview_label.setObjectName("PhotoPreview")
        self.preview_label.setFixedHeight(240)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)
        self.upload_btn = QPushButton()
        self.upload_btn.setObjectName("PrimaryButton")
        self.upload_btn.clicked.connect(self._choose_photo)
        layout.addWidget(self.upload_btn)

        self.preloader_label = QLabel()
        self.preloader_label.setObjectName("AIPreloader")
        self.preloader_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preloader_movie = None
        if os.path.exists(PRELOADER_GIF):
            self.preloader_movie = QMovie(PRELOADER_GIF)
            self.preloader_movie.setScaledSize(QSize(64, 64))
            self.preloader_label.setMovie(self.preloader_movie)
        self.preloader_label.hide()
        layout.addWidget(self.preloader_label)

        # Резервный вариант, если preloader.gif не нашёлся или не открылся
        # (например, файл повреждён в сборке) — виден пользователю прогресс,
        # а не пустой экран.
        self.progress = QProgressBar()
        self.progress.setObjectName("AIPreload")
        self.progress.setRange(0, 0)
        self.progress.setTextVisible(False)
        self.progress.hide()
        layout.addWidget(self.progress)
        self.status_label = QLabel()
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        self.result_frame = QFrame()
        self.result_layout = QVBoxLayout(self.result_frame)
        self.result_frame.hide()
        layout.addWidget(self.result_frame)
        layout.addStretch()
        self._set_emotion("happy")
        self.retranslate_ui()

    def _set_emotion(self, emotion: str):
        self.okto_label.setPixmap(emotion_pixmap(emotion, 82))

    def retranslate_ui(self):
        if self.task is not None:
            self.task["language"] = self.lang.current_lang
        self.back_btn.setText(self.lang.tr("back_short"))
        self.title.setText(self.lang.tr("ai_check_title"))
        if not self.image_path:
            self.preview_label.setText(self.lang.tr("ai_no_photo"))
        self.upload_btn.setText(self.lang.tr("ai_upload_btn"))

    def load_task(self, task: dict):
        self.task, self.image_path = dict(task), None
        self.task["language"] = self.lang.current_lang
        self._set_emotion("happy")
        self._hide_preloader()
        self.preview_label.clear()
        self.preview_label.setText(self.lang.tr("ai_no_photo"))
        self.status_label.clear()
        self._clear_result()

    def _choose_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, self.lang.tr("ai_upload_btn"), "", "Images (*.png *.jpg *.jpeg)")
        if not path:
            return
        self.image_path = path
        pixmap = QPixmap(path)
        self.preview_label.setPixmap(pixmap.scaledToHeight(220, Qt.TransformationMode.SmoothTransformation))
        self._run_check()

    def _run_check(self):
        if not self.task or not self.image_path:
            return
        self.upload_btn.setEnabled(False)
        self._set_emotion("thinking")
        self._show_preloader()
        self.status_label.setText(self.lang.tr("ai_analyzing"))
        self._clear_result()
        self.thread = SolutionCheckThread(self.image_path, self.task)
        self.thread.succeeded.connect(self._on_success)
        self.thread.failed.connect(self._on_failure)
        self.thread.finished.connect(self._analysis_finished)
        self.thread.start()

    def _show_preloader(self):
        if self.preloader_movie is not None:
            self.preloader_label.show()
            self.preloader_movie.start()
        else:
            self.progress.show()

    def _hide_preloader(self):
        if self.preloader_movie is not None:
            self.preloader_movie.stop()
            self.preloader_label.hide()
        self.progress.hide()

    def _analysis_finished(self):
        self._hide_preloader()
        self.upload_btn.setEnabled(True)

    def _on_success(self, result: dict):
        self.status_label.clear()
        if not result["readable"]:
            self._set_emotion("surprised")
            self.status_label.setText(self.lang.tr("ai_unreadable"))
            return
        self._set_emotion("happy" if result["correct"] else "frustrated")
        self.repo.save_result(DEMO_USER_ID, self.task["id"], {
            "correct": result["correct"], "score": result["score"], "mistake_type": result["main_mistake_type"],
        })
        verdict_key = "ai_verdict_correct" if result["correct"] else "ai_verdict_issues"
        verdict_label = QLabel(f"{self.lang.tr(verdict_key)}   —   {result['score']}%")
        verdict_label.setObjectName("ResultVerdict")
        verdict_label.setProperty("status", "correct" if result["correct"] else "warning")
        verdict_label.style().unpolish(verdict_label); verdict_label.style().polish(verdict_label)
        self.result_layout.addWidget(verdict_label)
        for err in result["errors"]:
            label_text = self.lang.tr(MISTAKE_KEYS.get(err["mistake_type"], "mistake_concept"))
            err_label = QLabel(f"⚠ {label_text}: {err['explanation']}")
            err_label.setWordWrap(True)
            self.result_layout.addWidget(err_label)
        self.result_frame.show()

    def _on_failure(self, reason: str):
        self._set_emotion("frustrated")
        self.status_label.setText(f"{self.lang.tr('ai_failed')}\n{self.lang.tr('ai_error_reason', reason=reason)}")

    def _clear_result(self):
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.result_frame.hide()
