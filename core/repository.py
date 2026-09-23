"""
core/repository.py

The ONLY module the UI (programmer #1) and Learning Engine (programmer #3)
should import from core. Returns plain dicts (via model.to_dict()), never
sqlite3.Row or model objects — keeps this easy to mock before the real DB
is wired up.

Public API (as specified):
    get_subjects()
    get_topics(subject_id=None, class_number=None)
    get_tasks(topic_id=None, kind='practice')
    get_task(task_id)
    get_user_progress(user_id)
    save_result(user_id, task_id, result)
    update_progress(user_id, topic_id)

Two additions beyond the original list, both needed to make the above
usable — flagging since they weren't explicitly requested:
    get_diagnostic_tasks(topic_id)  — the "1 диагностический тест" is a
        separate question set from the 5 practice заданий, so it needs
        its own getter rather than being mixed into get_tasks().
    create_user(name, class_number) / get_user(user_id) — save_result()
        and get_user_progress() need a user_id to exist against.
"""
from typing import Optional

from core.database import get_connection
from core.models import Subject, Topic, Task, User
from core import progress as progress_logic


class Repository:

    # ---------- users ----------

    def create_user(self, name: str, class_number: int) -> dict:
        conn = get_connection()
        cur = conn.execute(
            "INSERT INTO users (name, class_number) VALUES (?, ?)",
            (name, class_number),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
        conn.close()
        return User.from_row(row).to_dict()

    def get_user(self, user_id: int) -> Optional[dict]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return User.from_row(row).to_dict() if row else None

    # ---------- subjects ----------

    def get_subjects(self) -> list:
        conn = get_connection()
        rows = conn.execute("SELECT * FROM subjects ORDER BY id").fetchall()
        conn.close()
        return [Subject.from_row(r).to_dict() for r in rows]

    # ---------- topics ----------

    def get_topics(self, subject_id: Optional[int] = None, class_number: Optional[int] = None) -> list:
        """No args -> all topics. Filter by subject_id and/or class_number."""
        conn = get_connection()
        clauses, params = [], []
        if subject_id is not None:
            clauses.append("subject_id = ?")
            params.append(subject_id)
        if class_number is not None:
            clauses.append("class_number = ?")
            params.append(class_number)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = conn.execute(
            f"SELECT * FROM topics {where} ORDER BY order_index, id", params
        ).fetchall()
        conn.close()
        return [Topic.from_row(r).to_dict() for r in rows]

    # ---------- tasks ----------

    def get_tasks(self, topic_id: Optional[int] = None, kind: str = "practice") -> list:
        """
        Regular заданий for a topic. kind='practice' by default — pass
        kind=None to get everything, or use get_diagnostic_tasks() for
        the diagnostic set specifically.
        """
        conn = get_connection()
        clauses, params = [], []
        if topic_id is not None:
            clauses.append("topic_id = ?")
            params.append(topic_id)
        if kind is not None:
            clauses.append("kind = ?")
            params.append(kind)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = conn.execute(
            f"SELECT * FROM tasks {where} ORDER BY order_index, id", params
        ).fetchall()
        conn.close()
        return [Task.from_row(r).to_dict() for r in rows]

    def get_diagnostic_tasks(self, topic_id: int) -> list:
        return self.get_tasks(topic_id=topic_id, kind="diagnostic")

    # ---------- homework (stub — see core/config.py FEATURES["homework"]) ----------

    def get_homework(self, user_id: int) -> list:
        """
        No `homework` table exists yet (out of scope for the hackathon
        MVP — see core/config.py). Returns [] rather than raising, so
        the Homework Page screen can call this safely and render an
        empty/"coming soon" state instead of crashing or needing a
        try/except around a missing method.
        """
        return []

    def get_task(self, task_id: int) -> Optional[dict]:
        conn = get_connection()
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        return Task.from_row(row).to_dict() if row else None

    # ---------- progress ----------

    def get_user_progress(self, user_id: int) -> list:
        """All cached per-topic progress rows for a user (raw shape, topic_id only)."""
        conn = get_connection()
        rows = conn.execute(
            "SELECT * FROM progress WHERE user_id = ?", (user_id,)
        ).fetchall()
        conn.close()
        from core.models import ProgressEntry
        return [ProgressEntry.from_row(r).to_dict() for r in rows]

    def get_progress(self, user_id: int) -> list:
        """
        Same data as get_user_progress(), reshaped for Learning Engine
        (programmer #3's get_recommendation()), which needs a topic name
        alongside the id: [{"topic_id", "topic", "score", "mistake_type"}].

        mistake_type isn't tracked per-topic in the `progress` cache (only
        a count of `mistakes`), so it's populated from the most recent
        incorrect attempt on that topic, or None if there isn't one.
        """
        conn = get_connection()
        rows = conn.execute(
            """SELECT p.topic_id, t.name AS topic, p.score
               FROM progress p
               JOIN topics t ON t.id = p.topic_id
               WHERE p.user_id = ?
               ORDER BY t.order_index, t.id""",
            (user_id,),
        ).fetchall()

        result = []
        for r in rows:
            last_mistake = conn.execute(
                """SELECT a.mistake_type
                   FROM attempts a
                   JOIN tasks tk ON tk.id = a.task_id
                   WHERE a.user_id = ? AND tk.topic_id = ? AND a.correct = 0
                   ORDER BY a.id DESC LIMIT 1""",
                (user_id, r["topic_id"]),
            ).fetchone()
            result.append({
                "topic_id": r["topic_id"],
                "topic": r["topic"],
                "score": r["score"],
                "mistake_type": last_mistake["mistake_type"] if last_mistake else None,
            })
        conn.close()
        return result

    def update_progress(self, user_id: int, topic_id: int) -> dict:
        """
        Recomputes the cached progress row for (user_id, topic_id) from
        the attempts table. Called automatically by save_result(), but
        exposed separately in case something needs to force a recompute
        (e.g. after a bulk import).
        """
        conn = get_connection()
        entry = progress_logic.recompute(conn, user_id, topic_id)
        conn.close()
        return entry.to_dict()

    # ---------- the important one ----------

    def save_result(self, user_id: int, task_id: int, result: dict) -> dict:
        """
        Called by the UI after the Learning Engine (programmer #3) judged
        an answer. `result` is exactly what Learning Engine returns, e.g.:
            {"correct": True, "score": 90, "mistake_type": None}
            {"correct": False, "score": 0, "mistake_type": "calculation"}
        (Learning Engine's richer fields — recommendation, model_solution,
        mistakes list — are for the UI to display and aren't persisted
        here; only what feeds progress tracking is stored.)

        Logs the attempt, then recomputes and returns this user's updated
        progress on the task's topic via update_progress().
        """
        correct = bool(result.get("correct"))
        score = result.get("score", 100 if correct else 0)
        mistake_type = result.get("mistake_type")
        answer_given = result.get("answer_given")

        conn = get_connection()
        task_row = conn.execute(
            "SELECT topic_id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if task_row is None:
            conn.close()
            raise ValueError(f"No task with id={task_id}")
        topic_id = task_row["topic_id"]

        conn.execute(
            """INSERT INTO attempts
               (user_id, task_id, answer_given, correct, score, mistake_type)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, task_id, answer_given, int(correct), score, mistake_type),
        )
        conn.commit()

        entry = progress_logic.recompute(conn, user_id, topic_id)
        conn.close()
        return entry.to_dict()
