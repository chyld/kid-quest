import sqlite3
import csv
import io
from datetime import datetime

DATABASE_URL = "tasks.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def create_db_and_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reward INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def insert_task(title: str, reward: int, created_at: datetime, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, reward, created_at, status) VALUES (?, ?, ?, ?)", (title, reward, created_at.isoformat(), status))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return task_id

def get_all_tasks(status: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT id, title, reward, created_at, status FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT id, title, reward, created_at, status FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    conn.close()
    return [dict(task) for task in tasks]

def get_task_by_id(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, reward, created_at, status FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    conn.close()
    return dict(task) if task else None

def update_task(task_id: int, title: str, reward: int, status: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET title = ?, reward = ?, status = ? WHERE id = ?", (title, reward, status, task_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0 # Returns True if a row was updated, False otherwise

def delete_task(task_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0 # Returns True if a row was deleted, False otherwise

def update_task_status(task_id: int, new_status: str):
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()
    return cursor.rowcount > 0

def dump_tasks_to_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, reward, created_at, status FROM tasks ORDER BY created_at DESC")
    tasks = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow(["id", "title", "reward", "created_at", "status"])

    # Write data
    for task in tasks:
        writer.writerow([task["id"], task["title"], task["reward"], task["created_at"], task["status"]])

    return output.getvalue()
