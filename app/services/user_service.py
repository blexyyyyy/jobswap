from app.schemas.user import UserProfile
from database.connection import get_db_connection

class UserService:
    @staticmethod
    def update_profile(user_id: int, profile: UserProfile):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET
                    name = COALESCE(?, name),
                    phone = COALESCE(?, phone),
                    skills = COALESCE(?, skills),
                    experience_years = COALESCE(?, experience_years),
                    preferred_location = COALESCE(?, preferred_location),
                    preferred_seniority = COALESCE(?, preferred_seniority),
                    resume_text = COALESCE(?, resume_text),
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                profile.name,
                profile.phone,
                profile.skills,
                profile.experience_years,
                profile.preferred_location,
                profile.preferred_seniority,
                profile.resume_text,
                user_id
            ))
            conn.commit()
        return {"message": "Profile updated successfully"}

    @staticmethod
    def get_profile(user_id: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            user = cursor.fetchone()
        
        if not user:
             return None

        # Return relevant fields
        return {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "phone": user["phone"],
            "skills": user["skills"],
            "experience_years": user["experience_years"],
            "preferred_location": user["preferred_location"],
            "preferred_seniority": user["preferred_seniority"],
            "resume_file_path": user["resume_file_path"] if "resume_file_path" in user.keys() else None,
        }
    
    @staticmethod
    async def process_resume(file, user_id: int):
        from utils.file_handler import extract_text_from_file, save_resume_file
        from parsers.resume_parser import resume_parser
        from fastapi import HTTPException

        # Extract text
        try:
            text = await extract_text_from_file(file)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"File processing error: {str(e)}")
            
        # Save file to disk
        try:
            resume_path = save_resume_file(file, user_id=user_id)
        except Exception as e:
             print(f"Resume Save Error: {e}")
             resume_path = None
        
        # Parse with LLM
        try:
            parsed_data = resume_parser.parse_resume(text)
        except Exception as e:
            # Continue even if parsing fails, we have the file
            print(f"Parse Error: {e}")
            parsed_data = {}
            
        # Update user profile
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            try:
                skills_str = ",".join(parsed_data.get("skills", []))
                
                cursor.execute("""
                    UPDATE users SET
                        name = COALESCE(?, name),
                        email = COALESCE(?, email),
                        phone = COALESCE(?, phone),
                        skills = COALESCE(?, skills),
                        experience_years = COALESCE(?, experience_years),
                        resume_text = ?,
                        resume_file_path = ?,
                        preferred_location = COALESCE(?, preferred_location),
                        preferred_seniority = COALESCE(?, preferred_seniority),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    parsed_data.get("name"),
                    parsed_data.get("email"),
                    parsed_data.get("phone"),
                    skills_str if skills_str else None,
                    parsed_data.get("experience_years"),
                    text,
                    resume_path,
                    parsed_data.get("preferred_location"),
                    parsed_data.get("preferred_seniority"),
                    user_id
                ))
                conn.commit()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        
        return {
            "message": "Resume uploaded and parsed successfully",
            "parsed_data": parsed_data,
            "file_saved": bool(resume_path)
        }
