# data_guard/backup_manager.py

import shutil
from datetime import datetime
from pathlib import Path

from data_guard.paths import (
    get_database_path,
    get_backup_dir,
    ensure_data_guard_dirs,
)


AUTO_BACKUP_PREFIX = "auto"
MANUAL_BACKUP_PREFIX = "manual"
MAX_AUTO_BACKUPS = 10


def get_timestamp():
    """
    生成适合文件名使用的时间戳。
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def is_database_available():
    """
    判断数据库文件是否存在且不是空文件。
    """
    db_path = get_database_path()

    if not db_path.exists():
        return False

    if db_path.stat().st_size <= 0:
        return False

    return True


def create_backup(prefix=AUTO_BACKUP_PREFIX):
    """
    创建数据库备份。

    返回：
        Path：备份文件路径
        None：数据库不存在时返回 None
    """
    ensure_data_guard_dirs()

    if not is_database_available():
        return None

    db_path = get_database_path()
    backup_dir = get_backup_dir()

    timestamp = get_timestamp()
    backup_name = f"{prefix}_checkmate_{timestamp}.db"
    backup_path = backup_dir / backup_name

    shutil.copy2(db_path, backup_path)

    return backup_path


def create_auto_backup():
    """
    创建自动备份，并清理旧的自动备份。
    """
    backup_path = create_backup(AUTO_BACKUP_PREFIX)

    if backup_path is not None:
        cleanup_old_auto_backups()

    return backup_path


def create_manual_backup():
    """
    创建手动备份。
    后续可以接到设置页面或托盘菜单。
    """
    return create_backup(MANUAL_BACKUP_PREFIX)


def list_auto_backups():
    """
    获取所有自动备份，按修改时间从新到旧排序。
    """
    backup_dir = get_backup_dir()

    if not backup_dir.exists():
        return []

    backups = list(backup_dir.glob(f"{AUTO_BACKUP_PREFIX}_checkmate_*.db"))

    backups.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    return backups


def cleanup_old_auto_backups(max_count=MAX_AUTO_BACKUPS):
    """
    只保留最近 max_count 个自动备份。
    """
    backups = list_auto_backups()

    old_backups = backups[max_count:]

    for backup_path in old_backups:
        try:
            backup_path.unlink()
        except OSError:
            pass


def get_backup_summary():
    """
    返回备份状态摘要，方便调试或之后显示到设置页。
    """
    backup_dir = get_backup_dir()
    auto_backups = list_auto_backups()

    return {
        "backup_dir": str(backup_dir),
        "auto_backup_count": len(auto_backups),
        "latest_auto_backup": str(auto_backups[0]) if auto_backups else None,
    }

def get_backup_folder_path():
    """
    返回备份文件夹路径。
    """
    ensure_data_guard_dirs()
    return get_backup_dir()