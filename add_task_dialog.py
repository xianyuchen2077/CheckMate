from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QTimeEdit,
    QFormLayout,
    QDialogButtonBox,
    QVBoxLayout,
    QCheckBox,
    QTextEdit,
)

from styles import ADD_TASK_DIALOG_STYLE

class AddTaskDialog(QDialog):
    def __init__(self, parent=None, title="", remind_time=None, description=""):
        super().__init__(parent)

        self.setWindowTitle("添加任务" if not title else "编辑任务")
        self.resize(380, 210)

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

        if remind_time:
            self.enable_time_checkbox.setChecked(True)
            self.time_edit.setTime(QTime.fromString(remind_time, "HH:mm"))
            self.time_edit.setEnabled(True)
        else:
            self.enable_time_checkbox.setChecked(False)
            self.time_edit.setTime(QTime.currentTime())
            self.time_edit.setEnabled(False)

        self.enable_time_checkbox.stateChanged.connect(self.on_time_checkbox_changed)

        form_layout = QFormLayout()
        form_layout.addRow("任务名称：", self.title_edit)
        form_layout.addRow("备注说明：", self.description_edit)
        form_layout.addRow("", self.enable_time_checkbox)
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
        self.setStyleSheet(ADD_TASK_DIALOG_STYLE)

    def on_time_checkbox_changed(self):
        self.time_edit.setEnabled(self.enable_time_checkbox.isChecked())

    def get_data(self):
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()

        if self.enable_time_checkbox.isChecked():
            remind_time = self.time_edit.time().toString("HH:mm")
        else:
            remind_time = None

        return title, remind_time, description