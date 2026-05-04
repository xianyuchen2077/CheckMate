# data_guard/paths.py

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
    # parents[1] 就是 CheckMate/
    return Path(__file__).resolve().parents[1]


def get_database_dir():
    """
    当前阶段仍然使用项目内 data 目录。
    后续如果迁移到 AppData，主要改这里。
    """
    return get_app_dir() / "data"


def get_database_path():
    """
    获取当前数据库文件路径。
    """
    return get_database_dir() / DB_FILE_NAME


def get_backup_dir():
    """
    获取数据库备份目录。
    """
    return get_app_dir() / "data_backups"


def ensure_data_guard_dirs():
    """
    确保数据安全相关目录存在。
    """
    get_database_dir().mkdir(parents=True, exist_ok=True)
    get_backup_dir().mkdir(parents=True, exist_ok=True)

def get_data_guard_root_dir():
    """
    获取数据安全相关文件夹根目录。

    当前阶段放在项目目录下：
        CheckMate/data_backups/
    """
    return get_backup_dir()

def get_integrity_file_path():
    """
    获取数据库完整性校验文件路径。
    """
    return get_app_dir() / "integrity.json"