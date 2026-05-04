from datetime import datetime,timedelta

from PySide6.QtCore import QTimer

import database
from reminder_dialog import ReminderDialog, SnoozeDialog
from pet_system import pet_growth
from pet_growth_dialog import PetGrowthDialog

class ReminderManager:
    def __init__(self, main_window, tray_manager=None, pet_window=None):
        self.main_window = main_window
        self.tray_manager = tray_manager
        self.pet_window = pet_window
        self.reminded_keys = set()
        self.skip_today_keys = set()
        self.repeat_timer_keys = set()

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
            repeat_interval_minutes = task["repeat_interval_minutes"]

            today = database.get_today_string()
            skip_today_key = f"{today}-{task_id}"

            if skip_today_key in self.skip_today_keys:
                continue

            remind_key = f"{today}-{task_id}-{remind_time}"

            if remind_key in self.reminded_keys:
                continue

            self.reminded_keys.add(remind_key)
            self.show_reminder(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )

    def show_reminder(self, task_id, title, remind_time, repeat_interval_minutes=None):
        """
        显示提醒。
        如果任务设置了重复提醒，且用户没有完成任务、没有选择稍后提醒，
        则在弹窗关闭后安排下一次重复提醒。
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
            self.handle_done(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )
            return

        if action_result == ReminderDialog.RESULT_LATER:
            self.choose_snooze_option(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )
            return

        if action_result == ReminderDialog.RESULT_OPEN:
            self.main_window.show_main_window()

        self.schedule_repeat_if_needed(
            task_id,
            title,
            remind_time,
            repeat_interval_minutes
        )

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

    def handle_done(self, task_id, title, remind_time=None, repeat_interval_minutes=None):
        """
        处理“完成打卡”。

        普通任务：
            今天只完成一次，完成后不再提醒。

        重复提醒任务：
            每次点击完成都算完成本次。
            之后继续按 repeat_interval_minutes 安排下一次提醒。
        """
        is_repeat_task = repeat_interval_minutes is not None

        if is_repeat_task:
            task = database.get_task_by_id(task_id)

            growth_result = None
            if task is not None:
                growth_result = pet_growth.add_exp_for_completed_task(task)

            self.main_window.tip_label.setText(f"本次已完成：{title}")

            if growth_result is not None:
                self.main_window.tip_label.setText(growth_result["message"])

            self.main_window.load_tasks()

            if self.pet_window is not None:
                self.pet_window.refresh_growth_info()
                self.pet_window.set_done()

            if self.tray_manager is not None:
                self.tray_manager.show_message(
                    "CheckMate",
                    f"本次已完成，稍后还会继续提醒：{title}",
                    3000
                )

            if growth_result is not None:
                self.show_pet_growth_dialog(growth_result)

            self.schedule_repeat_if_needed(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )

            return

        # 普通任务：沿用原来的每日打卡逻辑
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

        if growth_result is not None:
            self.show_pet_growth_dialog(growth_result)

    def reset_repeat_timer_for_task(self, task_id):
        """
        编辑任务后清理该任务今天的提醒状态。

        作用：
            1. 允许编辑后的任务重新进入提醒逻辑
            2. 清理 repeat_timer_keys，避免旧状态挡住新状态
        """
        today = database.get_today_string()

        self.reminded_keys = {
            key for key in self.reminded_keys
            if not key.startswith(f"{today}-{task_id}-")
        }

        self.repeat_timer_keys.discard(f"{today}-{task_id}")

    def show_pet_growth_dialog(self, growth_result):
        """
        提醒弹窗完成任务后，显示宠物升级 / 进化提示。
        普通加经验不弹窗。
        """
        if not growth_result.get("leveled_up") and not growth_result.get("evolved"):
            return

        dialog = PetGrowthDialog(growth_result, self.main_window)
        dialog.exec()

    def choose_snooze_option(
        self,
        task_id,
        title,
        remind_time,
        repeat_interval_minutes=None
    ):
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

            self.schedule_snooze(
                task_id,
                title,
                remind_time,
                snooze_until,
                repeat_interval_minutes
            )

        elif action_result == SnoozeDialog.RESULT_TODAY_SKIP:
            self.skip_task_today(task_id, title)

        else:
            # 用户关闭稍后弹窗：
            # 如果是重复提醒任务，继续按重复间隔安排下一轮，避免链路断掉。
            self.schedule_repeat_if_needed(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )

    def schedule_snooze(
        self,
        task_id,
        title,
        remind_time,
        snooze_until,
        repeat_interval_minutes=None
    ):
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
            lambda: self.show_reminder(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )
        )

    def schedule_repeat_if_needed(
        self,
        task_id,
        title,
        remind_time,
        repeat_interval_minutes
    ):
        """
        安排下一次重复提醒。

        重复任务即使点击了“完成打卡”，也会继续安排下一次。

        停止条件：
            1. 今天不再提醒
            2. 任务被暂停
            3. repeat_interval_minutes 为空
            4. 当前任务已经有一个重复提醒定时器在等待
        """
        if repeat_interval_minutes is None:
            return

        try:
            repeat_interval_minutes = int(repeat_interval_minutes)
        except (TypeError, ValueError):
            return

        if repeat_interval_minutes <= 0:
            return

        today = database.get_today_string()
        skip_today_key = f"{today}-{task_id}"

        if skip_today_key in self.skip_today_keys:
            return

        if not database.is_task_active(task_id):
            return

        repeat_timer_key = f"{today}-{task_id}"

        # 防止同一个周期任务被重复安排多个定时器
        if repeat_timer_key in self.repeat_timer_keys:
            return

        self.repeat_timer_keys.add(repeat_timer_key)

        delay_ms = repeat_interval_minutes * 60 * 1000

        if self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate",
                f"{repeat_interval_minutes} 分钟后会再次提醒：{title}",
                3000
            )

        QTimer.singleShot(
            delay_ms,
            lambda: self.handle_repeat_timeout(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes,
                repeat_timer_key
            )
        )

    def handle_repeat_timeout(
        self,
        task_id,
        title,
        remind_time,
        repeat_interval_minutes,
        repeat_timer_key
    ):
        """
        重复提醒时间到。
        """
        self.repeat_timer_keys.discard(repeat_timer_key)

        today = database.get_today_string()
        skip_today_key = f"{today}-{task_id}"

        if skip_today_key in self.skip_today_keys:
            return

        if not database.is_task_active(task_id):
            return

        task = database.get_task_by_id(task_id)
        if task is None:
            return

        latest_title = task["title"]
        latest_remind_time = task["remind_time"]
        latest_repeat_interval_minutes = task["repeat_interval_minutes"]

        if latest_repeat_interval_minutes is None:
            return

        self.show_reminder(
            task_id,
            latest_title,
            latest_remind_time,
            latest_repeat_interval_minutes
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