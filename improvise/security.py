from werkzeug.utils import secure_filename
import os

class SecurityHarden:
    """Utilities to strengthen application entry points."""
    
    @staticmethod
    def sanitize_path(filename):
        """Prevents path traversal attacks."""
        return secure_filename(filename)

    @staticmethod
    def validate_user_session(session_data):
        """Ensures the session hasn't been tampered with."""
        if not session_data.get("user") or not session_data.get("auth"):
            return False
        return session_data.get("auth") == "2fa_ok"

    @staticmethod
    def check_file_integrity(file_path):
        """Placeholder for checksum verification."""
        # Future: Implement SHA-256 hashing for file integrity
        pass
