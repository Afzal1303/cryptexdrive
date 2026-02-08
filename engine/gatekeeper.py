import sqlite3
import secrets
import time
from werkzeug.security import generate_password_hash, check_password_hash

DB = "cryptex.db"

def get_db():
    return sqlite3.connect(DB, timeout=10, check_same_thread=False)

def init_users():
    conn = get_db()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                email TEXT,
                otp TEXT,
                otp_time INTEGER,
                last_otp_sent INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
        """)
        # Migration: add is_admin if it doesn't exist
        try:
            conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        conn.commit()
    finally:
        conn.close()

def is_admin(username):
    conn = get_db()
    try:
        cur = conn.execute("SELECT is_admin FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        return row and row[0] == 1
    finally:
        conn.close()

def register_user(username, password, email):
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Username or Email already exists
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_db()
    try:
        cur = conn.execute(
            "SELECT password FROM users WHERE username=?", (username,)
        )
        row = cur.fetchone()
        return row and check_password_hash(row[0], password)
    finally:
        conn.close()

def generate_otp(username):
    conn = get_db()
    try:
        cur = conn.execute(
            "SELECT last_otp_sent FROM users WHERE username=?", (username,)
        )
        row = cur.fetchone()

        last_sent = row[0] if row and row[0] else 0
        now = int(time.time())

        # ⛔ 1 OTP per 60 seconds
        if now - last_sent < 60:
            return None

        # Secure OTP generation
        otp = str(secrets.randbelow(900000) + 100000)

        conn.execute("""
            UPDATE users
            SET otp=?, otp_time=?, last_otp_sent=?
            WHERE username=?
        """, (otp, now, now, username))

        conn.commit()
        return otp
    finally:
        conn.close()

def verify_otp(username, code):
    conn = get_db()
    try:
        cur = conn.execute(
            "SELECT otp, otp_time FROM users WHERE username=?", (username,)
        )
        row = cur.fetchone()

        if not row or not row[0]:
            return False

        otp, ts = row

        # ⏱ valid 5 minutes
        if int(time.time()) - ts > 300:
            return False

        if otp == code:
            # ✅ Clear OTP after success to prevent reuse
            conn.execute(
                "UPDATE users SET otp=NULL, otp_time=NULL WHERE username=?",
                (username,)
            )
            conn.commit()
            return True
        
        return False
    finally:
        conn.close()

def get_email(username):
    conn = get_db()
    try:
        cur = conn.execute("SELECT email FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

def delete_user_db(username):
    conn = get_db()
    try:
        conn.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()
