import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import database
from pet_system import pet_growth


def main():
    print("=== 初始化数据库 ===")
    database.init_db()

    print("\n=== 当前宠物状态 ===")
    pet = database.get_pet_status()

    if pet is None:
        print("没有找到宠物状态")
        return

    print("名字：", pet["pet_name"])
    print("皮肤：", pet["skin"])
    print("等级：", pet["level"])
    print("经验：", pet["exp"])
    print("阶段：", pet["stage"])
    print("阶段名：", pet_growth.get_stage_name(pet["stage"]))
    print("心情：", pet["mood"])
    print("累计完成任务：", pet["total_tasks_done"])


if __name__ == "__main__":
    main()