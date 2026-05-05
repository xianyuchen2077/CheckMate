import sys
from pathlib import Path

from PySide6.QtCore import QTime, Qt
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

class AddTaskDialog(QDialog):
    def __init__(
        self,
        parent=None,
        title="",
        remind_time=None,
        description="",
        repeat_interval_minutes=None,
        task_type="habit"
    ):
        super().__init__(parent)

        self.task_type = task_type or "habit"

        self.setWindowTitle("添加任务" if not title else "编辑任务")
        # 固定尺寸，避免拖动或重绘时布局变形
        # 当前比例约为 1240:693
        self.setFixedSize(805, 450)
        self.setMinimumSize(805, 450)
        self.setMaximumSize(805, 450)

        self.type_left_label = QLabel("任务")
        self.type_left_label.setObjectName("typeSwitchLabel")

        self.task_type_switch = QCheckBox()
        self.task_type_switch.setObjectName("taskTypeSwitch")

        self.type_right_label = QLabel("习惯")
        self.type_right_label.setObjectName("typeSwitchLabel")

        # 约定：
        # 未选中 = task 一次性任务
        # 选中 = habit 长期习惯
        self.task_type_switch.setChecked(self.task_type == "habit")

        self.task_type_switch.stateChanged.connect(self.on_task_type_changed)

        type_switch_layout = QHBoxLayout()
        type_switch_layout.setSpacing(6)
        type_switch_layout.addWidget(self.type_left_label)
        type_switch_layout.addWidget(self.task_type_switch)
        type_switch_layout.addWidget(self.type_right_label)
        type_switch_layout.addStretch()

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
            self.enable_time_checkbox.setChecked(True)
            self.time_edit.setTime(QTime.fromString(remind_time, "HH:mm"))
            self.time_edit.setEnabled(True)
        else:
            self.enable_time_checkbox.setChecked(False)
            self.time_edit.setTime(QTime.currentTime())
            self.time_edit.setEnabled(False)

        self.time_minus_10_btn.setEnabled(self.enable_time_checkbox.isChecked())
        self.time_plus_10_btn.setEnabled(self.enable_time_checkbox.isChecked())
        self.time_now_btn.setEnabled(self.enable_time_checkbox.isChecked())

        self.repeat_widget = RepeatReminderWidget(repeat_interval_minutes)
        self.repeat_widget.set_time_enabled(self.enable_time_checkbox.isChecked())

        self.enable_time_checkbox.stateChanged.connect(self.on_time_checkbox_changed)

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
        repeat_label = self.create_form_label("重复提醒：", offset_y=54)

        form_layout.addRow(name_label, self.title_edit)
        form_layout.addRow(description_label, self.description_edit)
        form_layout.addRow("", self.enable_time_checkbox)
        form_layout.addRow(time_label, time_control_layout)
        form_layout.addRow(repeat_label, self.repeat_widget)

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

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addLayout(type_switch_layout)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        background_widget.setLayout(main_layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(background_widget)

        self.setLayout(outer_layout)
        self.setStyleSheet(get_add_task_dialog_style(get_add_task_background_path()))

        base_style = get_add_task_dialog_style(get_add_task_background_path())
        self.setStyleSheet(base_style + """
            #typeSwitchLabel {
                color: #111827;
                font-size: 13px;
                font-weight: 700;
                background-color: transparent;
            }

            #taskTypeSwitch {
                spacing: 6px;
                background-color: transparent;
            }

            #taskTypeSwitch::indicator {
                width: 46px;
                height: 24px;
            }
        """)

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
        else:
            remind_time = None

        repeat_interval_minutes = self.repeat_widget.get_repeat_interval_minutes()

        task_type = "habit" if self.task_type_switch.isChecked() else "task"

        return title, remind_time, description, repeat_interval_minutes, task_type

    def on_task_type_changed(self):
        """
        切换任务类型。
        未选中：任务 task
        选中：习惯 habit
        """
        if self.task_type_switch.isChecked():
            self.task_type = "habit"
        else:
            self.task_type = "task"