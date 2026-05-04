# data_guard/migration_manager.py

import shutil
from datetime import datetime
from pathlib import Path

from data_guard.paths import (
    get_database_path,
    get_backup_dir,
    get_integrity_file_path,
    get_legacy_database_path,
    get_legacy_backup_dir,
    ensure_data_guard_dirs,
)


def get_migration_marker_path():
    """
    迁移标记文件。

    用于记录已经执行过迁移，避免每次启动重复迁移。
    """
    return get_backup_dir() / "migration_done.txt"


def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def migrate_legacy_database_if_needed():
    """
    如果发现旧位置存在数据库，而新位置还没有数据库，则迁移旧数据库到新位置。

    迁移策略：
        1. 新数据库已存在：不覆盖。
        2. 新数据库不存在、旧数据库存在：复制旧数据库到新位置。
        3. 旧备份目录存在：复制旧备份文件到新备份目录。
        4. 写入 migration_done.txt 作为迁移记录。

    返回 dict，方便调试。
    """
    ensure_data_guard_dirs()

    new_db_path = get_database_path()
    old_db_path = get_legacy_database_path()

    result = {
        "migrated_database": False,
        "migrated_backups": False,
        "old_database_path": str(old_db_path),
        "new_database_path": str(new_db_path),
        "message": "",
    }

    # 1. 迁移数据库：只在新数据库不存在时复制，避免覆盖用户新数据
    if new_db_path.exists():
        result["message"] = "新数据库已存在，不需要迁移旧数据库。"
    elif old_db_path.exists():
        shutil.copy2(old_db_path, new_db_path)
        result["migrated_database"] = True
        result["message"] = "已将旧数据库迁移到用户数据目录。"
    else:
        result["message"] = "未发现旧数据库，将使用新数据库。"

    # 2. 迁移旧备份目录中的备份文件
    old_backup_dir = get_legacy_backup_dir()
    new_backup_dir = get_backup_dir()

    if old_backup_dir.exists():
        copied_count = 0

        for old_file in old_backup_dir.glob("*"):
            if not old_file.is_file():
                continue

            # 旧 integrity.json 不建议直接复制，
            # 因为数据库路径变了，后面会重新生成。
            if old_file.name == "integrity.json":
                continue

            new_file = new_backup_dir / old_file.name

            if new_file.exists():
                continue

            try:
                shutil.copy2(old_file, new_file)
                copied_count += 1
            except OSError:
                pass

        if copied_count > 0:
            result["migrated_backups"] = True

    # 3. 删除旧完整性记录的影响：新路径下重新生成 integrity.json
    integrity_path = get_integrity_file_path()

    if not integrity_path.exists():
        # 不在这里直接创建，交给 startup_guard / integrity_manager 创建
        pass

    # 4. 写迁移标记
    marker_path = get_migration_marker_path()

    try:
        marker_path.write_text(
            (
                f"Migration checked at: {get_timestamp()}\n"
                f"Old database: {old_db_path}\n"
                f"New database: {new_db_path}\n"
                f"Migrated database: {result['migrated_database']}\n"
                f"Migrated backups: {result['migrated_backups']}\n"
                f"Message: {result['message']}\n"
            ),
            encoding="utf-8"
        )
    except OSError:
        pass

    return result