from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QMenu,
    QStyle,
    QSystemTrayIcon,
)


class TrayManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tray_icon = None

    def init_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.warning(self.main_window, "提示", "当前系统不支持系统托盘。")
            return

        self.tray_icon = QSystemTrayIcon(self.main_window)

        icon = self.main_window.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon
        )
        self.tray_icon.setIcon(icon)

        tray_menu = QMenu()

        show_action = QAction("显示主窗口", self.main_window)
        show_action.triggered.connect(self.main_window.show_main_window)

        quit_action = QAction("退出程序", self.main_window)
        quit_action.triggered.connect(self.main_window.quit_app)

        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)

        self.tray_icon.setToolTip("CheckMate - 不要成为咸鱼")
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.main_window.show_main_window()

    def show_message(self, title, message, duration=3000):
        if self.tray_icon is None:
            return

        self.tray_icon.showMessage(
            title,
            message,
            QSystemTrayIcon.MessageIcon.Information,
            duration
        )

    def hide(self):
        if self.tray_icon is not None:
            self.tray_icon.hide()