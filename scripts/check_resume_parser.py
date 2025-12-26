
import sys
import os
import asyncio
from typing import Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from parsers.resume_parser import resume_parser

SAMPLE_RESUME = """
John Doe
Email: john.doe@example.com
Phone: +1 (555) 123-4567

Summary
Experienced Python Developer with 5 years of experience in building scalable web applications.
Skilled in Django, FastAPI, and React.

Experience
Senior Software Engineer | Tech Corp | 2020 - Present
- Built microservices using FastAPI and Docker.
- Optimized database queries for PostgreSQL.

Education
B.S. Computer Science | University of Tech
"""

def test_parser():
    print("--- Testing Resume Parser ---")
    data = resume_parser.parse_resume(SAMPLE_RESUME)
    print(f"Parsed Data: {data}")
    
    required_fields = ["name", "email", "skills", "experience_years"]
    missing = [f for f in required_fields if not data.get(f)]
    
    if missing:
        print(f"FAILED: Missing fields: {missing}")
    else:
        print("SUCCESS: All required fields extracted.")

if __name__ == "__main__":
    test_parser()
