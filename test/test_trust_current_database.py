import sys
import argparse
from pathlib import Path


# 当前文件在 CheckMate/test/test_trust_current_database.py
# parents[1] 是 CheckMate 项目根目录
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


from data_guard.paths import get_database_path, get_integrity_file_path
from data_guard.integrity_manager import (
    check_integrity,
    trust_current_database,
)


def print_result(title, result):
    print(f"\n=== {title} ===")

    if result is None:
        print("结果：None")
        return

    for key, value in result.items():
        print(f"{key}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description="强制信任当前 CheckMate 数据库，并刷新 integrity.json。"
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="跳过确认，直接信任当前数据库。"
    )

    args = parser.parse_args()

    db_path = get_database_path()
    integrity_path = get_integrity_file_path()

    print("当前数据库路径：")
    print(db_path)

    print("\n完整性记录路径：")
    print(integrity_path)

    if not db_path.exists():
        print("\n数据库文件不存在，无法更新完整性记录。")
        return

    before_result = check_integrity()
    print_result("更新前完整性检查", before_result)

    print("\n注意：")
    print("这个脚本会把当前 checkmate.db 作为可信数据库。")
    print("如果当前数据库其实已经被错误修改，运行后 integrity.json 会认可这个状态。")
    print("建议仅在调试时使用。")

    if not args.yes:
        confirm = input("\n确认要信任当前数据库吗？输入 y/Y 继续：")

        if confirm != "y" and confirm != "Y":
            print("已取消。")
            return

    info = trust_current_database()

    if info is None:
        print("\n更新失败：trust_current_database() 返回 None。")
        return

    print("\n已强制信任当前数据库，并更新 integrity.json。")

    print("\n新的完整性记录：")
    for key, value in info.items():
        print(f"{key}: {value}")

    after_result = check_integrity()
    print_result("更新后完整性检查", after_result)


if __name__ == "__main__":
    main()