
def insert_job(job_data: Dict[str, Any], summary_text: str = "") -> int:
    """
    Insert a job into the database.
    Avoids duplicates based on source_url.
    """
    import sqlite3
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        source = job_data.get("source_url", "")
        
        # Check if job exists
        if source:
            cursor.execute("SELECT id FROM jobs WHERE source_url = ?", (source,))
            existing = cursor.fetchone()
            if existing:
                return existing[0]
        
        # Use provided summary_text or fallbacks
        description = summary_text or job_data.get("description") or job_data.get("summary", "")
        
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
            description[:2000], 
            source
        ))
        conn.commit()
        job_id = cursor.lastrowid
        return job_id
    except Exception as e:
        print(f"Error inserting job: {e}")
        raise e
    finally:
        conn.close()
