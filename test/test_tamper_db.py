import sqlite3
from pathlib import Path

# 当前文件在 CheckMate/test/test_tamper_db.py
# parents[1] 才是 CheckMate 项目根目录
BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "data" / "checkmate.db"

print("数据库路径：", DB_PATH)

if not DB_PATH.exists():
    print("数据库文件不存在，请确认路径是否正确。")
    raise SystemExit

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT id, title
    FROM tasks
    ORDER BY id DESC
    LIMIT 1
""")

task = cursor.fetchone()

if task is None:
    print("没有找到任务，请先在 CheckMate 里添加一个任务。")
else:
    task_id, old_title = task
    new_title = old_title + "_tampered"

    cursor.execute("""
        UPDATE tasks
        SET title = ?
        WHERE id = ?
    """, (new_title, task_id))

    conn.commit()

    print("已篡改数据库：")
    print("任务 ID：", task_id)
    print("原标题：", old_title)
    print("新标题：", new_title)

conn.close()