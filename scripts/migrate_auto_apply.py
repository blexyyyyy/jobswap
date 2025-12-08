import sqlite3
import os

DB_NAME = "jobswipe.db"

def apply_migration():
    if not os.path.exists(DB_NAME):
        print(f"❌ Database {DB_NAME} not found.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print("🔄 Adding 'resume_file_path' to 'users' table...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN resume_file_path TEXT")
        print("   ✅ Added 'resume_file_path'")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("   ⚠️ Column 'resume_file_path' already exists. Skipping.")
        else:
            print(f"   ❌ Error: {e}")

    print("🔄 Creating 'auto_apply_queue' table...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS auto_apply_queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        to_email TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        resume_path TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        error TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        scheduled_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        sent_at DATETIME,
        retry_count INTEGER DEFAULT 0,
        CONSTRAINT fk_autoapply_user FOREIGN KEY (user_id) REFERENCES users(id),
        CONSTRAINT fk_autoapply_job FOREIGN KEY (job_id) REFERENCES jobs(id)
    );
    """)
    print("   ✅ Created 'auto_apply_queue'")

    conn.commit()
    conn.close()
    print("✨ Migration Complete.")

if __name__ == "__main__":
    apply_migration()
