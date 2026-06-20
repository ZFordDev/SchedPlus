import os
import sqlite3
from datetime import datetime
from ..scheduler import Task

# ---------------------------------------------------------
# Database location
# ---------------------------------------------------------

DB_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "tasks.db")
)
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# ---------------------------------------------------------
# Connection helper
# ---------------------------------------------------------

def _get_conn():
    return sqlite3.connect(DB_FILE)

# ---------------------------------------------------------
# Schema initialization
# ---------------------------------------------------------

def init_db():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            text TEXT NOT NULL,
            createdAt TEXT NOT NULL,
            updatedAt TEXT NOT NULL
        );
        """
    )

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Create
# ---------------------------------------------------------

def create_entry(task: Task):
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO entries (id, date, time, text, createdAt, updatedAt)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            task.id,
            task.date,
            task.time,
            task.text,
            task.createdAt,
            task.updatedAt,
        ),
    )

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Update
# ---------------------------------------------------------

def update_entry(task: Task):
    conn = _get_conn()
    cur = conn.cursor()

    task.updatedAt = datetime.utcnow().isoformat()

    cur.execute(
        """
        UPDATE entries
        SET date = ?, time = ?, text = ?, updatedAt = ?
        WHERE id = ?
        """,
        (task.date, task.time, task.text, task.updatedAt, task.id),
    )

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Delete
# ---------------------------------------------------------

def delete_entry(task_id: str):
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("DELETE FROM entries WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Read (single)
# ---------------------------------------------------------

def get_entry(task_id: str):
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT id, date, time, text, createdAt, updatedAt FROM entries WHERE id = ?",
        (task_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return Task(
        id=row[0],
        date=row[1],
        time=row[2],
        text=row[3],
        createdAt=row[4],
        updatedAt=row[5],
    )

# ---------------------------------------------------------
# Read (all)
# ---------------------------------------------------------

def list_entries():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, date, time, text, createdAt, updatedAt
        FROM entries
        ORDER BY date ASC, time ASC
        """
    )

    rows = cur.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append(
            Task(
                id=row[0],
                date=row[1],
                time=row[2],
                text=row[3],
                createdAt=row[4],
                updatedAt=row[5],
            )
        )

    return tasks