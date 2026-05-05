import sys
from pathlib import Path
from datetime import date, datetime, timedelta


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

import database


TEST_PREFIX = "__TEST_DAILY_REFRESH__"


def get_date_str(days_offset=0):
    return (date.today() + timedelta(days=days_offset)).isoformat()


def get_datetime_str(days_offset=0):
    target_date = date.today() + timedelta(days=days_offset)
    return f"{target_date.isoformat()} 09:00:00"


def cleanup_test_data():
    """
    清理本测试脚本创建的数据。
    """
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM tasks
        WHERE title LIKE ?
    """, (f"{TEST_PREFIX}%",))

    task_ids = [row["id"] for row in cursor.fetchall()]

    for task_id in task_ids:
        cursor.execute("""
            DELETE FROM checkins
            WHERE task_id = ?
        """, (task_id,))

        cursor.execute("""
            DELETE FROM tasks
            WHERE id = ?
        """, (task_id,))

    conn.commit()
    conn.close()


def insert_task(
    title,
    task_type,
    created_days_offset,
    task_date_days_offset,
    is_active=1,
    is_archived=0,
    remind_time="09:00",
    repeat_interval_minutes=None,
):
    """
    插入一条测试任务。

    created_days_offset:
        created_at 相对今天的偏移。
        -1 表示昨天，-2 表示前天。

    task_date_days_offset:
        task_date 相对今天的偏移。
    """
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            title,
            description,
            remind_time,
            repeat_interval_minutes,
            task_type,
            is_archived,
            task_date,
            is_active,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title,
        "daily refresh and history test",
        remind_time,
        repeat_interval_minutes,
        task_type,
        is_archived,
        get_date_str(task_date_days_offset),
        is_active,
        get_datetime_str(created_days_offset),
    ))

    task_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return task_id


def insert_checkin(task_id, days_offset):
    """
    插入指定日期的完成记录。
    """
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO checkins (
            task_id,
            checkin_date,
            checkin_time
        )
        VALUES (?, ?, ?)
    """, (
        task_id,
        get_date_str(days_offset),
        "10:00:00"
    ))

    conn.commit()
    conn.close()


def fetch_task(task_id):
    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            task_type,
            task_date,
            is_archived,
            is_active,
            created_at
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return dict(row)


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(
            f"{message}\n"
            f"期望：{expected}\n"
            f"实际：{actual}"
        )


def history_has_task(history, date_str, title):
    """
    判断历史记录中某一天是否包含某个任务。
    """
    for day in history:
        if day["date"] != date_str:
            continue

        for task in day["tasks"]:
            if task["title"] == title:
                return True

    return False


def history_task_done(history, date_str, title):
    """
    判断历史记录中某一天某个任务是否已完成。
    """
    for day in history:
        if day["date"] != date_str:
            continue

        for task in day["tasks"]:
            if task["title"] == title:
                return task["done"]

    return None


