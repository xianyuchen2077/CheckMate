"""
宠物养成系统核心逻辑。

这个文件只负责：
1. 计算升级所需经验
2. 根据等级计算进化阶段
3. 定义阶段名称
4. 后续处理宠物经验、升级、进化

注意：
这个文件暂时不直接操作 UI。
"""

import database

# ============================================================
# 默认宠物配置
# ============================================================
#
# DEFAULT_PET_SKIN:
#     当前默认宠物皮肤 ID。
#
#     它需要和资源文件夹名称保持一致。
#
#     例如：
#         DEFAULT_PET_SKIN = "salty_fish"
#
#     对应资源目录：
#         assets/icons/pets/salty_fish/
#
#     如果以后你新增了其他宠物，例如：
#         assets/icons/pets/cat/
#         assets/icons/pets/rabbit/
#
#     那么可以把这里改成：
#         DEFAULT_PET_SKIN = "cat"
#
DEFAULT_PET_SKIN = "salty_fish"


# DEFAULT_PET_NAME:
#     宠物默认显示名称。
#
#     这个名字会写入数据库 pet_status 表中。
#     后续如果做“给宠物改名”功能，可以从数据库读取并修改。
#
DEFAULT_PET_NAME = "咸鱼仔"

def get_required_exp(level):
    """
    获取当前等级升到下一级需要的经验值。

    设计规则：
    Lv.1 升 Lv.2 需要 120 EXP
    Lv.2 升 Lv.3 需要 140 EXP
    Lv.3 升 Lv.4 需要 160 EXP

    公式：
    100 + level * 20
    """
    return 100 + level * 20


def calculate_stage(level):
    """
    根据宠物等级计算进化阶段。

    当前阶段设计：

        Stage 1: Lv.1  - Lv.4
            名称：咸鱼苗
            说明：初始阶段，刚开始努力。

        Stage 2: Lv.5  - Lv.9
            名称：努力鱼
            说明：已经开始形成习惯。

        Stage 3: Lv.10 - Lv.19
            名称：自律鱼
            说明：坚持较稳定，进入自律状态。

        Stage 4: Lv.20+
            名称：时间管理大师鱼
            说明：长期坚持后的最终阶段。

    注意：
        这里返回的是数字阶段：
            1 / 2 / 3 / 4

        资源文件夹中建议对应：
            stage_1/
            stage_2/
            stage_3/
            stage_4/

        例如：
            assets/icons/pets/salty_fish/stage_1/
            assets/icons/pets/salty_fish/stage_2/
            assets/icons/pets/salty_fish/stage_3/
            assets/icons/pets/salty_fish/stage_4/

    后续如果想增加更多进化阶段，可以同时修改：
        1. calculate_stage()
        2. get_stage_name()
        3. 对应的资源文件夹
    """
    if level >= 20:
        return 4

    if level >= 10:
        return 3

    if level >= 5:
        return 2

    return 1


def get_stage_name(stage):
    """
    根据阶段编号返回阶段名称。

    阶段编号和名称对应关系：

        1 -> 咸鱼苗
        2 -> 努力鱼
        3 -> 自律鱼
        4 -> 时间管理大师鱼

    这个名称主要用于：
        1. 宠物窗口显示
        2. 升级 / 进化提示
        3. 后续宠物详情页面

    如果你想改阶段名字，例如把“咸鱼苗”改成“小咸鱼”，
    只需要修改下面这个字典。
    """
    stage_names = {
        1: "咸鱼苗",
        2: "努力鱼",
        3: "自律鱼",
        4: "时间管理大师鱼",
    }

    return stage_names.get(stage, "未知鱼")


def get_level_title(level):
    """
    根据等级返回当前称号。
    """
    stage = calculate_stage(level)
    return get_stage_name(stage)


