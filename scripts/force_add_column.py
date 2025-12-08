import sqlite3
import os

DB_PATH = "jobswipe.db"

def force_add():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(users)")
        cols = [col[1] for col in cursor.fetchall()]
        print(f"Existing Cols: {cols}")
        
        if "resume_file_path" not in cols:
            print("Adding resume_file_path...")
            cursor.execute("ALTER TABLE users ADD COLUMN resume_file_path TEXT")
            conn.commit()
            print("✅ Added resume_file_path.")
        else:
            print("✅ resume_file_path already exists.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    force_add()
