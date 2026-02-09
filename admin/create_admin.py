import sqlite3
from werkzeug.security import generate_password_hash
import sys
from engine.gatekeeper import init_users

def create_admin(username, password, email):
    # Ensure tables are initialized and migrated first
    init_users()
    
    conn = sqlite3.connect("cryptex.db")
    cur = conn.cursor()
    
    try:
        # 1. Insert user with admin flag set to 1
        cur.execute("""
            INSERT INTO users (username, password, email, is_admin) 
            VALUES (?, ?, ?, 1)
        """, (username, generate_password_hash(password), email))
        
        conn.commit()
        print(f"Successfully created Admin: {username}")
    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' or email '{email}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python create_admin.py <username> <password> <email>")
    else:
        create_admin(sys.argv[1], sys.argv[2], sys.argv[3])