"""
ui/math_render.py

Renders a solution_steps string (as stored by core/content.py — plain
Cyrillic text with math wrapped in $...$) into a QPixmap for display in
a QLabel. Uses matplotlib's mathtext engine, which understands LaTeX
syntax (\\frac, ^, _, \\pm, \\sqrt, \\cdot, \\Rightarrow, etc.) WITHOUT
needing a real LaTeX/TeXLive installation — matplotlib ships this itself,
so it packages cleanly with PyInstaller.

Usage in a task/lesson screen:

    from ui.math_render import render_step_pixmap

    for i, step in enumerate(task["solution_steps"], start=1):
        label = QLabel()
        label.setPixmap(render_step_pixmap(step))
        layout.addWidget(QLabel(f"Шаг {i}:"))
        layout.addWidget(label)

If a step has no $...$ math (e.g. some law-subject steps), this still
works fine — matplotlib just renders it as plain text.
"""
import matplotlib
matplotlib.use("Agg")  # no GUI backend needed; we only rasterize to a buffer
import matplotlib.pyplot as plt
import re
from io import BytesIO

from PyQt6.QtGui import QPixmap


_MATH_TOKEN_RE = re.compile(r"\$[^$]+\$")

def _wrap_step_text(step_text: str, wrap_chars: int = 42) -> str:
    """Переносит текст по ~wrap_chars символов, не разрывая $...$-блоки."""
    tokens, pos = [], 0
    for m in _MATH_TOKEN_RE.finditer(step_text):
        if m.start() > pos:
            tokens.extend(step_text[pos:m.start()].split())
        tokens.append(m.group(0))
        pos = m.end()
    if pos < len(step_text):
        tokens.extend(step_text[pos:].split())

    lines, current = [], ""
    for tok in tokens:
        candidate = f"{current} {tok}".strip()
        if current and len(candidate) > wrap_chars:
            lines.append(current)
            current = tok
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)


def render_step_pixmap(step_text: str,
                       fontsize: int = 16,
                       dpi: int = 200,
                       wrap_chars: int = 42) -> QPixmap:
    """
    Rasterizes one solution step (mixed plain text + $...$ LaTeX math) into
    a transparent-background QPixmap sized to fit its content.
    """
    wrapped = _wrap_step_text(step_text, wrap_chars=wrap_chars)
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.patch.set_alpha(0.0)
    fig.text(0, 0, wrapped, fontsize=fontsize, linespacing=1.4)

    buf = BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=dpi,
        transparent=True,
        bbox_inches="tight",
        pad_inches=0.08,
    )
    plt.close(fig)
    buf.seek(0)

    pixmap = QPixmap()
    pixmap.loadFromData(buf.read(), "PNG")
    return pixmap
