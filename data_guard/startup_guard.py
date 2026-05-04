from data_guard.backup_manager import (
    create_auto_backup,
    create_suspicious_backup,
    cleanup_suspicious_backups,
)

from data_guard.integrity_manager import (
    check_integrity,
    refresh_integrity_record,
    lock_integrity_updates,
)


def run_startup_data_guard():
    """
    程序启动时的数据安全检查流程。

    返回：
        dict，包含当前数据安全状态。
    """
    integrity_result = check_integrity()
    integrity_status = integrity_result["status"]

    result = {
        "integrity_status": integrity_status,
        "integrity_result": integrity_result,
        "auto_backup_path": None,
        "suspicious_backup_path": None,
        "should_warn_user": False,
        "message": integrity_result.get("message", ""),
    }

    if integrity_status == "changed":
        print("数据完整性警告：", integrity_result["message"])
        print("旧 hash：", integrity_result["old_hash"])
        print("当前 hash：", integrity_result["current_hash"])

        suspicious_backup_path = create_suspicious_backup()
        print("已备份可疑数据库：", suspicious_backup_path)

        lock_integrity_updates()

        result["suspicious_backup_path"] = str(suspicious_backup_path)
        result["should_warn_user"] = True

        return result

    if integrity_status == "db_missing":
        print("数据完整性警告：", integrity_result["message"])

        result["should_warn_user"] = True
        return result

    if integrity_status == "missing_record":
        print("数据完整性：", integrity_result["message"])

    auto_backup_path = create_auto_backup()
    print("自动备份结果：", auto_backup_path)

    cleanup_result = cleanup_suspicious_backups()
    print("特殊备份清理结果：", cleanup_result)

    refresh_integrity_record()

    result["auto_backup_path"] = str(auto_backup_path) if auto_backup_path else None

    return result