import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


# 让 test 文件可以导入项目根目录下的 reminder_dialog.py
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from reminder_dialog import ReminderDialog


def main():
    app = QApplication(sys.argv)

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    dialog = ReminderDialog(
        task_title="复习离散数学 40 分钟",
        remind_time="20:30"
    )

    dialog.exec()

    print("弹窗结果：", dialog.get_action_result())

    sys.exit(0)


if __name__ == "__main__":
    main()