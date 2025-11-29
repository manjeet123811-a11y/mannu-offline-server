# database.py — Fully Ready Version
import sqlite3
import os

DB_PATH = "users.db"


# ---------- Initialize database ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        chat_id TEXT DEFAULT '',
        name_prefix TEXT DEFAULT '',
        delay INTEGER DEFAULT 15,
        cookies TEXT DEFAULT '',
        messages TEXT DEFAULT '',
        running INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()


# Always call at import
init_db()


# ---------- Create User ----------
def create_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))

        conn.commit()
        conn.close()
        return True, "User created"
    except Exception as e:
        return False, str(e)


# ---------- Verify User ----------
def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    row = cur.fetchone()

    conn.close()
    return row[0] if row else None


# ---------- Get Username by ID ----------
def get_username(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT username FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return row[0] if row else None


# ---------- Get User Config ----------
def get_user_config(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT chat_id, name_prefix, delay, cookies, messages, running
        FROM users WHERE id=?
    """, (user_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "chat_id": row[0] or "",
        "name_prefix": row[1] or "",
        "delay": row[2] or 15,
        "cookies": row[3] or "",
        "messages": row[4] or "",
        "running": bool(row[5])
    }


# ---------- Update User Config ----------
def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages, running=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET chat_id = ?, name_prefix = ?, delay = ?, cookies = ?, messages = ?
        WHERE id = ?
    """, (chat_id, name_prefix, delay, cookies, messages, user_id))

    if running is not None:
        cur.execute("UPDATE users SET running = ? WHERE id = ?", (1 if running else 0, user_id))

    conn.commit()
    conn.close()


# ---------- Running state (START/STOP) ----------
def set_automation_running(user_id, is_running=True):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("UPDATE users SET running=? WHERE id=?", (1 if is_running else 0, user_id))

    conn.commit()
    conn.close()


def get_automation_running(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT running FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()

    conn.close()
    return bool(row[0]) if row else False
