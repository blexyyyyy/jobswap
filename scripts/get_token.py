import sys
import os
import sqlite3
import json

sys.path.append(os.getcwd())

# Ensure we can import from app
from app.core.security import create_access_token

def get_user():
    # Hardcoded path to ensure we hit the right DB
    db_path = 'database/jobmatcher.db' 
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users LIMIT 1")
    row = cursor.fetchone()
    if row:
        u = dict(row)
        # Convert row to dict for JSON serialization
        return u
    return None

if __name__ == "__main__":
    user = get_user()
    if user:
        token = create_access_token(user['id'], user['email'])
        data = {
            "token": token,
            "user": user
        }
        with open("token_data.json", "w") as f:
            json.dump(data, f)
        print("Done. Saved to token_data.json")
    else:
        print("NO_USER_FOUND")
