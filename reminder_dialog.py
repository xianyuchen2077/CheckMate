from datetime import datetime, date, time, timedelta

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QDialogButtonBox,
    QDateTimeEdit,
)


class ReminderDialog(QDialog):
    RESULT_DONE = "done"
    RESULT_LATER = "later"
    RESULT_OPEN = "open"
    RESULT_CANCEL = "cancel"

    def __init__(self, task_title, remind_time, parent=None):
        super().__init__(parent)

        self.task_title = task_title
        self.remind_time = remind_time
        self.action_result = self.RESULT_CANCEL

        self.setWindowTitle("CheckMate 提醒")
        self.setFixedSize(460, 320)
        self.setMinimumSize(460, 320)
        self.setMaximumSize(460, 320)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("reminderCard")
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        card.setFixedSize(424, 284)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(10)
        card.setLayout(card_layout)

        icon_label = QLabel("⏰")
        icon_label.setObjectName("iconLabel")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedHeight(42)

        title_label = QLabel("该打卡啦！")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(34)

        task_label = QLabel(f"任务：{self.task_title}")
        task_label.setObjectName("taskLabel")
        task_label.setWordWrap(True)
        task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        task_label.setMinimumHeight(42)
        task_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        time_label = QLabel(f"提醒时间：{self.remind_time}")
        time_label.setObjectName("timeLabel")
        time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        time_label.setFixedHeight(22)

        slogan_label = QLabel("今天不要成为咸鱼。")
        slogan_label.setObjectName("sloganLabel")
        slogan_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        slogan_label.setMinimumHeight(22)
        slogan_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        self.done_btn = QPushButton("完成打卡")
        self.later_btn = QPushButton("稍后提醒")
        self.open_btn = QPushButton("打开主窗口")

        for btn in [self.done_btn, self.later_btn, self.open_btn]:
            btn.setFixedHeight(38)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.done_btn.setObjectName("primaryButton")
        self.later_btn.setObjectName("secondaryButton")
        self.open_btn.setObjectName("secondaryButton")

        self.done_btn.clicked.connect(self.on_done)
        self.later_btn.clicked.connect(self.on_later)
        self.open_btn.clicked.connect(self.on_open)

        button_layout.addWidget(self.done_btn)
        button_layout.addWidget(self.later_btn)
        button_layout.addWidget(self.open_btn)

        card_layout.addWidget(icon_label)
        card_layout.addWidget(title_label)
        card_layout.addWidget(task_label)
        card_layout.addWidget(time_label)
        card_layout.addWidget(slogan_label)
        card_layout.addLayout(button_layout)

        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #eef2ff;
                font-family: "Microsoft YaHei";
            }

            #reminderCard {
                background-color: #ffffff;
                border: 1px solid #dbeafe;
                border-radius: 22px;
            }

            #iconLabel {
                font-size: 38px;
                background-color: transparent;
            }

            #titleLabel {
                color: #111827;
                font-size: 24px;
                font-weight: bold;
                background-color: transparent;
            }

            #taskLabel {
                color: #1f2937;
                font-size: 16px;
                font-weight: 600;
                background-color: transparent;
            }

            #timeLabel {
                color: #4b5563;
                font-size: 14px;
                background-color: transparent;
            }

            #sloganLabel {
                color: #6b7280;
                font-size: 13px;
                background-color: transparent;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 9px 12px;
                font-size: 13px;
                font-weight: 600;
            }

            #primaryButton {
                background-color: #2563eb;
                color: #ffffff;
            }

            #primaryButton:hover {
                background-color: #1d4ed8;
            }

            #primaryButton:pressed {
                background-color: #1e40af;
            }

            #secondaryButton {
                background-color: #e5e7eb;
                color: #111827;
            }

            #secondaryButton:hover {
                background-color: #d1d5db;
            }

            #secondaryButton:pressed {
                background-color: #9ca3af;
            }
        """)

    def on_done(self):
        self.action_result = self.RESULT_DONE
        self.accept()

    def on_later(self):
        self.action_result = self.RESULT_LATER
        self.accept()

    def on_open(self):
        self.action_result = self.RESULT_OPEN
        self.accept()

    def get_action_result(self):
        return self.action_result

class SnoozeDialog(QDialog):
    RESULT_CANCEL = "cancel"
    RESULT_TODAY_SKIP = "today_skip"
    RESULT_SNOOZE = "snooze"

    def __init__(self, task_title, parent=None):
        super().__init__(parent)

        self.task_title = task_title
        self.action_result = self.RESULT_CANCEL
        self.snooze_until = None

        self.setWindowTitle("稍后提醒")
        self.setFixedSize(480, 410)
        self.setMinimumSize(480, 410)
        self.setMaximumSize(480, 410)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.init_ui()
        self.apply_styles()

        layout = self.layout()
        if layout is not None:
            layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(18, 18, 18, 18)
        main_layout.setSpacing(0)

        card = QFrame()
        card.setObjectName("snoozeCard")
        card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        card.setFixedSize(444, 374)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(22, 18, 22, 18)
        card_layout.setSpacing(8)
        card.setLayout(card_layout)

        title_label = QLabel("你想拖多久？")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(34)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        task_label = QLabel(f"任务：{self.task_title}")
        task_label.setObjectName("taskLabel")
        task_label.setWordWrap(True)
        task_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        task_label.setMinimumHeight(42)
        task_label.setMaximumHeight(52)
        task_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.btn_5_min = QPushButton("再给我5分钟~")
        self.btn_10_min = QPushButton("向天再借600秒")
        self.btn_30_min = QPushButton("先拖半小时")
        self.btn_60_min = QPushButton("一个小时后之后再戳我")
        self.btn_skip_today = QPushButton("不干了！今天不干了！")
        self.btn_custom = QPushButton("说吧，你想拖多久")

        buttons = [
            self.btn_5_min,
            self.btn_10_min,
            self.btn_30_min,
            self.btn_60_min,
            self.btn_skip_today,
            self.btn_custom,
        ]

        for button in buttons:
            button.setObjectName("snoozeButton")
            button.setFixedHeight(36)
            button.setMinimumHeight(36)
            button.setMaximumHeight(36)
            button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.btn_skip_today.setObjectName("dangerButton")
        self.btn_custom.setObjectName("primaryButton")

        self.btn_5_min.clicked.connect(lambda: self.choose_minutes(5))
        self.btn_10_min.clicked.connect(lambda: self.choose_minutes(10))
        self.btn_30_min.clicked.connect(lambda: self.choose_minutes(30))
        self.btn_60_min.clicked.connect(lambda: self.choose_minutes(60))
        self.btn_skip_today.clicked.connect(self.skip_today)
        self.btn_custom.clicked.connect(self.choose_custom_time)

        card_layout.addWidget(title_label)
        card_layout.addWidget(task_label)
        card_layout.addSpacing(4)

        for button in buttons:
            card_layout.addWidget(button)

        main_layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #fff7ed;
                font-family: "Microsoft YaHei";
            }

            #snoozeCard {
                background-color: #ffffff;
                border: 1px solid #fed7aa;
                border-radius: 22px;
            }

            #titleLabel {
                color: #111827;
                font-size: 22px;
                font-weight: bold;
                background-color: transparent;
            }

            #taskLabel {
                color: #4b5563;
                font-size: 14px;
                background-color: transparent;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 600;
            }

            #snoozeButton {
                background-color: #f3f4f6;
                color: #111827;
            }

            #snoozeButton:hover {
                background-color: #e5e7eb;
            }

            #primaryButton {
                background-color: #2563eb;
                color: #ffffff;
            }

            #primaryButton:hover {
                background-color: #1d4ed8;
            }

            #dangerButton {
                background-color: #fee2e2;
                color: #991b1b;
            }

            #dangerButton:hover {
                background-color: #fecaca;
            }

            QDateTimeEdit {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """)

    def choose_minutes(self, minutes):
        self.action_result = self.RESULT_SNOOZE
        self.snooze_until = datetime.now() + timedelta(minutes=minutes)
        self.accept()

    def skip_today(self):
        self.action_result = self.RESULT_TODAY_SKIP
        self.snooze_until = None
        self.accept()

    def choose_custom_time(self):
        dialog = CustomSnoozeTimeDialog(self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.action_result = self.RESULT_SNOOZE
            self.snooze_until = dialog.get_selected_datetime()
            self.accept()

    def get_action_result(self):
        return self.action_result

    def get_snooze_until(self):
        return self.snooze_until

class CustomSnoozeTimeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("自定义稍后提醒时间")
        self.setFixedSize(400, 200)
        self.setMinimumSize(400, 200)
        self.setMaximumSize(400, 200)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)

        self.init_ui()
        self.apply_styles()

        layout = self.layout()
        if layout is not None:
            layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        title_label = QLabel("选择下次提醒时间")
        title_label.setObjectName("titleLabel")
        title_label.setFixedHeight(32)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.datetime_edit.setFixedHeight(40)
        self.datetime_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        default_time = QDateTime.currentDateTime().addSecs(15 * 60)
        self.datetime_edit.setDateTime(default_time)
        self.datetime_edit.setMinimumDateTime(QDateTime.currentDateTime().addSecs(60))

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.setFixedHeight(42)
        button_box.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(title_label)
        layout.addWidget(self.datetime_edit)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fb;
                font-family: "Microsoft YaHei";
            }

            QLabel {
                color: #111827;
                font-size: 16px;
                font-weight: bold;
                background-color: transparent;
            }

            QDateTimeEdit {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }

            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 7px 12px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }
        """)

    def get_selected_datetime(self):
        return self.datetime_edit.dateTime().toPython()