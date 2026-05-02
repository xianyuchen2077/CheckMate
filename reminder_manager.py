from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

import database


class ReminderManager:
    def __init__(self, main_window, tray_manager=None):
        self.main_window = main_window
        self.tray_manager = tray_manager
        self.reminded_keys = set()

        self.timer = QTimer(self.main_window)
        self.timer.timeout.connect(self.check_reminders)

    def start(self):
        self.timer.start(30 * 1000)
        self.check_reminders()

    def check_reminders(self):
        due_tasks = database.get_due_tasks_now()

        for task in due_tasks:
            task_id = task["id"]
            title = task["title"]
            remind_time = task["remind_time"]

            today = database.get_today_string()
            remind_key = f"{today}-{task_id}-{remind_time}"

            if remind_key in self.reminded_keys:
                continue

            self.reminded_keys.add(remind_key)
            self.show_reminder(task_id, title, remind_time)

    def show_reminder(self, task_id, title, remind_time):
        if self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate 提醒",
                f"{title} 的打卡时间到了：{remind_time}",
                5000
            )

        msg_box = QMessageBox(self.main_window)
        msg_box.setWindowTitle("CheckMate 提醒")
        msg_box.setText("该打卡啦！")
        msg_box.setInformativeText(
            f"任务：{title}\n提醒时间：{remind_time}\n\n今天不要成为咸鱼。"
        )

        done_button = msg_box.addButton("完成打卡", QMessageBox.ButtonRole.AcceptRole)
        later_button = msg_box.addButton("稍后提醒", QMessageBox.ButtonRole.ActionRole)
        open_button = msg_box.addButton("打开主窗口", QMessageBox.ButtonRole.ActionRole)

        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

        clicked_button = msg_box.clickedButton()

        if clicked_button == done_button:
            database.mark_task_done_today(task_id)
            self.main_window.tip_label.setText(f"已完成打卡：{title}")
            self.main_window.load_tasks()

        elif clicked_button == later_button:
            self.snooze_task(task_id, title, remind_time)

        elif clicked_button == open_button:
            self.main_window.show_main_window()

    def snooze_task(self, task_id, title, remind_time):
        QMessageBox.information(
            self.main_window,
            "稍后提醒",
            f"好，5 分钟后再提醒你：{title}"
        )

        QTimer.singleShot(
            5 * 60 * 1000,
            lambda: self.show_reminder(task_id, title, remind_time)
        )