
import sqlite3
import os

DB_PATH = "database/jobmatcher.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute('ALTER TABLE jobs ADD COLUMN source_url TEXT')
        print("Success: Added source_url column")
    except Exception as e:
        print(f"Info: {e}")
    conn.close()

if __name__ == "__main__":
    migrate()
