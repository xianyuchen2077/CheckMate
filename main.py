import sys
from PySide6.QtCore import QTime, QTimer
from PySide6.QtGui import QFont, QColor, QAction
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QMessageBox,
    QDialog,
    QLineEdit,
    QTimeEdit,
    QFormLayout,
    QDialogButtonBox,
    QSystemTrayIcon,
    QMenu,
    QStyle,
)

import database

class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("添加任务")
        self.resize(360, 180)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例如：背英语单词 30 个")

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(self.time_edit.time().currentTime())

        form_layout = QFormLayout()
        form_layout.addRow("任务名称：", self.title_edit)
        form_layout.addRow("提醒时间：", self.time_edit)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        main_layout = QVBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fb;
                color: #111827;
            }

            QWidget {
                background-color: transparent;
                color: #111827;
                font-family: "Microsoft YaHei";
            }

            QLabel {
                color: #111827;
                background-color: transparent;
                font-size: 14px;
            }

            QLineEdit, QTimeEdit {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                selection-background-color: #dbeafe;
                selection-color: #111827;
            }

            QLineEdit::placeholder {
                color: #9ca3af;
            }

            QTimeEdit::up-button,
            QTimeEdit::down-button {
                background-color: #e5e7eb;
                border: none;
                width: 16px;
            }

            QTimeEdit::up-button:hover,
            QTimeEdit::down-button:hover {
                background-color: #d1d5db;
            }

            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #1e40af;
                color: #ffffff;
            }

            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f9fafb;
            }
        """)

    def get_data(self):
        title = self.title_edit.text().strip()
        remind_time = self.time_edit.time().toString("HH:mm")
        return title, remind_time

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        database.init_db()

        self.setWindowTitle("CheckMate - 不要成为咸鱼")
        self.resize(900, 600)

        # 是否真正退出程序
        self.force_quit = False

        # 记录已经提醒过的任务，避免同一分钟疯狂弹窗
        self.reminded_keys = set()

        self.init_ui()
        self.apply_styles()
        self.load_tasks()

        # 初始化系统托盘
        self.init_tray()

        # 初始化提醒定时器
        self.init_reminder_timer()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        # ================= 左侧区域 =================
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

        task_layout.addWidget(task_title)
        task_layout.addWidget(self.task_list)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.add_btn = QPushButton("添加任务")
        self.complete_btn = QPushButton("完成打卡")
        self.delete_btn = QPushButton("删除任务")

        self.add_btn.clicked.connect(self.add_task)
        self.complete_btn.clicked.connect(self.complete_task)
        self.delete_btn.clicked.connect(self.delete_task)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.complete_btn)
        button_layout.addWidget(self.delete_btn)

        task_layout.addLayout(button_layout)
        left_panel.addWidget(task_card)

        # ================= 右侧区域 =================
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

        right_panel.addWidget(stats_card)
        right_panel.addWidget(tip_card)
        right_panel.addStretch()

        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 1)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fb;
            }

            QWidget {
                color: #111827;
                background-color: transparent;
                font-family: "Microsoft YaHei";
            }

            QLabel {
                color: #111827;
                background-color: transparent;
                font-size: 14px;
            }

            #titleLabel {
                font-size: 32px;
                font-weight: bold;
                color: #111827;
            }

            #subtitleLabel {
                font-size: 15px;
                color: #4b5563;
                margin-bottom: 10px;
            }

            #sectionTitle {
                font-size: 20px;
                font-weight: bold;
                color: #111827;
                margin-bottom: 6px;
            }

            #card {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 14px;
            }

            QListWidget {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 12px;
                padding: 8px;
                font-size: 15px;
                outline: none;
            }

            QListWidget::item {
                background-color: transparent;
                color: #111827;
                padding: 10px;
                border-radius: 8px;
            }

            QListWidget::item:hover {
                background-color: #f3f4f6;
                color: #111827;
            }

            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #111827;
            }

            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
                color: #ffffff;
            }

            QPushButton:pressed {
                background-color: #1e40af;
                color: #ffffff;
            }

            QPushButton:disabled {
                background-color: #9ca3af;
                color: #f9fafb;
            }

            QMessageBox {
                background-color: #ffffff;
                color: #111827;
            }

            QMessageBox QLabel {
                color: #111827;
                background-color: transparent;
            }

            QMessageBox QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border-radius: 8px;
                padding: 6px 12px;
            }

            #tipLabel {
                color: #374151;
                background-color: transparent;
                font-size: 14px;
                line-height: 1.6;
            }
        """)

    def init_tray(self):
        """
        初始化系统托盘。
        关闭窗口后，程序会隐藏到托盘继续运行。
        """
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.warning(self, "提示", "当前系统不支持系统托盘。")
            return

        self.tray_icon = QSystemTrayIcon(self)

        # 先使用系统默认图标，后面我们可以换成自己的图标
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()

        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.show_main_window)

        quit_action = QAction("退出程序", self)
        quit_action.triggered.connect(self.quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)

        # 双击托盘图标显示主窗口
        self.tray_icon.activated.connect(self.on_tray_activated)

        self.tray_icon.setToolTip("CheckMate - 不要成为咸鱼")
        self.tray_icon.show()


    def show_main_window(self):
        """
        显示主窗口。
        """
        self.show()
        self.raise_()
        self.activateWindow()


    def quit_app(self):
        """
        真正退出程序。
        """
        self.force_quit = True
        QApplication.quit()


    def on_tray_activated(self, reason):
        """
        双击托盘图标时显示主窗口。
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()

    def closeEvent(self, event):
        """
        点击右上角关闭按钮时，不退出程序，而是隐藏到系统托盘。
        """
        if self.force_quit:
            event.accept()
        else:
            event.ignore()
            self.hide()

            if hasattr(self, "tray_icon"):
                self.tray_icon.showMessage(
                    "CheckMate 仍在运行",
                    "我已经缩到系统托盘啦，到点还会提醒你，不要成为咸鱼。",
                    QSystemTrayIcon.MessageIcon.Information,
                    3000
                )

    def init_reminder_timer(self):
        """
        初始化提醒定时器。
        每 30 秒检查一次是否有任务需要提醒。
        """
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(30 * 1000)

        # 程序启动后先检查一次
        self.check_reminders()


    def check_reminders(self):
        """
        检查当前是否有到点但未完成的任务。
        """
        due_tasks = database.get_due_tasks_now()

        for task in due_tasks:
            task_id = task["id"]
            title = task["title"]
            remind_time = task["remind_time"]

            # 用 日期 + 任务ID + 时间 作为提醒标记
            today = database.get_today_string()
            remind_key = f"{today}-{task_id}-{remind_time}"

            if remind_key in self.reminded_keys:
                continue

            self.reminded_keys.add(remind_key)

            self.show_reminder(task_id, title, remind_time)


    def show_reminder(self, task_id, title, remind_time):
        """
        弹出提醒窗口。
        """
        if hasattr(self, "tray_icon"):
            self.tray_icon.showMessage(
                "CheckMate 提醒",
                f"{title} 的打卡时间到了：{remind_time}",
                QSystemTrayIcon.MessageIcon.Information,
                5000
            )

        msg_box = QMessageBox(self)
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
            self.tip_label.setText(f"已完成打卡：{title}")
            self.load_tasks()

        elif clicked_button == later_button:
            self.snooze_task(task_id, title, remind_time)

        elif clicked_button == open_button:
            self.show_main_window()


    def snooze_task(self, task_id, title, remind_time):
        """
        稍后提醒。
        这里先简单做成 5 分钟后再次提醒。
        """
        QMessageBox.information(
            self,
            "稍后提醒",
            f"好，5 分钟后再提醒你：{title}"
        )

        QTimer.singleShot(
            5 * 60 * 1000,
            lambda: self.show_reminder(task_id, title, remind_time)
        )

    def load_tasks(self):
        self.task_list.clear()

        tasks = database.get_all_tasks_with_today_status()

        for task in tasks:
            title = task["title"]
            remind_time = task["remind_time"]
            is_done_today = task["is_done_today"]
            task_id = task["id"]

            status_icon = "✅" if is_done_today else "⬜"

            if remind_time:
                display_text = f"{status_icon} {title}    ⏰ {remind_time}"
            else:
                display_text = f"{status_icon} {title}"

            item = QListWidgetItem(display_text)
            item.setData(1000, task_id)
            item.setData(1001, is_done_today)
            item.setForeground(QColor("#111827"))

            self.task_list.addItem(item)

        self.update_stats()

    def add_task(self):
        dialog = AddTaskDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, remind_time = dialog.get_data()

            if not title:
                QMessageBox.information(self, "提示", "任务名称不能为空。")
                return

            database.add_task(title, remind_time)
            self.tip_label.setText(f"新任务已添加：{title}，提醒时间：{remind_time}")
            self.load_tasks()

    def complete_task(self):
        current_item = self.task_list.currentItem()

        if current_item is None:
            QMessageBox.information(self, "提示", "请先选择一个任务。")
            return

        task_id = current_item.data(1000)
        is_done_today = current_item.data(1001)

        if is_done_today:
            QMessageBox.information(self, "提示", "这个任务今天已经完成打卡了。")
            return

        database.mark_task_done_today(task_id)
        self.tip_label.setText("不错，今天没有变咸鱼。")
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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 关键：关闭最后一个窗口时，不自动退出程序
    app.setQuitOnLastWindowClosed(False)

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())