def calculate_exp_reward(has_remind_time=False, streak_days=0, completed_all_today=False):
    """
    计算完成任务获得的经验值。

    参数：
    has_remind_time:
        是否是设置了提醒时间的任务

    streak_days:
        当前连续打卡天数

    completed_all_today:
        是否完成了今日全部任务
    """
    exp = 10

    if has_remind_time:
        exp += 5

    if streak_days > 0:
        exp += 5

    if completed_all_today:
        exp += 20

    return exp

def add_exp(exp_amount, reason=""):
    """
    给宠物增加经验，并自动处理升级和进化。

    参数：
        exp_amount: 本次增加的经验值
        reason: 增加经验的原因，例如“完成任务”

    返回：
        一个字典，包含本次成长结果。
    """
    pet = database.get_pet_status()

    if pet is None:
        database.init_db()
        pet = database.get_pet_status()

    old_level = pet["level"]
    old_exp = pet["exp"]
    old_stage = pet["stage"]

    pet_name = pet["pet_name"]
    skin = pet["skin"]
    mood = pet["mood"]
    total_tasks_done = pet["total_tasks_done"]

    new_exp = old_exp + exp_amount
    new_level = old_level
    leveled_up = False

    # 可能一次获得大量经验，所以用 while 支持连续升级
    while new_exp >= get_required_exp(new_level):
        required_exp = get_required_exp(new_level)
        new_exp -= required_exp
        new_level += 1
        leveled_up = True

    new_stage = calculate_stage(new_level)
    evolved = new_stage != old_stage

    # 有经验变化，累计完成任务数 +1
    new_total_tasks_done = total_tasks_done + 1

    # 根据成长结果更新心情
    if evolved:
        new_mood = "evolved"
    elif leveled_up:
        new_mood = "level_up"
    else:
        new_mood = "happy"

    database.save_pet_status(
        pet_name=pet_name,
        skin=skin,
        level=new_level,
        exp=new_exp,
        stage=new_stage,
        mood=new_mood,
        total_tasks_done=new_total_tasks_done
    )

    message = build_growth_message(
        exp_gained=exp_amount,
        old_level=old_level,
        new_level=new_level,
        old_stage=old_stage,
        new_stage=new_stage,
        leveled_up=leveled_up,
        evolved=evolved
    )

    return {
        "reason": reason,
        "exp_gained": exp_amount,
        "old_level": old_level,
        "new_level": new_level,
        "old_exp": old_exp,
        "new_exp": new_exp,
        "old_stage": old_stage,
        "new_stage": new_stage,
        "old_stage_name": get_stage_name(old_stage),
        "new_stage_name": get_stage_name(new_stage),
        "leveled_up": leveled_up,
        "evolved": evolved,
        "message": message,
    }

def build_growth_message(
    exp_gained,
    old_level,
    new_level,
    old_stage,
    new_stage,
    leveled_up,
    evolved
):
    """
    根据成长结果生成提示文案。
    """
    if evolved:
        return (
            f"获得 {exp_gained} EXP！"
            f"宠物进化了：{get_stage_name(old_stage)} → {get_stage_name(new_stage)}！"
        )

    if leveled_up:
        return (
            f"获得 {exp_gained} EXP！"
            f"宠物升级了：Lv.{old_level} → Lv.{new_level}！"
        )

    return f"获得 {exp_gained} EXP，宠物正在努力成长。"

def add_exp_for_completed_task(task):
    """
    根据任务信息，计算完成任务奖励，并给宠物增加经验。

    task 是 database.get_task_by_id(task_id) 返回的任务对象。
    """
    if task is None:
        return None

    has_remind_time = bool(task["remind_time"])

    streak_days = database.get_streak_days()

    total, done = database.get_today_stats()
    completed_all_today = total > 0 and done >= total

    exp_reward = calculate_exp_reward(
        has_remind_time=has_remind_time,
        streak_days=streak_days,
        completed_all_today=completed_all_today
    )

    return add_exp(
        exp_amount=exp_reward,
        reason=f"完成任务：{task['title']}"
    )