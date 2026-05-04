# data_guard/startup_guard.py

from data_guard.backup_manager import (
    create_auto_backup,
    create_suspicious_backup,
    cleanup_special_backups,
)

from data_guard.integrity_manager import (
    check_integrity,
    refresh_integrity_record,
    lock_integrity_updates,
)

from data_guard.logger import log_info, log_warning, log_error


def build_startup_guard_result(
    status,
    level,
    message,
    should_warn_user=False,
    integrity_status=None,
    integrity_result=None,
    auto_backup_path=None,
    suspicious_backup_path=None,
    cleanup_result=None,
):
    """
    构造统一的数据安全启动结果。

    status:
        ok
        missing_record
        changed
        db_missing
        error

    level:
        info
        warning
        error
    """
    return {
        "status": status,
        "level": level,
        "message": message,
        "should_warn_user": should_warn_user,
        "integrity_status": integrity_status or status,
        "integrity_result": integrity_result,
        "auto_backup_path": str(auto_backup_path) if auto_backup_path else None,
        "suspicious_backup_path": (
            str(suspicious_backup_path) if suspicious_backup_path else None
        ),
        "cleanup_result": cleanup_result,
    }


def run_startup_data_guard():
    """
    程序启动时的数据安全检查流程。

    返回：
        dict，包含当前数据安全状态。
    """
    try:
        integrity_result = check_integrity()
        integrity_status = integrity_result["status"]

        if integrity_status == "changed":
            log_warning(f"数据完整性警告：{integrity_result['message']}")
            log_warning(f"旧 hash：{integrity_result['old_hash']}")
            log_warning(f"当前 hash：{integrity_result['current_hash']}")

            suspicious_backup_path = create_suspicious_backup()
            log_warning(f"已备份可疑数据库：{suspicious_backup_path}")

            lock_integrity_updates()

            return build_startup_guard_result(
                status="changed",
                level="warning",
                message=integrity_result["message"],
                should_warn_user=True,
                integrity_status=integrity_status,
                integrity_result=integrity_result,
                suspicious_backup_path=suspicious_backup_path,
            )

        if integrity_status == "db_missing":
            log_warning(f"数据完整性警告：{integrity_result['message']}")

            return build_startup_guard_result(
                status="db_missing",
                level="warning",
                message=integrity_result["message"],
                should_warn_user=True,
                integrity_status=integrity_status,
                integrity_result=integrity_result,
            )

        if integrity_status == "missing_record":
            log_info(f"数据完整性：{integrity_result['message']}")

            auto_backup_path = create_auto_backup()
            log_info(f"自动备份结果：{auto_backup_path}")

            cleanup_result = cleanup_special_backups()
            log_info(f"特殊备份清理结果：{cleanup_result}")

            refresh_integrity_record()

            return build_startup_guard_result(
                status="missing_record",
                level="info",
                message=integrity_result["message"],
                should_warn_user=False,
                integrity_status=integrity_status,
                integrity_result=integrity_result,
                auto_backup_path=auto_backup_path,
                cleanup_result=cleanup_result,
            )

        if integrity_status == "ok":
            auto_backup_path = create_auto_backup()
            log_info(f"自动备份结果：{auto_backup_path}")

            cleanup_result = cleanup_special_backups()
            log_info(f"特殊备份清理结果：{cleanup_result}")

            refresh_integrity_record()

            return build_startup_guard_result(
                status="ok",
                level="info",
                message="数据库完整性正常。",
                should_warn_user=False,
                integrity_status=integrity_status,
                integrity_result=integrity_result,
                auto_backup_path=auto_backup_path,
                cleanup_result=cleanup_result,
            )

        log_warning(f"未知完整性状态：{integrity_status}")

        return build_startup_guard_result(
            status="unknown",
            level="warning",
            message=f"未知完整性状态：{integrity_status}",
            should_warn_user=True,
            integrity_status=integrity_status,
            integrity_result=integrity_result,
        )

    except Exception as e:
        log_error(f"启动数据安全检查失败：{e}")

        return build_startup_guard_result(
            status="error",
            level="error",
            message=f"启动数据安全检查失败：{e}",
            should_warn_user=True,
        )