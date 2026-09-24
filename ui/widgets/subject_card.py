from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal
from widgets.icon_utils import subject_icon_pixmap


class SubjectCard(QFrame):
    clicked = pyqtSignal(int)  # subject_id

    def __init__(self, subject_id: int, name: str, progress: int):
        super().__init__()
        self.subject_id = subject_id
        self.setObjectName("SubjectCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(220, 140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(8)

        title_row = QHBoxLayout()
        icon = QLabel()
        icon.setPixmap(subject_icon_pixmap(name, 34))
        name_label = QLabel(name)
        name_label.setObjectName("SubjectCardName")
        name_label.setWordWrap(True)
        title_row.addWidget(icon)
        title_row.addWidget(name_label, 1)

        bar = QProgressBar()
        bar.setObjectName("SubjectCardProgress")
        bar.setValue(progress)
        bar.setTextVisible(True)
        bar.setFormat(f"{progress}%")

        layout.addLayout(title_row)
        layout.addStretch()
        layout.addWidget(bar)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.subject_id)
        super().mousePressEvent(event)
        
