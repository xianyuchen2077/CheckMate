import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from tray_manager import TrayManager


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("托盘图标测试")
        self.resize(360, 280)

        self.tray_manager = TrayManager(self)
        self.tray_manager.init_tray()

        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        tests = [
            ("默认通知", "default"),
            ("提醒通知", "reminder"),
            ("完成通知", "done"),
            ("稍后通知", "snooze"),
            ("警告通知", "warning"),
            ("成功通知", "success"),
        ]

        for text, icon_type in tests:
            button = QPushButton(text)
            button.clicked.connect(
                lambda checked=False, t=text, i=icon_type: self.send_test_message(t, i)
            )
            layout.addWidget(button)

        auto_button = QPushButton("自动轮播所有通知")
        auto_button.clicked.connect(self.auto_test)
        layout.addWidget(auto_button)

    def send_test_message(self, text, icon_type):
        self.tray_manager.show_message(
            "CheckMate 图标测试",
            f"当前通知类型：{icon_type}",
            3000,
            icon_type=icon_type
        )

    def auto_test(self):
        icon_types = [
            "default",
            "reminder",
            "done",
            "snooze",
            "warning",
            "success",
        ]

        for index, icon_type in enumerate(icon_types):
            QTimer.singleShot(
                index * 2500,
                lambda i=icon_type: self.tray_manager.show_message(
                    "CheckMate 图标测试",
                    f"自动测试：{i}",
                    2000,
                    icon_type=i
                )
            )

    def show_main_window(self):
        self.show()
        self.raise_()
        self.activateWindow()


    def show_pet_window(self):
        print("测试窗口：show_pet_window 被调用，测试脚本中不显示宠物。")


    def quit_app(self):
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())