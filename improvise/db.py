import sqlite3
from contextlib import contextmanager
from config import DB_NAME

@contextmanager
def get_db_context():
    """Context manager for safe database operations."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_enhanced_tables():
    """Initializes tables for audit logs and file metadata."""
    with get_db_context() as db:
        # Audit Logs
        db.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                username TEXT,
                action TEXT,
                status TEXT,
                ip_address TEXT
            )
        """)
        
        # File Metadata (for AI Analysis)
        db.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_hash TEXT UNIQUE,
                filename TEXT,
                owner TEXT,
                size INTEGER,
                mime_type TEXT,
                risk_score INTEGER DEFAULT 0,
                ai_analysis TEXT,
                upload_time DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
