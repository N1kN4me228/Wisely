from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.repository import Repository
from core.config import DEMO_USER_ID
from ai_engine import check_answer
from math_render import render_step_pixmap
from styles.fonts import FORMULA_FONT
from localization.manager import LanguageManager
from answer_format import format_answer_display
from widgets.icon_utils import emotion_pixmap


class TaskPage(QWidget):
    back_requested = pyqtSignal()
    ai_check_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.repo = Repository()
        self.lang = LanguageManager.instance()
        self.lang.language_changed.connect(self.retranslate_ui)
        self.tasks = []
        self.current_index = 0

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 32)
        layout.setSpacing(16)

        header = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setObjectName("BackButton")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(self.back_btn)
        header.addStretch()
        self.progress_label = QLabel()
        self.progress_label.setObjectName("TaskProgressLabel")
        header.addWidget(self.progress_label)
        layout.addLayout(header)

        self.topic_title = QLabel()
        self.topic_title.setObjectName("PageTitle")
        layout.addWidget(self.topic_title)
        self.okto_label = QLabel()
        self.okto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.okto_label.setToolTip("Окто")
        layout.addWidget(self.okto_label)

        self.question_label = QLabel()
        self.question_label.setObjectName("TaskQuestion")
        self.question_label.setFont(FORMULA_FONT)
        self.question_label.setWordWrap(True)
        layout.addWidget(self.question_label)

        self.answer_input = QLineEdit()
        self.answer_input.setObjectName("AnswerInput")
        self.answer_input.returnPressed.connect(self._check_answer)
        layout.addWidget(self.answer_input)

        self.check_btn = QPushButton()
        self.check_btn.setObjectName("PrimaryButton")
        self.check_btn.clicked.connect(self._check_answer)
        layout.addWidget(self.check_btn)

        self.ai_check_btn = QPushButton()
        self.ai_check_btn.setObjectName("PrimaryButton")
        self.ai_check_btn.clicked.connect(self._request_ai_check)
        layout.addWidget(self.ai_check_btn)

        self.feedback_label = QLabel()
        self.feedback_label.setWordWrap(True)
        layout.addWidget(self.feedback_label)

        self.solution_frame = QFrame()
        self.solution_layout = QVBoxLayout(self.solution_frame)
        self.solution_frame.hide()
        layout.addWidget(self.solution_frame)

        self.next_btn = QPushButton()
        self.next_btn.setObjectName("PrimaryButton")
        self.next_btn.clicked.connect(self._next_task)
        self.next_btn.hide()
        layout.addWidget(self.next_btn)

        layout.addStretch()
        self._set_emotion("reading")
        self.retranslate_ui()

    def _set_emotion(self, emotion: str):
        self.okto_label.setPixmap(emotion_pixmap(emotion, 72))

    def _request_ai_check(self):
        if self.tasks:
            self.ai_check_requested.emit(self.tasks[self.current_index])

    def load_topic(self, topic_id: int, topic_name: str):
        self.tasks = self.repo.get_tasks(topic_id=topic_id, kind="practice")
        self.current_index = 0
        self.topic_title.setText(topic_name)
        self._show_current_task()

    def _show_current_task(self):
        self.feedback_label.setText("")
        self.answer_input.clear()
        self.answer_input.show()
        self.check_btn.show()
        self.next_btn.hide()
        self._clear_solution()

        if not self.tasks:
            self.question_label.setText(self.lang.tr("topics_empty"))
            return

        task = self.tasks[self.current_index]
        self.progress_label.setText(f"{self.current_index + 1} / {len(self.tasks)}")
        self.question_label.setText(task["question"])

    def _check_answer(self):
        if not self.tasks:
            return
        task = self.tasks[self.current_index]
        result = check_answer(task, self.answer_input.text())

        # ai_engine не знает про mistake_type для текстовых ответов —
        # это нормально, save_result() принимает mistake_type=None
        self.repo.save_result(DEMO_USER_ID, task["id"], {
            "correct": result["correct"],
            "score": result["score"],
            "answer_given": self.answer_input.text(),
        })

        if result["correct"]:
            self._set_emotion("happy")
            self.feedback_label.setText("✓ " + self.lang.tr("task_correct"))
        else:
            self._set_emotion("frustrated")
            hint = task.get("explanation") or ""
            self.feedback_label.setText(f"✗ {self.lang.tr('task_incorrect')}. {hint}")

        self._show_solution(task)
        self.answer_input.hide()
        self.check_btn.hide()
        self.next_btn.show()

    def _clear_solution(self):
        while self.solution_layout.count():
            item = self.solution_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.solution_frame.hide()

    def _next_task(self):
        if self.current_index + 1 < len(self.tasks):
            self.current_index += 1
            self._show_current_task()
        else:
            self.back_requested.emit()

    def retranslate_ui(self):
        self.back_btn.setText(self.lang.tr("back_short"))
        self.check_btn.setText(self.lang.tr("task_check"))
        self.ai_check_btn.setText(self.lang.tr("task_check_photo"))
        self.next_btn.setText(self.lang.tr("task_next"))
        self.answer_input.setPlaceholderText(self.lang.tr("task_placeholder"))

    def _show_solution(self, task):
        self._clear_solution()

        answer_label = QLabel(f"{self.lang.tr('correct_answer_label')}: {format_answer_display(task['answer'])}")
        answer_label.setObjectName("CorrectAnswer")
        self.solution_layout.addWidget(answer_label)

        for i, step in enumerate(task.get("solution_steps") or [], start=1):
            step_label = QLabel(f"{self.lang.tr('step_label')} {i}:")
            pixmap_label = QLabel()
            pixmap = render_step_pixmap(step)

            if pixmap.width() > 640:
                pixmap = pixmap.scaledToWidth(640, Qt.TransformationMode.SmoothTransformation)

            pixmap_label.setPixmap(pixmap)
            self.solution_layout.addWidget(step_label)
            self.solution_layout.addWidget(pixmap_label)
        self.solution_frame.show()
        
