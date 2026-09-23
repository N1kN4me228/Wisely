"""Wisely AI / Learning Engine (программист №3), всё в одном файле.

Публичный API:
    check_answer(task, user_answer)  -> dict   мгновенно, без сети
    check_solution(image, task)      -> dict   Gemini, 3-10 сек, вызывать из QThread
    get_recommendation(progress)     -> dict   что посоветовать ученику
    recommend(score)                 -> str     "repeat" | "practice" | "next_topic"
    AIError                                     исключение при сбое Gemini

task: dict с ключами question, answer; желательны explanation, subject, grade.
Ключ Gemini: переменная окружения GEMINI_API_KEY.
Разработка без ключа и сети: WISELY_MOCK=1.
Зависимости: pip install google-genai pydantic pillow
"""
import copy
import hashlib
import io
import mimetypes
import os
import re
import time
from typing import List, Literal, Optional, Tuple, Union

from pydantic import BaseModel

MODEL = "gemini-3.6-flash"
MAX_SIDE = 1600  # px, хватает для рукописного текста


class AIError(Exception):
    """Gemini недоступен / вернул мусор / фото не открылось. UI: «Попробуйте ещё раз»."""


# ============================================================ правила (без сети)
def recommend(score: int) -> str:
    if score < 50:
        return "repeat"
    if score < 80:
        return "practice"
    return "next_topic"


def _norm(s: str) -> str:
    s = str(s).lower()
    s = s.replace("х", "x").replace("−", "-").replace("–", "-").replace(",", ".")
    s = re.sub(r"\s+", "", s)
    return s.rstrip(".;")


def _numbers(s: str) -> List[float]:
    # x1 / x2 -> x, чтобы индексы корней не считались числами
    s = re.sub(r"([a-zа-я])\d+", r"\1", _norm(s))
    return sorted(round(float(n), 6) for n in re.findall(r"-?\d+(?:\.\d+)?", s))


def check_answer(task: dict, user_answer: str) -> dict:
    """Мгновенная проверка текстового ответа. В task["answer"] допустимы
    варианты через "|", например "x=3, x=2|2;3".
    -> {"correct": bool, "score": 0|100, "recommendation": str}"""
    user = (user_answer or "").strip()
    if not user:
        return {"correct": False, "score": 0, "recommendation": "repeat"}

    ok = False
    for variant in str(task["answer"]).split("|"):
        if _norm(user) == _norm(variant):
            ok = True
        else:
            a, b = _numbers(user), _numbers(variant)
            ok = bool(a) and a == b
        if ok:
            break

    score = 100 if ok else 0
    return {"correct": ok, "score": score, "recommendation": recommend(score)}


MISTAKE_HINTS = {
    "calculation": "Чаще всего ошибки в вычислениях — проверяй арифметику по шагам.",
    "formula": "Чаще всего ошибки в формулах — выпиши нужную формулу перед решением.",
    "concept": "Стоит перечитать теорию: не хватает понимания правила.",
    "formatting": "Решение верное, но подтяни оформление: выделяй ответ отдельной строкой.",
}


def get_recommendation(progress: List[dict]) -> dict:
    """progress — список по темам:
        {"topic_id": 3, "topic": "Теорема Виета", "score": 40, "mistake_type": "formula"}
    mistake_type необязателен; темы без попыток (score is None) пропускаются.
    -> {"action": "start"|"repeat"|"practice"|"next_topic",
        "topic_id": int|None, "topic": str|None, "message": str}"""
    tried = [p for p in (progress or []) if p.get("score") is not None]
    if not tried:
        return {"action": "start", "topic_id": None, "topic": None,
                "message": "Начни с первой темы — Wisely подстроится под твои результаты."}

    weakest = min(tried, key=lambda p: p["score"])
    action = recommend(weakest["score"])
    name = weakest.get("topic") or "эта тема"

    if action == "next_topic":
        msg = "Отличный прогресс! Можно переходить к следующей теме."
    elif action == "practice":
        msg = f"Потренируйся ещё в теме «{name}»: дополнительные задания помогут закрепить."
    else:
        msg = f"Wisely рекомендует повторить тему «{name}»."

    hint = MISTAKE_HINTS.get(weakest.get("mistake_type"))
    if hint and action != "next_topic":
        msg += " " + hint

    return {"action": action, "topic_id": weakest.get("topic_id"),
            "topic": weakest.get("topic"), "message": msg}


# ============================================================ схема ответа
# Те же категории, что в БД у программиста №2
MistakeType = Literal["calculation", "formula", "concept", "formatting"]


class ErrorItem(BaseModel):
    step: int
    user_input: str
    correction: str
    explanation: str
    mistake_type: MistakeType


class GeminiResult(BaseModel):
    readable: bool   # False, если фото не удалось разобрать
    correct: bool
    score: int       # 0..100
    summary: str
    errors: List[ErrorItem]
    perfect_solution: str


def _finalize(data: dict) -> dict:
    """Ограничивает score, добавляет recommendation и main_mistake_type."""
    data["score"] = max(0, min(100, int(data["score"])))
    if not data["readable"]:
        data["score"], data["correct"] = 0, False
    data["recommendation"] = recommend(data["score"])
    data["main_mistake_type"] = data["errors"][0]["mistake_type"] if data["errors"] else None
    return data


