import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from pet_system import pet_growth


def main():
    print("=== 宠物基础信息 ===")
    print("默认宠物皮肤：", pet_growth.DEFAULT_PET_SKIN)
    print("默认宠物名字：", pet_growth.DEFAULT_PET_NAME)

    print("\n=== 升级所需经验测试 ===")
    for level in range(1, 11):
        required_exp = pet_growth.get_required_exp(level)
        stage = pet_growth.calculate_stage(level)
        stage_name = pet_growth.get_stage_name(stage)

        print(
            f"Lv.{level} -> 下一级需要 {required_exp} EXP，"
            f"当前阶段：Stage {stage}，{stage_name}"
        )

    print("\n=== 阶段计算测试 ===")
    test_levels = [1, 4, 5, 9, 10, 19, 20, 30]

    for level in test_levels:
        stage = pet_growth.calculate_stage(level)
        stage_name = pet_growth.get_stage_name(stage)
        print(f"Lv.{level} -> Stage {stage}，{stage_name}")

    print("\n=== 经验奖励测试 ===")

    reward_1 = pet_growth.calculate_exp_reward(
        has_remind_time=False,
        streak_days=0,
        completed_all_today=False
    )
    print("普通任务：", reward_1, "EXP")

    reward_2 = pet_growth.calculate_exp_reward(
        has_remind_time=True,
        streak_days=0,
        completed_all_today=False
    )
    print("带提醒时间任务：", reward_2, "EXP")

    reward_3 = pet_growth.calculate_exp_reward(
        has_remind_time=True,
        streak_days=3,
        completed_all_today=False
    )
    print("带提醒时间 + 连续打卡：", reward_3, "EXP")

    reward_4 = pet_growth.calculate_exp_reward(
        has_remind_time=True,
        streak_days=5,
        completed_all_today=True
    )
    print("带提醒时间 + 连续打卡 + 今日全完成：", reward_4, "EXP")


if __name__ == "__main__":
    main()