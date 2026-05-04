import re

from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QVBoxLayout,
)

from styles import get_repeat_reminder_widget_style

class RepeatReminderWidget(QWidget):
    """
    重复提醒设置组件。

    返回值：
        None：不重复提醒
        int：重复提醒间隔分钟数

    支持：
        每隔 30 分钟提醒一次
        每隔 1 小时提醒一次
        每隔 2 小时提醒一次
        每隔 4 小时提醒一次
        自定义，例如：1h30min、2h、45min、1小时20分钟
    """

    def __init__(self, repeat_interval_minutes=None, parent=None):
        super().__init__(parent)

        self.init_ui()
        self.apply_styles()
        self.set_repeat_interval(repeat_interval_minutes)

    def init_ui(self):
        self.enable_repeat_checkbox = QCheckBox("重复提醒")
        self.enable_repeat_checkbox.setObjectName("repeatCheckBox")

        self.repeat_combo = QComboBox()
        self.repeat_combo.setObjectName("repeatComboBox")
        self.repeat_combo.addItem("每隔 30 分钟提醒一次", 30)
        self.repeat_combo.addItem("每隔 1 小时提醒一次", 60)
        self.repeat_combo.addItem("每隔 2 小时提醒一次", 120)
        self.repeat_combo.addItem("每隔 4 小时提醒一次", 240)
        self.repeat_combo.addItem("自定义提醒间隔", -1)
        self.repeat_combo.setEnabled(False)

        # 自定义输入框区域
        self.custom_input = QLineEdit()
        self.custom_input.setObjectName("repeatCustomInput")
        self.custom_input.setPlaceholderText("例如：1h30min / 45min / 2h")
        self.custom_input.setFixedHeight(30)

        # 时钟单独放在输入框右侧，不再和输入框共用边框
        self.side_clock_label = QLabel("⏰")
        self.side_clock_label.setObjectName("repeatSideClockLabel")
        self.side_clock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.side_clock_label.setFixedSize(50, 50)

        self.custom_row_layout = QHBoxLayout()
        self.custom_row_layout.setContentsMargins(0, 0, 0, 0)
        self.custom_row_layout.setSpacing(12)
        self.custom_row_layout.addWidget(self.custom_input)
        self.custom_row_layout.addWidget(self.side_clock_label)
        self.custom_row_layout.addStretch()

        self.custom_input_widget = QWidget()
        self.custom_input_widget.setLayout(self.custom_row_layout)
        self.custom_input_widget.setVisible(False)

        self.enable_repeat_checkbox.stateChanged.connect(
            self.on_repeat_checkbox_changed
        )
        self.repeat_combo.currentIndexChanged.connect(
            self.on_repeat_option_changed
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.addWidget(self.enable_repeat_checkbox)
        layout.addWidget(self.repeat_combo)
        layout.addWidget(self.custom_input_widget)

        self.setLayout(layout)

    def apply_styles(self):
        self.setStyleSheet(get_repeat_reminder_widget_style())

    def set_time_enabled(self, enabled):
        """
        外部提醒时间关闭时，重复提醒也应该关闭。
        """
        self.setEnabled(enabled)

        if not enabled:
            self.enable_repeat_checkbox.setChecked(False)
            self.repeat_combo.setEnabled(False)
            self.custom_input_widget.setVisible(False)
            self.custom_input.clear()
            return

        self.repeat_combo.setEnabled(self.enable_repeat_checkbox.isChecked())
        self.update_custom_input_visibility()

    def on_repeat_checkbox_changed(self):
        enabled = self.enable_repeat_checkbox.isChecked()
        self.repeat_combo.setEnabled(enabled)

        if not enabled:
            self.custom_input_widget.setVisible(False)
        else:
            self.update_custom_input_visibility()

    def on_repeat_option_changed(self):
        self.update_custom_input_visibility()

    def update_custom_input_visibility(self):
        """
        只有选择“自定义提醒间隔”时，才显示自定义输入框。
        """
        if not self.enable_repeat_checkbox.isChecked():
            self.custom_input_widget.setVisible(False)
            return

        interval = self.repeat_combo.currentData()
        self.custom_input_widget.setVisible(interval == -1)

    def set_repeat_interval(self, repeat_interval_minutes):
        """
        编辑任务时，把已有重复提醒间隔显示到 UI 上。
        """
        if not repeat_interval_minutes:
            self.enable_repeat_checkbox.setChecked(False)
            self.repeat_combo.setEnabled(False)
            self.custom_input_widget.setVisible(False)
            self.custom_input.clear()
            return

        self.enable_repeat_checkbox.setChecked(True)
        self.repeat_combo.setEnabled(True)

        if repeat_interval_minutes == 30:
            self.repeat_combo.setCurrentIndex(0)
            self.custom_input_widget.setVisible(False)
        elif repeat_interval_minutes == 60:
            self.repeat_combo.setCurrentIndex(1)
            self.custom_input_widget.setVisible(False)
        elif repeat_interval_minutes == 120:
            self.repeat_combo.setCurrentIndex(2)
            self.custom_input_widget.setVisible(False)
        elif repeat_interval_minutes == 240:
            self.repeat_combo.setCurrentIndex(3)
            self.custom_input_widget.setVisible(False)
        else:
            self.repeat_combo.setCurrentIndex(4)
            self.custom_input.setText(self.format_minutes_to_text(repeat_interval_minutes))
            self.custom_input_widget.setVisible(True)

    def get_repeat_interval_minutes(self):
        """
        获取重复提醒间隔。

        返回：
            None：未开启重复提醒，或自定义输入无效
            int：重复提醒间隔分钟数
        """
        if not self.isEnabled():
            return None

        if not self.enable_repeat_checkbox.isChecked():
            return None

        interval = self.repeat_combo.currentData()

        if interval != -1:
            return interval

        custom_text = self.custom_input.text().strip()
        return self.parse_custom_interval(custom_text)

    def parse_custom_interval(self, text):
        """
        解析自定义时间。

        支持格式：
            1h30min
            2h
            45min
            1小时30分钟
            90分钟
            90
        """
        if not text:
            return None

        text = text.lower()
        text = text.replace(" ", "")
        text = text.replace("小时", "h")
        text = text.replace("分钟", "min")
        text = text.replace("分", "min")

        # 纯数字默认按分钟处理，例如 90 -> 90min
        if text.isdigit():
            minutes = int(text)
            return minutes if minutes > 0 else None

        hour_match = re.search(r"(\d+)h", text)
        minute_match = re.search(r"(\d+)min", text)

        hours = int(hour_match.group(1)) if hour_match else 0
        minutes = int(minute_match.group(1)) if minute_match else 0

        total_minutes = hours * 60 + minutes

        if total_minutes <= 0:
            return None

        # 最多允许 24 小时
        if total_minutes > 24 * 60:
            return None

        return total_minutes

    def format_minutes_to_text(self, minutes):
        """
        把分钟数格式化成 xxhxxmin。
        """
        hours = minutes // 60
        remain_minutes = minutes % 60

        if hours > 0 and remain_minutes > 0:
            return f"{hours}h{remain_minutes}min"

        if hours > 0:
            return f"{hours}h"

        return f"{remain_minutes}min"