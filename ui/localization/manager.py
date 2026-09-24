from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QFontMetrics
from localization.translations import TRANSLATIONS


class LanguageManager(QObject):
    language_changed = pyqtSignal(str)
    _instance = None

    def __init__(self):
        super().__init__()
        self.current_lang = "ru"

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = LanguageManager()
        return cls._instance

    def set_language(self, lang: str):
        if lang not in TRANSLATIONS or lang == self.current_lang:
            return
        self.current_lang = lang
        self.language_changed.emit(lang)

    def tr(self, key: str, **kwargs) -> str:
        text = TRANSLATIONS.get(self.current_lang, {}).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def max_text_width(self, key: str, font) -> int:
        metrics = QFontMetrics(font)
        return max(
            metrics.horizontalAdvance(TRANSLATIONS[lang].get(key, ""))
            for lang in TRANSLATIONS
        )
    