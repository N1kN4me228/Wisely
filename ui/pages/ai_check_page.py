from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from core.repository import Repository
from core.config import DEMO_USER_ID
from ai_check_thread import SolutionCheckThread
from localization.manager import LanguageManager

MISTAKE_KEYS = {
    "calculation": "mistake_calculation",
    "formula": "mistake_formula",
    "concept": "mistake_concept",
    "formatting": "mistake_formatting",
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
        self.back_btn = QPushButton("← Назад")
        self.back_btn.setObjectName("BackButton")
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn)
        layout.addLayout(header)

        self.title = QLabel()
        self.title.setObjectName("PageTitle")
        layout.addWidget(self.title)

        self.preview_label = QLabel()
        self.preview_label.setObjectName("PhotoPreview")
        self.preview_label.setFixedHeight(240)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.preview_label)

        self.upload_btn = QPushButton()
        self.upload_btn.setObjectName("PrimaryButton")
        self.upload_btn.clicked.connect(self._choose_photo)
        layout.addWidget(self.upload_btn)

        self.status_label = QLabel()
        layout.addWidget(self.status_label)

        self.result_frame = QFrame()
        self.result_layout = QVBoxLayout(self.result_frame)
        self.result_frame.hide()
        layout.addWidget(self.result_frame)

        layout.addStretch()
        self.retranslate_ui()

    def retranslate_ui(self):
        self.title.setText(self.lang.tr("ai_check_title"))
        if not self.image_path:
            self.preview_label.setText(self.lang.tr("ai_no_photo"))
        self.upload_btn.setText(self.lang.tr("ai_upload_btn"))

    def load_task(self, task: dict):
        self.task = task
        self.image_path = None
        self.preview_label.setText(self.lang.tr("ai_no_photo"))
        self.status_label.setText("")
        self._clear_result()

    def _choose_photo(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.lang.tr("ai_upload_btn"), "", "Images (*.png *.jpg *.jpeg)"
        )
        if not path:
            return
        self.image_path = path
        self.preview_label.setPixmap(
            QPixmap(path).scaledToHeight(220, Qt.TransformationMode.SmoothTransformation)
        )
        self._run_check()

    def _run_check(self):
        if not self.task or not self.image_path:
            return
        self.upload_btn.setEnabled(False)
        self.status_label.setText(self.lang.tr("ai_analyzing"))
        self._clear_result()

        self.thread = SolutionCheckThread(self.image_path, self.task)
        self.thread.succeeded.connect(self._on_success)
        self.thread.failed.connect(self._on_failure)
        self.thread.finished.connect(lambda: self.upload_btn.setEnabled(True))
        self.thread.start()

    def _on_success(self, result: dict):
        self.status_label.setText("")

        if not result["readable"]:
            self.status_label.setText(self.lang.tr("ai_unreadable"))
            return

        self.repo.save_result(DEMO_USER_ID, self.task["id"], {
            "correct": result["correct"],
            "score": result["score"],
            "mistake_type": result["main_mistake_type"],
        })

        verdict_key = "ai_verdict_correct" if result["correct"] else "ai_verdict_issues"
        verdict_label = QLabel(f"{self.lang.tr(verdict_key)}   —   {result['score']}%")
        verdict_label.setObjectName("ResultVerdict")
        verdict_label.setProperty("status", "correct" if result["correct"] else "warning")
        verdict_label.style().unpolish(verdict_label)
        verdict_label.style().polish(verdict_label)
        self.result_layout.addWidget(verdict_label)

        for err in result["errors"]:
            label_text = self.lang.tr(MISTAKE_KEYS.get(err["mistake_type"], "mistake_concept"))
            err_label = QLabel(f"⚠ {label_text}: {err['explanation']}")
            err_label.setWordWrap(True)
            self.result_layout.addWidget(err_label)

        self.result_frame.show()

    def _on_failure(self, message: str):
        self.status_label.setText(self.lang.tr("ai_failed"))
        print(f"AIError: {message}")

    def _clear_result(self):
        while self.result_layout.count():
            item = self.result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.result_frame.hide()
        