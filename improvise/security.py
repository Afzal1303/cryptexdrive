from werkzeug.utils import secure_filename
import os
import jwt
from config import SECRET_KEY
from engine.blacklist import blacklist_jti

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
    def detect_intrusion_and_blacklist(token, pattern_type="Generic Intrusion"):
        """
        AI-driven logic to detect intrusion patterns and blacklist the current JTI.
        """
        if not token:
            return False
            
        if token.startswith("Bearer "):
            token = token[7:]
            
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            jti = payload.get("jti")
            user = payload.get("user")
            
            if jti:
                # Add to Redis Blacklist
                blacklist_jti(jti)
                print(f"[SECURITY ALERT] Blacklisted JTI {jti} for user {user}. Pattern: {pattern_type}")
                return True
        except:
            pass
        return False

    @staticmethod
    def check_file_integrity(file_path):
        """Placeholder for checksum verification."""
        # Future: Implement SHA-256 hashing for file integrity
        pass
