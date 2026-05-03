import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import database
from pet_system import pet_growth


def print_pet_status():
    pet = database.get_pet_status()

    print("名字：", pet["pet_name"])
    print("皮肤：", pet["skin"])
    print("等级：", pet["level"])
    print("经验：", pet["exp"], "/", pet_growth.get_required_exp(pet["level"]))
    print("阶段：", pet["stage"], pet_growth.get_stage_name(pet["stage"]))
    print("心情：", pet["mood"])
    print("累计完成任务：", pet["total_tasks_done"])


def main():
    database.init_db()

    print("=== 加经验前 ===")
    print_pet_status()

    print("\n=== 模拟获得 50 EXP ===")
    result = pet_growth.add_exp(50, reason="测试加经验")
    print(result["message"])

    print("\n=== 加经验后 ===")
    print_pet_status()

    print("\n=== 模拟获得 200 EXP，测试升级 ===")
    result = pet_growth.add_exp(200, reason="测试升级")
    print(result["message"])

    print("\n=== 最终宠物状态 ===")
    print_pet_status()


if __name__ == "__main__":
    main()