import os
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt


ICONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")


def safe_icon(filename: str) -> QIcon:
    path = os.path.join(ICONS_DIR, filename)

    if os.path.exists(path):
        return QIcon(path)
    
    return QIcon()


MASCOT_PATH = os.path.join(ICONS_DIR, "mascot.png")
EMOTIONS_DIR = os.path.join(ICONS_DIR, "emotions")
SUBJECTS_DIR = os.path.join(ICONS_DIR, "subjects")

# One slug per school subject, mapped from every string that can arrive at
# subject_icon_pixmap(): the SUBJECT_KEYS translation key used on the
# onboarding chips (subject_algebra, ...), and every localized display name
# that can come back from core.repository / localization.content.localize_content
# — Russian (DB source of truth) and Kazakh (core/content.py's CONTENT_KZ).
# Unknown subjects (or ones without an icon yet) fall back to the mascot
# rather than showing nothing.
_SUBJECT_SLUGS = {
    # onboarding translation keys
    "subject_algebra": "algebra", "subject_geometry": "geometry", "subject_law": "law",
    "subject_physics": "physics", "subject_chemistry": "chemistry", "subject_biology": "biology",
    # Russian display names
    "Алгебра": "algebra", "Геометрия": "geometry", "Основы права": "law",
    "Физика": "physics", "Химия": "chemistry", "Биология": "biology",
    # Kazakh display names (see core/content.py CONTENT_KZ and
    # ui/localization/translations.py)
    "Algebra": "algebra", "Geometriya": "geometry", "Qūqyq negızderı": "law",
    "Fizika": "physics", "Ximiya": "chemistry", "Biologiya": "biology",
}


def subject_icon_pixmap(identifier: str, size: int = 32) -> QPixmap:
    """Icon for a school subject (algebra, geometry, law, physics, chemistry,
    biology), looked up by translation key or by localized display name.
    Falls back to the Okto mascot for subjects without a dedicated icon yet,
    so a new/unmapped subject still shows *something* next to its name."""
    slug = _SUBJECT_SLUGS.get(identifier or "")
    path = os.path.join(SUBJECTS_DIR, f"{slug}.png") if slug else None
    pixmap = QPixmap(path) if path and os.path.exists(path) else QPixmap()
    if pixmap.isNull():
        return mascot_pixmap(size)
    return pixmap.scaled(
        size,
        size,
        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        transformMode=Qt.TransformationMode.SmoothTransformation,
    )


def subject_icon(identifier: str) -> QIcon:
    """QIcon variant of subject_icon_pixmap(), for setIcon() on buttons."""
    slug = _SUBJECT_SLUGS.get(identifier or "")
    path = os.path.join(SUBJECTS_DIR, f"{slug}.png") if slug else None
    if path and os.path.exists(path):
        return QIcon(path)
    return safe_icon("mascot.png")


def mascot_pixmap(size: int = 44) -> QPixmap:
    pixmap = QPixmap(MASCOT_PATH)
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(
        size,
        size,
        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        transformMode=Qt.TransformationMode.SmoothTransformation,
    )


def emotion_pixmap(emotion: str = "happy", size: int = 64) -> QPixmap:
    """Load one of the reviewed Okto emotion assets with a safe fallback."""
    path = os.path.join(EMOTIONS_DIR, f"{emotion}.png")
    pixmap = QPixmap(path if os.path.exists(path) else MASCOT_PATH)
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(
        size,
        size,
        aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
        transformMode=Qt.TransformationMode.SmoothTransformation,
    )
