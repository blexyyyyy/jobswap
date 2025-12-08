import sqlite3
import os

DB_PATH = "jobswipe.db"

def fix_schema():
    print(f"Fixing schema in {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(jobs)")
        cols = [col[1] for col in cursor.fetchall()]
        if "source_url" not in cols:
            print("Adding source_url column...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN source_url TEXT")
            conn.commit()
            print("✅ Column added.")
        else:
            print("✅ Column source_url already exists.")
            
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_schema()
