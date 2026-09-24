"""Localized labels for seeded learning content.

The source database remains Russian so answer checking and the AI prompt keep a
stable canonical form. Only presentation labels are translated here.
"""

CONTENT_KZ = {
    "Алгебра": "Algebra",
    "Основы права": "Qūqyq negızderı",
    "Квадратные уравнения": "Kvadrattyq teñdeuler",
    "Системы уравнений": "Teñdeuler jüiesı",
    "Правонарушения": "Qūqyq būzuşylyqtar",
    "Решение квадратных уравнений через дискриминант": "Kvadrattyq teñdeulerdi diskriminant arqyly şeşu",
    "Системы линейных уравнений с двумя переменными": "Eki aynymaly sızıqty teñdeuler jüiesı",
    "Понятие, виды и признаки правонарушений": "Qūqyq būzuşylyqtyñ ūğymy, türlerı jäne belgılerı",
}


def localize_content(value: str | None, language: str) -> str:
    if not value or language != "kz":
        return value or ""
    return CONTENT_KZ.get(value, value)
