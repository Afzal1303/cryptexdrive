import sqlite3
import sys

def promote_to_admin(username):
    conn = sqlite3.connect("cryptex.db")
    cur = conn.cursor()
    cur.execute("UPDATE users SET is_admin = 1 WHERE username = ?", (username,))
    if cur.rowcount > 0:
        print(f"User {username} is now an admin.")
    else:
        print(f"User {username} not found.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_admin.py <username>")
    else:
        promote_to_admin(sys.argv[1])
