r"""
ui/math_render.py

Renders a solution_steps string (as stored by core/content.py — plain
Cyrillic text with math wrapped in $...$) into a QPixmap for display in
a QLabel. Uses matplotlib's mathtext engine, which understands LaTeX
syntax (\frac, ^, _, \pm, \sqrt, \cdot, \Rightarrow, etc.) WITHOUT
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

NOTE on a bug that used to live here: a step that mixes plain text and
$...$ math (e.g. "Подставьте в первое: $(2+y)+2y=8...$") wraps onto more
than one line. The old version passed the whole wrapped string to a
single `fig.text(...)` call as one multi-line Text artist. Matplotlib's
mathtext parser computes line height differently for a mathtext line
than for a plain-text line, and mixing both inside one Text artist means
its internal `linespacing` doesn't account for that difference — the
result is lines that visually overlap (see the "Шаг 2" screenshot). The
fix below renders each wrapped line as its OWN Text artist, stacked using
an explicit line height we control, so mathtext and plain-text lines
never share (and fight over) the same spacing metric.
"""
import matplotlib
matplotlib.use("Agg")  # no GUI backend needed; we only rasterize to a buffer
import matplotlib.pyplot as plt
import re
from io import BytesIO

from PyQt6.QtGui import QPixmap


_MATH_TOKEN_RE = re.compile(r"\$[^$]+\$")


def _wrap_step_lines(step_text: str, wrap_chars: int = 42) -> list[str]:
    """Разбивает текст на строки по ~wrap_chars символов, не разрывая $...$-блоки."""
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
    return lines or [""]


def render_step_pixmap(step_text: str,
                       fontsize: int = 16,
                       dpi: int = 200,
                       wrap_chars: int = 42) -> QPixmap:
    """
    Rasterizes one solution step (mixed plain text + $...$ LaTeX math) into
    a transparent-background QPixmap sized to fit its content.

    Each wrapped line is its own Text artist, stacked top-to-bottom with a
    fixed line height (1.6x fontsize, in points) instead of relying on a
    single multiline Text object — see the module docstring for why.
    """
    lines = _wrap_step_lines(step_text, wrap_chars=wrap_chars)

    line_height_in = (fontsize * 1.6) / 72.0  # points -> inches
    fig_w_in = max(1.0, (max(len(l) for l in lines) * fontsize * 0.62) / 72.0 + 0.3)
    fig_h_in = line_height_in * len(lines) + 0.15
    fig = plt.figure(figsize=(fig_w_in, fig_h_in))
    fig.patch.set_alpha(0.0)

    top_in = fig_h_in
    for i, line in enumerate(lines):
        y_in = top_in - (i + 1) * line_height_in
        fig.text(0.02, y_in / fig_h_in, line,
                  fontsize=fontsize, linespacing=1.0,
                  va="top", ha="left", transform=fig.transFigure)

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
