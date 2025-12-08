import sqlite3
import os

DB_PATH = "database/jobmatcher.db"

def sync_legacy_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ {DB_PATH} not found.")
        return

    print(f"Syncing {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 1. Check users.resume_file_path
        cursor.execute("PRAGMA table_info(users)")
        cols = [col[1] for col in cursor.fetchall()]
        if "resume_file_path" not in cols:
            print("Adding resume_file_path to users...")
            cursor.execute("ALTER TABLE users ADD COLUMN resume_file_path TEXT")
        else:
            print("p_resume_file_path already exists.")

        # 2. Check jobs.source_url
        cursor.execute("PRAGMA table_info(jobs)")
        cols = [col[1] for col in cursor.fetchall()]
        if "source_url" not in cols:
            print("Adding source_url to jobs...")
            cursor.execute("ALTER TABLE jobs ADD COLUMN source_url TEXT")
        else:
             print("source_url already exists.")
             
        # 3. Check auto_apply_queue table
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='auto_apply_queue'")
        if not cursor.fetchone():
             print("Creating auto_apply_queue...")
             cursor.execute("""
                CREATE TABLE IF NOT EXISTS auto_apply_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    job_id INTEGER NOT NULL,
                    to_email TEXT NOT NULL,
                    subject TEXT,
                    body TEXT,
                    resume_path TEXT,
                    status TEXT DEFAULT 'pending', -- pending, sent, failed
                    error TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    scheduled_at DATETIME,
                    sent_at DATETIME,
                    retry_count INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
                );
             """)

        conn.commit()
        print("✅ Sync Complete.")
    except Exception as e:
        print(f"❌ Error syncing: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    sync_legacy_db()
