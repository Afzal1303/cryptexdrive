import sqlite3
import os
import shutil
import sys

DB_NAME = "cryptex.db"
UPLOAD_FOLDER = "uploads"

def delete_user_completely(username):
    if not username:
        print("Error: No username provided.")
        return

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    try:
        # 1. Check if user exists
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        
        if not user:
            print(f"[-] User '{username}' not found in database.")
            return

        # 2. Delete from users table
        cur.execute("DELETE FROM users WHERE username = ?", (username,))
        
        # 3. Delete from file_metadata table (if it exists)
        try:
            cur.execute("DELETE FROM file_metadata WHERE owner = ?", (username,))
        except sqlite3.OperationalError:
            # Table doesn't exist yet, which is fine
            pass
        
        # 4. Remove physical files
        user_dir = os.path.join(UPLOAD_FOLDER, username)
        if os.path.exists(user_dir):
            shutil.rmtree(user_dir)
            print(f"[+] Deleted file directory: {user_dir}")
        
        conn.commit()
        print(f"[+] Successfully removed user '{username}' and all associated data.")

    except Exception as e:
        print(f"[!] Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_user_manually.py <username>")
        print("\nExisting users:")
        try:
            conn = sqlite3.connect(DB_NAME)
            users = conn.execute("SELECT username FROM users").fetchall()
            for u in users:
                print(f" - {u[0]}")
            conn.close()
        except Exception as e:
            print(f"Error listing users: {e}")
    else:
        target = sys.argv[1]
        delete_user_completely(target)
