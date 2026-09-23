from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class HomeworkPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Homework — TODO"))
