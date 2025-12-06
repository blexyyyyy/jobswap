import sqlite3
import os

DB_PATH = "database/jobmatcher.db"

def cleanup():
    """Vacuum and analyze database for performance."""
    print(f"Cleaning up database: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        # Enable WAL if not already
        conn.execute("PRAGMA journal_mode=WAL;")
        
        # Free up unused space
        print("Vacuuming...")
        conn.execute("VACUUM;")
        
        # Optimize query planner
        print("Analyzing...")
        conn.execute("ANALYZE;")
        
        # Remove very old jobs (optional policy)
        # conn.execute("DELETE FROM jobs WHERE created_at < date('now', '-3 months')")
        
        print("Done.")
    except Exception as e:
        print(f"Error during cleanup: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    cleanup()
