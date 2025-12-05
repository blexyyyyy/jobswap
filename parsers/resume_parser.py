import json
from typing import Dict, Any, List
from core.llm_client import LLMClient

class ResumeParser:
    def __init__(self):
        self.llm_client = LLMClient()

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """
        Parse resume text into structured data using LLM.
        """
        prompt = f"""
        You are an expert resume parser. Extract the following information from the resume text below:
        1. Name
        2. Email
        3. Phone
        4. Skills (as a list of strings)
        5. Experience in years (integer)
        6. Summary (brief professional summary)
        7. Preferred Location (infer from address or context, defaults to "Remote")
        8. Preferred Seniority (infer from experience, e.g., Junior, Mid, Senior, Lead)

        Return the output as a valid JSON object with keys: 
        "name", "email", "phone", "skills", "experience_years", "summary", "preferred_location", "preferred_seniority".

        Resume Text:
        {text[:4000]}  # Limit text to avoid token limits if necessary
        """

        try:
            response = self.llm_client.generate_content(prompt)
            # Basic cleanup to ensure json matching
            response_text = response.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            data = json.loads(response_text)
            
            # Ensure proper types
            if isinstance(data.get("experience_years"), str):
                 try:
                     data["experience_years"] = int(''.join(filter(str.isdigit, data["experience_years"])))
                 except:
                     data["experience_years"] = 0
            
            return data
        except Exception as e:
            print(f"Error parsing resume with LLM: {e}")
            # Return empty structure on failure
            return {
                "name": "", 
                "email": "", 
                "phone": "", 
                "skills": [], 
                "experience_years": 0, 
                "summary": "",
                "preferred_location": "",
                "preferred_seniority": ""
            }

resume_parser = ResumeParser()
