"""
core/content.py

Demo content, matching this exact structure:

    9 класс
     └── Алгебра
          ├── Квадратные уравнения
          │    ├── 5 заданий
          │    └── 1 диагностический тест
          └── Системы уравнений
               └── 5 заданий
    10 класс
     └── Основы права
          └── Правонарушения
               └── 5 заданий

Run:  python -m core.content
Idempotent — wipes and re-inserts every time.
"""
import json

from core.database import init_db, get_connection
from core.config import DEMO_USER_ID


def seed():
    init_db()
    conn = get_connection()

    for table in ("attempts", "progress", "tasks", "topics", "subjects", "users"):
        conn.execute(f"DELETE FROM {table}")
        # DELETE alone doesn't reset AUTOINCREMENT — sqlite keeps the high
        # watermark in sqlite_sequence, so ids would climb on every reseed
        # (id=1, then 2, then 3...) and silently break DEMO_USER_ID=1.
        conn.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))

    # ---------- subjects ----------
    algebra_id = conn.execute(
        "INSERT INTO subjects (name) VALUES ('Алгебра')"
    ).lastrowid
    law_id = conn.execute(
        "INSERT INTO subjects (name) VALUES ('Основы права')"
    ).lastrowid

    # ---------- topics ----------
    quad_id = conn.execute(
        """INSERT INTO topics (subject_id, class_number, name, description, order_index)
           VALUES (?, 9, 'Квадратные уравнения', 'Решение квадратных уравнений через дискриминант', 1)""",
        (algebra_id,),
    ).lastrowid

    systems_id = conn.execute(
        """INSERT INTO topics (subject_id, class_number, name, description, order_index)
           VALUES (?, 9, 'Системы уравнений', 'Системы линейных уравнений с двумя переменными', 2)""",
        (algebra_id,),
    ).lastrowid

    law_topic_id = conn.execute(
        """INSERT INTO topics (subject_id, class_number, name, description, order_index)
           VALUES (?, 10, 'Правонарушения', 'Понятие, виды и признаки правонарушений', 1)""",
        (law_id,),
    ).lastrowid

    # ---------- Квадратные уравнения: 5 заданий (kind='practice') ----------
    # `solution_steps`: math is wrapped in $...$ (LaTeX syntax: \frac, ^, _,
    # \pm, \sqrt, \cdot) so it renders with proper fraction bars, exponents
    # and sign placement via matplotlib mathtext — not unicode-in-a-row.
    # Plain Cyrillic outside $...$ renders as normal text in the same line.
    # `explanation` stays a short plain-text one-liner for the wrong-answer hint.
    quad_practice = [
        ("x² - 5x + 6 = 0", "x1=2;x2=3", 1, "D=25-24=1, x=(5±1)/2",
         [r"$D = b^2 - 4ac = (-5)^2 - 4\cdot1\cdot6 = 1$",
          r"$x = \frac{5 \pm \sqrt{1}}{2} = \frac{5 \pm 1}{2}$",
          r"$x_1 = 3,\ \ x_2 = 2$"]),
        ("x² - 4 = 0", "x1=-2;x2=2", 1, "x²=4, значит x=±2",
         [r"$x^2 = 4$",
          r"$x_{1,2} = \pm\sqrt{4}$",
          r"$x_1 = -2,\ \ x_2 = 2$"]),
        ("x² + 2x - 3 = 0", "x1=-3;x2=1", 2, "D=4+12=16, x=(-2±4)/2",
         [r"$D = b^2 - 4ac = 2^2 - 4\cdot1\cdot(-3) = 4 + 12 = 16$",
          r"$x = \frac{-2 \pm \sqrt{16}}{2} = \frac{-2 \pm 4}{2}$",
          r"$x_1 = -3,\ \ x_2 = 1$"]),
        ("x² - 7x + 10 = 0", "x1=2;x2=5", 2, "D=49-40=9, x=(7±3)/2",
         [r"$D = (-7)^2 - 4\cdot1\cdot10 = 49 - 40 = 9$",
          r"$x = \frac{7 \pm \sqrt{9}}{2} = \frac{7 \pm 3}{2}$",
          r"$x_1 = 2,\ \ x_2 = 5$"]),
        ("x² + 4x = 0", "x1=-4;x2=0", 2, "x(x+4)=0, значит x=0 или x=-4",
         [r"$x(x+4)=0$",
          r"x = 0 или $x+4=0$",
          r"$x_1 = 0,\ \ x_2 = -4$"]),
    ]
    for i, (q, a, diff, expl, steps) in enumerate(quad_practice, start=1):
        conn.execute(
            """INSERT INTO tasks (topic_id, question, type, kind, answer, difficulty, explanation, solution_steps, order_index)
               VALUES (?, ?, 'text', 'practice', ?, ?, ?, ?, ?)""",
            (quad_id, f"Решите уравнение: {q}", a, diff, expl, json.dumps(steps, ensure_ascii=False), i),
        )

    # ---------- Квадратные уравнения: 1 диагностический тест (5 вопросов, kind='diagnostic') ----------
    # Separate from the 5 practice tasks: this is the one-time placement
    # test, not part of the ongoing progress score (see core/progress.py).
    quad_diagnostic = [
        ("x² - 9 = 0", "x1=-3;x2=3", 1, "x²=9, значит x=±3",
         [r"$x^2 = 9$", r"$x_1 = -3,\ \ x_2 = 3$"]),
        ("x² + 6x + 9 = 0", "x=-3", 2, "D=0, (x+3)²=0, корень один: x=-3",
         [r"$D = 6^2 - 4\cdot1\cdot9 = 36 - 36 = 0$",
          r"$(x + 3)^2 = 0$",
          r"$x = -3$ (единственный корень)"]),
        ("x² - x - 6 = 0", "x1=-2;x2=3", 2, "D=1+24=25, x=(1±5)/2",
         [r"$D = (-1)^2 - 4\cdot1\cdot(-6) = 1 + 24 = 25$",
          r"$x = \frac{1 \pm \sqrt{25}}{2} = \frac{1 \pm 5}{2}$",
          r"$x_1 = -2,\ \ x_2 = 3$"]),
        ("3x² - 12 = 0", "x1=-2;x2=2", 1, "x²=4, значит x=±2",
         [r"Разделите обе части на 3: $x^2 = 4$",
          r"$x_1 = -2,\ \ x_2 = 2$"]),
        ("x² - 3x - 10 = 0", "x1=-2;x2=5", 3, "D=9+40=49, x=(3±7)/2",
         [r"$D = (-3)^2 - 4\cdot1\cdot(-10) = 9 + 40 = 49$",
          r"$x = \frac{3 \pm \sqrt{49}}{2} = \frac{3 \pm 7}{2}$",
          r"$x_1 = -2,\ \ x_2 = 5$"]),
    ]
    for i, (q, a, diff, expl, steps) in enumerate(quad_diagnostic, start=1):
        conn.execute(
            """INSERT INTO tasks (topic_id, question, type, kind, answer, difficulty, explanation, solution_steps, order_index)
               VALUES (?, ?, 'text', 'diagnostic', ?, ?, ?, ?, ?)""",
            (quad_id, f"Решите уравнение: {q}", a, diff, expl, json.dumps(steps, ensure_ascii=False), i),
        )

    # ---------- Системы уравнений: 5 заданий ----------
    systems_practice = [
        ("x+y=5; x-y=1", "x=3;y=2", 1, "Сложите уравнения: 2x=6, x=3, затем y=2",
         [r"Сложите уравнения: $2x = 6$",
          r"$x = 3$",
          r"$y = 5 - 3 = 2$"]),
        ("2x+y=8; x-y=1", "x=3;y=2", 2, "Из второго: y=x-1, подставьте в первое: 3x-1=8",
         [r"Из второго уравнения: $y = x - 1$",
          r"Подставьте в первое: $2x + (x-1) = 8 \Rightarrow 3x = 9$",
          r"$x = 3,\ \ y = 2$"]),
        ("x+2y=8; x-y=2", "x=4;y=2", 2, "Из второго: x=2+y, подставьте: 2+y+2y=8",
         [r"Из второго уравнения: $x = 2 + y$",
          r"Подставьте в первое: $(2+y) + 2y = 8 \Rightarrow 3y = 6$",
          r"$y = 2,\ \ x = 4$"]),
        ("3x+y=10; x+y=4", "x=3;y=1", 2, "Вычтите: 2x=6, x=3, затем y=1",
         [r"Вычтите второе из первого: $(3x+y)-(x+y)=10-4 \Rightarrow 2x=6$",
          r"$x = 3$",
          r"$y = 4 - 3 = 1$"]),
        ("x+y=10; x-y=4", "x=7;y=3", 1, "Сложите уравнения: 2x=14, x=7, затем y=3",
         [r"Сложите уравнения: $2x = 14$",
          r"$x = 7$",
          r"$y = 10 - 7 = 3$"]),
    ]
    for i, (q, a, diff, expl, steps) in enumerate(systems_practice, start=1):
        conn.execute(
            """INSERT INTO tasks (topic_id, question, type, kind, answer, difficulty, explanation, solution_steps, order_index)
               VALUES (?, ?, 'text', 'practice', ?, ?, ?, ?, ?)""",
            (systems_id, f"Решите систему: {q}", a, diff, expl, json.dumps(steps, ensure_ascii=False), i),
        )

    # ---------- Правонарушения: 5 заданий ----------
    # Demo content only — legal wording/answers deserve a review pass by
    # someone who actually teaches this subject before it ships.
    law_practice = [
        ("Как называется противоправное виновное деяние, влекущее юридическую ответственность?", "правонарушение", 1, "Это и есть определение правонарушения",
         ["Вспомните признаки: противоправность, виновность, наказуемость", "Термин, объединяющий эти признаки — правонарушение"]),
        ("Какой вид ответственности наступает за преступления?", "уголовная", 1, "За преступления наступает уголовная ответственность",
         ["Определите вид деяния — преступление", "Ответственность за преступления — уголовная"]),
        ("С какого возраста наступает полная уголовная ответственность по общему правилу?", "16", 2, "Общий возраст уголовной ответственности — 16 лет, по отдельным составам — 14",
         ["Общий возраст наступления уголовной ответственности — 16 лет", "Для отдельных тяжких составов — с 14 лет"]),
        ("Как называется правонарушение, не являющееся преступлением, но запрещённое законом?", "проступок", 1, "Проступки менее опасны, чем преступления",
         ["Такое деяние не является преступлением, но запрещено законом", "Это называется проступком"]),
        ("Какой документ фиксирует факт административного правонарушения?", "протокол", 1, "Составляется протокол об административном правонарушении",
         ["Факт правонарушения фиксируется документально", "Этот документ называется протокол"]),
    ]
    for i, (q, a, diff, expl, steps) in enumerate(law_practice, start=1):
        conn.execute(
            """INSERT INTO tasks (topic_id, question, type, kind, answer, difficulty, explanation, solution_steps, order_index)
               VALUES (?, ?, 'text', 'practice', ?, ?, ?, ?, ?)""",
            (law_topic_id, q, a, diff, expl, json.dumps(steps, ensure_ascii=False), i),
        )

    # ---------- demo user ----------
    # No login screen in the MVP — every UI screen should just import and
    # use core.config.DEMO_USER_ID instead of hardcoding an id. This insert
    # relies on AUTOINCREMENT starting at 1 (guaranteed since the table
    # was just wiped above), but we check it rather than assume it, so a
    # future change to this function can't silently desync from config.py.
    demo_user_id = conn.execute(
        "INSERT INTO users (name, class_number) VALUES ('Руслан', 9)"
    ).lastrowid
    assert demo_user_id == DEMO_USER_ID, (
        f"Seeded user got id={demo_user_id}, but core/config.py DEMO_USER_ID="
        f"{DEMO_USER_ID}. Update config.py to match, or fix the seed order."
    )

    conn.commit()
    conn.close()
    print("Content seeded: 2 subjects, 3 topics, 15 practice + 5 diagnostic tasks.")


if __name__ == "__main__":
    seed()
