"""
Database initialization script for production (PostgreSQL on Render)
Run this after deploying to set up the database schema
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    """Initialize PostgreSQL database with schema"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL environment variable not set")
        return False
    
    try:
        # Connect to PostgreSQL
        print("Connecting to PostgreSQL...")
        conn = psycopg2.connect(database_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Read schema file
        print("Reading schema file...")
        schema_path = os.path.join(os.path.dirname(__file__), "database", "schema_postgres.sql")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema
        print("Creating tables...")
        cursor.execute(schema_sql)
        
        # Create default test user (optional)
        print("Creating default test user...")
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        test_password_hash = pwd_context.hash("password")
        
        cursor.execute("""
            INSERT INTO users (email, password_hash, name, skills, experience_years, preferred_location, preferred_seniority)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, (
            "debuguser@example.com",
            test_password_hash,
            "Debug User",
            "Python,JavaScript,React,FastAPI",
            3,
            "Remote",
            "Mid"
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✓ Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    exit(0 if success else 1)
