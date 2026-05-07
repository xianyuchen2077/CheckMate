import sys


APP_USER_MODEL_ID = "XianYu.CheckMate.Desktop"


def setup_windows_app_identity():
    """
    设置 Windows AppUserModelID。

    作用：
        1. 避免通知标题显示 NotifyIconGeneratedAumid_xxx
        2. 让 Windows 把通知归到 CheckMate 这个应用下面
        3. 改善任务栏 / 通知中心图标识别
    """
    if sys.platform != "win32":
        return

    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            APP_USER_MODEL_ID
        )
    except Exception:
        pass