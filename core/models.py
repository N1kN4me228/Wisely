"""
core/models.py

Plain dataclasses the rest of the app works with, so nobody outside
core/database.py ever touches a sqlite3.Row. Every model has:
  - from_row(row): build from a sqlite3.Row
  - to_dict(): JSON/UI-friendly plain dict (what Repository actually returns)
"""
import json
from dataclasses import dataclass, asdict
from typing import Optional, List


@dataclass
class User:
    id: int
    name: str
    class_number: int

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(id=row["id"], name=row["name"], class_number=row["class_number"])

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Subject:
    id: int
    name: str

    @classmethod
    def from_row(cls, row) -> "Subject":
        return cls(id=row["id"], name=row["name"])

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Topic:
    id: int
    subject_id: int
    class_number: int
    name: str
    description: Optional[str]
    order_index: int

    @classmethod
    def from_row(cls, row) -> "Topic":
        return cls(
            id=row["id"],
            subject_id=row["subject_id"],
            class_number=row["class_number"],
            name=row["name"],
            description=row["description"],
            order_index=row["order_index"],
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Task:
    id: int
    topic_id: int
    question: str
    type: str
    kind: str  # 'practice' | 'diagnostic'
    answer: str
    difficulty: int
    explanation: Optional[str]
    solution_steps: List[str]
    order_index: int

    @classmethod
    def from_row(cls, row) -> "Task":
        return cls(
            id=row["id"],
            topic_id=row["topic_id"],
            question=row["question"],
            type=row["type"],
            kind=row["kind"],
            answer=row["answer"],
            difficulty=row["difficulty"],
            explanation=row["explanation"],
            solution_steps=json.loads(row["solution_steps"]),
            order_index=row["order_index"],
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ProgressEntry:
    user_id: int
    topic_id: int
    score: int
    completed: bool
    mistakes: int
    updated_at: str

    @classmethod
    def from_row(cls, row) -> "ProgressEntry":
        return cls(
            user_id=row["user_id"],
            topic_id=row["topic_id"],
            score=row["score"],
            completed=bool(row["completed"]),
            mistakes=row["mistakes"],
            updated_at=row["updated_at"],
        )

    def to_dict(self) -> dict:
        return asdict(self)
