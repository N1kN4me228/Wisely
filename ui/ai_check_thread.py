from PyQt6.QtCore import QThread, pyqtSignal


class SolutionCheckThread(QThread):
    succeeded = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, image_path: str, task: dict):
        super().__init__()
        self.image_path = image_path
        self.task = task

    def run(self):
        from ai_engine import check_solution, AIError
        try:
            result = check_solution(self.image_path, self.task)
            self.succeeded.emit(result)
        except AIError as e:
            self.failed.emit(e.public_message)
        except Exception:
            # Никогда не показываем пользователю traceback, URL или содержимое секретов.
            self.failed.emit("ИИ не смог завершить анализ. Попробуйте ещё раз.")
            
