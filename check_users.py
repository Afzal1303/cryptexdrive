import sqlite3
conn = sqlite3.connect("cryptex.db")
cur = conn.cursor()
try:
    cur.execute("SELECT username, is_admin FROM users")
    rows = cur.fetchall()
    print("Username | Is Admin")
    print("-" * 20)
    for row in rows:
        print(f"{row[0]} | {row[1]}")
except Exception as e:
    print(f"Error: {e}")
conn.close()
