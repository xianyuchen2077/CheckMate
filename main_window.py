import sys
from pathlib import Path

from PySide6.QtGui import QColor, QFont, QIcon, QDesktopServices
from PySide6.QtCore import QUrl, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import database
import config_manager
from add_task_dialog import AddTaskDialog
from history_dialog import HistoryDialog
from reminder_manager import ReminderManager
from styles import get_main_window_style
from tray_manager import TrayManager
from pet_window import PetWindow
from pet_system import pet_growth
from pet_growth_dialog import PetGrowthDialog
from data_guard.startup_guard import run_startup_data_guard
from data_guard.migration_manager import migrate_legacy_database_if_needed
from data_guard.logger import log_info

def get_base_dir():
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent

def get_background_path():
    background_path = get_base_dir() / "assets" / "backgrounds/main_bg.png"

    if background_path.exists():
        return str(background_path).replace("\\", "/")

    return None

def get_icon_path():
    icon_path = get_base_dir() / "assets" / "icons" / "checkmate_icon.png"

    if icon_path.exists():
        return str(icon_path)

    return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        migration_result = migrate_legacy_database_if_needed()
        log_info(f"数据库迁移检查：{migration_result['message']}")

        database.init_db()

        refresh_result = database.refresh_tasks_for_today()

        if refresh_result["total_changed"] > 0:
            log_info(
                "每日任务刷新："
                f"习惯更新 {refresh_result['habit_updated']} 个，"
                f"任务归档 {refresh_result['task_archived']} 个，"
                f"任务顺延 {refresh_result['task_rolled']} 个"
            )

        self.data_guard_result = run_startup_data_guard()

        self.setWindowTitle("CheckMate - 不要成为咸鱼")
        self.resize(1050, 700)

        self.force_quit = False

        self.init_ui()
        self.apply_styles()
        self.load_tasks()

        self.tray_manager = TrayManager(self)
        self.tray_manager.init_tray()

        self.init_pet()

        self.reminder_manager = ReminderManager(self, self.tray_manager, self.pet_window)
        self.reminder_manager.start()

        QTimer.singleShot(0, self.show_data_guard_warning_if_needed)

        self.current_task_date = database.get_today_string()

        self.daily_refresh_timer = QTimer(self)
        self.daily_refresh_timer.timeout.connect(self.check_daily_refresh)
        self.daily_refresh_timer.start(60 * 1000)

        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("mainBackground")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        title_label = QLabel("CheckMate")
        title_label.setObjectName("titleLabel")

        subtitle_label = QLabel("不要成为咸鱼 · 你的桌面打卡督促助手")
        subtitle_label.setObjectName("subtitleLabel")

        left_panel.addWidget(title_label)
        left_panel.addWidget(subtitle_label)

        task_card = QFrame()
        task_card.setObjectName("card")
        task_layout = QVBoxLayout()
        task_layout.setSpacing(12)
        task_card.setLayout(task_layout)

        task_title = QLabel("今日任务")
        task_title.setObjectName("sectionTitle")

        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        self.task_list.currentItemChanged.connect(self.update_task_detail)

        task_layout.addWidget(task_title)
        task_layout.addWidget(self.task_list)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_btn = QPushButton("添加任务")
        self.edit_btn = QPushButton("编辑任务")
        self.complete_btn = QPushButton("完成打卡")
        self.delete_btn = QPushButton("删除任务")
        self.toggle_active_btn = QPushButton("暂停/启用")
        self.history_btn = QPushButton("历史记录")

        self.add_btn.clicked.connect(self.add_task)
        self.edit_btn.clicked.connect(self.edit_task)
        self.complete_btn.clicked.connect(self.complete_task)
        self.delete_btn.clicked.connect(self.delete_task)
        self.toggle_active_btn.clicked.connect(self.toggle_task_active)
        self.history_btn.clicked.connect(self.show_history)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.complete_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.toggle_active_btn)
        button_layout.addWidget(self.history_btn)
        task_layout.addLayout(button_layout)
        left_panel.addWidget(task_card)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        stats_card = QFrame()
        stats_card.setObjectName("card")
        stats_card.setMinimumHeight(180)

        stats_layout = QVBoxLayout()
        stats_layout.setSpacing(10)
        stats_card.setLayout(stats_layout)

        stats_title = QLabel("打卡统计")
        stats_title.setObjectName("sectionTitle")

        self.today_stat = QLabel("今日完成：0")
        self.streak_stat = QLabel("连续打卡：0 天")
        self.month_stat = QLabel("本月完成率：0%")
        self.fish_stat = QLabel("咸鱼值：50")

        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(self.today_stat)
        stats_layout.addWidget(self.streak_stat)
        stats_layout.addWidget(self.month_stat)
        stats_layout.addWidget(self.fish_stat)

        tip_card = QFrame()
        tip_card.setObjectName("card")
        tip_card.setMinimumHeight(150)

        tip_layout = QVBoxLayout()
        tip_card.setLayout(tip_layout)

        tip_title = QLabel("今日提醒")
        tip_title.setObjectName("sectionTitle")

        self.tip_label = QLabel("开始行动吧，今天不要成为咸鱼。")
        self.tip_label.setWordWrap(True)
        self.tip_label.setObjectName("tipLabel")

        tip_layout.addWidget(tip_title)
        tip_layout.addWidget(self.tip_label)

        detail_card = QFrame()
        detail_card.setObjectName("card")
        detail_card.setMinimumHeight(230)

        detail_layout = QVBoxLayout()
        detail_layout.setSpacing(8)
        detail_card.setLayout(detail_layout)

        detail_title = QLabel("任务详情")
        detail_title.setObjectName("sectionTitle")

        self.detail_name = QLabel("任务名称：未选择")
        self.detail_time = QLabel("提醒时间：-")
        self.detail_active = QLabel("任务状态：-")
        self.detail_today = QLabel("今日状态：-")
        self.detail_description = QLabel("备注说明：-")
        self.detail_description.setWordWrap(True)

        detail_layout.addWidget(detail_title)
        detail_layout.addWidget(self.detail_name)
        detail_layout.addWidget(self.detail_time)
        detail_layout.addWidget(self.detail_active)
        detail_layout.addWidget(self.detail_today)
        detail_layout.addWidget(self.detail_description)

        # 右侧三张卡片按比例铺满整列
        # 打卡统计较短，任务详情和今日提醒更长
        right_panel.addWidget(stats_card, 5)
        right_panel.addWidget(detail_card, 7)
        right_panel.addWidget(tip_card, 2)

        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 1)

    def init_pet(self):
        """
        初始化桌面宠物浮窗。
        """
        self.pet_window = PetWindow(self)

        pet_config = config_manager.get_pet_config()
        if pet_config.get("show_on_startup", True):
            self.pet_window.show()

    def apply_styles(self):
        self.setStyleSheet(get_main_window_style(get_background_path()))

    def show_main_window(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def show_pet_window(self):
        if hasattr(self, "pet_window"):
            self.pet_window.show()
            self.pet_window.raise_()
            self.pet_window.activateWindow()

    def show_history(self):
        dialog = HistoryDialog(self)
        dialog.exec()

    def show_data_guard_warning_if_needed(self):
        """
        如果启动时检测到数据库异常，给用户一个温和提示。
        """
        result = getattr(self, "data_guard_result", None)

        if not result:
            return

        if not result.get("should_warn_user"):
            return

        status = result.get("status")
        message = result.get("message", "数据文件可能存在异常。")
        suspicious_backup_path = result.get("suspicious_backup_path")

        detail_lines = [
            message,
            "",
            "当前数据文件可能被外部修改或发生损坏。",
        ]

        if suspicious_backup_path:
            detail_lines.extend([
                "",
                "程序已经把当前可疑数据库单独备份，方便之后排查或恢复：",
                suspicious_backup_path,
            ])

        detail_lines.extend([
            "",
            "你可以继续使用程序。",
            "如果后续发现数据异常，可以从备份中恢复。",
        ])

        QMessageBox.warning(
            self,
            "数据安全提醒",
            "\n".join(detail_lines)
        )

    def update_pet_progress(self):
        total, done = database.get_today_stats()

        if hasattr(self, "pet_window"):
            self.pet_window.refresh_growth_info()
            self.pet_window.set_progress(done, total)
            self.pet_window.show()
            self.pet_window.raise_()
            self.pet_window.activateWindow()

    def quit_app(self):
        self.force_quit = True

        if hasattr(self, "pet_window"):
            self.pet_window.close()

        if hasattr(self, "tray_manager"):
            self.tray_manager.hide()

        QApplication.quit()

    def closeEvent(self, event):
        if self.force_quit:
            event.accept()
            return

        event.ignore()
        self.hide()

        if hasattr(self, "tray_manager"):
            self.tray_manager.show_message(
                "CheckMate 仍在运行",
                "我已经缩到系统托盘啦，到点还会提醒你，不要成为咸鱼。",
                3000,
                icon_type="default"
            )

    def load_tasks(self):
        self.task_list.clear()

        tasks = database.get_all_tasks_with_today_status()

        for task in tasks:
            title = task["title"]
            remind_time = task["remind_time"]
            repeat_interval_minutes = task["repeat_interval_minutes"]
            is_done_today = task["is_done_today"]
            is_active = task["is_active"]
            task_id = task["id"]
            task_type = task["task_type"]

            status_icon = self.get_task_icon(
                is_active=is_active,
                is_done_today=is_done_today,
                repeat_interval_minutes=repeat_interval_minutes
            )

            type_icon = "📝" if task_type == "task" else "🌱"

            next_remind_time = self.get_runtime_next_remind_time_text(task_id)

            if repeat_interval_minutes:
                repeat_text = self.format_repeat_interval(repeat_interval_minutes)

                if next_remind_time:
                    display_text = (
                        f"{status_icon} {type_icon} {title}    "
                        f"⏭ 下次 {next_remind_time}    "
                    )
                elif remind_time:
                    display_text = (
                        f"{status_icon} {type_icon} {title}    "
                        f"⏰ {remind_time}    "
                    )
                else:
                    display_text = f"{status_icon} {type_icon} {title}    {repeat_text}"
            else:
                if next_remind_time:
                    display_text = f"{status_icon} {type_icon} {title}    ⏭ 下次 {next_remind_time}"
                elif remind_time:
                    display_text = f"{status_icon} {type_icon} {title}    ⏰ {remind_time}"
                else:
                    display_text = f"{status_icon} {type_icon} {title}"

            item = QListWidgetItem(display_text)
            item.setData(1000, task_id)
            item.setData(1001, is_done_today)
            item.setData(1002, is_active)

            # 保存重复提醒间隔，后面完成任务时用它判断是否是周期任务
            item.setData(1003, repeat_interval_minutes)

            item.setForeground(QColor("#111827"))

            self.task_list.addItem(item)

        self.update_stats()
        self.update_task_detail()

    def update_task_detail(self):
        if not hasattr(self, "detail_name"):
            return

        current_item = self.task_list.currentItem()

        if current_item is None:
            self.detail_name.setText("任务名称：未选择")
            self.detail_time.setText("提醒时间：-")
            self.detail_active.setText("任务状态：-")
            self.detail_today.setText("今日状态：-")
            self.detail_description.setText("备注说明：-")
            return

        task_id = current_item.data(1000)
        is_done_today = current_item.data(1001)
        is_active = current_item.data(1002)

        task = database.get_task_by_id(task_id)

        if task is None:
            self.detail_name.setText("任务名称：任务不存在")
            self.detail_time.setText("提醒时间：-")
            self.detail_active.setText("任务状态：-")
            self.detail_today.setText("今日状态：-")
            self.detail_description.setText("备注说明：-")
            return

        # 记录“今天这个重复任务至少完成过一次”
        # 即使重复任务一天完成多轮，checkins 表里也只需要有一条当天记录
        database.mark_task_done_today(task_id)

        title = task["title"]
        remind_time = task["remind_time"] or "未设置"
        description = task["description"] or "暂无备注"
        repeat_interval_minutes = task["repeat_interval_minutes"]
        next_remind_time = self.get_runtime_next_remind_time_text(task_id)
        task_type = task["task_type"]

        if repeat_interval_minutes:
            repeat_text = self.format_repeat_interval(repeat_interval_minutes)
        else:
            repeat_text = "不重复"

        active_text = "启用中" if is_active else "已暂停"
        today_text = "已完成" if is_done_today else "未完成"
        type_text = "任务" if task_type == "task" else "习惯"

        self.detail_name.setText(f"任务名称：{title}（{type_text}）")
        if next_remind_time:
            self.detail_time.setText(
                f"提醒时间：{remind_time} / 下次提醒：{next_remind_time} / 重复：{repeat_text}"
            )
        else:
            self.detail_time.setText(
                f"提醒时间：{remind_time} / 重复：{repeat_text}"
            )
        self.detail_active.setText(f"任务状态：{active_text}")
        self.detail_today.setText(f"今日状态：{today_text}")
        self.detail_description.setText(f"备注说明：{description}")

    def add_task(self):
        dialog = AddTaskDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, remind_time, description, repeat_interval_minutes, task_type = dialog.get_data()

            if not title:
                QMessageBox.information(self, "提示", "任务名称不能为空。")
                return

            database.add_task(
                title,
                remind_time,
                description,
                repeat_interval_minutes,
                task_type
            )

            if remind_time:
                self.tip_label.setText(f"新任务已添加：{title}，提醒时间：{remind_time}")
            else:
                self.tip_label.setText(f"新任务已添加：{title}，未设置提醒时间")

            self.load_tasks()

    def edit_task(self):
        current_item = self.task_list.currentItem()

        if current_item is None:
            QMessageBox.information(self, "提示", "请先选择一个任务。")
            return

        task_id = current_item.data(1000)
        task = database.get_task_by_id(task_id)

        if task is None:
            QMessageBox.warning(self, "错误", "没有找到这个任务，可能已经被删除。")
            self.load_tasks()
            return

        dialog = AddTaskDialog(
            self,
            title=task["title"],
            remind_time=task["remind_time"],
            description=task["description"],
            repeat_interval_minutes=task["repeat_interval_minutes"],
            task_type=task["task_type"]
        )

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        title, remind_time, description, repeat_interval_minutes, task_type = dialog.get_data()

        if not title:
            QMessageBox.information(self, "提示", "任务名称不能为空。")
            return

        # 用关键字参数，避免 title / remind_time / description /
        # repeat_interval_minutes / task_type 顺序错位
        database.update_task(
            task_id=task_id,
            title=title,
            remind_time=remind_time,
            description=description,
            repeat_interval_minutes=repeat_interval_minutes,
            task_type=task_type
        )

        # 编辑后，同步提醒管理器
        if hasattr(self, "reminder_manager") and self.reminder_manager is not None:
            # 不管新任务是否重复，都先清掉旧的重复提醒计时器
            self.reminder_manager.reset_repeat_timer_for_task(task_id)

            # 只有“设置了提醒时间”且“是重复任务”时，才重新安排下一次重复提醒
            if remind_time and self.is_repeat_task(repeat_interval_minutes):
                self.reminder_manager.schedule_repeat_if_needed(
                    task_id,
                    title,
                    remind_time,
                    repeat_interval_minutes
                )

        if remind_time:
            self.tip_label.setText(f"任务已更新：{title}，提醒时间：{remind_time}")
        else:
            self.tip_label.setText(f"任务已更新：{title}，未设置提醒时间")

        self.load_tasks()

        # 尝试重新选中刚刚编辑的任务
        # 如果任务仍在今日任务列表中，就自动选回来
        for row in range(self.task_list.count()):
            item = self.task_list.item(row)

            if item.data(1000) == task_id:
                self.task_list.setCurrentItem(item)
                break

    def complete_task(self):
        current_item = self.task_list.currentItem()

        if current_item is None:
            QMessageBox.information(self, "提示", "请先选择一个任务。")
            return

        task_id = current_item.data(1000)
        is_done_today = current_item.data(1001)
        is_active = current_item.data(1002)
        repeat_interval_minutes = current_item.data(1003)

        if not is_active:
            QMessageBox.information(self, "提示", "这个任务已暂停，不能打卡。")
            return

        # 周期性任务：不调用 database.mark_task_done_today()
        if self.is_repeat_task(repeat_interval_minutes):
            self.complete_repeat_task(task_id)
            return

        # 普通任务：沿用每日打卡逻辑
        if is_done_today:
            QMessageBox.information(self, "提示", "这个任务今天已经完成打卡了。")
            return

        is_new_checkin = database.mark_task_done_today(task_id)

        if not is_new_checkin:
            QMessageBox.information(self, "提示", "这个任务今天已经完成打卡了。")
            return

        task = database.get_task_by_id(task_id)
        growth_result = pet_growth.add_exp_for_completed_task(task)

        if growth_result is not None:
            self.tip_label.setText(growth_result["message"])
        else:
            self.tip_label.setText("不错，今天没有变咸鱼。")

        self.load_tasks()

        if hasattr(self, "pet_window"):
            self.pet_window.refresh_growth_info()
            self.pet_window.set_done()

        if growth_result is not None:
            self.show_pet_growth_dialog(growth_result)

    def complete_repeat_task(self, task_id):
        """
        完成一次周期性任务。

        注意：
            周期性任务不调用 database.mark_task_done_today(task_id)
            因为它不是“今天完成一次就结束”的任务。
            它只是表示“本轮提醒已完成”，后续仍然会继续重复提醒。
        """
        task = database.get_task_by_id(task_id)

        if task is None:
            QMessageBox.warning(self, "错误", "没有找到这个任务，可能已经被删除。")
            self.load_tasks()
            return

        title = task["title"]
        remind_time = task["remind_time"]
        repeat_interval_minutes = task["repeat_interval_minutes"]

        growth_result = pet_growth.add_exp_for_completed_task(task)

        if growth_result is not None:
            self.tip_label.setText(growth_result["message"])
        else:
            self.tip_label.setText(f"本次周期任务已完成：{title}")

        self.load_tasks()

        if hasattr(self, "pet_window"):
            self.pet_window.refresh_growth_info()
            self.pet_window.set_done()

        if hasattr(self, "tray_manager") and self.tray_manager is not None:
            self.tray_manager.show_message(
                "CheckMate",
                f"本次已完成：{title}",
                3000,
                icon_type="done"
            )

        if growth_result is not None:
            self.show_pet_growth_dialog(growth_result)

        # 如果提醒管理器已经启动，则继续安排下一次周期提醒
        if hasattr(self, "reminder_manager") and self.reminder_manager is not None:
            self.reminder_manager.schedule_repeat_if_needed(
                task_id,
                title,
                remind_time,
                repeat_interval_minutes
            )

    def toggle_task_active(self):
        current_item = self.task_list.currentItem()

        if current_item is None:
            QMessageBox.information(self, "提示", "请先选择一个任务。")
            return

        task_id = current_item.data(1000)

        database.toggle_task_active(task_id)

        self.tip_label.setText("任务状态已切换。")
        self.load_tasks()

    def delete_task(self):
        current_item = self.task_list.currentItem()

        if current_item is None:
            QMessageBox.information(self, "提示", "请先选择一个任务。")
            return

        task_id = current_item.data(1000)
        item_text = current_item.text()

        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除这个任务吗？\n\n{item_text}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            database.delete_task(task_id)
            self.tip_label.setText(f"已删除任务：{item_text}")
            self.load_tasks()

    def after_task_saved(
        self,
        task_id,
        title,
        remind_time,
        repeat_interval_minutes,
        is_edit=False
    ):
        """
        添加 / 编辑任务保存后，处理提醒管理器同步。

        重点：
            如果任务被设置为重复提醒，不应该只等每天 remind_time 那一分钟。
            编辑后应该主动安排下一轮重复提醒。
        """
        if not remind_time:
            return

        if not self.is_repeat_task(repeat_interval_minutes):
            return

        if not hasattr(self, "reminder_manager") or self.reminder_manager is None:
            return

        self.reminder_manager.reset_repeat_timer_for_task(task_id)

        self.reminder_manager.schedule_repeat_if_needed(
            task_id,
            title,
            remind_time,
            repeat_interval_minutes
        )

    def update_stats(self):
        total, done = database.get_today_stats()

        self.today_stat.setText(f"今日完成：{done} / {total}")

        streak = database.get_streak_days()
        self.streak_stat.setText(f"连续打卡：{streak} 天")

        month_percent = database.get_month_stats()
        self.month_stat.setText(f"本月完成率：{month_percent}%")

        fish_value = max(0, 100 - done * 15 - streak * 5)
        self.fish_stat.setText(f"咸鱼值：{fish_value}")

        if hasattr(self, "pet_window"):
            self.pet_window.update_by_fish_value(fish_value, done, total)

    def show_pet_growth_dialog(self, growth_result):
        """
        显示宠物成长提示。
        只有升级或进化时弹窗；普通加经验只更新 tip_label。
        """
        if not growth_result.get("leveled_up") and not growth_result.get("evolved"):
            return

        dialog = PetGrowthDialog(growth_result, self)
        dialog.exec()

    def is_repeat_task(self, repeat_interval_minutes):
        try:
            if repeat_interval_minutes is None:
                return False

            repeat_interval_minutes = int(repeat_interval_minutes)
            return repeat_interval_minutes > 0

        except (TypeError, ValueError):
            return False


    def get_task_icon(self, is_active, is_done_today, repeat_interval_minutes):
        """
        根据任务状态返回任务列表图标。

        图标规则：
            ⏸️  已暂停任务
            🔁  周期性重复提醒任务
            ✅  普通任务今日已完成
            ⬜  普通任务今日未完成
        """
        if not is_active:
            return "⏸️"

        if self.is_repeat_task(repeat_interval_minutes):
            return "🔁"

        if is_done_today:
            return "✅"

        return "⬜"


    def format_repeat_interval(self, repeat_interval_minutes):
        """
        把重复提醒间隔格式化成显示文字。
        """
        if repeat_interval_minutes is None:
            return ""

        if repeat_interval_minutes < 60:
            return f"每隔 {repeat_interval_minutes} 分钟"

        hours = repeat_interval_minutes // 60
        minutes = repeat_interval_minutes % 60

        if minutes == 0:
            return f"每隔 {hours} 小时"

        return f"每隔 {hours} 小时 {minutes} 分钟"

    def get_runtime_next_remind_time_text(self, task_id):
        """
        获取运行时下一次提醒时间文本。

        如果 ReminderManager 中记录了下一次真实提醒时间，
        则返回 HH:mm。
        """
        if not hasattr(self, "reminder_manager"):
            return None

        if self.reminder_manager is None:
            return None

        next_remind_times = getattr(self.reminder_manager, "next_remind_times", {})

        next_time = next_remind_times.get(task_id)

        if next_time is None:
            return None

        return next_time.strftime("%H:%M")

    def check_daily_refresh(self):
        """
        程序运行中跨过 00:00 后，自动刷新任务日期。
        """
        today = database.get_today_string()

        if today == self.current_task_date:
            return

        self.current_task_date = today
        self.refresh_tasks_for_new_day()

    def refresh_tasks_for_new_day(self):
        """
        执行每日任务刷新，并同步 UI 与提醒状态。
        """
        refresh_result = database.refresh_tasks_for_today()

        if refresh_result["total_changed"] > 0:
            log_info(
                "每日任务刷新："
                f"习惯更新 {refresh_result['habit_updated']} 个，"
                f"任务归档 {refresh_result['task_archived']} 个，"
                f"任务顺延 {refresh_result['task_rolled']} 个"
            )

        if hasattr(self, "reminder_manager") and self.reminder_manager is not None:
            self.reminder_manager.reset_daily_state()

        self.load_tasks()

        if hasattr(self, "pet_window"):
            self.pet_window.refresh_growth_info()
