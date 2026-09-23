"""
Проверка ai_engine.py напрямую, без интерфейса.
Запуск из корня проекта: python test_ai_engine.py
"""
import os
from ai_engine import check_answer, check_solution, get_recommendation, AIError

print("Режим:", "MOCK (без сети)" if os.environ.get("WISELY_MOCK") == "1" else "РЕАЛЬНЫЙ Gemini")
print("GEMINI_API_KEY задан:", bool(os.environ.get("GEMINI_API_KEY")))
print("-" * 40)

# --- 1. Текстовый ответ (без сети, всегда должно работать) ---
task = {"question": "x² - 5x + 6 = 0", "answer": "x1=2;x2=3"}
print("check_answer(верный вариант):", check_answer(task, "x1=3;x2=2"))
print("check_answer(неверный вариант):", check_answer(task, "x=100"))
print("-" * 40)

# --- 2. Рекомендация (без сети) ---
progress = [{"topic_id": 1, "topic": "Квадратные уравнения", "score": 40, "mistake_type": "formula"}]
print("get_recommendation:", get_recommendation(progress))
print("-" * 40)

# --- 3. Фото решения (нужен WISELY_MOCK=1 либо реальный GEMINI_API_KEY) ---
photo_path = "test_photo.jpg"  # положи сюда любое фото рядом со скриптом
if os.path.exists(photo_path):
    try:
        result = check_solution(photo_path, task)
        print("check_solution — УСПЕХ:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    except AIError as e:
        print("check_solution — ОШИБКА (AIError):", e)
else:
    print(f"Файл {photo_path} не найден — положи тестовое фото решения рядом со скриптом")
    