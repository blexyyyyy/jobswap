import os
from pathlib import Path
from typing import Tuple, List, BinaryIO

from fastapi import UploadFile

# Use backend directory for uploads
UPLOAD_DIR = Path("uploads/resumes")

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text content from a PDF or TXT resume file.
    Note: For PDF, this is a distinct task. We'll implement a basic one or placeholder.
    """
    content = await file.read()
    
    # Save position to reset after read
    await file.seek(0)
    
    filename = file.filename.lower()
    
    if filename.endswith(".pdf"):
        try:
            from pypdf import PdfReader
            from io import BytesIO
            
            # Simple wrapper to handle async read
            reader = PdfReader(BytesIO(content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"PDF Extract Error: {e}")
            return "" # Fallback
            
    # Default to text
    try:
        return content.decode("utf-8")
    except:
        return content.decode("latin-1")

def save_resume_file(file: UploadFile, user_id: int) -> str:
    """
    Save resume to disk under uploads/resumes/<user_id>.<ext>
    Returns relative path as string.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1] or ".pdf"
    filename = f"user_{user_id}{ext}"
    dest = UPLOAD_DIR / filename

    # Write file content
    with dest.open("wb") as f:
        # file.file is the underlying BinaryIO
        # We need to ensure we read from start if it was read before
        file.file.seek(0) 
        f.write(file.file.read())
        file.file.seek(0) # Reset again just in case

    return str(dest)