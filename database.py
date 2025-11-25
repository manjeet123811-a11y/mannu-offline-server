import sqlite3

DB = "users.db"

def connect():
    return sqlite3.connect(DB, check_same_thread=False)

def setup():
    conn = connect()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS configs (
            user_id INTEGER,
            chat_id TEXT,
            chat_type TEXT,
            delay INTEGER,
            cookies TEXT,
            messages TEXT,
            running INTEGER DEFAULT 0,
            PRIMARY KEY(user_id)
        )
    """)
    conn.commit()
    conn.close()

setup()


def create_user(u, p):
    try:
        conn = connect()
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password) VALUES(?,?)", (u, p))
        uid = c.lastrowid
        c.execute("INSERT INTO configs(user_id) VALUES(?)", (uid,))
        conn.commit()
        conn.close()
        return True, "OK"
    except Exception as e:
        return False, str(e)


def verify_user(u, p):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None


def get_user_config(uid):
    conn = connect()
    c = conn.cursor()
    c.execute("SELECT chat_id, chat_type, delay, cookies, messages, running FROM configs WHERE user_id=?", (uid,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "chat_id": row[0] or "",
            "chat_type": row[1] or "E2EE",
            "delay": row[2] or 15,
            "cookies": row[3] or "",
            "messages": row[4] or "",
            "running": bool(row[5])
        }
    return {}


def update_user_config(uid, chat_id, chat_type, delay, cookies, messages, running=False):
    conn = connect()
    c = conn.cursor()
    c.execute("""
        UPDATE configs
        SET chat_id=?, chat_type=?, delay=?, cookies=?, messages=?, running=?
        WHERE user_id=?
    """, (chat_id, chat_type, delay, cookies, messages, 1 if running else 0, uid))
    conn.commit()
    conn.close()
