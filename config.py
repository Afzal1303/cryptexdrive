import sqlite3

SECRET_KEY = "cryptexdrive-ultra-secret-key"

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = "cryptexdrive1@gmail.com"
MAIL_PASSWORD = "offt uasp ydge lrlc"

DB_NAME = "cryptex.db"

UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

def get_db():
    return sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)
