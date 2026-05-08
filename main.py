import sys
from pathlib import Path

from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

from app_identity import setup_windows_app_identity
from main_window import MainWindow
import config_manager


def get_base_dir():
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def get_app_icon_path():
    base_dir = get_base_dir()

    candidates = [
        base_dir / "assets" / "icons" / "checkmate_icon.ico",
        base_dir / "assets" / "icons" / "checkmate_icon2.ico",
        base_dir / "assets" / "icons" / "checkmate_icon.png",
        base_dir / "assets" / "icons" / "checkmate_icon2.png",
    ]

    for path in candidates:
        if path.exists():
            return str(path)

    return None


def main():
    setup_windows_app_identity()

    app = QApplication(sys.argv)
    app.setApplicationName("CheckMate")
    app.setApplicationDisplayName("CheckMate")
    app.setOrganizationName("XianYu")

    app.setQuitOnLastWindowClosed(False)

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    icon_path = get_app_icon_path()
    if icon_path:
        app.setWindowIcon(QIcon(icon_path))

    window = MainWindow()

    if icon_path:
        window.setWindowIcon(QIcon(icon_path))

    general_config = config_manager.get_general_config()

    if general_config.get("show_main_window_on_startup", True):
        window.show()
    else:
        window.hide()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()