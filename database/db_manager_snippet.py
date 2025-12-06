
def insert_job(job_data: dict, summary_emb: str = "") -> int:
    """
    Insert a job into the database.
    Avoids duplicates based on source_url.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if job exists
        cursor.execute("SELECT id FROM jobs WHERE source_url = ?", (job_data.get("source_url"),))
        existing = cursor.fetchone()
        if existing:
            return existing[0]
            
        cursor.execute("""
            INSERT INTO jobs (
                title, company, location, skills, description, 
                source_url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            job_data.get("title"),
            job_data.get("company"),
            job_data.get("location"),
            job_data.get("skills"),
            job_data.get("summary", "")[:2000], # Description/Summary
            job_data.get("source_url")
        ))
        conn.commit()
        job_id = cursor.lastrowid
        return job_id
    except Exception as e:
        print(f"Error inserting job: {e}")
        raise e
    finally:
        conn.close()
