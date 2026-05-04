# data_guard/integrity_manager.py

import hashlib
import json
from datetime import datetime

from data_guard.paths import (
    get_database_path,
    get_integrity_file_path,
    ensure_data_guard_dirs,
)

_INTEGRITY_UPDATE_LOCKED = False

def calculate_file_sha256(file_path):
    """
    计算文件的 SHA256。
    """
    file_path = get_database_path() if file_path is None else file_path

    if not file_path.exists():
        return None

    sha256 = hashlib.sha256()

    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def load_integrity_info():
    """
    读取完整性校验信息。
    """
    integrity_path = get_integrity_file_path()

    if not integrity_path.exists():
        return None

    try:
        with integrity_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def save_integrity_info():
    """
    保存当前数据库完整性校验信息。
    """
    ensure_data_guard_dirs()

    db_path = get_database_path()
    integrity_path = get_integrity_file_path()

    db_hash = calculate_file_sha256(db_path)

    if db_hash is None:
        return None

    info = {
        "database_path": str(db_path),
        "sha256": db_hash,
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "version": 1,
    }

    with integrity_path.open("w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=4)

    return info


def check_integrity():
    """
    检查数据库完整性。

    返回：
        {
            "status": "ok" | "missing_record" | "db_missing" | "changed",
            "message": "...",
            "old_hash": "...",
            "current_hash": "..."
        }
    """
    ensure_data_guard_dirs()

    db_path = get_database_path()

    if not db_path.exists():
        return {
            "status": "db_missing",
            "message": "数据库文件不存在。",
            "old_hash": None,
            "current_hash": None,
        }

    current_hash = calculate_file_sha256(db_path)
    old_info = load_integrity_info()

    if old_info is None:
        save_integrity_info()
        return {
            "status": "missing_record",
            "message": "未找到完整性记录，已创建新的完整性记录。",
            "old_hash": None,
            "current_hash": current_hash,
        }

    old_hash = old_info.get("sha256")

    if old_hash != current_hash:
        return {
            "status": "changed",
            "message": "数据库文件可能被外部修改或发生损坏。",
            "old_hash": old_hash,
            "current_hash": current_hash,
        }

    return {
        "status": "ok",
        "message": "数据库完整性正常。",
        "old_hash": old_hash,
        "current_hash": current_hash,
    }

def refresh_integrity_record():
    """
    数据库正常变化后，刷新完整性记录。

    如果完整性更新已被锁定，说明当前数据库处于可疑状态，
    此时不能刷新 integrity.json。
    """
    if is_integrity_update_locked():
        return None

    return save_integrity_info()

def lock_integrity_updates():
    """
    锁定完整性记录更新。

    当启动时检测到数据库疑似被外部修改后，
    不应该继续自动刷新 integrity.json。
    否则会把可疑数据库登记为正常数据库。
    """
    global _INTEGRITY_UPDATE_LOCKED
    _INTEGRITY_UPDATE_LOCKED = True


def unlock_integrity_updates():
    """
    解锁完整性记录更新。

    后续用户明确选择“信任当前数据库”或“恢复备份”后再调用。
    当前阶段暂时可以不用。
    """
    global _INTEGRITY_UPDATE_LOCKED
    _INTEGRITY_UPDATE_LOCKED = False


def is_integrity_update_locked():
    """
    判断当前是否禁止刷新完整性记录。
    """
    return _INTEGRITY_UPDATE_LOCKED


def trust_current_database():
    """
    信任当前数据库。

    使用场景：
        用户确认当前数据库没有问题，
        或者从备份恢复数据库之后，
        需要把当前数据库重新登记为可信状态。
    """
    unlock_integrity_updates()
    return save_integrity_info()