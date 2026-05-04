# data_guard/paths.py

import os
import sys
from pathlib import Path


APP_NAME = "CheckMate"
DB_FILE_NAME = "checkmate.db"


def get_app_dir():
    """
    获取程序所在目录。

    开发环境：
        CheckMate/

    打包环境：
        release/CheckMate/
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    # 当前文件是 CheckMate/data_guard/paths.py
    # parents[1] 是 CheckMate 项目根目录
    return Path(__file__).resolve().parents[1]


def get_user_data_root_dir():
    """
    获取用户数据根目录。

    Windows：
        C:/Users/用户名/AppData/Local/CheckMate

    非 Windows：
        ~/.local/share/CheckMate
    """
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")

        if local_app_data:
            return Path(local_app_data) / APP_NAME

        return Path.home() / "AppData" / "Local" / APP_NAME

    return Path.home() / ".local" / "share" / APP_NAME


def get_database_dir():
    """
    获取数据库目录。
    """
    return get_user_data_root_dir() / "data"


def get_database_path():
    """
    获取正式数据库文件路径。
    """
    return get_database_dir() / DB_FILE_NAME


def get_backup_dir():
    """
    获取数据库备份目录。
    """
    return get_user_data_root_dir() / "data_backups"


def get_integrity_file_path():
    """
    获取完整性校验文件路径。
    """
    return get_backup_dir() / "integrity.json"


def get_legacy_database_path():
    """
    获取旧版本数据库路径。

    旧版本数据库位于：
        CheckMate/data/checkmate.db
    """
    return get_app_dir() / "data" / DB_FILE_NAME


def get_legacy_backup_dir():
    """
    获取旧版本备份目录。

    旧版本备份目录位于：
        CheckMate/data_backups/
    """
    return get_app_dir() / "data_backups"


def ensure_data_guard_dirs():
    """
    确保数据安全相关目录存在。
    """
    get_database_dir().mkdir(parents=True, exist_ok=True)
    get_backup_dir().mkdir(parents=True, exist_ok=True)
    get_log_dir().mkdir(parents=True, exist_ok=True)


def get_log_dir():
    """
    获取日志目录。
    """
    return get_user_data_root_dir() / "logs"


def get_data_guard_log_path():
    """
    获取 data_guard 日志文件路径。
    """
    return get_log_dir() / "data_guard.log"