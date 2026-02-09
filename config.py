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
DATABASE_URL = os.getenv("DATABASE_URL") # For PostgreSQL in production

# S3 Configuration
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")
S3_SECRET = os.getenv("S3_SECRET")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_ENDPOINT = os.getenv("S3_ENDPOINT") # For S3-compatible services like DigitalOcean

UPLOAD_FOLDER = "uploads"
MAX_CONTENT_LENGTH = 10 * 1024 * 1024

USER_PORTAL_URL = os.getenv("USER_PORTAL_URL", "http://localhost:5000")
ADMIN_PANEL_URL = os.getenv("ADMIN_PANEL_URL", "http://localhost:5001")

def get_db():
    if DATABASE_URL:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
        return conn
    return sqlite3.connect(DB_NAME, timeout=10, check_same_thread=False)