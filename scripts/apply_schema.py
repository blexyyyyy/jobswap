import sqlite3
import os

DB_PATH = "jobswipe.db"

def apply_base_schema():
    print(f"Applying schema to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    try:
        with open("database/schema.sql", "r") as f:
            conn.executescript(f.read())
        conn.commit()
        print("✅ Schema applied.")
    except Exception as e:
        print(f"❌ Error applying schema: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_base_schema()
