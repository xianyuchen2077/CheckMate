import sys
from pathlib import Path

from PySide6.QtGui import QColor, QFont, QIcon
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

        database.init_db()

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

        right_panel.addWidget(stats_card)
        right_panel.addWidget(detail_card)
        right_panel.addWidget(tip_card)
        right_panel.addStretch()

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
                3000
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

            status_icon = self.get_task_icon(
                is_active=is_active,
                is_done_today=is_done_today,
                repeat_interval_minutes=repeat_interval_minutes
            )

            if repeat_interval_minutes:
                repeat_text = self.format_repeat_interval(repeat_interval_minutes)

                if remind_time:
                    display_text = (
                        f"{status_icon} {title}    "
                        f"⏰ {remind_time}    "
                        f"{repeat_text}"
                    )
                else:
                    display_text = f"{status_icon} {title}    {repeat_text}"

            else:
                if remind_time:
                    display_text = f"{status_icon} {title}    ⏰ {remind_time}"
                else:
                    display_text = f"{status_icon} {title}"

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

        title = task["title"]
        remind_time = task["remind_time"] or "未设置"
        description = task["description"] or "暂无备注"
        repeat_interval_minutes = task["repeat_interval_minutes"]

        if repeat_interval_minutes:
            repeat_text = self.format_repeat_interval(repeat_interval_minutes)
        else:
            repeat_text = "不重复"

        active_text = "启用中" if is_active else "已暂停"
        today_text = "已完成" if is_done_today else "未完成"

        self.detail_name.setText(f"任务名称：{title}")
        self.detail_time.setText(f"提醒时间：{remind_time} / 重复：{repeat_text}")
        self.detail_active.setText(f"任务状态：{active_text}")
        self.detail_today.setText(f"今日状态：{today_text}")
        self.detail_description.setText(f"备注说明：{description}")

    def add_task(self):
        dialog = AddTaskDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, remind_time, description, repeat_interval_minutes = dialog.get_data()

            if not title:
                QMessageBox.information(self, "提示", "任务名称不能为空。")
                return

            database.add_task(
                title,
                remind_time,
                description,
                repeat_interval_minutes
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
            repeat_interval_minutes=task["repeat_interval_minutes"]
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, remind_time, description, repeat_interval_minutes = dialog.get_data()

            if not title:
                QMessageBox.information(self, "提示", "任务名称不能为空。")
                return

            database.update_task(
                task_id,
                title,
                remind_time,
                description,
                repeat_interval_minutes
            )

            if remind_time:
                self.tip_label.setText(f"任务已更新：{title}，提醒时间：{remind_time}")
            else:
                self.tip_label.setText(f"任务已更新：{title}，未设置提醒时间")

            self.load_tasks()

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
                3000
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
        """
        判断是否为周期性重复提醒任务。
        """
        return repeat_interval_minutes is not None and repeat_interval_minutes > 0


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