from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
)


class PetWindow(QWidget):
    def __init__(self, main_window=None):
        super().__init__()

        self.main_window = main_window
        self.drag_position = QPoint()
        self.is_dragging = False

        self.setMouseTracking(True)

        self.setWindowTitle("CheckMate Pet")

        # 无边框、置顶、工具窗口
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        # 背景透明
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.init_ui()
        self.move_to_bottom_right()

    def init_ui(self):
        self.container = QFrame()
        self.container.setObjectName("petContainer")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.container.setGraphicsEffect(shadow)

        self.pet_face = QLabel("🐟")
        self.pet_face.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_face.setObjectName("petFace")

        self.pet_text = QLabel("今天不要成为咸鱼")
        self.pet_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_text.setWordWrap(True)
        self.pet_text.setObjectName("petText")

        self.container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.pet_face.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.pet_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        layout.addWidget(self.pet_face)
        layout.addWidget(self.pet_text)

        self.container.setLayout(layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.addWidget(self.container)

        self.setLayout(outer_layout)
        self.setFixedSize(190, 150)

        self.setStyleSheet("""
            #petContainer {
                background-color: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 20px;
            }

            #petFace {
                font-size: 44px;
                background-color: transparent;
                color: #111827;
            }

            #petText {
                font-size: 13px;
                font-weight: 600;
                color: #111827;
                background-color: transparent;
            }
        """)

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()

        x = screen.right() - self.width() - 30
        y = screen.bottom() - self.height() - 30

        self.move(x, y)

    def set_idle(self):
        self.pet_face.setText("🐟")
        self.pet_text.setText("今天不要成为咸鱼")

    def set_reminding(self, task_title):
        self.pet_face.setText("⚠️")
        self.pet_text.setText(f"该打卡啦：{task_title}")

    def set_done(self):
        self.pet_face.setText("😎")
        self.pet_text.setText("不错，今天没当咸鱼")

    def set_lazy(self):
        self.pet_face.setText("🫠")
        self.pet_text.setText("再拖就要咸起来了")

    def set_sleeping(self):
        self.pet_face.setText("💤")
        self.pet_text.setText("暂时休息一下")

    def mousePressEvent(self, event):
        """
        鼠标左键按下时，记录鼠标相对窗口左上角的位置。
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        """
        鼠标左键拖动时，移动整个宠物窗口。
        """
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


    def mouseReleaseEvent(self, event):
        """
        鼠标松开时，结束拖动。
        """
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            event.accept()


    def mouseDoubleClickEvent(self, event):
        """
        双击宠物窗口，打开主窗口。
        """
        if event.button() == Qt.MouseButton.LeftButton:
            if self.main_window is not None:
                self.main_window.show_main_window()
            event.accept()