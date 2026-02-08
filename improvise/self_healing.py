import os
import time
import threading
from .db import get_db_context
from .audit import AuditLogger
from config import UPLOAD_FOLDER

def monitor_and_heal():
    """
    Background function that periodically checks for files with risk_score > 80.
    Quarantines high-risk files and updates the database.
    """
    while True:
        try:
            with get_db_context() as db:
                # Find high-risk active files
                files_to_heal = db.execute("""
                    SELECT filename, owner, risk_score 
                    FROM file_metadata 
                    WHERE risk_score > 80 AND is_active = 1
                """).fetchall()

                for file_info in files_to_heal:
                    filename = file_info['filename']
                    owner = file_info['owner']
                    
                    user_dir = os.path.join(UPLOAD_FOLDER, owner)
                    old_path = os.path.join(user_dir, filename)
                    new_filename = f"{filename}.quarantine"
                    new_path = os.path.join(user_dir, new_filename)

                    if os.path.exists(old_path):
                        # 1. Rename the file
                        os.rename(old_path, new_path)
                        
                        # 2. Update database
                        db.execute("""
                            UPDATE file_metadata 
                            SET is_active = 0, filename = ? 
                            WHERE filename = ? AND owner = ?
                        """, (new_filename, filename, owner))
                        
                        # 3. Log the action
                        AuditLogger.log_event(
                            owner, 
                            f"Critical Self-Healing Action: Quarantined {filename} (Risk: {file_info['risk_score']})",
                            "healed"
                        )
                        print(f"[SELF-HEALING] Quarantined {filename} for user {owner}")

        except Exception as e:
            print(f"[SELF-HEALING ERROR] {e}")

        # Check every 60 seconds (can be adjusted)
        time.sleep(60)

def start_self_healing():
    """Starts the self-healing monitor in a background thread."""
    thread = threading.Thread(target=monitor_and_heal, daemon=True)
    thread.start()
    print("[SYSTEM] Self-Healing Module Started.")
