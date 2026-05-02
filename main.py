import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
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
    QInputDialog,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CheckMate - 不要成为咸鱼")
        self.resize(900, 600)

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        # ===== 中央组件 =====
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        central_widget.setLayout(main_layout)

        # ================= 左侧区域 =================
        left_panel = QVBoxLayout()
        left_panel.setSpacing(15)

        # 标题区
        title_label = QLabel("CheckMate")
        title_label.setObjectName("titleLabel")

        subtitle_label = QLabel("不要成为咸鱼 · 你的桌面打卡督促助手")
        subtitle_label.setObjectName("subtitleLabel")

        left_panel.addWidget(title_label)
        left_panel.addWidget(subtitle_label)

        # 今日任务卡片
        task_card = QFrame()
        task_card.setObjectName("card")
        task_layout = QVBoxLayout()
        task_layout.setSpacing(12)
        task_card.setLayout(task_layout)

        task_title = QLabel("今日任务")
        task_title.setObjectName("sectionTitle")

        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")

        # 先加几条示例数据
        sample_tasks = [
            "背英语单词 30 个",
            "复习离散数学 40 分钟",
            "写代码 30 分钟",
        ]
        for task in sample_tasks:
            self.task_list.addItem(QListWidgetItem(task))

        task_layout.addWidget(task_title)
        task_layout.addWidget(self.task_list)

        # 按钮区域
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

        # 统计卡片
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

        # 提示卡片
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

        # 左右布局占比
        main_layout.addLayout(left_panel, 3)
        main_layout.addLayout(right_panel, 1)

        # 初始化统计
        self.update_stats()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f7fb;
            }

            QLabel {
                color: #1f2937;
                font-size: 14px;
            }

            #titleLabel {
                font-size: 32px;
                font-weight: bold;
                color: #111827;
            }

            #subtitleLabel {
                font-size: 15px;
                color: #6b7280;
                margin-bottom: 10px;
            }

            #sectionTitle {
                font-size: 20px;
                font-weight: bold;
                color: #111827;
                margin-bottom: 6px;
            }

            #card {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 14px;
            }

            QListWidget {
                background-color: #fcfcfd;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 8px;
                font-size: 15px;
            }

            QListWidget::item {
                padding: 10px;
                border-radius: 8px;
            }

            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #111827;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background-color: #1d4ed8;
            }

            QPushButton:pressed {
                background-color: #1e40af;
            }

            #tipLabel {
                color: #374151;
                font-size: 14px;
                line-height: 1.6;
            }
        """)

    def add_task(self):
        text, ok = QInputDialog.getText(self, "添加任务", "请输入任务内容：")
        if ok and text.strip():
            self.task_list.addItem(text.strip())
            self.tip_label.setText(f"新任务已添加：{text.strip()}")
            self.update_stats()

    def complete_task(self):
        current_item = self.task_list.currentItem()
        if current_item is None:
            QMessageBox.information(self, "提示", "请先选择一个任务。")
            return

        text = current_item.text()
        if not text.startswith("✅ "):
            current_item.setText("✅ " + text)
            self.tip_label.setText("不错，今天没有变咸鱼。")
        else:
            QMessageBox.information(self, "提示", "这个任务已经完成打卡了。")

        self.update_stats()

    def delete_task(self):
        current_row = self.task_list.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "提示", "请先选择一个任务。")
            return

        item_text = self.task_list.item(current_row).text()
        self.task_list.takeItem(current_row)
        self.tip_label.setText(f"已删除任务：{item_text}")
        self.update_stats()

    def update_stats(self):
        total = self.task_list.count()
        done = 0

        for i in range(total):
            text = self.task_list.item(i).text()
            if text.startswith("✅ "):
                done += 1

        self.today_stat.setText(f"今日完成：{done} / {total}")
        self.streak_stat.setText(f"连续打卡：{done} 天")
        percent = int((done / total) * 100) if total > 0 else 0
        self.month_stat.setText(f"本月完成率：{percent}%")

        fish_value = max(0, 100 - done * 15)
        self.fish_stat.setText(f"咸鱼值：{fish_value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 可选：设置全局字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())