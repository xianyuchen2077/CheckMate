from datetime import datetime,timedelta

from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QApplication, QMessageBox

import database
from reminder_dialog import ReminderDialog, SnoozeDialog
from pet_system import pet_growth
from pet_growth_dialog import PetGrowthDialog
import config_manager

def get_base_dir():
    """
    获取项目基础目录。
    """
    import sys

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


REMINDER_SOUNDS_DIR = get_base_dir() / "assets" / "sounds" / "reminders"

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

        # 保存重复提醒任务的下一轮计时器
        self.repeat_timers = {}
        # 保存稍后提醒的计时器
        self.snooze_timers = {}
        # 保存运行时下一次真实提醒时间
        # task_id -> datetime
        self.next_remind_times = {}

        # 自定义提醒音效播放器
        self.sound_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.sound_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)

    def get_reminder_config(self):
        """
        获取提醒设置配置。
        """
        return config_manager.get_reminder_config()

    def parse_time_text(self, time_text):
        """
        解析 HH:mm 文本为 time 对象。
        """
        try:
            return datetime.strptime(str(time_text).strip(), "%H:%M").time()
        except (TypeError, ValueError):
            return None

    def parse_quiet_range_text(self, quiet_range):
        """
        解析静默时段预设文本。

        支持：
            22-8
            00-6
            00-7
            00-8
            12-14

        返回：
            (start_time_text, end_time_text)
        """
        quiet_range = str(quiet_range).strip()

        preset_map = {
            "22-8": ("22:00", "08:00"),
            "00-6": ("00:00", "06:00"),
            "00-7": ("00:00", "07:00"),
            "00-8": ("00:00", "08:00"),
            "12-14": ("12:00", "14:00"),
        }

        return preset_map.get(quiet_range)

    def is_time_in_range(self, now_time, start_time, end_time):
        """
        判断 now_time 是否处于 start_time 到 end_time 之间。

        支持跨天：
            22:00 - 08:00

        支持不跨天：
            12:00 - 14:00
        """
        if start_time is None or end_time is None:
            return False

        # start == end 时，视为全天静默
        if start_time == end_time:
            return True

        # 不跨天，例如 12:00 - 14:00
        if start_time < end_time:
            return start_time <= now_time < end_time

        # 跨天，例如 22:00 - 08:00
        return now_time >= start_time or now_time < end_time

    def is_now_in_quiet_hours(self):
        """
        判断当前是否处于静默时段。
        """
        reminder_config = self.get_reminder_config()

        if not reminder_config.get("quiet_hours_enabled", False):
            return False

        quiet_range = str(
            reminder_config.get("quiet_hours_range", "22-8")
        ).strip()

        # 全天静默
        if quiet_range == "全天静默":
            return True

        # 自定义静默
        if quiet_range == "自定义":
            start_text = str(
                reminder_config.get("quiet_hours_custom_start", "22:00")
            )

            end_text = str(
                reminder_config.get("quiet_hours_custom_end", "08:00")
            )
        else:
            parsed_range = self.parse_quiet_range_text(quiet_range)

            if parsed_range is None:
                return False

            start_text, end_text = parsed_range

        start_time = self.parse_time_text(start_text)
        end_time = self.parse_time_text(end_text)

        now_time = datetime.now().time()

        return self.is_time_in_range(
            now_time,
            start_time,
            end_time
        )

    def handle_quiet_reminder(self, task_id, title, remind_time, repeat_interval_minutes=None):
        """
        静默时段内到点提醒的处理。

        规则：
            1. 不弹提醒窗口
            2. 不发系统通知
            3. 不播放声音
            4. 不切换宠物提醒状态
            5. 重复提醒任务继续安排下一轮
            6. 普通任务保持未完成状态
        """
        if self.main_window is not None and hasattr(self.main_window, "tip_label"):
            self.main_window.tip_label.setText(
                f"当前处于静默时段，已暂不打扰：{title}"
            )

        self.schedule_repeat_if_needed(
            task_id,
            title,
            remind_time,
            repeat_interval_minutes
        )

    def start(self):
        """
        启动提醒检查定时器。
        每 30 秒检查一次普通到点提醒。

        重复提醒任务会在启动时按基础提醒时间和重复间隔，
        自动计算第一个晚于当前时间的提醒点。
        """
        self.timer.start(30 * 1000)

        # 启动时补齐重复提醒链：
        # 例如 09:00 + 每 1 小时，当前 09:10，则安排到 10:00。
        self.schedule_all_repeat_tasks_from_base()

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

            # 重复提醒任务由 repeat_timers 接管
            if self.is_valid_repeat_task(repeat_interval_minutes):
                continue

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
        reminder_config = self.get_reminder_config()

        if self.is_now_in_quiet_hours():
            self.handle_quiet_reminder(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )
            return

        self.notify_pet_reminding(title)
        self.notify_tray_reminding(title, remind_time)
        self.play_reminder_sound()

        # 如果关闭提醒弹窗，则只保留宠物状态 / 系统通知。
        # 对重复提醒任务来说，需要继续安排下一轮，避免提醒链断掉。
        if not reminder_config.get("show_reminder_popup", True):
            self.schedule_repeat_if_needed(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )
            return

        dialog = ReminderDialog(
            task_title=title,
            remind_time=remind_time,
            parent=self.main_window
        )

        self.apply_reminder_dialog_settings(dialog)

        if reminder_config.get("reminder_popup_auto_focus", False):
            QTimer.singleShot(0, dialog.raise_)
            QTimer.singleShot(0, dialog.activateWindow)

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

    def refresh_main_window_tasks(self):
        """
        提醒时间变化后，刷新主窗口任务列表和详情。
        """
        if self.main_window is not None and hasattr(self.main_window, "load_tasks"):
            self.main_window.load_tasks()

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
        reminder_config = self.get_reminder_config()

        if self.is_now_in_quiet_hours():
            return

        # 设置中关闭系统通知后，到点提醒不再弹 Windows 托盘通知。
        if not reminder_config.get("show_system_notification", True):
            return

        if self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate 提醒",
                f"{title} 的打卡时间到了：{remind_time}",
                5000,
                icon_type="reminder"
            )

    def apply_reminder_dialog_settings(self, dialog):
        """
        根据设置调整提醒弹窗行为。
        """
        reminder_config = self.get_reminder_config()

        always_on_top = bool(
            reminder_config.get("reminder_popup_always_on_top", True)
        )

        auto_focus = bool(
            reminder_config.get("reminder_popup_auto_focus", False)
        )

        dialog.setWindowFlag(
            Qt.WindowType.WindowStaysOnTopHint,
            always_on_top
        )

        if auto_focus:
            dialog.raise_()
            dialog.activateWindow()

    def play_sound_file(self, sound_path):
        """
        播放指定音频文件。
        """
        path = Path(sound_path)

        if not path.exists():
            QApplication.beep()
            return

        self.sound_player.stop()
        self.sound_player.setSource(QUrl.fromLocalFile(str(path)))
        self.sound_player.play()

    def play_reminder_sound(self):
        """
        播放提醒音效。

        优先播放 assets/sounds/reminders 中配置的音频文件；
        未选择或文件不存在时，回退到系统提示音。
        """
        reminder_config = self.get_reminder_config()

        if self.is_now_in_quiet_hours():
            return

        if not reminder_config.get("reminder_sound_enabled", True):
            return

        sound_file = str(reminder_config.get("reminder_sound_file", "") or "").strip()

        # 兼容旧配置：如果以前保存过绝对路径，也尽量能播放
        old_sound_path = str(reminder_config.get("reminder_sound_path", "") or "").strip()

        if sound_file:
            sound_path = REMINDER_SOUNDS_DIR / sound_file
            self.play_sound_file(sound_path)
            return

        if old_sound_path:
            self.play_sound_file(old_sound_path)
            return

        QApplication.beep()

    def handle_done(self, task_id, title, remind_time=None, repeat_interval_minutes=None):
        """
        处理“完成打卡”。

        普通任务：
            今天只完成一次，完成后不再提醒。

        重复提醒任务：
            每次点击完成都算完成本次。
            之后继续按 repeat_interval_minutes 安排下一次提醒。
        """
        is_repeat_task = repeat_interval_minutes is not None and repeat_interval_minutes > 0

        # 关键：完成当前这轮前，先取消该任务残留的 timer
        # 避免稍后提醒链和重复提醒链同时存在。
        self.cancel_task_timers(task_id)

        if is_repeat_task:
            task = database.get_task_by_id(task_id)

            # 记录今天至少完成过一次
            database.mark_task_done_today(task_id)

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
                    3000,
                    icon_type="done"
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
            3. 取消该任务已经安排的重复提醒 / 稍后提醒计时器
        """
        today = database.get_today_string()

        self.reminded_keys = {
            key for key in self.reminded_keys
            if not key.startswith(f"{today}-{task_id}-")
        }

        self.repeat_timer_keys.discard(f"{today}-{task_id}")

        self.cancel_task_timers(task_id)

    def is_valid_repeat_task(self, repeat_interval_minutes):
        """
        判断是否是有效重复提醒任务。
        """
        if repeat_interval_minutes is None:
            return False

        try:
            repeat_interval_minutes = int(repeat_interval_minutes)
        except (TypeError, ValueError):
            return False

        return repeat_interval_minutes > 0

    def calculate_next_repeat_time_from_base(self, remind_time, repeat_interval_minutes):
        try:
            repeat_interval_minutes = int(repeat_interval_minutes)
        except (TypeError, ValueError):
            return None

        if repeat_interval_minutes <= 0:
            return None

        if not remind_time:
            return None

        try:
            hour, minute = map(int, remind_time.split(":"))
        except (TypeError, ValueError):
            return None

        now = datetime.now()

        candidate = now.replace(
            hour=hour,
            minute=minute,
            second=0,
            microsecond=0
        )

        # 如果今天的基础提醒时间还没到，就直接用今天 remind_time
        if candidate > now:
            return candidate

        # 如果已经过了，就不断加重复间隔，直到找到第一个未来时间
        interval = timedelta(minutes=repeat_interval_minutes)

        while candidate <= now:
            candidate += interval

        return candidate

    def set_next_remind_time(self, task_id, next_time):
        """
        记录某个任务下一次真实提醒时间，并刷新 UI。
        """
        self.next_remind_times[task_id] = next_time
        self.refresh_main_window_tasks()

    def clear_next_remind_time(self, task_id):
        """
        清除某个任务的运行时下一次提醒时间。
        """
        if task_id in self.next_remind_times:
            self.next_remind_times.pop(task_id, None)
            self.refresh_main_window_tasks()

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
            if self.confirm_skip_today_if_needed(title):
                self.skip_task_today(task_id, title)
            else:
                self.schedule_repeat_if_needed(
                    task_id,
                    title,
                    remind_time,
                    repeat_interval_minutes
                )

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

        关键规则：
            对重复提醒任务来说，稍后提醒会接管当前提醒链。
            因此需要取消该任务已有的重复提醒 timer 和稍后提醒 timer。

        效果：
            重复任务 09:00 提醒，间隔 1h。
            如果选择 09:30 稍后提醒，则下一次提醒是 09:30。
            09:30 完成后，再从 09:30 开始按 1h 安排下一轮。
        """
        now = datetime.now()
        delay_ms = int((snooze_until - now).total_seconds() * 1000)

        if delay_ms < 1000:
            delay_ms = 1000

        # 关键：稍后提醒会接管这条任务提醒链
        # 所以必须取消旧的 repeat timer 和旧的 snooze timer
        self.cancel_task_timers(task_id)

        display_time = snooze_until.strftime("%H:%M")

        if self.tray_manager is not None and not self.is_now_in_quiet_hours():
            self.tray_manager.show_message(
                "CheckMate",
                f"好，{display_time} 再提醒你：{title}",
                3000,
                icon_type="snooze"
            )

        timer = QTimer(self.main_window)
        timer.setSingleShot(True)

        timer.timeout.connect(
            lambda: self.handle_snooze_timeout(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )
        )

        self.snooze_timers[task_id] = timer
        timer.start(delay_ms)

        self.set_next_remind_time(task_id, snooze_until)

    def confirm_skip_today_if_needed(self, title):
        """
        根据设置决定“今天不再提醒”前是否需要二次确认。
        """
        reminder_config = self.get_reminder_config()

        if not reminder_config.get("confirm_skip_today", True):
            return True

        reply = QMessageBox.question(
            self.main_window,
            "确认今天不再提醒",
            (
                f"确定今天不再提醒「{title}」吗？🐟\n\n"
                "这个任务今天将不会再弹出提醒。"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        return reply == QMessageBox.StandardButton.Yes

    def handle_snooze_timeout(
        self,
        task_id,
        title,
        remind_time,
        repeat_interval_minutes=None
    ):
        """
        稍后提醒时间到。

        注意：
            这里只负责再次弹出提醒。
            不在这里安排重复提醒下一轮。

            如果用户点击完成，
            handle_done() 会在完成后安排下一轮重复提醒。
        """
        self.snooze_timers.pop(task_id, None)
        self.next_remind_times.pop(task_id, None)

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

        self.show_reminder(
            task_id,
            latest_title,
            latest_remind_time,
            latest_repeat_interval_minutes
        )

    def schedule_repeat_from_base_if_needed(
        self,
        task_id,
        title,
        remind_time,
        repeat_interval_minutes
    ):
        """
        根据任务原始 remind_time 和 repeat_interval_minutes，
        安排第一个晚于当前时间的重复提醒。

        用于：
            1. 程序启动后初始化重复提醒
            2. 每日刷新后重新安排重复提醒
            3. 编辑任务后重新安排重复提醒

        注意：
            用户点击完成后的下一次提醒，仍然使用 schedule_repeat_if_needed()，
            即“当前完成时间 + repeat_interval_minutes”。
        """
        if not self.is_valid_repeat_task(repeat_interval_minutes):
            return

        today = database.get_today_string()
        skip_today_key = f"{today}-{task_id}"

        if skip_today_key in self.skip_today_keys:
            return

        if not database.is_task_active(task_id):
            return

        next_time = self.calculate_next_repeat_time_from_base(
            remind_time,
            repeat_interval_minutes
        )

        if next_time is None:
            return

        delay_ms = int((next_time - datetime.now()).total_seconds() * 1000)

        if delay_ms <= 0:
            delay_ms = 1000

        repeat_timer_key = f"{today}-{task_id}"

        # 重新按基础时间安排前，先取消这个任务旧的重复 / 稍后 timer
        self.cancel_task_timers(task_id)

        timer = QTimer(self.main_window)
        timer.setSingleShot(True)

        timer.timeout.connect(
            lambda: self.handle_repeat_timeout(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes,
                repeat_timer_key
            )
        )

        self.repeat_timers[task_id] = timer
        self.repeat_timer_keys.add(repeat_timer_key)

        timer.start(delay_ms)

        self.set_next_remind_time(task_id, next_time)

    def schedule_repeat_if_needed(
        self,
        task_id,
        title,
        remind_time,
        repeat_interval_minutes
    ):
        """
        安排下一次重复提醒。

        规则：
            同一个 task_id 同一时间只能存在一个重复提醒 timer。

        停止条件：
            1. 今天不再提醒
            2. 任务被暂停
            3. repeat_interval_minutes 为空
            4. repeat_interval_minutes <= 0
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

        # 安排新的重复提醒前，先取消这个任务旧的重复提醒 timer
        old_timer = self.repeat_timers.pop(task_id, None)
        if old_timer is not None:
            old_timer.stop()
            old_timer.deleteLater()

        self.repeat_timer_keys.discard(repeat_timer_key)

        delay_ms = repeat_interval_minutes * 60 * 1000
        next_time = datetime.now() + timedelta(minutes=repeat_interval_minutes)

        if self.tray_manager is not None and not self.is_now_in_quiet_hours():
            self.tray_manager.show_message(
                "CheckMate",
                f"{repeat_interval_minutes} 分钟后会再次提醒：{title}",
                3000,
                icon_type="reminder"
            )

        timer = QTimer(self.main_window)
        timer.setSingleShot(True)

        timer.timeout.connect(
            lambda: self.handle_repeat_timeout(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes,
                repeat_timer_key
            )
        )

        self.repeat_timers[task_id] = timer
        self.repeat_timer_keys.add(repeat_timer_key)

        timer.start(delay_ms)

        self.set_next_remind_time(task_id, next_time)

    def schedule_all_repeat_tasks_from_base(self):
        """
        根据当前今日任务列表，为所有有效重复提醒任务安排下一次提醒。

        用于：
            - ReminderManager.start()
            - 每日刷新后
            - 批量刷新提醒链路时
        """
        tasks = database.get_all_tasks_with_today_status()

        for task in tasks:
            task_id = task["id"]
            title = task["title"]
            remind_time = task["remind_time"]
            repeat_interval_minutes = task["repeat_interval_minutes"]
            is_active = task["is_active"]

            if not is_active:
                continue

            if not remind_time:
                continue

            if not self.is_valid_repeat_task(repeat_interval_minutes):
                continue

            self.schedule_repeat_from_base_if_needed(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
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
        self.repeat_timers.pop(task_id, None)
        self.next_remind_times.pop(task_id, None)

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
        self.cancel_task_timers(task_id)

        today = database.get_today_string()
        skip_today_key = f"{today}-{task_id}"
        self.skip_today_keys.add(skip_today_key)

        if self.pet_window is not None:
            self.pet_window.set_lazy()

        if self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate",
                f"今天不再提醒：{title}",
                3000,
                icon_type="warning"
            )

    def cancel_task_timers(self, task_id):
        """
        取消某个任务当前所有已安排的提醒计时器。

        用于避免：
            重复提醒链
            稍后提醒链
            同时存在，导致提醒分叉。
        """
        repeat_timer = self.repeat_timers.pop(task_id, None)

        if repeat_timer is not None:
            repeat_timer.stop()
            repeat_timer.deleteLater()

        snooze_timer = self.snooze_timers.pop(task_id, None)

        if snooze_timer is not None:
            snooze_timer.stop()
            snooze_timer.deleteLater()

        today = database.get_today_string()
        self.repeat_timer_keys.discard(f"{today}-{task_id}")

        self.next_remind_times.pop(task_id, None)
        self.refresh_main_window_tasks()

    def reset_daily_state(self):
        """
        跨天后清理提醒管理器的当天状态。
        """
        self.reminded_keys.clear()
        self.skip_today_keys.clear()
        self.repeat_timer_keys.clear()

        for timer in self.repeat_timers.values():
            timer.stop()
            timer.deleteLater()
        self.repeat_timers.clear()

        for timer in self.snooze_timers.values():
            timer.stop()
            timer.deleteLater()
        self.snooze_timers.clear()

        if hasattr(self, "next_remind_times"):
            self.next_remind_times.clear()

        self.schedule_all_repeat_tasks_from_base()