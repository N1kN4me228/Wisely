from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, pyqtProperty
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel
from widgets.icon_utils import emotion_pixmap


class MascotWidget(QLabel):
    """Small animated Okto illustration used across the main product screens."""

    def __init__(self, emotion: str = "happy", size: int = 110, parent=None):
        super().__init__(parent)
        self._size = size
        self._rest_y = None
        self.setAlignment(self.alignment().AlignCenter)
        self.setToolTip("Окто")

        self._opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity_effect)
        self._fade = QPropertyAnimation(self._opacity_effect, b"opacity", self)
        self._fade.setDuration(420)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._bob = QPropertyAnimation(self, b"okto_y", self)
        self._bob.setDuration(1800)
        self._bob.setStartValue(0)
        self._bob.setEndValue(-5)
        self._bob.setEasingCurve(QEasingCurve.Type.InOutSine)
        self._bob.setLoopCount(-1)
        self._set_emotion(emotion)

    def _set_emotion(self, emotion: str):
        pixmap = emotion_pixmap(emotion, self._size)
        self.setPixmap(pixmap)
        self.setFixedSize(self._size + 18, self._size + 18)

    def set_emotion(self, emotion: str):
        self._set_emotion(emotion)
        self._fade.stop()
        self._fade.start()

    def showEvent(self, event):
        super().showEvent(event)
        self._rest_y = self.y()
        self._fade.start()
        QTimer.singleShot(430, self._start_bob)

    def _start_bob(self):
        if self.isVisible() and self._bob.state() == QPropertyAnimation.State.Stopped:
            self._bob.start()

    def get_okto_y(self):
        return 0

    def set_okto_y(self, value):
        if self._rest_y is not None:
            self.move(self.x(), self._rest_y + value)

    okto_y = pyqtProperty(int, get_okto_y, set_okto_y)
