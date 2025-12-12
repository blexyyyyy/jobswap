import os
from dotenv import load_dotenv

load_dotenv()

# App
SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_key")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Backward compatibility if needed elsewhere
JWT_SECRET = SECRET_KEY

# Database
if os.getenv("VERCEL"):
    # On Vercel, use /tmp for write access (ephemeral)
    DB_PATH = "/tmp/jobswipe.db"
else:
    # Local development
    DB_PATH = os.getenv("DB_PATH", "jobswipe.db")

# SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)
AUTO_APPLY_MAX_PER_HOUR = int(os.getenv("AUTO_APPLY_MAX_PER_HOUR", "20"))
