import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

import database


def main():
    database.init_db()

    conn = database.get_connection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(tasks)")
    columns = cursor.fetchall()

    print("tasks 表字段：")
    for column in columns:
        print(column["name"])

    conn.close()


if __name__ == "__main__":
    main()