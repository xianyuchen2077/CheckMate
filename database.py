import sqlite3
import sys
from pathlib import Path
from datetime import date, datetime, timedelta

from pet_system import pet_growth
from data_guard.integrity_manager import refresh_integrity_record
from data_guard.paths import get_database_dir, get_database_path

def get_app_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


DB_DIR = get_database_dir()
DB_PATH = get_database_path()


def get_connection():
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def refresh_integrity_after_db_change():
    """
    数据库发生正常写入后，刷新完整性记录。

    如果当前数据库处于可疑状态，
    integrity_manager 会自动跳过刷新。
    """
    try:
        refresh_integrity_record()
    except Exception as e:
        print("刷新数据库完整性记录失败：", e)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 任务表：保存长期存在的任务
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            remind_time TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 如果是旧数据库，tasks 表可能没有 remind_time 字段，这里自动补上
    cursor.execute("PRAGMA table_info(tasks)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "remind_time" not in columns:
        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN remind_time TEXT
        """)

    if "is_active" not in columns:
        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
        """)

    if "description" not in columns:
        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN description TEXT
        """)

    if "repeat_interval_minutes" not in columns:
        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN repeat_interval_minutes INTEGER
        """)

    if "task_type" not in columns:
        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN task_type TEXT NOT NULL DEFAULT 'habit'
        """)

    if "is_archived" not in columns:
        cursor.execute("""
            ALTER TABLE tasks
            ADD COLUMN is_archived INTEGER NOT NULL DEFAULT 0
        """)

    # 打卡记录表：保存每天的完成记录
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            checkin_date TEXT NOT NULL,
            checkin_time TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(task_id) REFERENCES tasks(id),
            UNIQUE(task_id, checkin_date)
        )
    """)

    # 宠物状态表：保存宠物等级、经验和进化阶段
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pet_status (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            pet_name TEXT NOT NULL,
            skin TEXT NOT NULL,
            level INTEGER NOT NULL DEFAULT 1,
            exp INTEGER NOT NULL DEFAULT 0,
            stage INTEGER NOT NULL DEFAULT 1,
            mood TEXT NOT NULL DEFAULT 'idle',
            total_tasks_done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 第一版只养一只宠物，所以固定 id = 1
    cursor.execute("""
        INSERT OR IGNORE INTO pet_status (
            id,
            pet_name,
            skin,
            level,
            exp,
            stage,
            mood,
            total_tasks_done
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        pet_growth.DEFAULT_PET_NAME,
        pet_growth.DEFAULT_PET_SKIN,
        1,
        0,
        1,
        "idle",
        0
    ))

    conn.commit()
    conn.close()


def migrate_old_tasks_table():
    """
    兼容之前的旧数据库。
    如果 tasks 表里还有 is_done 字段，也不强行删除。
    新版本代码只是不再使用 is_done。
    """
    pass


def get_today_string():
    return date.today().isoformat()


def get_all_tasks_with_today_status():
    """
    获取今日任务列表。

    habit：
        只要未归档，每天都显示。

    task：
        只在创建当天显示。
        第二天会被归档，不再显示。
    """
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tasks.id,
            tasks.title,
            tasks.remind_time,
            tasks.repeat_interval_minutes,
            tasks.task_type,
            tasks.is_archived,
            tasks.is_active,
            tasks.created_at,
            CASE
                WHEN checkins.id IS NULL THEN 0
                ELSE 1
            END AS is_done_today
        FROM tasks
        LEFT JOIN checkins
            ON tasks.id = checkins.task_id
            AND checkins.checkin_date = ?
        WHERE tasks.is_archived = 0
          AND (
                tasks.task_type = 'habit'
                OR (
                    tasks.task_type = 'task'
                    AND substr(tasks.created_at, 1, 10) = ?
                )
          )
        ORDER BY tasks.id DESC
    """, (today, today))

    tasks = cursor.fetchall()
    conn.close()

    return tasks


def add_task(
    title,
    remind_time=None,
    description=None,
    repeat_interval_minutes=None,
    task_type="habit"
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            title,
            remind_time,
            description,
            repeat_interval_minutes,
            task_type,
            is_archived
        )
        VALUES (?, ?, ?, ?, ?, 0)
    """, (
        title,
        remind_time,
        description,
        repeat_interval_minutes,
        task_type
    ))

    conn.commit()
    conn.close()

    refresh_integrity_after_db_change()

def get_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            remind_time,
            description,
            repeat_interval_minutes,
            task_type,
            is_archived,
            created_at,
            is_active
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    task = cursor.fetchone()
    conn.close()

    return task

def update_task(
    task_id,
    title,
    remind_time,
    description=None,
    repeat_interval_minutes=None,
    task_type="habit"
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET title = ?,
            remind_time = ?,
            description = ?,
            repeat_interval_minutes = ?,
            task_type = ?
        WHERE id = ?
    """, (
        title,
        remind_time,
        description,
        repeat_interval_minutes,
        task_type,
        task_id
    ))

    conn.commit()
    conn.close()

    refresh_integrity_after_db_change()

