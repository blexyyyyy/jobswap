import json
import re
import logging
from typing import Dict, Any, List
from app.llm.wrapper import LLMWrapper

logger = logging.getLogger(__name__)

def import_json(text: str) -> Dict[str, Any]:
    """Parse JSON from LLM response, handling markdown code blocks."""
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"JSON parse failed: {e}")
        return {}

def extract_with_regex(text: str) -> Dict[str, Any]:
    """Fallback regex extraction when LLM fails."""
    data = {
        "name": "",
        "email": "",
        "phone": "",
        "skills": [],
        "experience_years": 0,
        "summary": "",
        "preferred_location": "Remote",
        "preferred_seniority": "Mid"
    }
    
    # Extract email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        data["email"] = email_match.group()
    
    # Extract phone (improved regex for various formats)
    # Matches: +1-555-555-5555, (555) 555-5555, 555.555.5555, etc.
    phone_match = re.search(r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?', text)
    if phone_match:
         data["phone"] = phone_match.group(0).strip()
    
    # Extract years of experience
    # Matches: "5+ years", "5 years", "5 yrs", "5+ yrs"
    exp_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)', text, re.IGNORECASE)
    if exp_match:
        data["experience_years"] = int(exp_match.group(1))
    
    # Extract skills (common tech keywords)
    common_skills = [
        'Python', 'JavaScript', 'TypeScript', 'Java', 'C++', 'C#', 'Go', 'Rust',
        'React', 'Angular', 'Vue', 'Node.js', 'Django', 'FastAPI', 'Flask',
        'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
        'AWS', 'Azure', 'GCP', 'Linux', 'Git', 'HTML', 'CSS', 'REST', 'GraphQL',
        'Machine Learning', 'AI', 'TensorFlow', 'PyTorch', 'Data Science', 'Pandas', 'NumPy'
    ]
    found_skills = []
    text_lower = text.lower()
    for skill in common_skills:
        # Use word boundary check to avoid partial matches (e.g. "Go" in "Google")
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            found_skills.append(skill)
            
    data["skills"] = found_skills[:15]  # Limit to 15 skills
    
    # Extract name (Heuristic: First non-empty line that isn't a header)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:10]:
        # Skip simple headers
        if line.lower() in ['resume', 'curriculum vitae', 'cv', 'summary', 'profile', 'experience', 'education']:
            continue
        # Skip email/phone/url lines
        if '@' in line or re.search(r'\d{5,}', line) or 'http' in line:
            continue
        # Look for name-like pattern (2-4 capitalized words, no numbers)
        if re.match(r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})$', line):
            data["name"] = line
            break

    # If no name found, try to find "Name: [Value]" pattern
    if not data["name"]:
        name_label_match = re.search(r'Name:\s*([A-Za-z\s]+)', text, re.IGNORECASE)
        if name_label_match:
             data["name"] = name_label_match.group(1).strip()
    
    # Determine seniority based on experience
    exp = data["experience_years"]
    if exp >= 8:
        data["preferred_seniority"] = "Lead"
    elif exp >= 5:
        data["preferred_seniority"] = "Senior"
    elif exp >= 2:
        data["preferred_seniority"] = "Mid"
    else:
        data["preferred_seniority"] = "Junior"
    
    return data

class ResumeParser:
    def __init__(self):
        # Use LOCAL Ollama first (skip Groq due to bad API key)
        self.llm = LLMWrapper(provider_names=["ollama", "gemini"])

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Parse resume text into structured data using LLM with regex fallback."""
        prompt = f"""You are an extremely accurate resume parser. Your job is to extract unstructured resume text into rigid JSON.

Resume Text:
{text[:4000]}

Instructions:
1. Extract the candidate's Full Name. If not explicitly found, make a best guess from the header.
2. Extract Email and Phone.
3. Identify top 10 technical Skills.
4. Estimate total Years of Experience (integer) based on the work history dates.
5. Create a short professional Summary (2 sentences max).
6. Infer Preferred Location (City, Country) or "Remote".
7. Infer Seniority Level (Junior, Mid, Senior, Lead, Executive).

Output Format:
Return ONLY valid JSON. Do not include markdown formatting (like ```json).
Keys: "name", "email", "phone", "skills", "experience_years", "summary", "preferred_location", "preferred_seniority".
"""

        try:
            # Short timeout for interactive feel
            result = self.llm.generate(
                prompt=prompt,
                temperature=0.0,
                max_tokens=1024,
                meta={"json_mode": True}
            )
            
            data = import_json(result["text"])
            
            # Validate we got useful data
            if not data or not isinstance(data, dict):
                 raise ValueError("LLM returned non-dict or empty data")

            # Check for critical missing fields that regex might find
            if not data.get("name") or not data.get("email") or not data.get("skills"):
                 logger.warning("[ResumeParser] LLM missed critical fields, running hybrid merge with regex.")
                 regex_data = extract_with_regex(text)
                 # Merge: keep LLM data if present, else use regex
                 for key, value in regex_data.items():
                     if not data.get(key) and value:
                         data[key] = value
                         
            data["_source"] = result["provider"]
            
            # Ensure proper types
            if "experience_years" in data:
                if isinstance(data["experience_years"], str):
                    try:
                        # Extract first number found
                        nums = re.findall(r'\d+', str(data["experience_years"]))
                        data["experience_years"] = int(nums[0]) if nums else 0
                    except:
                        data["experience_years"] = 0
            else:
                 data["experience_years"] = 0
            
            # Ensure skills is a list
            if isinstance(data.get("skills"), str):
                data["skills"] = [s.strip() for s in data["skills"].split(",")]
            
            print(f"[ResumeParser] Success via {data.get('_source', 'unknown')}")
            # print(f"[ResumeParser] Extracted: name={data.get('name')}, skills={len(data.get('skills', []))}")
            return data
            
        except Exception as e:
            logger.error(f"LLM parsing failed: {e}")
            print(f"[ResumeParser ERROR] {e} - using regex fallback")
            data = extract_with_regex(text)
            data["_source"] = "regex_fallback_error"
            return data

resume_parser = ResumeParser()