def test_daily_refresh_rules():
    """
    测试每日刷新规则。

    规则：
        habit：
            每天更新到今天，不归档。

        active task + 昨天已完成：
            归档。

        active task + 昨天未完成：
            顺延到今天。

        paused task：
            不管昨天完成没完成，都顺延到今天，不归档，保持暂停。

        archived task：
            跳过，不处理。
    """
    print("\n=== 测试每日刷新规则 ===")

    today = get_date_str(0)
    yesterday = get_date_str(-1)

    habit_id = insert_task(
        title=f"{TEST_PREFIX}habit_yesterday",
        task_type="habit",
        created_days_offset=-3,
        task_date_days_offset=-1,
        is_active=1,
        is_archived=0,
    )

    active_done_task_id = insert_task(
        title=f"{TEST_PREFIX}active_task_done_yesterday",
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=-1,
        is_active=1,
        is_archived=0,
    )
    insert_checkin(active_done_task_id, -1)

    active_undone_task_id = insert_task(
        title=f"{TEST_PREFIX}active_task_undone_yesterday",
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=-1,
        is_active=1,
        is_archived=0,
    )

    paused_done_task_id = insert_task(
        title=f"{TEST_PREFIX}paused_task_done_yesterday",
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=-1,
        is_active=0,
        is_archived=0,
    )
    insert_checkin(paused_done_task_id, -1)

    paused_undone_task_id = insert_task(
        title=f"{TEST_PREFIX}paused_task_undone_yesterday",
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=-1,
        is_active=0,
        is_archived=0,
    )

    archived_task_id = insert_task(
        title=f"{TEST_PREFIX}archived_task_should_skip",
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=-1,
        is_active=1,
        is_archived=1,
    )

    result = database.refresh_tasks_for_today()
    print("refresh result:", result)

    habit = fetch_task_required(habit_id)
    active_done = fetch_task_required(active_done_task_id)
    active_undone = fetch_task_required(active_undone_task_id)
    paused_done = fetch_task_required(paused_done_task_id)
    paused_undone = fetch_task_required(paused_undone_task_id)
    archived = fetch_task_required(archived_task_id)

    assert_equal(habit["task_date"], today, "habit 应该更新到今天")
    assert_equal(habit["is_archived"], 0, "habit 不应该归档")

    assert_equal(active_done["task_date"], yesterday, "已完成 task 归档后 task_date 应保持昨天")
    assert_equal(active_done["is_archived"], 1, "启用中的已完成 task 应该归档")

    assert_equal(active_undone["task_date"], today, "未完成 task 应该顺延到今天")
    assert_equal(active_undone["is_archived"], 0, "未完成 task 不应该归档")

    assert_equal(paused_done["task_date"], today, "暂停且已完成 task 也应该顺延到今天")
    assert_equal(paused_done["is_archived"], 0, "暂停 task 不管完成与否都不应该归档")
    assert_equal(paused_done["is_active"], 0, "暂停 task 顺延后仍应保持暂停")

    assert_equal(paused_undone["task_date"], today, "暂停且未完成 task 应该顺延到今天")
    assert_equal(paused_undone["is_archived"], 0, "暂停且未完成 task 不应该归档")
    assert_equal(paused_undone["is_active"], 0, "暂停状态应该保留")

    assert_equal(archived["task_date"], yesterday, "已归档任务应该跳过，不更新 task_date")
    assert_equal(archived["is_archived"], 1, "已归档任务应保持归档")

    print("每日刷新规则测试通过。")