def delete_task(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    # 先删这个任务相关的打卡记录
    cursor.execute("""
        DELETE FROM checkins
        WHERE task_id = ?
    """, (task_id,))

    # 再删任务本身
    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    refresh_integrity_after_db_change()

def mark_task_done_today(task_id):
    """
    标记任务今天已完成。

    返回：
        True：本次确实新增了一条打卡记录
        False：今天已经打过卡，没有重复新增
    """
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO checkins (task_id, checkin_date)
        VALUES (?, ?)
    """, (task_id, today))

    is_new_checkin = cursor.rowcount > 0

    conn.commit()
    conn.close()

    if is_new_checkin:
        refresh_integrity_after_db_change()

    return is_new_checkin


def get_today_stats():
    """
    获取今日任务统计。

    只统计今日任务列表中应该出现的任务：
        1. 未归档 habit
        2. 未归档且今天创建的 task
    """
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM tasks
        WHERE is_archived = 0
          AND (
                task_type = 'habit'
                OR (
                    task_type = 'task'
                    AND substr(created_at, 1, 10) = ?
                )
          )
    """, (today,))
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS done
        FROM checkins
        INNER JOIN tasks
            ON tasks.id = checkins.task_id
        WHERE checkins.checkin_date = ?
          AND tasks.is_archived = 0
          AND (
                tasks.task_type = 'habit'
                OR (
                    tasks.task_type = 'task'
                    AND substr(tasks.created_at, 1, 10) = ?
                )
          )
    """, (today, today))
    done = cursor.fetchone()["done"]

    conn.close()

    return total, done


def get_month_stats():
    today = date.today()
    month_prefix = today.strftime("%Y-%m")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total_tasks
        FROM tasks
    """)
    total_tasks = cursor.fetchone()["total_tasks"]

    cursor.execute("""
        SELECT COUNT(*) AS done_count
        FROM checkins
        WHERE checkin_date LIKE ?
    """, (month_prefix + "%",))
    done_count = cursor.fetchone()["done_count"]

    conn.close()

    if total_tasks == 0:
        return 0

    # 简化计算：用“本月累计打卡次数 / 任务数 * 当前日期天数”
    days_passed = today.day
    possible_count = total_tasks * days_passed

    if possible_count == 0:
        return 0

    return int(done_count / possible_count * 100)


def get_streak_days():
    """
    计算连续打卡天数。
    简化规则：
    只要某一天有任意任务完成，就算当天打卡。
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT checkin_date
        FROM checkins
        ORDER BY checkin_date DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    checked_dates = {row["checkin_date"] for row in rows}

    streak = 0
    current_day = date.today()

    while current_day.isoformat() in checked_dates:
        streak += 1
        current_day = date.fromordinal(current_day.toordinal() - 1)

    return streak

def get_due_tasks_now():
    """
    获取当前时间需要提醒的任务。

    habit：
        每天保留并提醒。

    task：
        只在创建当天提醒。
        第二天归档后不再提醒。

    重复提醒任务：
        不受今日 checkins 限制。
    """
    now_time = datetime.now().strftime("%H:%M")
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tasks.id,
            tasks.title,
            tasks.remind_time,
            tasks.repeat_interval_minutes,
            tasks.task_type
        FROM tasks
        LEFT JOIN checkins
            ON tasks.id = checkins.task_id
            AND checkins.checkin_date = ?
        WHERE tasks.is_active = 1
          AND tasks.is_archived = 0
          AND tasks.remind_time IS NOT NULL
          AND tasks.remind_time != ''
          AND tasks.remind_time = ?
          AND (
                tasks.task_type = 'habit'
                OR (
                    tasks.task_type = 'task'
                    AND substr(tasks.created_at, 1, 10) = ?
                )
          )
          AND (
                tasks.repeat_interval_minutes IS NOT NULL
                OR checkins.id IS NULL
          )
    """, (today, now_time, today))

    tasks = cursor.fetchall()
    conn.close()

    return tasks

