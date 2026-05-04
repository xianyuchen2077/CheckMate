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
SUSPICIOUS_BACKUP_PREFIX = "suspicious"
RESTORE_BACKUP_PREFIX = "before_restore"


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

def create_suspicious_backup():
    """
    创建可疑数据库备份。

    当完整性检查发现数据库可能被外部修改时，
    不应该立刻刷新 integrity.json，
    而是先把当前数据库保存为 suspicious 备份。
    """
    return create_backup(SUSPICIOUS_BACKUP_PREFIX)

def list_backups(prefix=None):
    """
    列出备份文件。

    prefix:
        None：列出所有 .db 备份
        "auto"：只列出自动备份
        "manual"：只列出手动备份
        "suspicious"：只列出可疑备份

    返回：
        按修改时间从新到旧排序的 Path 列表。
    """
    backup_dir = get_backup_dir()

    if not backup_dir.exists():
        return []

    if prefix is None:
        backups = list(backup_dir.glob("*_checkmate_*.db"))
    else:
        backups = list(backup_dir.glob(f"{prefix}_checkmate_*.db"))

    backups.sort(
        key=lambda path: path.stat().st_mtime,
        reverse=True
    )

    return backups

def get_latest_auto_backup():
    """
    获取最近一次自动备份。
    """
    backups = list_backups(AUTO_BACKUP_PREFIX)

    if not backups:
        return None

    return backups[0]

def restore_database_from_backup(backup_path):
    """
    从指定备份恢复数据库。

    注意：
        这个函数只负责复制文件。
        调用前最好确保程序没有正在写数据库。
    """
    ensure_data_guard_dirs()

    backup_path = Path(backup_path)
    db_path = get_database_path()

    if not backup_path.exists():
        return {
            "success": False,
            "message": "备份文件不存在。",
            "backup_path": str(backup_path),
            "database_path": str(db_path),
        }

    if backup_path.suffix.lower() != ".db":
        return {
            "success": False,
            "message": "备份文件格式不正确。",
            "backup_path": str(backup_path),
            "database_path": str(db_path),
        }

    # 恢复前先备份当前数据库，防止误恢复
    before_restore_backup = create_backup(RESTORE_BACKUP_PREFIX)

    shutil.copy2(backup_path, db_path)

    return {
        "success": True,
        "message": "数据库已从备份恢复。",
        "backup_path": str(backup_path),
        "database_path": str(db_path),
        "before_restore_backup": str(before_restore_backup) if before_restore_backup else None,
    }

def restore_from_latest_auto_backup():
    """
    从最近一次自动备份恢复数据库。
    """
    latest_backup = get_latest_auto_backup()

    if latest_backup is None:
        return {
            "success": False,
            "message": "没有找到可用的自动备份。",
            "backup_path": None,
            "database_path": str(get_database_path()),
        }

    return restore_database_from_backup(latest_backup)