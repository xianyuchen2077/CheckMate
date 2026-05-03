import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from reminder_dialog import SnoozeDialog


def main():
    app = QApplication(sys.argv)

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    dialog = SnoozeDialog("复习离散数学 40 分钟")
    dialog.exec()

    print("选择结果：", dialog.get_action_result())
    print("下次提醒时间：", dialog.get_snooze_until())

    sys.exit(0)


if __name__ == "__main__":
    main()