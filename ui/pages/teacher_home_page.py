from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class TeacherHomePage(QWidget):
    """
    Учительский режим — TODO.
    Здесь будет отдельное меню (ученики, проверка ДЗ, статистика класса),
    не связанное с ученическим Sidebar/Dashboard/Subjects/Homework/Progress.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title = QLabel("Учительский режим")
        title.setObjectName("PageTitle")
        todo = QLabel("TODO: меню и разделы для учителя")
        layout.addWidget(title)
        layout.addWidget(todo)
        