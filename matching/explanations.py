from core.llm_client import client, GEMINI_MODEL
from google.genai import types
from typing import Dict, Any, List
import json
import os
from groq import Groq

def import_json(text):
    try:
        return json.loads(text)
    except:
        return {
                "match_reason": "Good potential match based on your profile.",
                "match_score": 70,
                "missing_skills": [],
                "career_tip": "Apply to learn more.",
                "match_type": "medium"
            }

def log_error(msg):
    try:
        with open("error_final_dump.txt", "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    except:
        pass

# Initialize clients lazily to handle env loading timing
_groq_client = None

def get_groq_client():
    """Lazy initialization of Groq client"""
    global _groq_client
    if _groq_client is None:
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if api_key:
                _groq_client = Groq(api_key=api_key)
                print(f"[Groq Init] Successfully initialized with key: {api_key[:10]}...")
            else:
                print("[Groq Init] No API key found")
                log_error("[Groq Init] GROQ_API_KEY not found in environment")
        except Exception as e:
            log_error(f"[Groq Init Error] {str(e)}")
            print(f"[Groq Init Error] {ascii(e)}")
    return _groq_client

class ExplanationGenerator:
    def __init__(self):
        pass

    def generate_explanation(self, candidate_profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a match explanation using LLM (Groq first, Gemini fallback), enriched with ML model insights.
        """
        ml_score = job.get('ml_score')
        ml_features = job.get('ml_features', {})
        
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
        
        ML Model Insights (Behavioral Prediction):
        - Predicted Match Probability: {ml_score}% (This is based on historical user swipes)
        - Key Features: 
            - Skill Overlap Count: {ml_features.get('skill_overlap', 0)}
            - Location Match: {'Yes' if ml_features.get('location_match') else 'No'}
            - Seniority Match: {'Yes' if ml_features.get('seniority_match') else 'No'}
        
        Task:
        Explain WHY this job has the predicted match score. 
        If the score is high (>70), focus on the strengths.
        If the score is low (<30), explain the dealbreakers.
        
        Output Requirements:
        1. "match_type": MUST be one of ["high", "medium", "low"] aligning with the score ({ml_score}). 
        
        2. "match_reason": Start with "Good match because..." or "Not a good match because...". Be specific about *which* skills matched or missed.
        
        3. "match_score": Return the ML score provided ({ml_score}) unless you found a MAJOR contradiction in the text data, in which case correct it.
        
        4. "missing_skills": List of critical skills the candidate lacks.
        
        5. "career_tip": A 1-sentence actionable tip.

        Return strictly as JSON with keys: "match_reason", "match_score", "missing_skills", "career_tip", "match_type".
        '''

        # Try Groq first
        groq_client = get_groq_client()
        if groq_client:
            try:
                print(f"[ExplanationGen] Using Groq for job: {job.get('title')}")
                completion = groq_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that outputs only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                response_text = completion.choices[0].message.content
                print(f"[ExplanationGen] Groq response: {response_text[:200]}...")
                data = import_json(response_text)
                data["generator_source"] = "groq"
                return data
            except Exception as e:
                log_error(f"[Groq Failed] {str(e)}")
                print(f"[ExplanationGen] Groq failed: {ascii(e)}. Falling back to Gemini.")
        
        # Fallback to Gemini
        return self._call_gemini(prompt)

    def _call_gemini(self, prompt):
        try:
            print(f"[ExplanationGen] Using Gemini fallback...")
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
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            data = import_json(response_text)
            data["generator_source"] = "gemini"
            print(f"[ExplanationGen] Parsed data: {data}")
            return data
        except Exception as e:
            log_error(f"[Gemini Failed] {str(e)}")
            print(f"[ExplanationGen ERROR] {ascii(e)}")
            # Ultimate Fallback
            return {
                "match_reason": "This job aligns with your skills and experience level.",
                "match_score": 75,
                "missing_skills": [],
                "career_tip": "Highlight your relevant projects in your application.",
                "match_type": "medium",
                "generator_source": "fallback_static"
            }

explanation_generator = ExplanationGenerator()
