"""
Обёртка над HTTP AI-сервисом программиста №3.
Если сервис не запущен (или упал) — возвращает безопасный fallback,
а не роняет приложение.
"""
import requests


AI_SERVICE_URL = "http://127.0.0.1:8000/api/v1/assess-solution"


def check_solution(subject: str, grade_level: int, task_statement: str, user_solution_text: str) -> dict:
    payload = {
        "subject": subject,
        "grade_level": grade_level,
        "task_statement": task_statement,
        "user_solution_text": user_solution_text,
    }
    try:
        response = requests.post(AI_SERVICE_URL, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"AI-сервис недоступен: {e}")
        return {
            "correct": False,
            "score": 0,
            "is_correct": False,
            "summary": "Не удалось связаться с сервисом проверки.",
            "errors": [],
            "perfect_solution": "",
        }

    # приводим ответ Gemini-сервиса к тому, что ждёт repository.save_result()
    return {
        "correct": data.get("is_correct", False),
        "score": data.get("score", 0),
        "mistake_type": None,  # пока №3 не добавит категоризацию — оставляем пустым
        "summary": data.get("summary", ""),
        "errors": data.get("errors", []),
        "perfect_solution": data.get("perfect_solution", ""),
    }
