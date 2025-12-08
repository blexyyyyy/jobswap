import sys
import os

# Ensure we can import app
try:
    from app.main import app
    print("✅ Successfully imported app.main")
except Exception as e:
    print(f"❌ Import Failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
