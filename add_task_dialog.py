import sys
from pathlib import Path

from PySide6.QtCore import QTime, Qt, Signal, QRectF
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QCheckBox,
    QWidget,
    QLabel,
)

from styles import get_add_task_dialog_style
from repeat_reminder_widget import RepeatReminderWidget

def get_base_dir():
    """
    获取项目基础目录。
    开发环境：项目根目录
    打包环境：exe 所在目录或 PyInstaller 临时目录
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def get_add_task_background_path():
    """
    获取添加任务弹窗背景图片路径。

    当前默认路径：
        assets/backgrounds/add_task_bg.png

    如果图片不存在，返回 None。
    styles.py 会自动使用浅灰色背景。
    """
    background_path = get_base_dir() / "assets" / "backgrounds" / "add_task_bg.png"

    if background_path.exists():
        return str(background_path).replace("\\", "/")

    return None

class ToggleSwitch(QWidget):
    toggled = Signal(bool)

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self._checked = checked
        self.setFixedSize(64, 36)

    def isChecked(self):
        return self._checked

    def setChecked(self, checked):
        checked = bool(checked)
        if self._checked == checked:
            return
        self._checked = checked
        self.update()
        self.toggled.emit(self._checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # 背景轨道
        track_rect = QRectF(2, 2, w - 4, h - 4)
        radius = track_rect.height() / 2

        if self._checked:
            track_color = QColor("#10c95b")   # 绿色
        else:
            track_color = QColor("#d1d5db")   # 灰色

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, radius, radius)

        # 滑块
        margin = 5
        thumb_diameter = h - margin * 2

        if self._checked:
            thumb_x = w - thumb_diameter - margin
        else:
            thumb_x = margin

        thumb_rect = QRectF(
            thumb_x,
            margin,
            thumb_diameter,
            thumb_diameter
        )

        painter.setBrush(QColor("#ffffff"))
        painter.setPen(QPen(QColor("#e5e7eb"), 1))
        painter.drawEllipse(thumb_rect)

        painter.end()

class AddTaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
        title="",
        remind_time=None,
        description="",
        repeat_interval_minutes=None,
        task_type="habit",
        default_remind_time=None,
        repeat_active_start=None,
        repeat_active_end=None
    ):
        super().__init__(parent)

        self.task_type = task_type or "habit"
        self.default_remind_time = default_remind_time or "10:00"
        self.repeat_active_start = repeat_active_start or "08:00"
        self.repeat_active_end = repeat_active_end or "22:00"

        self.repeat_active_widget = None
        self.repeat_active_start_combo = None
        self.repeat_active_end_combo = None

        self.setWindowTitle("添加任务" if not title else "编辑任务")
        # 固定尺寸，避免拖动或重绘时布局变形
        # 当前比例约为 1240:693
        self.setFixedSize(985, 550)
        self.setMinimumSize(985, 550)
        self.setMaximumSize(985, 550)

        self.type_left_label = QLabel("任务")
        self.type_left_label.setObjectName("typeSwitchLabel")

        self.task_type_switch = ToggleSwitch(
            checked=(self.task_type == "habit")
        )

        self.type_right_label = QLabel("习惯")
        self.type_right_label.setObjectName("typeSwitchLabel")

        self.task_type_switch.toggled.connect(self.on_task_type_changed)
        self.task_type_switch.toggled.connect(self.update_task_type_label_style)

        type_switch_layout = QHBoxLayout()
        type_switch_layout.setContentsMargins(0, 0, 0, 0)
        type_switch_layout.setSpacing(8)
        type_switch_layout.addWidget(self.type_left_label)
        type_switch_layout.addWidget(self.task_type_switch)
        type_switch_layout.addWidget(self.type_right_label)

        self.update_task_type_label_style()

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例如：背英语单词 30 个")
        self.title_edit.setText(title)

        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("任务描述（可选）")
        self.description_edit.setMaximumHeight(70)
        self.description_edit.setText(description or "")

        self.enable_time_checkbox = QCheckBox("设置提醒时间")

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")

        # 允许键盘输入，同时也允许用按钮 / 鼠标调整
        self.time_edit.setKeyboardTracking(True)
        self.time_edit.setButtonSymbols(QTimeEdit.ButtonSymbols.UpDownArrows)

        # 每点一次上下箭头，按“分钟”调整，而不是卡在小时段
        self.time_edit.setCurrentSection(QTimeEdit.Section.MinuteSection)

        # 让控件在编辑时优先处理当前 section，而不是被外部布局/焦点影响
        self.time_edit.setWrapping(True)

        self.time_minus_10_btn = QPushButton("-10")
        self.time_plus_10_btn = QPushButton("+10")
        self.time_now_btn = QPushButton("现在")

        self.time_minus_10_btn.setFixedSize(60, 30)
        self.time_plus_10_btn.setFixedSize(60, 30)
        self.time_now_btn.setFixedSize(60, 30)

        self.time_minus_10_btn.clicked.connect(lambda: self.adjust_time(-10))
        self.time_plus_10_btn.clicked.connect(lambda: self.adjust_time(10))
        self.time_now_btn.clicked.connect(self.set_time_now)

        time_control_layout = QHBoxLayout()
        time_control_layout.setSpacing(6)
        time_control_layout.addWidget(self.time_edit)
        time_control_layout.addWidget(self.time_minus_10_btn)
        time_control_layout.addWidget(self.time_plus_10_btn)
        time_control_layout.addWidget(self.time_now_btn)

        if remind_time:
            # 编辑已有提醒任务：使用任务原本的提醒时间，并自动勾选提醒
            self.enable_time_checkbox.setChecked(True)
            self.time_edit.setTime(QTime.fromString(remind_time, "HH:mm"))
            self.time_edit.setEnabled(True)
        else:
            # 新建任务或编辑无提醒任务：
            # 默认不启用提醒，但时间框预填设置页里的默认提醒时间
            self.enable_time_checkbox.setChecked(False)

            default_time = QTime.fromString(self.default_remind_time, "HH:mm")

            if not default_time.isValid():
                default_time = QTime.fromString("09:00", "HH:mm")

            self.time_edit.setTime(default_time)
            self.time_edit.setEnabled(False)

        self.time_minus_10_btn.setEnabled(self.enable_time_checkbox.isChecked())
        self.time_plus_10_btn.setEnabled(self.enable_time_checkbox.isChecked())
        self.time_now_btn.setEnabled(self.enable_time_checkbox.isChecked())

        self.repeat_widget = RepeatReminderWidget(repeat_interval_minutes)
        self.repeat_widget.set_time_enabled(self.enable_time_checkbox.isChecked())

        self.enable_time_checkbox.stateChanged.connect(self.on_time_checkbox_changed)

        self.repeat_active_widget = QWidget()
        repeat_active_layout = QHBoxLayout()
        repeat_active_layout.setContentsMargins(0, 0, 0, 0)
        repeat_active_layout.setSpacing(8)
        self.repeat_active_widget.setLayout(repeat_active_layout)

        self.repeat_active_start_combo = QComboBox()
        self.repeat_active_end_combo = QComboBox()

        time_items = [
            "00:00", "01:00", "02:00", "03:00",
            "04:00", "05:00", "06:00", "07:00",
            "08:00", "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00", "15:00",
            "16:00", "17:00", "18:00", "19:00",
            "20:00", "21:00", "22:00", "23:00",
        ]

        self.repeat_active_start_combo.addItems(time_items)
        self.repeat_active_end_combo.addItems(time_items)

        if self.repeat_active_start in time_items:
            self.repeat_active_start_combo.setCurrentText(self.repeat_active_start)
        else:
            self.repeat_active_start_combo.setCurrentText("08:00")

        if self.repeat_active_end in time_items:
            self.repeat_active_end_combo.setCurrentText(self.repeat_active_end)
        else:
            self.repeat_active_end_combo.setCurrentText("22:00")

        repeat_active_layout.addWidget(QLabel("从"))
        repeat_active_layout.addWidget(self.repeat_active_start_combo)
        repeat_active_layout.addWidget(QLabel("到"))
        repeat_active_layout.addWidget(self.repeat_active_end_combo)
        repeat_active_layout.addWidget(QLabel("期间重复提醒"))
        repeat_active_layout.addStretch()

        # 尝试监听 RepeatReminderWidget 内部的下拉框变化
        for combo in self.repeat_widget.findChildren(QComboBox):
            combo.currentIndexChanged.connect(self.update_repeat_active_visibility)

        self.enable_time_checkbox.stateChanged.connect(self.update_repeat_active_visibility)

        form_layout = QFormLayout()

        # 左侧文字放在对应输入框的正左边，并垂直居中
        form_layout.setLabelAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )

        # 右侧控件靠左排列
        form_layout.setFormAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )

        # 左侧文字和右侧输入框之间的距离
        form_layout.setHorizontalSpacing(10)

        # 每一行之间的上下距离
        form_layout.setVerticalSpacing(12)
        name_label = self.create_form_label("任务名称：", offset_y=0)
        description_label = self.create_form_label("备注说明：", offset_y=12)
        time_label = self.create_form_label("提醒时间：", offset_y=4)
        repeat_label = self.create_form_label("重复提醒：", offset_y=80)
        repeat_active_label = self.create_form_label("激活时段：", offset_y=4)

        form_layout.addRow(name_label, self.title_edit)
        form_layout.addRow(description_label, self.description_edit)
        form_layout.addRow("", self.enable_time_checkbox)
        form_layout.addRow(time_label, time_control_layout)
        form_layout.addRow(repeat_label, self.repeat_widget)
        form_layout.addRow(repeat_active_label, self.repeat_active_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        background_widget = QWidget()
        background_widget.setObjectName("addTaskBackground")

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(22, 20, 22, 18)
        main_layout.setSpacing(12)

        # “任务/习惯” 类型切换放在顶部
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addStretch()
        top_layout.addLayout(type_switch_layout)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        background_widget.setLayout(main_layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(background_widget)

        self.update_repeat_active_visibility()

        self.setLayout(outer_layout)
        self.setStyleSheet(get_add_task_dialog_style(get_add_task_background_path()))

    def create_form_label(self, text, offset_y=0):
        """
        创建表单左侧文字。

        offset_y:
            控制文字上下平移。
            正数：向下移动
            负数：向上移动
        """
        label = QLabel(text)
        label.setObjectName("formLabel")
        label.setContentsMargins(0, offset_y, 0, 0)
        return label

    def on_time_checkbox_changed(self):
        enabled = self.enable_time_checkbox.isChecked()

        self.time_edit.setEnabled(enabled)
        self.time_minus_10_btn.setEnabled(enabled)
        self.time_plus_10_btn.setEnabled(enabled)
        self.time_now_btn.setEnabled(enabled)

        self.repeat_widget.set_time_enabled(enabled)
        self.update_repeat_active_visibility()

    def is_repeat_enabled(self):
        """
        判断当前是否启用了重复提醒。
        """
        if not self.enable_time_checkbox.isChecked():
            return False

        repeat_interval_minutes = self.repeat_widget.get_repeat_interval_minutes()

        try:
            if repeat_interval_minutes is None:
                return False

            repeat_interval_minutes = int(repeat_interval_minutes)
            return repeat_interval_minutes > 0

        except (TypeError, ValueError):
            return False


    def update_repeat_active_visibility(self):
        """
        只有启用提醒时间，并且选择了重复提醒时，
        才显示“重复提醒激活时段”。
        """
        if self.repeat_active_widget is None:
            return

        self.repeat_active_widget.setVisible(self.is_repeat_enabled())

    def adjust_time(self, minutes):
        """
        用按钮调整提醒时间，不依赖键盘输入。
        """
        current_time = self.time_edit.time()
        self.time_edit.setTime(current_time.addSecs(minutes * 60))

    def set_time_now(self):
        """
        快速设置为当前时间。
        """
        self.time_edit.setTime(QTime.currentTime())

    def get_data(self):
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()

        if self.enable_time_checkbox.isChecked():
            remind_time = self.time_edit.time().toString("HH:mm")
            repeat_interval_minutes = self.repeat_widget.get_repeat_interval_minutes()
        else:
            remind_time = None
            repeat_interval_minutes = None

        task_type = "habit" if self.task_type_switch.isChecked() else "task"

        repeat_active_start = None
        repeat_active_end = None

        if repeat_interval_minutes is not None:
            try:
                repeat_interval_value = int(repeat_interval_minutes)
            except (TypeError, ValueError):
                repeat_interval_value = 0

            if repeat_interval_value > 0:
                repeat_active_start = None
                repeat_active_end = None

                if repeat_interval_minutes is not None:
                    try:
                        repeat_interval_value = int(repeat_interval_minutes)
                    except (TypeError, ValueError):
                        repeat_interval_value = 0

                    if (
                        repeat_interval_value > 0
                        and self.repeat_active_start_combo is not None
                        and self.repeat_active_end_combo is not None
                    ):
                        repeat_active_start = self.repeat_active_start_combo.currentText()
                        repeat_active_end = self.repeat_active_end_combo.currentText()

        return (
            title,
            remind_time,
            description,
            repeat_interval_minutes,
            task_type,
            repeat_active_start,
            repeat_active_end
        )

    def on_task_type_changed(self, checked):
        """
        未选中：task
        选中：habit
        """
        if checked:
            self.task_type = "habit"
        else:
            self.task_type = "task"

    def update_task_type_label_style(self, checked=None):
        """
        根据当前任务类型，更新“任务 / 习惯”文字高亮。

        不在这里写具体颜色和字体。
        具体样式统一放在 styles.py：
            #typeSwitchLabelActive
            #typeSwitchLabelInactive
        """
        if not hasattr(self, "task_type_switch"):
            return

        if self.task_type_switch.isChecked():
            # 当前是“习惯”
            self.type_left_label.setObjectName("typeSwitchLabelInactive")
            self.type_right_label.setObjectName("typeSwitchLabelActive")
        else:
            # 当前是“任务”
            self.type_left_label.setObjectName("typeSwitchLabelActive")
            self.type_right_label.setObjectName("typeSwitchLabelInactive")

        # objectName 改变后，需要重新刷新样式
        self.type_left_label.style().unpolish(self.type_left_label)
        self.type_left_label.style().polish(self.type_left_label)
        self.type_left_label.update()

        self.type_right_label.style().unpolish(self.type_right_label)
        self.type_right_label.style().polish(self.type_right_label)
        self.type_right_label.update()