import os
import io
import docx2txt
from pypdf import PdfReader
from fastapi import UploadFile, HTTPException

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extract text from uploaded PDF or DOCX file.
    """
    filename = file.filename.lower()
    content = await file.read()
    file_stream = io.BytesIO(content)
    
    text = ""
    
    try:
        if filename.endswith('.pdf'):
            reader = PdfReader(file_stream)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                
        elif filename.endswith('.docx'):
            text = docx2txt.process(file_stream)
            
        elif filename.endswith('.txt'):
            text = content.decode('utf-8')
            
        else:
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file format. Please upload PDF, DOCX, or TXT."
            )
            
        if not text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
            
        return text.strip()
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
    finally:
        await file.seek(0)