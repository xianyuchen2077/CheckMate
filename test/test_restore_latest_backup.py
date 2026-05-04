import sys
from pathlib import Path

# 当前文件在 CheckMate/test/test_restore_lastest_backup.py
# parents[1] 是 CheckMate 项目根目录
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from data_guard.backup_manager import restore_from_latest_auto_backup
from data_guard.integrity_manager import trust_current_database


result = restore_from_latest_auto_backup()

print("恢复结果：")
for key, value in result.items():
    print(f"{key}: {value}")

if result.get("success"):
    info = trust_current_database()
    print("已信任恢复后的数据库：")
    print(info)