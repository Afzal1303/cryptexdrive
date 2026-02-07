import os
import sqlite3
from dotenv import load_dotenv

# Load environment variables from .env if it exists
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "cryptexdrive-ultra-secret-key")

MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True") == "True"
MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False") == "True"
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "cryptexdrive1@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "offt uasp ydge lrlc")

DB_NAME = os.getenv("DB_NAME", "cryptex.db")

UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

def get_db():
    return sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)