import sqlite3
from pathlib import Path
from datetime import date, datetime, timedelta


DB_DIR = Path("data")
DB_PATH = DB_DIR / "checkmate.db"


def get_connection():
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 任务表：保存长期存在的任务
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
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
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tasks.id,
            tasks.title,
            tasks.remind_time,
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
        ORDER BY tasks.id DESC
    """, (today,))

    tasks = cursor.fetchall()
    conn.close()

    return tasks


def add_task(title, remind_time=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, remind_time)
        VALUES (?, ?)
    """, (title, remind_time))

    conn.commit()
    conn.close()

def get_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, remind_time, created_at, is_active
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    task = cursor.fetchone()
    conn.close()

    return task


def update_task(task_id, title, remind_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET title = ?, remind_time = ?
        WHERE id = ?
    """, (title, remind_time, task_id))

    conn.commit()
    conn.close()

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


def mark_task_done_today(task_id):
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    # INSERT OR IGNORE 可以避免同一天重复打卡
    cursor.execute("""
        INSERT OR IGNORE INTO checkins (task_id, checkin_date, checkin_time)
        VALUES (?, ?, ?)
    """, (task_id, today, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()


def get_today_stats():
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM tasks
    """)
    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS done
        FROM checkins
        WHERE checkin_date = ?
    """, (today,))
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
    获取当前时间需要提醒、且今天还没完成的任务。
    没有设置提醒时间的任务不会触发提醒。
    暂停任务不会触发提醒。
    """
    now_time = datetime.now().strftime("%H:%M")
    today = get_today_string()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tasks.id,
            tasks.title,
            tasks.remind_time
        FROM tasks
        LEFT JOIN checkins
            ON tasks.id = checkins.task_id
            AND checkins.checkin_date = ?
        WHERE tasks.is_active = 1
          AND tasks.remind_time IS NOT NULL
          AND tasks.remind_time != ''
          AND tasks.remind_time = ?
          AND checkins.id IS NULL
    """, (today, now_time))

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

def get_history_records(days=7):
    """
    获取最近 days 天的打卡历史。
    只显示任务创建日期之后的记录。

    返回结构：
    [
        {
            "date": "2026-05-03",
            "tasks": [
                {"title": "背单词", "done": True},
                {"title": "写代码", "done": False},
            ]
        }
    ]
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, created_at
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

            # created_at 通常形如：2026-05-03 12:30:00
            # 这里只取前 10 位日期部分：2026-05-03
            created_date = created_at[:10] if created_at else date_str

            # 如果任务是在 current_date 之后创建的，
            # 那么这一天不显示这个任务
            if created_date > date_str:
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
                "done": checkin is not None
            })

        history.append({
            "date": date_str,
            "tasks": day_tasks
        })

    conn.close()
    return history