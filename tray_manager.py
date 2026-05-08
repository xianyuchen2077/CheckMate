import sys
from pathlib import Path

from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QMenu,
    QStyle,
    QSystemTrayIcon,
)

import auto_start

def get_base_dir():
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)

        if meipass:
            return Path(meipass)

        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def get_assets_dir():
    """
    获取 assets 目录。

    开发环境：
        项目根目录/assets

    PyInstaller onedir：
        可能是 exe 同级 assets
        也可能是 _internal/assets
    """
    base_dir = get_base_dir()

    candidates = [
        base_dir / "assets",
        base_dir / "_internal" / "assets",
    ]

    for path in candidates:
        if path.exists():
            return path

    return candidates[0]


def get_icon(icon_name="checkmate_icon.png"):
    """
    获取指定图标。

    icon_name:
        assets/icons/ 下的文件名。
    """
    assets_dir = get_assets_dir()
    icon_path = assets_dir / "icons" / icon_name

    # Debug 输出路径信息，帮助排查图标加载问题
    # print("[TrayManager] assets_dir =", assets_dir)
    # print("[TrayManager] icon_path =", icon_path)
    # print("[TrayManager] exists =", icon_path.exists())


    if icon_path.exists():
        icon = QIcon(str(icon_path))

        if not icon.isNull():
            return icon

    return None


def get_tray_icon():
    """
    获取默认托盘图标。
    Windows 下优先使用 ico，失败再回退 png。
    """
    icon = get_icon("checkmate_icon.ico")

    if icon is not None:
        return icon

    return get_icon("checkmate_icon.png")


class TrayManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tray_icon = None
        self.default_icon = None

    def init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.warning(self.main_window, "提示", "当前系统不支持系统托盘。")
            return

        self.tray_icon = QSystemTrayIcon(self.main_window)

        icon = get_tray_icon()

        if icon is not None:
            self.default_icon = icon
        else:
            self.default_icon = self.main_window.style().standardIcon(
                QStyle.StandardPixmap.SP_ComputerIcon
            )

        self.tray_icon.setIcon(self.default_icon)

        tray_menu = QMenu()

        show_action = QAction("显示主窗口", self.main_window)
        show_action.triggered.connect(self.main_window.show_main_window)

        show_pet_action = QAction("显示桌面宠物", self.main_window)
        show_pet_action.triggered.connect(self.main_window.show_pet_window)

        self.auto_start_action = QAction("开机自启动", self.main_window)
        self.auto_start_action.setCheckable(True)
        self.auto_start_action.setChecked(auto_start.is_auto_start_enabled())
        self.auto_start_action.triggered.connect(self.toggle_auto_start)

        settings_action = QAction("设置", self.main_window)
        settings_action.triggered.connect(self.main_window.show_settings)

        quit_action = QAction("退出程序", self.main_window)
        quit_action.triggered.connect(self.main_window.quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addAction(show_pet_action)
        tray_menu.addSeparator()
        tray_menu.addAction(self.auto_start_action)
        tray_menu.addSeparator()
        tray_menu.addAction(settings_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)

        self.tray_icon.setToolTip("CheckMate - 不要成为咸鱼")
        self.tray_icon.show()

    def toggle_auto_start(self, checked):
        try:
            if checked:
                auto_start.enable_auto_start()
                self.show_message(
                    "CheckMate",
                    "已启用开机自启动。",
                    3000,
                    icon_type="success"
                )
            else:
                auto_start.disable_auto_start()
                self.show_message(
                    "CheckMate",
                    "已关闭开机自启动。",
                    3000,
                    icon_type="warning"
                )

            self.auto_start_action.setChecked(auto_start.is_auto_start_enabled())

        except Exception as e:
            self.auto_start_action.setChecked(auto_start.is_auto_start_enabled())
            QMessageBox.warning(
                self.main_window,
                "开机自启动设置失败",
                f"设置开机自启动时出现错误：\n{e}"
            )

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.main_window.show_main_window()

    def show_message(self, title, message, duration=3000, icon_type="default"):
        """
        显示系统托盘通知。

        目标：
            1. 托盘小图标临时切换
            2. Windows 通知尽量使用 CheckMate 自定义图标
            3. 通知结束后恢复默认托盘图标
        """
        if self.tray_icon is None:
            return

        icon = self.get_notification_icon(icon_type)

        if icon is None:
            icon = self.default_icon

        if icon is not None:
            self.tray_icon.setIcon(icon)

        # 优先使用 QIcon 版本的 showMessage，让通知卡片尽量使用自定义图标
        if icon is not None and not icon.isNull():
            try:
                self.tray_icon.showMessage(
                    title,
                    message,
                    icon,
                    duration
                )
            except TypeError:
                # 某些 PySide6 版本如果不支持 QIcon 重载，就退回 NoIcon
                self.tray_icon.showMessage(
                    title,
                    message,
                    QSystemTrayIcon.MessageIcon.NoIcon,
                    duration
                )
        else:
            self.tray_icon.showMessage(
                title,
                message,
                QSystemTrayIcon.MessageIcon.NoIcon,
                duration
            )

        if self.default_icon is not None:
            QTimer.singleShot(
                max(duration, 1200),
                self.restore_default_icon
            )

    def hide(self):
        if self.tray_icon is not None:
            self.tray_icon.hide()

    def restore_default_icon(self):
        """
        恢复默认托盘图标。
        """
        if self.tray_icon is None:
            return

        if self.default_icon is None:
            return

        self.tray_icon.setIcon(self.default_icon)

    def get_notification_icon(self, icon_type):
        """
        根据通知类型获取图标。

        优先级：
            1. 使用 icon_type 对应的专用通知图标
            2. 如果专用图标不存在，回退到 checkmate_icon2.png
            3. 如果 checkmate_icon2.png 也不存在，回退到初始化时的 default_icon
        """
        icon_map = {
            "default": "checkmate_icon2.png",
            "reminder": "notify_reminder.png",
            "done": "notify_done.png",
            "snooze": "notify_snooze.png",
            "warning": "notify_warning.png",
            "success": "notify_success.png",
        }

        icon_name = icon_map.get(icon_type, "checkmate_icon2.png")

        # 1. 先尝试加载当前通知类型对应的图标
        icon = get_icon(icon_name)

        if icon is not None:
            return icon

        # 2. 当前类型图标不存在时，统一回退到 CheckMate 默认图标
        fallback_icon = get_icon("checkmate_icon2.png")

        if fallback_icon is not None:
            return fallback_icon

        # 3. 最后回退到托盘初始化时保存的默认图标
        return self.default_icon