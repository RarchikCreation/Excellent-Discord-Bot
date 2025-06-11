import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = "data/tickets.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            message_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            issue_text TEXT NOT NULL,
            channel_id INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_limits (
            user_id INTEGER PRIMARY KEY,
            last_ticket_time TEXT NOT NULL
        )
    """)
    cursor.execute("""
          CREATE TABLE IF NOT EXISTS created_tickets (
              ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              channel_id INTEGER NOT NULL,
              issue_text TEXT NOT NULL,
              created_at TEXT NOT NULL
          )
      """)
    conn.commit()
    conn.close()

def migrate_db():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE created_tickets ADD COLUMN moderator_id INTEGER")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE created_tickets ADD COLUMN created_at TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


def log_created_ticket(user_id: int, channel_id: int, issue_text: str, moderator_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().isoformat()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS created_tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            issue_text TEXT NOT NULL,
            moderator_id INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        INSERT INTO created_tickets (user_id, channel_id, issue_text, moderator_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, channel_id, issue_text, moderator_id, created_at))
    conn.commit()
    conn.close()

def load_all_created_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, channel_id FROM created_tickets")
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_ticket(message_id: int, user_id: int, issue_text: str, channel_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO tickets (message_id, user_id, issue_text, channel_id) VALUES (?, ?, ?, ?)",
                   (message_id, user_id, issue_text, channel_id))
    conn.commit()
    conn.close()

def load_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT message_id, user_id, issue_text, channel_id FROM tickets")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_ticket(message_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE message_id = ?", (message_id,))
    conn.commit()
    conn.close()

def can_create_ticket(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT last_ticket_time FROM ticket_limits WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return True
    last_time = datetime.fromisoformat(row[0])
    return datetime.now() - last_time >= timedelta(days=1)

def update_ticket_time(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("INSERT OR REPLACE INTO ticket_limits (user_id, last_ticket_time) VALUES (?, ?)", (user_id, now))
    conn.commit()
    conn.close()
