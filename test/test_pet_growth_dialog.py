import sys
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from pet_growth_dialog import PetGrowthDialog


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei", 10))

    growth_result = {
        "exp_gained": 20,
        "old_level": 4,
        "new_level": 5,
        "old_stage": 1,
        "new_stage": 2,
        "old_stage_name": "咸鱼苗",
        "new_stage_name": "努力鱼",
        "leveled_up": True,
        "evolved": True,
        "message": "获得 20 EXP！宠物进化了：咸鱼苗 → 努力鱼！",
    }

    dialog = PetGrowthDialog(growth_result)
    dialog.exec()

    sys.exit(0)


if __name__ == "__main__":
    main()