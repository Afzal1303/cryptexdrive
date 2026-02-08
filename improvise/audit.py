from flask import request
from .db import get_db_context

class AuditLogger:
    """Logs system events for security monitoring."""
    
    @staticmethod
    def log_event(username, action, status="success"):
        ip = request.remote_addr if request else "0.0.0.0"
        with get_db_context() as db:
            db.execute("""
                INSERT INTO audit_logs (username, action, status, ip_address)
                VALUES (?, ?, ?, ?)
            """, (username, action, status, ip))
        print(f"[AUDIT] {username} performed {action}: {status}")

    @staticmethod
    def get_all_logs(limit=100):
        """Retrieves the latest system logs."""
        with get_db_context() as db:
            logs = db.execute("""
                SELECT timestamp, username, action, status, ip_address 
                FROM audit_logs 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(log) for log in logs]
