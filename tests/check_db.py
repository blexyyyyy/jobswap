import sqlite3
import os

DB_PATH = "jobswipe.db"

if not os.path.exists(DB_PATH):
    print("❌ jobswipe.db does not exist!")
else:
    print(f"✅ jobswipe.db found (Size: {os.path.getsize(DB_PATH)} bytes)")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("Tables:", [t[0] for t in tables])
        
        # Check jobs columns
        if ('jobs',) in tables:
            cursor.execute("PRAGMA table_info(jobs)")
            cols = [col[1] for col in cursor.fetchall()]
            print("Jobs Columns:", cols)
            
        # Check users columns
        if ('users',) in tables:
            cursor.execute("PRAGMA table_info(users)")
            cols = [col[1] for col in cursor.fetchall()]
            print("Users Columns:", cols)

        conn.close()
    except Exception as e:
        print(f"❌ Error reading DB: {e}")
