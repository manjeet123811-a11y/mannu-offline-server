# database.py
import sqlite3

def get_conn():
    return sqlite3.connect("users.db", check_same_thread=False)

def verify_user(u, p):
    c = get_conn().cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p))
    row = c.fetchone()
    return row[0] if row else None

def create_user(u, p):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?,?)", (u,p))
        conn.commit()
        return True, "OK"
    except Exception as e:
        return False, str(e)

def get_user_config(uid):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT chat_id, chat_type, delay, cookies, messages, running FROM config WHERE user_id=?", (uid,))
    row = c.fetchone()
    if not row: 
        return {}
    keys = ["chat_id","chat_type","delay","cookies","messages","running"]
    return dict(zip(keys, row))

def update_user_config(uid, chat_id, chat_type, delay, cookies, messages, running):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE config SET chat_id=?, chat_type=?, delay=?, cookies=?, messages=?, running=? WHERE user_id=?",
              (chat_id, chat_type, delay, cookies, messages, running, uid))
    conn.commit()
