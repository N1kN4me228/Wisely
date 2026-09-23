import re


SUBSCRIPT_DIGITS = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def format_answer_display(raw: str) -> str:
    """
    "x1=2;x2=3"  ->  "x₁ = 2, x₂ = 3"
    "16"         ->  "16"              (без изменений)
    "правонарушение" -> "правонарушение" (текстовые предметы — как есть)
    """
    if "=" not in raw:
        return raw

    parts = [p.strip() for p in raw.split(";") if p.strip()]
    formatted = []
    for part in parts:
        m = re.match(r"^([a-zA-Zа-яА-Я]+)(\d+)=(.+)$", part)
        if m:
            name, idx, value = m.groups()
            formatted.append(f"{name}{idx.translate(SUBSCRIPT_DIGITS)} = {value}")
        else:
            formatted.append(part)
    return ", ".join(formatted)
