from typing import Dict, Any, List
import json
import logging
from app.llm.wrapper import LLMWrapper

logger = logging.getLogger(__name__)

def import_json(text):
    try:
        # Check if wrapped in markdown code blocks
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
        
        return json.loads(text)
    except Exception as e:
        logger.warning(f"JSON parsing failed for text: {text[:100]}... Error: {e}")
        return None

class ExplanationGenerator:
    def __init__(self):
        # Initialize wrapper with prioritized providers
        # Use LOCAL Ollama first (skip Groq due to bad API key)
        self.llm = LLMWrapper(provider_names=["ollama", "gemini"])

    def generate_explanation(self, candidate_profile: Dict[str, Any], job: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a match explanation using LLM Wrapper.
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

        # Define fallback upfront
        fallback_response = {
            "match_reason": "This job aligns with your general profile, though our AI couldn't generate a specific detailed analysis at this moment.",
            "match_score": ml_score or 50,
            "missing_skills": [],
            "career_tip": "Review the job description carefully to see if it fits your goals.",
            "match_type": "medium",
            "generator_source": "fallback_error"
        }

        try:
            # Call wrapper
            result = self.llm.generate(
                prompt=prompt, 
                temperature=0.2, 
                max_tokens=512,
                meta={"json_mode": True}
            )
            
            # 1. Check for empty text
            if not result or not result.get("text"):
                logger.error("[ExplanationGen] LLM returned empty text/result")
                return fallback_response

            # 2. Parse JSON
            data = import_json(result["text"])
            if not data:
                logger.error(f"[ExplanationGen] Failed to parse JSON from: {result['text'][:200]}...")
                return fallback_response

            # 3. Validate & Fix Keys
            # Remap common mistakes
            if "explanation" in data and "match_reason" not in data:
                data["match_reason"] = data["explanation"]
            if "reason" in data and "match_reason" not in data:
                data["match_reason"] = data["reason"]
            if "score" in data and "match_score" not in data:
                data["match_score"] = data["score"]

            # Ensure required keys exist
            required_keys = ["match_reason", "match_score", "match_type"]
            missing = [k for k in required_keys if k not in data]
            
            if missing:
                logger.error(f"[ExplanationGen] JSON missing keys: {missing}. Data: {data}")
                # Patch missing keys from fallback if possible, or just return fallback if critical keys missing
                if "match_reason" in missing:
                    return fallback_response # Critical failure handling
                
                # Non-critical, patch defaults
                if "match_type" in missing:
                    data["match_type"] = "medium"
                if "match_score" in missing:
                    data["match_score"] = ml_score

            data["generator_source"] = result["provider"]
            
            # logger.info(f"[ExplanationGen] Success using {result['provider']}")
            return data

        except Exception as e:
            logger.error(f"Explanation generation failed completely: {e}")
            # logger.error called above already, this print is redundant or better logged.
            # We already logged "Explanation generation failed completely: {e}" 
            # so we can just remove this print or ensure it's not double logged.
            # But prompt says replace print.
            pass
            return fallback_response

explanation_generator = ExplanationGenerator()
