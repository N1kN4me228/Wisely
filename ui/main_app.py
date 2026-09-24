from PyQt6.QtCore import QEasingCurve, QPropertyAnimation
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget, QHBoxLayout, QStackedWidget
from widgets.sidebar import Sidebar
from pages.dashboard_page import DashboardPage
from pages.subjects_page import SubjectsPage
from pages.homework_page import HomeworkPage
from pages.progress_page import ProgressPage
from pages.topics_list_page import TopicsListPage
from pages.task_page import TaskPage
from pages.ai_check_page import AICheckPage
from pages.teacher_home_page import TeacherHomePage


class MainAppWidget(QWidget):
    def __init__(self, role: str = "student"):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if role == "teacher":
            from pages.teacher_home_page import TeacherHomePage
            layout.addWidget(TeacherHomePage())
            return

        self.sidebar = Sidebar()
        self.content_stack = QStackedWidget()
        self._page_opacity = QGraphicsOpacityEffect(self.content_stack)
        self.content_stack.setGraphicsEffect(self._page_opacity)
        self._page_fade = QPropertyAnimation(self._page_opacity, b"opacity", self)
        self._page_fade.setDuration(220)
        self._page_fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.dashboard_page = DashboardPage()
        self.subjects_page = SubjectsPage()
        self.homework_page = HomeworkPage()
        self.progress_page = ProgressPage()
        self.topics_list_page = TopicsListPage()
        self.task_page = TaskPage()
        self.ai_check_page = AICheckPage()

        for page in (self.dashboard_page, self.subjects_page, self.homework_page,
                     self.progress_page, self.topics_list_page, self.task_page,
                     self.ai_check_page):
            self.content_stack.addWidget(page)

        self.task_page.ai_check_requested.connect(self._open_ai_check)
        self.homework_page.topic_requested.connect(self._open_tasks)
        self.ai_check_page.back_requested.connect(
            lambda: self._show_page(self.task_page)
        )

        self.sidebar.page_selected.connect(self._on_sidebar_selected)
        self.subjects_page.subject_opened.connect(self._open_topics)
        self.topics_list_page.topic_opened.connect(self._open_tasks)
        self.topics_list_page.back_requested.connect(
            lambda: self._show_page(self.subjects_page)
        )
        self.task_page.back_requested.connect(
            lambda: self._show_page(self.topics_list_page)
        )

        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_stack)
        self._show_page(self.dashboard_page, animate=False)

    def _show_page(self, page, animate=True):
        self.content_stack.setCurrentWidget(page)
        if not animate:
            self._page_opacity.setOpacity(1.0)
            return
        self._page_fade.stop()
        self._page_fade.setStartValue(0.55)
        self._page_fade.setEndValue(1.0)
        self._page_fade.start()

    def _on_sidebar_selected(self, index: int):
        pages = [self.dashboard_page, self.subjects_page, self.homework_page, self.progress_page]
        self._show_page(pages[index])

    def _open_topics(self, subject_id: int, subject_name: str):
        self.topics_list_page.load_subject(subject_id, subject_name)
        self._show_page(self.topics_list_page)

    def _open_tasks(self, topic_id: int, topic_name: str):
        self.task_page.load_topic(topic_id, topic_name)
        self._show_page(self.task_page)

    def _open_ai_check(self, task: dict):
        self.ai_check_page.load_task(task)
        self._show_page(self.ai_check_page)
