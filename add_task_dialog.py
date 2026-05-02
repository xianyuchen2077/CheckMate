from PySide6.QtCore import QTime
from PySide6.QtWidgets import (
    QDialog,
    QLineEdit,
    QTimeEdit,
    QFormLayout,
    QDialogButtonBox,
    QVBoxLayout,
)

from styles import ADD_TASK_DIALOG_STYLE


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("添加任务")
        self.resize(360, 180)

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("例如：背英语单词 30 个")

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())

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
        self.setStyleSheet(ADD_TASK_DIALOG_STYLE)

    def get_data(self):
        title = self.title_edit.text().strip()
        remind_time = self.time_edit.time().toString("HH:mm")
        return title, remind_time