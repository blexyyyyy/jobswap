
import sqlite3
from bs4 import BeautifulSoup
import re

DB_PATH = "database/jobmatcher.db"

def clean_html():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, description FROM jobs")
        rows = cursor.fetchall()
        
        count = 0
        for row in rows:
            raw = row["description"]
            if not raw or "<" not in raw:
                continue
                
            soup = BeautifulSoup(raw, "html.parser")
            clean_text = soup.get_text(separator=" ")
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            cursor.execute("UPDATE jobs SET description = ? WHERE id = ?", (clean_text[:2000], row["id"]))
            count += 1
            
        conn.commit()
        print(f"Cleaned {count} jobs")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    clean_html()
