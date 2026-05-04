import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication


# 让 test 文件可以导入项目根目录下的模块
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from add_task_dialog import AddTaskDialog


def main():
    app = QApplication(sys.argv)

    app.setFont(QFont("Microsoft YaHei", 10))

    dialog = AddTaskDialog(
        title="",
        remind_time=None,
        description="",
        repeat_interval_minutes=None
    )

    result = dialog.exec()

    if result == AddTaskDialog.DialogCode.Accepted:
        data = dialog.get_data()

        print("=== 添加任务弹窗返回数据 ===")
        print("任务名称：", data[0])
        print("提醒时间：", data[1])
        print("任务描述：", data[2])

        if len(data) >= 4:
            print("重复提醒间隔：", data[3], "分钟")
    else:
        print("用户取消了添加任务")

    sys.exit(0)


if __name__ == "__main__":
    main()