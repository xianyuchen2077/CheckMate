from datetime import datetime,timedelta

from PySide6.QtCore import QTimer

import database
from reminder_dialog import ReminderDialog, SnoozeDialog
from pet_system import pet_growth

class ReminderManager:
    def __init__(self, main_window, tray_manager=None, pet_window=None):
        self.main_window = main_window
        self.tray_manager = tray_manager
        self.pet_window = pet_window
        self.reminded_keys = set()
        self.skip_today_keys = set()

        self.timer = QTimer(self.main_window)
        self.timer.timeout.connect(self.check_reminders)

    def start(self):
        """
        启动提醒检查定时器。
        每 30 秒检查一次是否有到点且未完成的任务。
        """
        self.timer.start(30 * 1000)
        self.check_reminders()

    def check_reminders(self):
        """
        检查当前是否有需要提醒的任务。
        """
        due_tasks = database.get_due_tasks_now()

        for task in due_tasks:
            task_id = task["id"]
            title = task["title"]
            remind_time = task["remind_time"]

            today = database.get_today_string()
            skip_today_key = f"{today}-{task_id}"

            if skip_today_key in self.skip_today_keys:
                continue

            remind_key = f"{today}-{task_id}-{remind_time}"

            if remind_key in self.reminded_keys:
                continue

            self.reminded_keys.add(remind_key)
            self.show_reminder(task_id, title, remind_time)

    def show_reminder(self, task_id, title, remind_time):
        """
        显示提醒。

        ReminderManager 只负责业务流程：
        - 更新宠物状态
        - 发送托盘通知
        - 调用 ReminderDialog 显示弹窗
        - 根据用户选择执行后续动作
        """
        self.notify_pet_reminding(title)
        self.notify_tray_reminding(title, remind_time)

        dialog = ReminderDialog(
            task_title=title,
            remind_time=remind_time,
            parent=self.main_window
        )

        dialog.exec()
        action_result = dialog.get_action_result()

        if action_result == ReminderDialog.RESULT_DONE:
            self.handle_done(task_id, title)

        elif action_result == ReminderDialog.RESULT_LATER:
            self.choose_snooze_option(task_id, title, remind_time)

        elif action_result == ReminderDialog.RESULT_OPEN:
            self.main_window.show_main_window()

        else:
            # 用户关闭弹窗，暂时不做处理
            pass

    def notify_pet_reminding(self, title):
        """
        通知桌面宠物进入提醒状态。
        """
        if self.pet_window is not None:
            self.pet_window.set_reminding(title)

    def notify_tray_reminding(self, title, remind_time):
        """
        发送系统托盘提醒。
        """
        if self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate 提醒",
                f"{title} 的打卡时间到了：{remind_time}",
                5000
            )

    def handle_done(self, task_id, title):
        """
        处理“完成打卡”。
        """
        is_new_checkin = database.mark_task_done_today(task_id)

        if not is_new_checkin:
            self.main_window.tip_label.setText(f"今天已经完成过：{title}")
            return

        task = database.get_task_by_id(task_id)
        growth_result = pet_growth.add_exp_for_completed_task(task)

        if growth_result is not None:
            self.main_window.tip_label.setText(growth_result["message"])
        else:
            self.main_window.tip_label.setText(f"已完成打卡：{title}")

        self.main_window.load_tasks()

        if self.pet_window is not None:
            self.pet_window.refresh_growth_info()
            self.pet_window.set_done()

        if self.tray_manager is not None and growth_result is not None:
            self.tray_manager.show_message(
                "宠物成长",
                growth_result["message"],
                4000
            )

    def choose_snooze_option(self, task_id, title, remind_time):
        """
        打开稍后提醒选项弹窗。
        """
        if self.pet_window is not None:
            self.pet_window.set_lazy()

        dialog = SnoozeDialog(title, self.main_window)
        dialog.exec()

        action_result = dialog.get_action_result()

        if action_result == SnoozeDialog.RESULT_SNOOZE:
            snooze_until = dialog.get_snooze_until()

            if snooze_until is None:
                return

            self.schedule_snooze(task_id, title, remind_time, snooze_until)

        elif action_result == SnoozeDialog.RESULT_TODAY_SKIP:
            self.skip_task_today(task_id, title)

        else:
            # 用户关闭稍后弹窗，不做处理
            pass

    def schedule_snooze(self, task_id, title, remind_time, snooze_until):
        """
        安排下一次稍后提醒。
        """
        now = datetime.now()
        delay_ms = int((snooze_until - now).total_seconds() * 1000)

        if delay_ms < 1000:
            delay_ms = 1000

        display_time = snooze_until.strftime("%H:%M")

        if self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate",
                f"好，{display_time} 再提醒你：{title}",
                3000
            )

        QTimer.singleShot(
            delay_ms,
            lambda: self.show_reminder(task_id, title, remind_time)
        )

    def skip_task_today(self, task_id, title):
        """
        今天不再提醒这个任务。
        """
        today = database.get_today_string()
        skip_today_key = f"{today}-{task_id}"
        self.skip_today_keys.add(skip_today_key)

        if self.pet_window is not None:
            self.pet_window.set_lazy()

        if self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate",
                f"今天不再提醒：{title}",
                3000
            )