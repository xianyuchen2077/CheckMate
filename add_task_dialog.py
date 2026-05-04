import sys
from pathlib import Path

from PySide6.QtCore import QTime
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
        repeat_interval_minutes=None
    ):
        super().__init__(parent)

        self.setWindowTitle("添加任务" if not title else "编辑任务")
        # 固定尺寸，避免拖动或重绘时布局变形
        # 当前比例约为 1240:693
        self.setFixedSize(805, 450)
        self.setMinimumSize(805, 450)
        self.setMaximumSize(805, 450)

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
        form_layout.setSpacing(12)
        form_layout.addRow("任务名称：", self.title_edit)
        form_layout.addRow("备注说明：", self.description_edit)
        form_layout.addRow("", self.enable_time_checkbox)
        form_layout.addRow("提醒时间：", time_control_layout)
        form_layout.addRow("重复提醒：", self.repeat_widget)

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
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.button_box)

        background_widget.setLayout(main_layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(background_widget)

        self.setLayout(outer_layout)
        self.setStyleSheet(get_add_task_dialog_style(get_add_task_background_path()))

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

        return title, remind_time, description, repeat_interval_minutes