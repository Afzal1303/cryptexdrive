import sqlite3
import random
import time
from werkzeug.security import generate_password_hash, check_password_hash

DB = "cryptex.db"

def get_db():
    return sqlite3.connect(DB, timeout=10, check_same_thread=False)

def init_users():
    db = get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            otp TEXT,
            otp_time INTEGER,
            last_otp_sent INTEGER DEFAULT 0
        )
    """)
    db.commit()
    db.close()

def register_user(username, password, email):
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), email)
        )
        db.commit()
        return True
    except:
        return False
    finally:
        db.close()

def verify_user(username, password):
    db = get_db()
    cur = db.execute(
        "SELECT password FROM users WHERE username=?", (username,)
    )
    row = cur.fetchone()
    db.close()
    return row and check_password_hash(row[0], password)

def generate_otp(username):
    db = get_db()
    cur = db.execute(
        "SELECT last_otp_sent FROM users WHERE username=?", (username,)
    )
    row = cur.fetchone()

    last_sent = row[0] if row and row[0] else 0
    now = int(time.time())

    # ⛔ 1 OTP per 60 seconds
    if now - last_sent < 60:
        db.close()
        return None

    otp = str(random.randint(100000, 999999))

    db.execute("""
        UPDATE users
        SET otp=?, otp_time=?, last_otp_sent=?
        WHERE username=?
    """, (otp, now, now, username))

    db.commit()
    db.close()
    return otp

def verify_otp(username, code):
    db = get_db()
    cur = db.execute(
        "SELECT otp, otp_time FROM users WHERE username=?", (username,)
    )
    row = cur.fetchone()
    db.close()

    if not row or not row[0]:
        return False

    otp, ts = row

    # ⏱ valid 5 minutes
    if int(time.time()) - ts > 300:
        return False

    return otp == code
