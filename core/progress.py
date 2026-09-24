"""
core/progress.py

Pure aggregation logic: turns raw `attempts` rows into a cached `progress`
row. Kept separate from repository.py so the scoring rule can change
(or be tuned by programmer #3's adaptive logic) without touching the
public Repository API.

NOTE: this is aggregation only ("how well is topic_id going for user_id"),
not the adaptive recommendation ("what should they do next"). That's
Learning Engine's get_recommendation(user_id) — programmer #3's part.
"""
from core.models import ProgressEntry

# How many of the most recent attempts on a topic count toward its score.
# Keeps one bad attempt from months ago from permanently tanking the number.
PROGRESS_WINDOW = 10

# Score (0-100) at/above which a topic counts as "completed", provided
# every task in the topic has been solved correctly at least once.
COMPLETION_THRESHOLD = 80


def recompute(conn, user_id: int, topic_id: int) -> ProgressEntry:
    """
    Reads recent attempts for (user_id, topic_id) from `attempts`, writes
    the aggregate back to `progress`, and returns it. Only counts
    kind='practice' tasks — diagnostic-test attempts don't feed progress,
    they're a one-time placement signal, not ongoing mastery.
    """
    recent = conn.execute(
        """SELECT a.correct, a.score
           FROM attempts a
           JOIN tasks t ON t.id = a.task_id
           WHERE a.user_id = ? AND t.topic_id = ? AND t.kind = 'practice'
           ORDER BY a.id DESC
           LIMIT ?""",
        (user_id, topic_id, PROGRESS_WINDOW),
    ).fetchall()

    if not recent:
        avg_score = 0
        mistakes = 0
    else:
        avg_score = round(sum(r["score"] for r in recent) / len(recent))
        mistakes = sum(1 for r in recent if not r["correct"])

    total_practice_tasks = conn.execute(
        "SELECT COUNT(*) AS c FROM tasks WHERE topic_id = ? AND kind = 'practice'",
        (topic_id,),
    ).fetchone()["c"]

    distinct_solved = conn.execute(
        """SELECT COUNT(DISTINCT a.task_id) AS c
           FROM attempts a JOIN tasks t ON t.id = a.task_id
           WHERE a.user_id = ? AND t.topic_id = ? AND t.kind = 'practice' AND a.correct = 1""",
        (user_id, topic_id),
    ).fetchone()["c"]

    completed = int(
        total_practice_tasks > 0
        and distinct_solved >= total_practice_tasks
        and avg_score >= COMPLETION_THRESHOLD
    )

    conn.execute(
        """INSERT INTO progress (user_id, topic_id, score, completed, mistakes, updated_at)
           VALUES (?, ?, ?, ?, ?, datetime('now'))
           ON CONFLICT(user_id, topic_id) DO UPDATE SET
               score = excluded.score,
               completed = excluded.completed,
               mistakes = excluded.mistakes,
               updated_at = excluded.updated_at""",
        (user_id, topic_id, avg_score, completed, mistakes),
    )
    conn.commit()

    row = conn.execute(
        "SELECT * FROM progress WHERE user_id = ? AND topic_id = ?",
        (user_id, topic_id),
    ).fetchone()
    return ProgressEntry.from_row(row)
