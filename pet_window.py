from pathlib import Path
import random
import sys

import database
from pet_system import pet_growth

from PySide6.QtCore import Qt, QPoint, QTimer, QSize
from PySide6.QtGui import QColor, QPixmap, QAction, QMovie
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QMenu,
)

def get_base_dir():
    """
    获取项目资源基础目录。
    开发环境：项目根目录
    打包环境：exe 所在目录或 PyInstaller 临时目录
    """
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent

# assets 根目录
ASSETS_DIR = get_base_dir() / "assets"

# 宠物资源目录：assets/pets/
PETS_DIR = ASSETS_DIR / "pets"

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

        # 当前宠物皮肤，对应 assets/pets/salty_fish/
        self.current_skin = "salty_fish"

        # 当前进化阶段，对应 stage_1 / stage_2 / stage_3 / stage_4
        self.current_stage = 1

        # 当前宠物状态图片路径
        self.image_paths = self.build_image_paths()

        # Debug:输出资源调试信息，帮助开发时确认资源路径和存在性
        # self.print_resource_debug_info()

        # 当前 GIF 动画对象，必须保存引用，否则动画可能不播放
        self.current_movie = None

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
        self.refresh_growth_info()
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

        self.pet_growth_label = QLabel("Lv.1 · 咸鱼苗\nEXP 0 / 120")
        self.pet_growth_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_growth_label.setObjectName("petGrowthLabel")
        self.pet_growth_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.pet_text = QLabel()
        self.pet_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_text.setWordWrap(True)
        self.pet_text.setObjectName("petText")
        self.pet_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)
        layout.addWidget(self.pet_image)
        layout.addWidget(self.pet_growth_label)
        layout.addWidget(self.pet_text)
        self.container.setLayout(layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.addWidget(self.container)

        self.setLayout(outer_layout)
        self.setFixedSize(200, 230) # 调整宠物窗口大小

        self.setStyleSheet("""
            #petContainer {
                background-color: transparent;
                border: none;
            }

            #petImage {
                background-color: transparent;
            }

            #petGrowthLabel {
                font-size: 12px;
                font-weight: 700;
                color: #2563eb;
                background-color: transparent;
            }

            #petText {
                font-size: 13px;
                font-weight: 600;
                color: #111827;
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
        """
        根据状态加载宠物图片。
        支持 gif 动画和 png 静态图。
        """
        # 停止之前的 GIF 动画
        if self.current_movie is not None:
            self.current_movie.stop()
            self.current_movie = None

        image_candidates = self.image_paths.get(state_name, [])

        image_path = None
        for candidate in image_candidates:
            if candidate.exists():
                image_path = candidate
                break

        # 找不到资源时，回退显示 emoji
        if image_path is None:
            self.pet_image.setPixmap(QPixmap())
            self.pet_image.setText("🐟")
            self.pet_image.setStyleSheet("""
                font-size: 48px;
                color: #111827;
                background-color: transparent;
            """)
            return

        suffix = image_path.suffix.lower()

        # GIF 动画
        if suffix == ".gif":
            movie = QMovie(str(image_path))

            if not movie.isValid():
                self.pet_image.setPixmap(QPixmap())
                self.pet_image.setText("🐟")
                return

            movie.setScaledSize(QSize(120, 120))

            self.pet_image.setText("")
            self.pet_image.setStyleSheet("background-color: transparent;")
            self.pet_image.setMovie(movie)

            self.current_movie = movie
            movie.start()
            return

        # PNG / JPG 静态图片
        pixmap = QPixmap(str(image_path))

        if pixmap.isNull():
            self.pet_image.setPixmap(QPixmap())
            self.pet_image.setText("🐟")
            return

        scaled_pixmap = pixmap.scaled(
            120,
            120,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.pet_image.setText("")
        self.pet_image.setStyleSheet("background-color: transparent;")
        self.pet_image.setPixmap(scaled_pixmap)

    def get_pet_assets_dir(self):
        """
        获取当前宠物资源目录。
        优先使用 stage_x 文件夹；如果没有，则回退到皮肤根目录。
        """
        staged_dir = PETS_DIR / self.current_skin / f"stage_{self.current_stage}"
        fallback_dir = PETS_DIR / self.current_skin

        if staged_dir.exists():
            return staged_dir

        return fallback_dir


    def build_image_paths(self):
        """
        构建宠物各状态图片路径。
        每个状态优先加载 gif，没有 gif 再加载 png。
        """
        pet_assets_dir = self.get_pet_assets_dir()

        return {
            "idle": [
                pet_assets_dir / "pet_idle.gif",
                pet_assets_dir / "pet_idle.png",
            ],
            "remind": [
                pet_assets_dir / "pet_remind.gif",
                pet_assets_dir / "pet_remind.png",
            ],
            "done": [
                pet_assets_dir / "pet_done.gif",
                pet_assets_dir / "pet_done.png",
            ],
            "lazy": [
                pet_assets_dir / "pet_lazy.gif",
                pet_assets_dir / "pet_lazy.png",
            ],
            "sleep": [
                pet_assets_dir / "pet_sleep.gif",
                pet_assets_dir / "pet_sleep.png",
            ],
        }

    def switch_skin(self, skin_name):
        """
        切换宠物皮肤。
        skin_name 必须对应 assets/icons/pets/ 下的文件夹名。
        """
        self.current_skin = skin_name
        self.image_paths = self.build_image_paths()
        self.set_idle()

    def switch_stage(self, stage):
        """
        切换宠物进化阶段。
        stage=1 对应 stage_1，stage=2 对应 stage_2。
        """
        self.current_stage = stage
        self.image_paths = self.build_image_paths()
        self.refresh_growth_info()
        self.set_idle()

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

    def refresh_growth_info(self):
        """
        从数据库读取宠物等级、经验、阶段，并刷新显示与资源路径。
        """
        pet = database.get_pet_status()

        if pet is None:
            self.current_stage = 1
            self.image_paths = self.build_image_paths()
            self.pet_growth_label.setText("Lv.1 · 咸鱼苗\nEXP 0 / 120")
            return

        level = pet["level"]
        exp = pet["exp"]
        stage = pet["stage"]

        # 如果数据库里的阶段变化了，就切换资源目录
        if stage != self.current_stage:
            self.current_stage = stage
            self.image_paths = self.build_image_paths()

        stage_name = pet_growth.get_stage_name(stage)
        required_exp = pet_growth.get_required_exp(level)

        self.pet_growth_label.setText(
            f"Lv.{level} · {stage_name}\n"
            f"EXP {exp} / {required_exp}"
        )

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

        # 皮肤切换
        morty_action = QAction("切换为 Morty", self)
        morty_action.triggered.connect(lambda: self.switch_skin("Morty"))

        rick_action = QAction("切换为 Rick", self)
        rick_action.triggered.connect(lambda: self.switch_skin("Rick"))

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
        menu.addSeparator()
        menu.addAction(morty_action)
        menu.addAction(rick_action)

        menu.exec(self.mapToGlobal(position))

    def open_main_window(self):
        if self.main_window is not None:
            self.main_window.show_main_window()

    def print_resource_debug_info(self):
        print("[PetWindow] ASSETS_DIR:", ASSETS_DIR)
        print("[PetWindow] PETS_DIR:", PETS_DIR)
        print("[PetWindow] current_skin:", self.current_skin)
        print("[PetWindow] current_stage:", self.current_stage)
        print("[PetWindow] pet_assets_dir:", self.get_pet_assets_dir())
        print("[PetWindow] image_paths:")
        for state, paths in self.image_paths.items():
            print(f"  {state}:")
            for path in paths:
                print(f"    {path} exists={path.exists()}")