def test_history_existing_task_rules():
    """
    测试历史记录规则。

    规则：
        不管 task / habit / archived / paused，
        只要任务在某一天存在过，就应该出现在那一天历史记录中。

    存在区间：
        habit：
            created_at 到今天。

        task：
            created_at 到 task_date。
    """
    print("\n=== 测试历史记录存在区间规则 ===")

    today = get_date_str(0)
    yesterday = get_date_str(-1)
    two_days_ago = get_date_str(-2)
    three_days_ago = get_date_str(-3)

    task_finished_yesterday_title = f"{TEST_PREFIX}history_task_finished_yesterday"
    task_rolled_to_today_title = f"{TEST_PREFIX}history_task_rolled_to_today"
    habit_title = f"{TEST_PREFIX}history_habit"
    paused_task_title = f"{TEST_PREFIX}history_paused_task"

    task_finished_yesterday_id = insert_task(
        title=task_finished_yesterday_title,
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=-1,
        is_active=1,
        is_archived=1,
    )
    insert_checkin(task_finished_yesterday_id, -1)

    insert_task(
        title=task_rolled_to_today_title,
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=0,
        is_active=1,
        is_archived=0,
    )

    habit_id = insert_task(
        title=habit_title,
        task_type="habit",
        created_days_offset=-3,
        task_date_days_offset=0,
        is_active=1,
        is_archived=0,
    )
    insert_checkin(habit_id, -1)

    paused_task_id = insert_task(
        title=paused_task_title,
        task_type="task",
        created_days_offset=-2,
        task_date_days_offset=0,
        is_active=0,
        is_archived=0,
    )
    insert_checkin(paused_task_id, -2)

    history = database.get_history_records(days=4)

    # task：前天创建，昨天完成并归档
    assert_equal(
        history_has_task(history, two_days_ago, task_finished_yesterday_title),
        True,
        "已归档 task 在创建当天应该显示"
    )
    assert_equal(
        history_has_task(history, yesterday, task_finished_yesterday_title),
        True,
        "已归档 task 在完成当天应该显示"
    )
    assert_equal(
        history_has_task(history, today, task_finished_yesterday_title),
        False,
        "已归档 task 在 task_date 之后不应该继续显示"
    )
    assert_equal(
        history_task_done(history, yesterday, task_finished_yesterday_title),
        True,
        "已归档 task 在完成当天应该显示已完成"
    )

    # task：前天创建，顺延到今天
    assert_equal(
        history_has_task(history, two_days_ago, task_rolled_to_today_title),
        True,
        "顺延 task 在创建当天应该显示"
    )
    assert_equal(
        history_has_task(history, yesterday, task_rolled_to_today_title),
        True,
        "顺延 task 在中间日期应该显示"
    )
    assert_equal(
        history_has_task(history, today, task_rolled_to_today_title),
        True,
        "顺延 task 在今天应该显示"
    )
    assert_equal(
        history_task_done(history, today, task_rolled_to_today_title),
        False,
        "未完成的顺延 task 今天应该显示未完成"
    )

    # habit：从创建日起每天显示
    assert_equal(
        history_has_task(history, three_days_ago, habit_title),
        True,
        "habit 在创建当天应该显示"
    )
    assert_equal(
        history_has_task(history, yesterday, habit_title),
        True,
        "habit 在昨天应该显示"
    )
    assert_equal(
        history_has_task(history, today, habit_title),
        True,
        "habit 在今天应该显示"
    )
    assert_equal(
        history_task_done(history, yesterday, habit_title),
        True,
        "habit 昨天有 checkin 时应该显示已完成"
    )

    # paused task：不因暂停而从历史记录消失
    assert_equal(
        history_has_task(history, two_days_ago, paused_task_title),
        True,
        "暂停 task 在创建当天应该显示"
    )
    assert_equal(
        history_has_task(history, yesterday, paused_task_title),
        True,
        "暂停 task 在顺延期间应该显示"
    )
    assert_equal(
        history_has_task(history, today, paused_task_title),
        True,
        "暂停 task 在今天应该显示"
    )
    assert_equal(
        history_task_done(history, two_days_ago, paused_task_title),
        True,
        "暂停 task 在有 checkin 的日期应该显示已完成"
    )

    print("历史记录存在区间规则测试通过。")


def run_tests():
    """
    运行全部测试。

    注意：
        这个测试会直接写入当前正式数据库。
        测试结束后会清理 TEST_PREFIX 开头的测试任务。
    """
    print("开始测试每日刷新与历史记录规则。")

    database.init_db()

    cleanup_test_data()

    try:
        test_daily_refresh_rules()
        cleanup_test_data()

        test_history_existing_task_rules()
        cleanup_test_data()

        print("\n全部测试通过。")

    except Exception:
        print("\n测试失败，保留测试数据方便排查。")
        raise

    finally:
        # 如果你的 database.py 里有完整性刷新函数，则同步刷新完整性记录
        if hasattr(database, "refresh_integrity_after_db_change"):
            database.refresh_integrity_after_db_change()

def fetch_task_required(task_id):
    """
    获取任务，如果不存在则直接抛出错误。
    用于测试断言，避免 Pylance 认为返回值可能是 None。
    """
    task = fetch_task(task_id)

    if task is None:
        raise AssertionError(f"没有找到测试任务，task_id = {task_id}")

    return task

if __name__ == "__main__":
    run_tests()