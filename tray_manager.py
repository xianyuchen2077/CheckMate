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


def get_icon(icon_name="checkmate_icon.png"):
    """
    获取指定图标。

    icon_name:
        assets/icons/ 下的文件名。
    """
    icon_path = get_base_dir() / "assets" / "icons" / icon_name

    # Debug 输出图标路径和存在性检查
    # print("[TrayManager] 尝试加载图标：", icon_path)
    # print("[TrayManager] 图标是否存在：", icon_path.exists())

    if icon_path.exists():
        return QIcon(str(icon_path))

    return None


def get_tray_icon():
    """
    获取默认托盘图标。
    """
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

        quit_action = QAction("退出程序", self.main_window)
        quit_action.triggered.connect(self.main_window.quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addAction(show_pet_action)
        tray_menu.addSeparator()
        tray_menu.addAction(self.auto_start_action)
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

        icon_type:
            default
            reminder
            done
            snooze
            warning
            success
        """
        if self.tray_icon is None:
            return

        icon = self.get_notification_icon(icon_type)

        if icon is not None:
            self.tray_icon.setIcon(icon)

        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.NoIcon,
            duration
        )

        # 通知发出后恢复默认托盘图标
        if self.default_icon is not None:
            QTimer.singleShot(
                1200,
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
        """
        icon_map = {
            "default": "checkmate_icon.png",
            "reminder": "notify_reminder.png",
            "done": "notify_done.png",
            "snooze": "notify_snooze.png",
            "warning": "notify_warning.png",
            "success": "notify_success.png",
        }

        icon_name = icon_map.get(icon_type, "checkmate_icon.png")

        icon = get_icon(icon_name)

        if icon is not None:
            return icon

        # print("[TrayManager] 图标加载失败，回退默认图标")

        return self.default_icon