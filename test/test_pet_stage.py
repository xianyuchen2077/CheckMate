import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import database


def main():
    database.init_db()

    pet = database.get_pet_status()

    if pet is None:
        print("没有找到宠物状态")
        return

    database.save_pet_status(
        pet_name=pet["pet_name"],
        skin=pet["skin"],
        level=1,
        exp=0,
        stage=1,
        mood="evolved",
        total_tasks_done=pet["total_tasks_done"]
    )

    print("已把宠物强制设置为 Lv.1 / Stage 1")


if __name__ == "__main__":
    main()