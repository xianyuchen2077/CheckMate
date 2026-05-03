import sys
import winreg
from pathlib import Path


APP_NAME = "CheckMate"

RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"


def get_startup_command():
    """
    获取开机自启动命令。

    开发阶段：
        使用 pythonw.exe 启动 main.py，避免弹出黑色命令行窗口。

    打包成 exe 后：
        sys.executable 会指向 exe 文件，可以直接启动 exe。
    """
    executable = Path(sys.executable)

    # 如果是打包后的 exe
    if getattr(sys, "frozen", False):
        return f'"{executable}"'

    # 开发阶段，寻找 pythonw.exe
    pythonw = executable.with_name("pythonw.exe")
    main_py = Path(__file__).resolve().parent / "main.py"

    if pythonw.exists():
        return f'"{pythonw}" "{main_py}"'

    # 兜底：用当前 python.exe 启动
    return f'"{executable}" "{main_py}"'


def enable_auto_start():
    command = get_startup_command()

    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER,
        RUN_KEY_PATH,
        0,
        winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)


def disable_auto_start():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, APP_NAME)
    except FileNotFoundError:
        pass


def is_auto_start_enabled():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return bool(value)
    except FileNotFoundError:
        return False


def get_auto_start_command():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_READ
        ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return value
    except FileNotFoundError:
        return None