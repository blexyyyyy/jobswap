from core.llm_client import client, GEMINI_MODEL
from google.genai import types
from typing import Dict, Any, List
import json

def import_json(text):
    try:
        return json.loads(text)
    except:
        return {
                "match_reason": "Good potential match based on your profile.",
                "match_score": 70,
                "missing_skills": [],
                "career_tip": "Apply to learn more."
            }

class ExplanationGenerator:
    def __init__(self):
        pass

    def generate_explanation(self, candidate_profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a match explanation using LLM.
        """
        prompt = f'''You are an expert career coach AI determining if a job is a "Good Match" or "Bad Match" for a candidate.
        
        Candidate Profile:
        - Skills: {', '.join(candidate_profile.get('skills', []))}
        - Experience: {candidate_profile.get('experience_years', 0)} years
        - Preferences: {candidate_profile.get('preferred_location', 'Any')}, {candidate_profile.get('preferred_seniority', 'Any')}
        - Resume Summary: {candidate_profile.get('resume_text', 'Not provided')[:1000]}
        
        Job Description:
        - Title: {job.get('title')}
        - Company: {job.get('company')}
        - Location: {job.get('location')}
        - Required Skills: {', '.join(job.get('skills', []))}
        - Description: {job.get('description', '')[:800]}

        Analyze strictly based on skills and experience overlap.
        
        Output Requirements:
        1. "match_type": MUST be one of ["high", "medium", "low"]. 
           - "high": Strong skill overlap (>70%) and relevant experience.
           - "medium": Some overlap (~50%), trainable gaps.
           - "low": Minimal overlap, wrong seniority, or completely different field.
        
        2. "match_reason": Start with "Good match because..." or "Not a good match because...". Be specific about *which* skills matched or missed.
        
        3. "match_score": Integer 0-100 reflecting the fit.
        
        4. "missing_skills": List of critical skills the candidate lacks.
        
        5. "career_tip": A 1-sentence actionable tip.

        Return strictly as JSON with keys: "match_reason", "match_score", "missing_skills", "career_tip", "match_type".
        '''

        try:
            print(f"[ExplanationGen] Generating for job: {job.get('title')}")
            print(f"[ExplanationGen] User skills: {candidate_profile.get('skills', [])}")
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json"
                )
            )
             # Basic cleanup
            response_text = response.text.strip() if response.text else ""
            print(f"[ExplanationGen] Raw response: {response_text[:200]}...")
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            data = import_json(response_text) # Helper for safe json load
            print(f"[ExplanationGen] Parsed data: {data}")
            return data
        except Exception as e:
            print(f"[ExplanationGen ERROR] {e}")
            # Fallback
            return {
                "match_reason": "This job aligns with your skills and experience level.",
                "match_score": 75,
                "missing_skills": [],
                "career_tip": "Highlight your relevant projects in your application.",
                "match_type": "medium"
            }

explanation_generator = ExplanationGenerator()

def import_json(text):
    import json
    try:
        return json.loads(text)
    except:
        return {
                "match_reason": "Good potential match based on your profile.",
                "match_score": 70,
                "missing_skills": [],
                "career_tip": "Apply to learn more."
            }

explanation_generator = ExplanationGenerator()