def toggle_task_active(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET is_active = CASE
            WHEN is_active = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
    """, (task_id,))

    conn.commit()
    conn.close()

    refresh_integrity_after_db_change()

def get_history_records(days=7):
    """
    获取最近 days 天的打卡历史。

    显示规则：
        habit：
            从创建日期开始，每一天都显示。

        task：
            只在创建当天显示。
            即使第二天被归档，也仍然能在创建当天的历史记录里看到。
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            created_at,
            task_type,
            is_archived
        FROM tasks
        ORDER BY id ASC
    """)
    tasks = cursor.fetchall()

    history = []
    today = date.today()

    for offset in range(days):
        current_date = today - timedelta(days=offset)
        date_str = current_date.isoformat()

        day_tasks = []

        for task in tasks:
            created_at = task["created_at"]
            created_date = created_at[:10] if created_at else date_str

            task_type = task["task_type"] or "habit"

            # 如果任务是在 current_date 之后创建的，
            # 那么这一天不显示这个任务
            if created_date > date_str:
                continue

            # 一次性任务只在创建当天显示到历史记录里
            # 即使它已经被归档，也仍然保留创建当天的历史展示
            if task_type == "task" and created_date != date_str:
                continue

            cursor.execute("""
                SELECT id
                FROM checkins
                WHERE task_id = ?
                  AND checkin_date = ?
            """, (task["id"], date_str))

            checkin = cursor.fetchone()

            day_tasks.append({
                "title": task["title"],
                "description": task["description"],
                "done": checkin is not None,
                "task_type": task_type,
                "is_archived": task["is_archived"],
            })

        history.append({
            "date": date_str,
            "tasks": day_tasks
        })

    conn.close()
    return history


def get_pet_status():
    """
    获取当前宠物状态。
    第一版只支持一只宠物，所以固定查询 id = 1。
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            pet_name,
            skin,
            level,
            exp,
            stage,
            mood,
            total_tasks_done,
            created_at,
            updated_at
        FROM pet_status
        WHERE id = 1
    """)

    pet_status = cursor.fetchone()
    conn.close()

    return pet_status

def update_pet_status(level, exp, stage, mood=None, total_tasks_done=None):
    """
    更新宠物状态。
    """
    conn = get_connection()
    cursor = conn.cursor()

    if mood is not None and total_tasks_done is not None:
        cursor.execute("""
            UPDATE pet_status
            SET level = ?,
                exp = ?,
                stage = ?,
                mood = ?,
                total_tasks_done = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (level, exp, stage, mood, total_tasks_done))

    elif mood is not None:
        cursor.execute("""
            UPDATE pet_status
            SET level = ?,
                exp = ?,
                stage = ?,
                mood = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (level, exp, stage, mood))

    elif total_tasks_done is not None:
        cursor.execute("""
            UPDATE pet_status
            SET level = ?,
                exp = ?,
                stage = ?,
                total_tasks_done = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (level, exp, stage, total_tasks_done))

    else:
        cursor.execute("""
            UPDATE pet_status
            SET level = ?,
                exp = ?,
                stage = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = 1
        """, (level, exp, stage))

    conn.commit()
    conn.close()

    refresh_integrity_after_db_change()

def save_pet_status(
    pet_name,
    skin,
    level,
    exp,
    stage,
    mood,
    total_tasks_done
):
    """
    保存宠物完整状态。
    第一版只支持一只宠物，所以固定 id = 1。

    使用 UPSERT：
        如果 id=1 已存在，则更新；
        如果 id=1 不存在，则自动插入。
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pet_status (
            id,
            pet_name,
            skin,
            level,
            exp,
            stage,
            mood,
            total_tasks_done
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            pet_name = excluded.pet_name,
            skin = excluded.skin,
            level = excluded.level,
            exp = excluded.exp,
            stage = excluded.stage,
            mood = excluded.mood,
            total_tasks_done = excluded.total_tasks_done,
            updated_at = CURRENT_TIMESTAMP
    """, (
        1,
        pet_name,
        skin,
        level,
        exp,
        stage,
        mood,
        total_tasks_done
    ))

    conn.commit()
    conn.close()

    # 如果你已经在 database.py 里加了完整性刷新函数，就保留这一句。
    # 如果没有这个函数，先注释掉。
    try:
        refresh_integrity_after_db_change()
    except NameError:
        pass

def is_task_done_today(task_id):
    """
    判断任务今天是否已经完成。
    """
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM checkins
        WHERE task_id = ?
          AND checkin_date = ?
    """, (task_id, today))

    row = cursor.fetchone()
    conn.close()

    return row is not None


def is_task_active(task_id):
    """
    判断任务是否仍然启用。
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT is_active
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return False

    return row["is_active"] == 1

def archive_expired_one_day_tasks():
    """
    归档过期的一次性任务。

    规则：
        task_type = 'task' 的任务只在创建当天显示。
        第二天启动程序时，将其 is_archived 设为 1。

    注意：
        不删除 tasks 记录。
        不删除 checkins 记录。
        这样历史记录仍然可以看到昨天完成过的一次性任务。
    """
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET is_archived = 1
        WHERE task_type = 'task'
          AND is_archived = 0
          AND substr(created_at, 1, 10) < ?
    """, (today,))

    archived_count = cursor.rowcount

    conn.commit()
    conn.close()

    if archived_count > 0:
        refresh_integrity_after_db_change()

    return archived_count