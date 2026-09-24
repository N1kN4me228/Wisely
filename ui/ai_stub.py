class AIStub:
    def check_answer(self, task, user_answer):
        return {"correct": True, "score": 100}


    def check_solution(self, image, task):
        return {
            "correct": True,
            "score": 85,
            "mistakes": ["answer_not_highlighted"],
            "recommendation": "Записывайте итоговый ответ отдельной строкой.",
        }
    