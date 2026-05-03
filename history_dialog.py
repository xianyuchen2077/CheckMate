from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
)

import database


class HistoryDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("打卡历史记录")
        self.resize(520, 520)

        self.init_ui()
        self.load_history()

    def init_ui(self):
        layout = QVBoxLayout()

        title_label = QLabel("最近 7 天打卡记录")
        title_label.setObjectName("historyTitle")

        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)

        layout.addWidget(title_label)
        layout.addWidget(self.history_text)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7fb;
                color: #111827;
                font-family: "Microsoft YaHei";
            }

            QLabel {
                color: #111827;
                background-color: transparent;
            }

            #historyTitle {
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 8px;
            }

            QTextEdit {
                background-color: #ffffff;
                color: #111827;
                border: 1px solid #d1d5db;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
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
            }
        """)

    def load_history(self):
        history = database.get_history_records(days=7)

        lines = []

        for day in history:
            lines.append(f"📅 {day['date']}")

            if not day["tasks"]:
                lines.append("  暂无任务")
            else:
                for task in day["tasks"]:
                    icon = "✅" if task["done"] else "❌"
                    lines.append(f"  {icon} {task['title']}")

                    if task.get("description"):
                        lines.append(f"     备注：{task['description']}")

            lines.append("")

        self.history_text.setPlainText("\n".join(lines))