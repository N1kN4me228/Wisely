import sys
import os


# добавляем корень проекта (на уровень выше ui/), чтобы core.* был виден отовсюду
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase, QFont, QIcon
from main_window import MainWindow


# В исходниках ресурсы лежат рядом с main.py, а в сборке — внутри _MEIPASS/ui.
BASE_DIR = os.path.join(getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "ui") 


def load_app_icon() -> QIcon:
    icons_dir = os.path.join(BASE_DIR, "resources", "icons")
    ico_path = os.path.join(icons_dir, "icon.ico")
    png_path = os.path.join(icons_dir, "icon.png")

    icon = QIcon(ico_path) if os.path.exists(ico_path) else QIcon()
    if icon.isNull() and os.path.exists(png_path):
        icon = QIcon(png_path)   # .ico не нашёлся/битый — берём .png
    return icon


def load_app_fonts() -> dict[str, str]:
    fonts_dir = os.path.join(BASE_DIR, "resources", "fonts")
    weight_map = {
        "Regular": os.path.join(fonts_dir, "Druk-Wide-Cyr.ttf"),
    }
    families = {}
    for weight, path in weight_map.items():
        font_id = QFontDatabase.addApplicationFont(path)
        if font_id == -1:
            print(f"Не удалось загрузить шрифт: {path}")
            continue
        families[weight] = QFontDatabase.applicationFontFamilies(font_id)[0]
    return families


def main():
    app = QApplication(sys.argv)

    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("wisely.app")
        except Exception:
            pass

    app_icon = load_app_icon()
    app.setWindowIcon(app_icon)

    fonts = load_app_fonts()
    base_family = fonts.get("Regular", "Arial")
    app.setFont(QFont(base_family, 10))

    style_path = os.path.join(BASE_DIR, "styles", "style.qss")

    with open(style_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow()
    window.setWindowIcon(app_icon)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
    
