from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)


class CountdownPage(QWidget):
    """
    倒计时页面。

    第一版功能：
        1. 显示一个大号倒计时
        2. 支持 5 / 10 / 25 / 45 分钟快捷设置
        3. 支持自定义分钟数
        4. 支持开始 / 暂停 / 重置
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.total_seconds = 25 * 60
        self.remaining_seconds = self.total_seconds
        self.is_running = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)

        self.init_ui()
        self.apply_styles()
        self.update_time_label()
        self.update_button_state()
        self.update_custom_time_edit()

    def init_ui(self):
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.setLayout(root_layout)

        self.panel = QFrame()
        self.panel.setObjectName("countdownPanel")

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(36, 34, 36, 34)
        panel_layout.setSpacing(22)
        self.panel.setLayout(panel_layout)

        title_label = QLabel("专注倒计时")
        title_label.setObjectName("countdownTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("先专注一小段时间，咸鱼会替你盯着。")
        subtitle_label.setObjectName("countdownSubtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.time_label = QLabel("25:00")
        self.time_label.setObjectName("countdownTime")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        preset_layout = QHBoxLayout()
        preset_layout.setSpacing(10)

        self.btn_5 = QPushButton("5 分钟")
        self.btn_10 = QPushButton("10 分钟")
        self.btn_25 = QPushButton("25 分钟")
        self.btn_45 = QPushButton("45 分钟")

        preset_buttons = [
            self.btn_5,
            self.btn_10,
            self.btn_25,
            self.btn_45,
        ]

        for button in preset_buttons:
            button.setObjectName("countdownPresetButton")
            button.setFixedHeight(36)
            preset_layout.addWidget(button)

        self.btn_5.clicked.connect(lambda: self.set_minutes(5))
        self.btn_10.clicked.connect(lambda: self.set_minutes(10))
        self.btn_25.clicked.connect(lambda: self.set_minutes(25))
        self.btn_45.clicked.connect(lambda: self.set_minutes(45))

        custom_layout = QHBoxLayout()
        custom_layout.setSpacing(10)

        custom_label = QLabel("自定义：")
        custom_label.setObjectName("countdownCustomLabel")
        custom_label.setFixedHeight(38)
        custom_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        self.custom_time_edit = QTimeEdit()
        self.custom_time_edit.setObjectName("countdownTimeEdit")

        # 三块：小时 / 分钟 / 秒
        # 默认 00小时 00分钟 00秒
        self.custom_time_edit.setDisplayFormat("HH小时 mm分钟 ss秒")
        self.custom_time_edit.setTime(QTime(0, 0, 0))

        # 隐藏 QTimeEdit 自带的内部上下箭头。
        # 后面使用外部按钮控制，避免点击箭头时误切换输入区域。
        self.custom_time_edit.setButtonSymbols(QTimeEdit.ButtonSymbols.NoButtons)
        self.custom_time_edit.setKeyboardTracking(True)
        self.custom_time_edit.setWrapping(True)
        self.custom_time_edit.setCurrentSection(QTimeEdit.Section.MinuteSection)

        self.custom_time_edit.setFixedHeight(38)
        self.custom_time_edit.setFixedWidth(150)

        time_adjust_layout = QHBoxLayout()
        time_adjust_layout.setContentsMargins(0, 0, 0, 0)
        time_adjust_layout.setSpacing(6)

        self.custom_time_up_btn = QPushButton("▲")
        self.custom_time_down_btn = QPushButton("▼")

        self.custom_time_up_btn.setObjectName("countdownAdjustButton")
        self.custom_time_down_btn.setObjectName("countdownAdjustButton")

        self.custom_time_up_btn.setFixedSize(42, 38)
        self.custom_time_down_btn.setFixedSize(42, 38)

        self.custom_time_up_btn.clicked.connect(
            lambda: self.adjust_custom_time_section(1)
        )
        self.custom_time_down_btn.clicked.connect(
            lambda: self.adjust_custom_time_section(-1)
        )

        # 左边是上箭头，右边是下箭头
        time_adjust_layout.addWidget(self.custom_time_up_btn)
        time_adjust_layout.addWidget(self.custom_time_down_btn)

        self.custom_apply_btn = QPushButton("应用")
        self.custom_apply_btn.setObjectName("countdownSecondaryButton")
        self.custom_apply_btn.setFixedHeight(38)
        self.custom_apply_btn.setFixedWidth(76)

        self.custom_apply_btn.clicked.connect(self.apply_custom_time)

        custom_layout.addStretch()
        custom_layout.addWidget(custom_label)
        custom_layout.addWidget(self.custom_time_edit)
        custom_layout.addLayout(time_adjust_layout)
        custom_layout.addWidget(self.custom_apply_btn)
        custom_layout.addStretch()

        control_layout = QHBoxLayout()
        control_layout.setSpacing(12)

        self.start_pause_btn = QPushButton("开始")
        self.reset_btn = QPushButton("重置")

        self.start_pause_btn.setObjectName("countdownPrimaryButton")
        self.reset_btn.setObjectName("countdownSecondaryButton")

        self.start_pause_btn.setFixedHeight(42)
        self.reset_btn.setFixedHeight(42)

        self.start_pause_btn.clicked.connect(self.toggle_start_pause)
        self.reset_btn.clicked.connect(self.reset_countdown)

        control_layout.addStretch()
        control_layout.addWidget(self.start_pause_btn)
        control_layout.addWidget(self.reset_btn)
        control_layout.addStretch()

        hint_label = QLabel("提示：倒计时期间切回“今日任务”也不会中断。")
        hint_label.setObjectName("countdownHint")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        panel_layout.addStretch()
        panel_layout.addWidget(title_label)
        panel_layout.addWidget(subtitle_label)
        panel_layout.addWidget(self.time_label)
        panel_layout.addLayout(preset_layout)
        panel_layout.addLayout(custom_layout)
        panel_layout.addLayout(control_layout)
        panel_layout.addWidget(hint_label)
        panel_layout.addStretch()

        root_layout.addWidget(self.panel)

    def apply_styles(self):
        self.setStyleSheet("""
            #countdownPanel {
                background-color: rgba(255, 255, 255, 235);
                border: 1px solid #d1d5db;
                border-radius: 12px;
            }

            #countdownTitle {
                color: #111827;
                font-size: 26px;
                font-weight: 800;
                background-color: transparent;
            }

            #countdownSubtitle {
                color: #6b7280;
                font-size: 15px;
                background-color: transparent;
            }

            #countdownTime {
                color: #111827;
                font-size: 72px;
                font-weight: 900;
                background-color: transparent;
                letter-spacing: 2px;
            }

            #countdownCustomLabel {
                color: #374151;
                font-size: 14px;
                font-weight: 600;
                background-color: transparent;
            }

            #countdownTimeEdit {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 5px 8px;
                font-size: 13px;
                min-width: 150px;
                max-width: 150px;
            }

            #countdownTimeEdit:focus {
                border: 1px solid #2563eb;
            }

            #countdownAdjustButton {
                background-color: #e5e7eb;
                color: #374151;
                border: none;
                border-radius: 10px;
                padding: 0px;
                font-size: 17px;
                font-weight: 800;
            }

            #countdownAdjustButton:hover {
                background-color: #d1d5db;
            }

            #countdownAdjustButton:pressed {
                background-color: #9ca3af;
            }

            QPushButton {
                border: none;
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 14px;
                font-weight: 700;
            }

            #countdownPresetButton {
                background-color: #eef2ff;
                color: #1e3a8a;
            }

            #countdownPresetButton:hover {
                background-color: #dbeafe;
            }

            #countdownPrimaryButton {
                background-color: #2563eb;
                color: #ffffff;
                min-width: 120px;
            }

            #countdownPrimaryButton:hover {
                background-color: #1d4ed8;
            }

            #countdownSecondaryButton {
                background-color: #e5e7eb;
                color: #111827;
                min-width: 90px;
            }

            #countdownSecondaryButton:hover {
                background-color: #d1d5db;
            }

            #countdownHint {
                color: #9ca3af;
                font-size: 13px;
                background-color: transparent;
            }
        """)

    def get_custom_total_seconds(self):
        """
        获取自定义倒计时时长，单位：秒。

        QTimeEdit 分为：
            HH 小时
            mm 分钟
            ss 秒
        """
        custom_time = self.custom_time_edit.time()

        hours = custom_time.hour()
        minutes = custom_time.minute()
        seconds = custom_time.second()

        return hours * 3600 + minutes * 60 + seconds

    def adjust_custom_time_section(self, step):
        """
        调整自定义时间输入框当前选中的部分。

        当前选中小时：调整小时
        当前选中分钟：调整分钟
        当前选中秒：调整秒
        """
        current_time = self.custom_time_edit.time()
        current_section = self.custom_time_edit.currentSection()

        hours = current_time.hour()
        minutes = current_time.minute()
        seconds = current_time.second()

        if current_section == QTimeEdit.Section.HourSection:
            hours = (hours + step) % 24
        elif current_section == QTimeEdit.Section.MinuteSection:
            minutes = (minutes + step) % 60
        elif current_section == QTimeEdit.Section.SecondSection:
            seconds = (seconds + step) % 60
        else:
            minutes = (minutes + step) % 60

        self.custom_time_edit.setTime(QTime(hours, minutes, seconds))

    def apply_custom_time(self):
        """
        应用自定义倒计时时长。
        """
        if self.is_running:
            QMessageBox.information(
                self,
                "倒计时进行中",
                "请先暂停或重置当前倒计时，再修改时长。"
            )
            return

        total_seconds = self.get_custom_total_seconds()

        if total_seconds <= 0:
            QMessageBox.information(
                self,
                "时间太短啦",
                "请至少设置 1 秒钟。"
            )
            return

        self.set_total_seconds(total_seconds)

    def set_total_seconds(self, seconds):
        """
        设置倒计时时长，单位：秒。
        """
        if self.is_running:
            QMessageBox.information(
                self,
                "倒计时进行中",
                "请先暂停或重置当前倒计时，再修改时长。"
            )
            return

        seconds = int(seconds)

        if seconds <= 0:
            seconds = 1

        self.total_seconds = seconds
        self.remaining_seconds = self.total_seconds

        self.update_custom_time_edit()
        self.update_time_label()
        self.update_button_state()

    def set_minutes(self, minutes):
        """
        设置倒计时时长，单位：分钟。
        """
        self.set_total_seconds(int(minutes) * 60)

    def update_custom_time_edit(self):
        """
        根据当前 total_seconds 同步自定义时间输入框。
        """
        hours = self.total_seconds // 3600
        minutes = (self.total_seconds % 3600) // 60
        seconds = self.total_seconds % 60

        # QTimeEdit 的小时范围是 0~23。
        # 当前倒计时作为专注计时器，先限制到 23:59:59 以内。
        if hours > 23:
            hours = 23
            minutes = 59
            seconds = 59

        self.custom_time_edit.setTime(QTime(hours, minutes, seconds))

    def toggle_start_pause(self):
        """
        开始或暂停倒计时。
        """
        if self.is_running:
            self.pause_countdown()
        else:
            self.start_countdown()

    def start_countdown(self):
        """
        开始倒计时。
        """
        if self.remaining_seconds <= 0:
            self.remaining_seconds = self.total_seconds

        self.is_running = True
        self.timer.start(1000)
        self.update_button_state()

    def pause_countdown(self):
        """
        暂停倒计时。
        """
        self.is_running = False
        self.timer.stop()
        self.update_button_state()

    def reset_countdown(self):
        """
        重置倒计时。
        """
        self.is_running = False
        self.timer.stop()
        self.remaining_seconds = self.total_seconds
        self.update_time_label()
        self.update_button_state()

    def tick(self):
        """
        每秒更新倒计时。
        """
        if self.remaining_seconds <= 0:
            self.finish_countdown()
            return

        self.remaining_seconds -= 1
        self.update_time_label()

        if self.remaining_seconds <= 0:
            self.finish_countdown()

    def finish_countdown(self):
        """
        倒计时结束。
        """
        self.is_running = False
        self.timer.stop()
        self.remaining_seconds = 0
        self.update_time_label()
        self.update_button_state()

        QMessageBox.information(
            self,
            "倒计时结束",
            "时间到啦，🐟宣布你刚刚认真过一小会儿。"
        )

    def update_time_label(self):
        """
        刷新倒计时显示。
        """
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60

        if hours > 0:
            self.time_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        else:
            self.time_label.setText(f"{minutes:02d}:{seconds:02d}")

    def update_button_state(self):
        """
        刷新按钮文字和可用状态。
        """
        if self.is_running:
            self.start_pause_btn.setText("暂停")
        else:
            self.start_pause_btn.setText("开始")

        can_change_duration = not self.is_running

        self.btn_5.setEnabled(can_change_duration)
        self.btn_10.setEnabled(can_change_duration)
        self.btn_25.setEnabled(can_change_duration)
        self.btn_45.setEnabled(can_change_duration)
        self.custom_time_edit.setEnabled(can_change_duration)
        self.custom_time_up_btn.setEnabled(can_change_duration)
        self.custom_time_down_btn.setEnabled(can_change_duration)
        self.custom_apply_btn.setEnabled(can_change_duration)