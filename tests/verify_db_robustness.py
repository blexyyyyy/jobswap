import sqlite3
import os
from database.connection import get_db_connection

DB_PATH = "database/jobmatcher.db"

def verify():
    print(f"Verifying DB at {DB_PATH}")
    
    # 1. Check direct connection & WAL mode
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check journal_mode
        cursor.execute("PRAGMA journal_mode;")
        mode = cursor.fetchone()[0]
        print(f"Journal Mode: {mode}")
        
        if mode.upper() != "WAL":
            print("❌ WAL mode INVALID")
        else:
            print("✅ WAL mode VALID")
            
        # 2. Check simple query
        cursor.execute("SELECT count(*) FROM sqlite_master;")
        count = cursor.fetchone()[0]
        print(f"✅ DB Connected (Found {count} schema items)")

if __name__ == "__main__":
    verify()