# ============================================================ промпт
SYSTEM_PROMPT = """Ты — школьный преподаватель, проверяющий решение ученика по фотографии.
Тебе дают конкретное условие задачи и фото решения. Проверяй именно это решение
и именно это условие; не придумывай и не меняй условие.

Правила:
- Если фото нечитаемо или это не решение задачи: readable=false, correct=false, score=0,
  errors=[], в summary объясни, что нужно переснять.
- score от 0 до 100: правильность важнее оформления.
- Для каждой ошибки укажи mistake_type строго из списка:
  calculation (арифметика/вычисления), formula (неверная или не та формула),
  concept (не понято правило/понятие), formatting (оформление: нет ответа, нет единиц, нет «Дано/Решение»).
- Если решение верное, но плохо оформлено — correct=true и ошибка типа formatting.
- perfect_solution — короткое пошаговое решение, шаги через перевод строки.
- Пиши на русском, обращайся к ученику на «ты», дружелюбно и коротко.
Ответ строго в JSON по схеме."""


def _user_prompt(task: dict) -> str:
    return (
        f"Предмет: {task.get('subject', '')}, класс: {task.get('grade', '')}\n"
        f"Условие: {task['question']}\n"
        f"Эталонный ответ: {task.get('answer', '')}\n"
        f"Пояснение автора задания: {task.get('explanation', '')}"
    )


# ============================================================ фото
def _prepare_image(image: Union[str, bytes]) -> Tuple[bytes, str]:
    """-> (bytes, mime). Поворот по EXIF, сжатие до MAX_SIDE, JPEG.
    Без Pillow отдаёт файл как есть. Бросает OSError/ValueError."""
    if isinstance(image, (bytes, bytearray)):
        raw = bytes(image)
    else:
        with open(image, "rb") as f:
            raw = f.read()
    try:
        from PIL import Image, ImageOps
    except ImportError:
        guessed = mimetypes.guess_type(image)[0] if isinstance(image, str) else None
        return raw, guessed or "image/jpeg"
    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    except Exception as e:
        raise ValueError(f"Не удалось открыть изображение: {e}")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return buf.getvalue(), "image/jpeg"


# ============================================================ Gemini
_client = None
_cache: dict = {}

# Заглушка для WISELY_MOCK=1 (разработка UI без ключа, запасной вариант на демо)
MOCK_RESULT = {
    "readable": True,
    "correct": True,
    "score": 85,
    "summary": "Решение верное, но ответ не выделен отдельной строкой.",
    "errors": [{
        "step": 3,
        "user_input": "x1 = 3, x2 = 2",
        "correction": "Ответ: x1 = 3, x2 = 2",
        "explanation": "Записывай итоговый ответ отдельной строкой со словом «Ответ».",
        "mistake_type": "formatting",
    }],
    "perfect_solution": "D = b² - 4ac\nD = 25 - 24 = 1\nx1 = (5 + 1)/2 = 3, x2 = (5 - 1)/2 = 2\nОтвет: x1 = 3, x2 = 2",
}


def _get_client():
    global _client
    if _client is None:
        key = os.environ.get("GEMINI_API_KEY")
        if not key:
            raise AIError("Не задан GEMINI_API_KEY")
        from google import genai
        _client = genai.Client(api_key=key)
    return _client


def check_solution(image: Union[str, bytes], task: dict, use_cache: bool = True) -> dict:
    """Проверка фото решения. image — путь к файлу или bytes.
    Блокирующий вызов: в PyQt запускать из QThread/QRunnable. Бросает AIError.

    -> {"readable", "correct", "score", "summary",
        "errors": [{"step","user_input","correction","explanation","mistake_type"}],
        "perfect_solution", "recommendation", "main_mistake_type"}"""
    try:
        data, mime = _prepare_image(image)
    except (OSError, ValueError) as e:
        raise AIError(str(e))

    if os.environ.get("WISELY_MOCK") == "1":
        time.sleep(1.5)  # чтобы UI успел показать «Анализируем...»
        return _finalize(copy.deepcopy(MOCK_RESULT))

    key = hashlib.sha256(
        data + task["question"].encode() + str(task.get("answer", "")).encode()
    ).hexdigest()
    if use_cache and key in _cache:
        return copy.deepcopy(_cache[key])

    from google.genai import types
    part = types.Part.from_bytes(data=data, mime_type=mime)

    last_err: Optional[Exception] = None
    for attempt in range(2):  # одна повторная попытка
        try:
            resp = _get_client().models.generate_content(
                model=MODEL,
                contents=[part, _user_prompt(task)],
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=GeminiResult,
                    temperature=0.2,
                ),
            )
            result = _finalize(GeminiResult.model_validate_json(resp.text).model_dump())
            break
        except AIError:
            raise
        except Exception as e:  # сеть, квота, битый JSON
            last_err = e
            if attempt == 0:
                time.sleep(1)
    else:
        raise AIError(f"Ошибка проверки: {last_err}")

    if result["readable"]:
        _cache[key] = copy.deepcopy(result)
    return result
