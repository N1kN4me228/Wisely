"""Small, deterministic helpers for daily learning activity."""
from datetime import date, datetime, timedelta


def _as_date(value: str) -> date:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def activity_days(created_at_values: list[str]) -> set[date]:
    """Return unique calendar days on which the user completed an attempt."""
    days = set()
    for value in created_at_values:
        try:
            days.add(_as_date(value))
        except (TypeError, ValueError):
            continue
    return days


def streak_from(days: set[date], start: date) -> int:
    length = 0
    cursor = start
    while cursor in days:
        length += 1
        cursor -= timedelta(days=1)
    return length


def current_streak(days: set[date], today: date | None = None) -> int:
    """Count consecutive active days ending today; an empty day breaks the streak."""
    today = today or date.today()
    return streak_from(days, today)


def best_streak(days: set[date]) -> int:
    if not days:
        return 0
    return max(streak_from(days, day) for day in days)


def last_days(days: set[date], count: int = 7, today: date | None = None) -> list[tuple[date, bool]]:
    today = today or date.today()
    first = today - timedelta(days=count - 1)
    return [(first + timedelta(days=index), first + timedelta(days=index) in days) for index in range(count)]
