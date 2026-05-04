# data_guard/logger.py

from datetime import datetime

from data_guard.paths import (
    ensure_data_guard_dirs,
    get_data_guard_log_path,
)


def get_now_string():
    """
    获取当前时间字符串。
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def write_data_guard_log(level, message):
    """
    写入 data_guard 日志。

    level:
        INFO
        WARNING
        ERROR
    """
    ensure_data_guard_dirs()

    log_path = get_data_guard_log_path()

    line = f"[{get_now_string()}] [{level}] {message}\n"

    try:
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        # 日志写入失败不应该影响主程序运行
        pass


def log_info(message):
    write_data_guard_log("INFO", message)


def log_warning(message):
    write_data_guard_log("WARNING", message)


def log_error(message):
    write_data_guard_log("ERROR", message)