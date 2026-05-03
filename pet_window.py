from pathlib import Path
import random

from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QColor, QPixmap, QAction
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QMenu,
)


ASSETS_DIR = Path(__file__).resolve().parent / "assets"


class PetWindow(QWidget):
    def __init__(self, main_window=None):
        super().__init__()

        self.main_window = main_window
        self.drag_position = QPoint()
        self.is_dragging = False
        self.is_reminding = False
        self.is_status_locked = False
        self.press_global_pos = QPoint()

        self.setMouseTracking(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        self.setWindowTitle("CheckMate Pet")

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.image_paths = {
            "idle": ASSETS_DIR / "pet_idle.png",
            "remind": ASSETS_DIR / "pet_remind.png",
            "done": ASSETS_DIR / "pet_done.png",
            "lazy": ASSETS_DIR / "pet_lazy.png",
            "sleep": ASSETS_DIR / "pet_sleep.png",
        }

        self.idle_messages = [
            "今天不要成为咸鱼",
            "先做五分钟也算开始",
            "别等状态来了，状态是做出来的",
            "你离完成只差一个开始",
            "少刷一会儿，多赢一点",
            "现在动一下，晚上少后悔一点",
            "别装没看见，我在盯着你",
            "今天也要稍微支棱一下",
        ]

        self.done_messages = [
            "不错，今天没当咸鱼",
            "可以，拖延症挨了一拳",
            "这一小步很稳",
            "继续保持，别让手感凉了",
            "你刚刚赢了自己一次",
        ]

        self.lazy_messages = [
            "再拖就要咸起来了",
            "稍后可以，但别无限稍后",
            "你不是没时间，你是在加载中",
            "我先记你一笔，等会儿回来",
            "咸鱼值正在偷偷上涨",
        ]

        self.init_ui()
        self.move_to_bottom_right()
        self.set_idle()

        self.init_message_timer()

    def init_ui(self):
        self.container = QFrame()
        self.container.setObjectName("petContainer")
        self.container.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(22)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.container.setGraphicsEffect(shadow)

        self.pet_image = QLabel()
        self.pet_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_image.setObjectName("petImage")
        self.pet_image.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.pet_text = QLabel()
        self.pet_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_text.setWordWrap(True)
        self.pet_text.setObjectName("petText")
        self.pet_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        layout.addWidget(self.pet_image)
        layout.addWidget(self.pet_text)

        self.container.setLayout(layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.addWidget(self.container)

        self.setLayout(outer_layout)
        self.setFixedSize(210, 190)

        self.setStyleSheet("""
            #petContainer {
                background-color: transparent;
                border: none;
            }

            #petImage {
                background-color: transparent;
            }

            #petText {
                font-size: 13px;
                font-weight: 600;
                color: {color};
                background-color: transparent;
            }
        """)

    def init_message_timer(self):
        """
        初始化宠物随机语录定时器。
        默认每 60 秒换一句普通语录。
        """
        self.message_timer = QTimer(self)
        self.message_timer.timeout.connect(self.auto_change_message)
        self.message_timer.start(60 * 1000) # 更改切换频率修改此处

    def load_pet_image(self, state_name):
        image_path = self.image_paths.get(state_name)

        print(f"[PetWindow] 当前状态：{state_name}")
        print(f"[PetWindow] 图片路径：{image_path}")

        if image_path is None:
            print("[PetWindow] 错误：没有找到对应状态的图片路径")
            self.pet_image.setText("🐟")
            return

        if not image_path.exists():
            print(f"[PetWindow] 错误：图片文件不存在：{image_path}")
            self.pet_image.setText("🐟")
            self.pet_image.setStyleSheet("""
                font-size: 48px;
                color: #111827;
                background-color: transparent;
            """)
            return

        pixmap = QPixmap(str(image_path))

        if pixmap.isNull():
            print(f"[PetWindow] 错误：QPixmap 加载失败，可能图片格式不受支持或文件损坏：{image_path}")
            self.pet_image.setText("🐟")
            return

        print(f"[PetWindow] 图片加载成功：{image_path}")

        scaled_pixmap = pixmap.scaled(
            120,
            120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.pet_image.setStyleSheet("background-color: transparent;")
        self.pet_image.setText("")
        self.pet_image.setPixmap(scaled_pixmap)

    def move_to_bottom_right(self):
        screen = QApplication.primaryScreen().availableGeometry()

        x = screen.right() - self.width() - 30
        y = screen.bottom() - self.height() - 30

        self.move(x, y)

    def say_random_idle_message(self):
        self.is_reminding = False
        self.load_pet_image("idle")
        self.pet_text.setText(random.choice(self.idle_messages))

    def auto_change_message(self):
        """
        自动切换宠物语录。
        提醒状态或短暂状态锁定时，不自动覆盖。
        """
        if getattr(self, "is_reminding", False):
            return

        if getattr(self, "is_status_locked", False):
            return

        self.say_random_idle_message()

    def unlock_status(self):
        self.is_status_locked = False
        self.say_random_idle_message()

    def set_text_color(self, color):
        self.pet_text.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {color};
            background-color: transparent;
        """)

    def set_idle(self):
        self.is_reminding = False
        self.set_text_color("#405279")
        self.say_random_idle_message()

    def set_reminding(self, task_title):
        self.is_reminding = True
        self.is_status_locked = False
        self.set_text_color("#b91c1c")
        self.load_pet_image("remind")
        self.pet_text.setText(f"该打卡啦：{task_title}")

    def set_done(self):
        self.is_reminding = False
        self.is_status_locked = True
        self.set_text_color("#d1449b")

        self.load_pet_image("done")
        self.pet_text.setText(random.choice(self.done_messages))

        QTimer.singleShot(8 * 1000, self.unlock_status)

    def set_lazy(self):
        self.is_reminding = False
        self.is_status_locked = True
        self.set_text_color("#c48d34")

        self.load_pet_image("lazy")
        self.pet_text.setText(random.choice(self.lazy_messages))

        QTimer.singleShot(8 * 1000, self.unlock_status)

    def set_sleeping(self):
        self.is_reminding = False
        self.is_status_locked = True
        self.set_text_color("#397250")
        self.load_pet_image("sleep")
        self.pet_text.setText("暂时休息一下")

    def set_progress(self, done, total):
        self.is_reminding = False
        self.set_text_color("#F9F756")

        if total == 0:
            self.load_pet_image("idle")
            self.pet_text.setText("今天还没有任务")
        elif done == total:
            self.load_pet_image("done")
            self.pet_text.setText(f"今日进度：{done} / {total}，全部完成")
        elif done == 0:
            self.load_pet_image("lazy")
            self.pet_text.setText(f"今日进度：0 / {total}，还没开始")
        else:
            self.load_pet_image("idle")
            self.pet_text.setText(f"今日进度：{done} / {total}")

    def update_by_fish_value(self, fish_value, done, total):
        """
        根据咸鱼值和今日进度自动切换宠物状态。
        提醒状态或短暂锁定状态下，不自动覆盖当前状态。
        """
        if getattr(self, "is_reminding", False):
            return

        if getattr(self, "is_status_locked", False):
            return

        if total == 0:
            self.load_pet_image("idle")
            self.set_text_color("#374151")
            self.pet_text.setText("今天还没有任务，可以先添加一个")
            return

        # 今日任务全部完成：优先显示完成状态
        if done >= total:
            self.load_pet_image("done")
            self.set_text_color("#16a34a")
            self.pet_text.setText("今日任务全部完成，不错")
            return

        # 今日还没开始：优先显示咸鱼状态
        if done == 0:
            self.load_pet_image("lazy")
            self.set_text_color("#ea580c")
            self.pet_text.setText(f"今日进度：0 / {total}，先动一下吧")
            return

        # 已经完成一部分，但还没全部完成：再根据咸鱼值细分状态
        if fish_value <= 30:
            self.load_pet_image("done")
            self.set_text_color("#16a34a")
            self.pet_text.setText(f"状态不错！今日进度：{done} / {total}")
        elif fish_value <= 70:
            self.load_pet_image("idle")
            self.set_text_color("#374151")
            self.pet_text.setText(f"继续推进，今日进度：{done} / {total}")
        else:
            self.load_pet_image("lazy")
            self.set_text_color("#ea580c")
            self.pet_text.setText(f"咸鱼值偏高，再完成一个任务吧：{done} / {total}")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.press_global_pos = event.globalPosition().toPoint()
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            release_pos = event.globalPosition().toPoint()
            moved_distance = (release_pos - self.press_global_pos).manhattanLength()

            self.is_dragging = False

            # 移动距离很小，认为是一次单击
            if moved_distance < 5:
                self.say_random_idle_message()

            event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_main_window()
            event.accept()

    def show_today_progress(self):
        if self.main_window is not None:
            self.main_window.update_pet_progress()

    def show_context_menu(self, position):
        menu = QMenu(self)

        show_action = QAction("显示主窗口", self)
        show_action.triggered.connect(self.open_main_window)

        progress_action = QAction("今日进度", self)
        progress_action.triggered.connect(self.show_today_progress)

        change_message_action = QAction("换一句话", self)
        change_message_action.triggered.connect(self.say_random_idle_message)

        idle_action = QAction("恢复默认状态", self)
        idle_action.triggered.connect(self.set_idle)

        reset_position_action = QAction("回到右下角", self)
        reset_position_action.triggered.connect(self.move_to_bottom_right)

        hide_action = QAction("隐藏宠物", self)
        hide_action.triggered.connect(self.hide)

        quit_action = QAction("退出程序", self)
        if self.main_window is not None:
            quit_action.triggered.connect(self.main_window.quit_app)

        menu.addAction(show_action)
        menu.addAction(progress_action)
        menu.addAction(change_message_action)
        menu.addSeparator()
        menu.addAction(idle_action)
        menu.addAction(reset_position_action)
        menu.addSeparator()
        menu.addAction(hide_action)
        menu.addSeparator()
        menu.addAction(quit_action)

        menu.exec(self.mapToGlobal(position))

    def open_main_window(self):
        if self.main_window is not None:
            self.main_window.show_main_window()

