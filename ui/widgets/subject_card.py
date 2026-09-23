from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal


class SubjectCard(QFrame):
    clicked = pyqtSignal(int)  # subject_id

    def __init__(self, subject_id: int, name: str, progress: int):
        super().__init__()
        self.subject_id = subject_id
        self.setObjectName("SubjectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(220, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        name_label = QLabel(name)
        name_label.setObjectName("SubjectCardName")

        bar = QProgressBar()
        bar.setObjectName("SubjectCardProgress")
        bar.setValue(progress)
        bar.setTextVisible(True)
        bar.setFormat(f"{progress}%")

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(bar)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.subject_id)
        super().mousePressEvent(event)
        