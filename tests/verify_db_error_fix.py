import sqlite3
import os

DB_PATH = "database/jobmatcher.db"

def verify_query():
    print(f"Checking database at {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
            SELECT j.* FROM jobs j
            WHERE j.id NOT IN (
                SELECT job_id FROM user_swipes WHERE user_id = ?
            )
            ORDER BY j.created_at DESC
    """
    
    try:
        # Use EXPLAIN to check syntax without executing or needing data
        cursor.execute(f"EXPLAIN {query}", (1,))
        print("✅ Query Syntax Valid")
    except sqlite3.Error as e:
        print(f"❌ Query Syntax Error: {e}")
        exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    verify_query()
