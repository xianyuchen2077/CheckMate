from pathlib import Path
import random
import sys
import time

import database
import config_manager
from pet_system import pet_growth
from pet_settings_dialog import PetSettingsDialog

from PySide6.QtCore import Qt, QPoint, QTimer, QSize, QDateTime
from PySide6.QtGui import QColor, QPixmap, QAction, QMovie
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QVBoxLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QMenu,
    QProgressBar,
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
        self.pet_config = config_manager.get_pet_config()
        self.drag_position = QPoint()
        self.is_dragging = False
        self.is_reminding = False
        self.is_status_locked = False
        self.press_global_pos = QPoint()
        self.drag_started = False
        self.click_move_threshold = 10

        self.main_window_focus_grace_until = 0.0
        self.pet_click_mode_until = 0.0

        # 宠物连点彩蛋：
        # 5 秒内连续点击 15 次及以上触发
        self.pet_easter_click_count = 0
        self.pet_easter_first_click_time = None
        self.is_pet_easter_mode = False


        # 超级赛亚人彩蛋：
        self.is_super_fish_mode = False
        self.super_fish_finished_callback = None

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
        self.current_pet_state = "idle"

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
        self.refresh_growth_info()
        self.set_idle()
        self.apply_pet_settings()

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

        # 等级 + 宠物名字，例如：Lv.1 · 咸鱼仔
        self.pet_level_label = QLabel("Lv.1 · 咸鱼仔")
        self.pet_level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_level_label.setObjectName("petLevelLabel")
        self.pet_level_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 当前阶段名称，例如：咸鱼苗 / 努力鱼 / 自律鱼
        self.pet_stage_label = QLabel("咸鱼苗")
        self.pet_stage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_stage_label.setObjectName("petStageLabel")
        self.pet_stage_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 经验进度条
        self.pet_exp_bar = QProgressBar()
        self.pet_exp_bar.setObjectName("petExpBar")
        self.pet_exp_bar.setRange(0, 100)
        self.pet_exp_bar.setValue(0)
        self.pet_exp_bar.setTextVisible(False)
        self.pet_exp_bar.setFixedHeight(10) # 调整经验条高度
        self.pet_exp_bar.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # 经验数字，例如：EXP 0 / 120
        self.pet_exp_label = QLabel("EXP 0 / 120")
        self.pet_exp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_exp_label.setObjectName("petExpLabel")
        self.pet_exp_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        self.pet_text = QLabel()
        self.pet_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pet_text.setWordWrap(True)
        self.pet_text.setObjectName("petText")
        self.pet_text.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6) # 调整控件之间的垂直间距
        layout.addWidget(self.pet_image)
        layout.addWidget(self.pet_level_label)
        layout.addWidget(self.pet_stage_label)
        layout.addWidget(self.pet_exp_bar)
        layout.addWidget(self.pet_exp_label)
        layout.addWidget(self.pet_text)
        self.container.setLayout(layout)

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.addWidget(self.container)

        self.setLayout(outer_layout)
        self.setFixedSize(200, 260) # 调整宠物窗口大小

        self.setStyleSheet("""
            #petContainer {
                background-color: transparent;
                border: none;
            }

            #petImage {
                background-color: transparent;
            }

            #petLevelLabel {
                font-size: 12px;
                font-weight: 800;
                color: #2563eb;
                background-color: transparent;
            }

            #petStageLabel {
                font-size: 11px;
                font-weight: 600;
                color: #64748b;
                background-color: transparent;
            }

            #petExpLabel {
                font-size: 10px;
                font-weight: 600;
                color: #475569;
                background-color: transparent;
            }

            #petExpBar {
                background-color: rgba(226, 232, 240, 180);
                border: 1px solid rgba(148, 163, 184, 160);
                border-radius: 5px;
                text-align: center;
            }

            #petExpBar::chunk {
                background-color: #4ade80;
                border-radius: 5px;
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

        self.current_pet_state = state_name

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
        优先加载当前阶段资源。
        当前阶段缺失时，回退到 stage_1。
        每个状态优先 gif，再 png。
        """
        current_stage_dir = PETS_DIR / self.current_skin / f"stage_{self.current_stage}"
        stage_1_dir = PETS_DIR / self.current_skin / "stage_1"
        skin_root_dir = PETS_DIR / self.current_skin

        def candidates(file_base_name):
            return [
                current_stage_dir / f"{file_base_name}.gif",
                current_stage_dir / f"{file_base_name}.png",
                stage_1_dir / f"{file_base_name}.gif",
                stage_1_dir / f"{file_base_name}.png",
                skin_root_dir / f"{file_base_name}.gif",
                skin_root_dir / f"{file_base_name}.png",
            ]

        return {
            "idle": candidates("pet_idle"),
            "remind": candidates("pet_remind"),
            "done": candidates("pet_done"),
            "lazy": candidates("pet_lazy"),
            "sleep": candidates("pet_sleep"),

            # 彩蛋状态
            # 宠物连击彩蛋
            "tired": candidates("tired") + candidates("pet_lazy"),
            "unconscious": candidates("unconscious") + candidates("pet_sleep") + candidates("pet_lazy"),
            "dead": candidates("dead") + candidates("pet_dead_fish") + candidates("pet_sleep") + candidates("pet_lazy"),
            # 超级赛亚人彩蛋
            "super_fish": candidates("Super_Saiyan") + candidates("pet_done") + candidates("pet_idle"),
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
        手动切换宠物进化阶段。
        主要用于测试或后续调试。
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
        if getattr(self, "is_super_fish_mode", False):
            return

        if getattr(self, "is_pet_easter_mode", False):
            return

        if getattr(self, "is_status_locked", False):
            return

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

        if getattr(self, "is_pet_easter_mode", False):
            return

        if getattr(self, "is_super_fish_mode", False):
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
        从数据库读取宠物等级、经验、阶段，并刷新等级文字和经验条。
        """
        pet = database.get_pet_status()

        if pet is None:
            self.current_stage = 1
            self.image_paths = self.build_image_paths()

            self.pet_level_label.setText("Lv.1 · 咸鱼仔")
            self.pet_stage_label.setText("咸鱼苗")
            self.pet_exp_bar.setValue(0)
            self.pet_exp_label.setText("EXP 0 / 120")

            return

        pet_name = pet["pet_name"]
        level = pet["level"]
        exp = pet["exp"]
        stage = pet["stage"]

        if stage != self.current_stage:
            self.current_stage = stage
            self.image_paths = self.build_image_paths()

        stage_name = pet_growth.get_stage_name(stage)
        required_exp = pet_growth.get_required_exp(level)

        if required_exp <= 0:
            progress_percent = 0
        else:
            progress_percent = int(exp / required_exp * 100)

        progress_percent = max(0, min(progress_percent, 100))

        self.pet_level_label.setText(f"Lv.{level} · {pet_name}")
        self.pet_stage_label.setText(stage_name)
        self.pet_exp_bar.setValue(progress_percent)
        self.pet_exp_label.setText(f"EXP {exp} / {required_exp}")

    def apply_pet_settings(self):
        """
        应用宠物配置：
        - 不透明度
        - 是否置顶
        - 保存的位置
        """
        pet_config = config_manager.get_pet_config()

        opacity = float(pet_config.get("opacity", 1.0))
        self.setWindowOpacity(opacity)

        always_on_top = bool(pet_config.get("always_on_top", True))
        self.set_always_on_top(always_on_top)

        x = pet_config.get("x")
        y = pet_config.get("y")

        if x is not None and y is not None:
            self.move(int(x), int(y))
        else:
            self.move_to_bottom_right()

    def set_always_on_top(self, enabled):
        """
        设置宠物窗口是否始终置顶。
        修改窗口 flags 后，Qt 可能会重建窗口，因此需要重新加载宠物图片。
        """
        was_visible = self.isVisible()

        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool

        if enabled:
            flags |= Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(flags)

        if was_visible:
            self.show()

        # 重新加载当前阶段资源和当前状态图片，避免图片消失
        self.image_paths = self.build_image_paths()
        self.load_pet_image(getattr(self, "current_pet_state", "idle"))

    def set_idle(self):
        self.is_reminding = False
        self.is_status_locked = False
        self.is_pet_easter_mode = False
        self.is_super_fish_mode = False

        self.set_text_color("#405279")
        self.load_pet_image("idle")
        self.pet_text.setText(random.choice(self.idle_messages))

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

    def handle_pet_click_easter_egg(self):
        """
        宠物连点彩蛋。

        触发规则：
            5 秒内连续点击桌面宠物 15 次及以上。

        效果：
            从 tired / unconscious / dead 三种状态里随机选一种，
            持续 5 秒后恢复正常。
        """
        if self.is_pet_easter_mode:
            return

        # 提醒状态下不触发彩蛋，避免盖掉重要提醒
        if getattr(self, "is_reminding", False):
            return

        now = QDateTime.currentDateTime()

        if self.pet_easter_first_click_time is None:
            self.pet_easter_first_click_time = now
            self.pet_easter_click_count = 1
        else:
            elapsed_ms = self.pet_easter_first_click_time.msecsTo(now)

            # 超过 5 秒，重新计数
            if elapsed_ms > 5 * 1000:
                self.pet_easter_first_click_time = now
                self.pet_easter_click_count = 1
            else:
                self.pet_easter_click_count += 1

        # 还没到 15 次，不触发
        if self.pet_easter_click_count < 15:
            return

        self.pet_easter_click_count = 0
        self.pet_easter_first_click_time = None

        random_state = random.choice(["tired", "unconscious", "dead"])

        self.enter_pet_easter_mode(
            state_name=random_state,
            message="我先躺一会儿，你继续努力。",
            duration_ms=5 * 1000,
        )

    def resolve_pet_click_easter_egg(self, count_snapshot):
        """
        用户停止连点后，根据 10 秒内最终点击次数触发不同状态。
        """
        if self.is_pet_easter_mode:
            return

        # 如果这 700ms 内又点了新的次数，说明用户还没停，当前判断作废。
        if count_snapshot != self.pet_easter_click_count:
            return

        click_count = self.pet_easter_click_count

        if click_count < 10:
            return

        if 10 <= click_count <= 15:
            self.enter_pet_easter_mode(
                state_name="tired",
                message="我有点累了，但还能抢救一下。",
                duration_ms=5 * 1000,
            )
        elif 16 <= click_count <= 24:
            self.enter_pet_easter_mode(
                state_name="unconscious",
                message="我先晕一会儿，你继续努力。",
                duration_ms=5 * 1000,
            )
        else:
            self.enter_pet_easter_mode(
                state_name="dead",
                message="我先躺一会儿，你继续努力。",
                duration_ms=5 * 1000,
            )

        self.pet_easter_click_count = 0
        self.pet_easter_first_click_time = None

    def enter_pet_easter_mode(self, state_name, message, duration_ms=5000):
        """
        进入宠物连点彩蛋状态。
        """
        if self.is_pet_easter_mode:
            return

        self.is_pet_easter_mode = True
        self.is_reminding = False
        self.is_status_locked = True

        self.set_text_color("#6b7280")
        self.load_pet_image(state_name)
        self.pet_text.setText(message)

        QTimer.singleShot(duration_ms, self.exit_pet_easter_mode)


    def exit_pet_easter_mode(self):
        """
        退出宠物连点彩蛋状态，恢复普通状态。
        """
        self.is_pet_easter_mode = False
        self.is_status_locked = False
        self.set_idle()

    def set_konami_flash_on(self):
        """
        Konami Code 彩蛋闪烁：亮起。
        """
        self.container.setStyleSheet("""
            #petContainer {
                background-color: rgba(255, 247, 237, 220);
                border: 2px solid #f97316;
                border-radius: 18px;
            }
        """)

        self.setWindowOpacity(1.0)

    def set_konami_flash_off(self):
        """
        Konami Code 彩蛋闪烁：恢复。
        """
        self.container.setStyleSheet("""
            #petContainer {
                background-color: transparent;
                border: none;
            }
        """)

        pet_config = config_manager.get_pet_config()
        opacity = float(pet_config.get("opacity", 1.0))
        self.setWindowOpacity(opacity)

    def enter_super_fish_mode(self, on_finished=None):
        """
        Konami Code 彩蛋：超级咸鱼模式。
        闪烁结束后切换到 super_fish 图片。
        """
        if getattr(self, "is_reminding", False):
            if on_finished is not None:
                on_finished()
            return

        self.is_super_fish_mode = True
        self.is_status_locked = True
        self.is_reminding = False
        self.super_fish_finished_callback = on_finished

        self.set_konami_flash_on()
        self.set_text_color("#f97316")
        self.load_pet_image("super_fish")
        self.pet_text.setText("你输入了古老的咒语，鱼开始发光。")

        QTimer.singleShot(5 * 1000, self.exit_super_fish_mode)

    def exit_super_fish_mode(self):
        """
        退出超级咸鱼模式。
        """
        self.is_super_fish_mode = False
        self.is_status_locked = False

        # 超级赛亚鱼结束后，关闭宠物发光效果
        self.set_konami_flash_off()

        self.set_idle()

        callback = getattr(self, "super_fish_finished_callback", None)
        self.super_fish_finished_callback = None

        if callback is not None:
            callback()

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
            self.drag_started = False

            self.press_global_pos = event.globalPosition().toPoint()
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()

    def mouseMoveEvent(self, event):
        if not self.is_dragging:
            return

        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        current_pos = event.globalPosition().toPoint()
        moved_distance = (current_pos - self.press_global_pos).manhattanLength()

        # 鼠标抖动距离很小时，不认为是在拖动
        if moved_distance < self.click_move_threshold:
            event.accept()
            return

        self.drag_started = True
        self.move(current_pos - self.drag_position)
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        release_pos = event.globalPosition().toPoint()
        moved_distance = (release_pos - self.press_global_pos).manhattanLength()

        self.is_dragging = False

        # 确实拖动过：
        # 保存宠物位置，并在接下来 3 秒内不再让双击宠物置顶主窗口。
        if moved_distance >= 5:
            config_manager.update_pet_config(
                x=self.pos().x(),
                y=self.pos().y()
            )

            self.pet_click_mode_until = time.monotonic() + 3.0
            event.accept()
            return

        # 普通点击：用于宠物连点彩蛋
        self.handle_pet_click_easter_egg()

        if not self.is_pet_easter_mode:
            self.say_random_idle_message()

        event.accept()

    def mouseDoubleClickEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        main_window = self.main_window

        if main_window is None:
            event.accept()
            return

        now = time.monotonic()

        # 宠物点击保护期内：
        # 用户正在操作宠物本体，不再重复唤醒 / 置顶主窗口。
        if now < self.pet_click_mode_until:
            event.accept()
            return

        # 主窗口隐藏 / 最小化：
        # 第一次双击宠物用于唤醒主窗口。
        if not main_window.isVisible() or main_window.isMinimized():
            main_window.bring_main_window_to_front()
            self.pet_click_mode_until = time.monotonic() + 3.0
            event.accept()
            return

        # 主窗口已经显示：
        # 第一次双击宠物用于置顶主窗口。
        # 之后 3 秒内继续点宠物，就进入宠物彩蛋点击模式。
        main_window.bring_main_window_to_front()
        self.pet_click_mode_until = time.monotonic() + 3.0
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

        settings_action = QAction("宠物设置", self)
        settings_action.triggered.connect(self.open_pet_settings)

        # 皮肤切换
        # morty_action = QAction("切换为 Morty", self)
        # morty_action.triggered.connect(lambda: self.switch_skin("Morty"))

        # rick_action = QAction("切换为 Rick", self)
        # rick_action.triggered.connect(lambda: self.switch_skin("Rick"))

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
        menu.addAction(settings_action)
        menu.addSeparator()
        # menu.addAction(morty_action)
        # menu.addAction(rick_action)

        menu.exec(self.mapToGlobal(position))

    def open_main_window(self):
        main_window = self.main_window

        if main_window is None:
            return

        main_window.bring_main_window_to_front()

    def open_pet_settings(self):
        dialog = PetSettingsDialog(self, self.main_window)
        dialog.exec()

    def print_resource_debug_info(self):
        for state, paths in self.image_paths.items():
            print(f"  {state}:")
            for path in paths:
                print(f"    {path} exists={path.exists()}")