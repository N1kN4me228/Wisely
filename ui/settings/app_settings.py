from PyQt6.QtCore import QSettings


class AppSettings:
    def __init__(self):
        self.qs = QSettings("Wisely", "WiselyApp")

    def get_language(self) -> str | None:
        return self.qs.value("language", None)

    def set_language(self, lang: str):
        self.qs.setValue("language", lang)

    def get_role(self) -> str | None:
        return self.qs.value("role", None)

    def set_role(self, role: str):
        self.qs.setValue("role", role)

    def get_subjects(self) -> list[str]:
        value = self.qs.value("preferred_subjects", [])
        return value if isinstance(value, list) else []

    def set_subjects(self, subjects: list[str]):
        self.qs.setValue("preferred_subjects", subjects)

    def is_onboarding_done(self) -> bool:
        return self.qs.value("onboarding_done", False, type=bool)

    def set_onboarding_done(self, value: bool = True):
        self.qs.setValue("onboarding_done", value)

    def reset(self):
        self.qs.clear()
