from app.schemas.chat import ChatMessage
from database.connection import get_db_connection
import random

class ChatService:
    @staticmethod
    def get_messages(user_id: int, job_id: int):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM messages
                WHERE user_id = ? AND job_id = ?
                ORDER BY created_at ASC
            """, (user_id, job_id))
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def send_message(user_id: int, job_id: int, msg: ChatMessage):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert user message
            cursor.execute("""
                INSERT INTO messages (user_id, job_id, sender_type, message)
                VALUES (?, ?, 'user', ?)
            """, (user_id, job_id, msg.message))
            
            # Generate AI employer response (demo mode)
            responses = [
                "Thanks for reaching out! We've reviewed your application and would like to schedule an interview. Are you available this week?",
                "Hello! Your profile looks great. Could you tell us more about your experience with {skill}?",
                "Hi there! We're excited about your application. What's your expected salary range?",
                "Thank you for applying! We'd love to learn more about your recent projects. Can you share some details?",
                "Great to hear from you! When would be a good time for a quick call to discuss this role?"
            ]
            
            employer_response = random.choice(responses)
            
            # Get job info to personalize response
            cursor.execute("SELECT skills FROM jobs WHERE id = ?", (job_id,))
            job = cursor.fetchone()
            if job and job["skills"]:
                skills = job["skills"].split(",")
                employer_response = employer_response.replace("{skill}", skills[0].strip())
            
            # Insert employer response
            cursor.execute("""
                INSERT INTO messages (user_id, job_id, sender_type, message)
                VALUES (?, ?, 'employer', ?)
            """, (user_id, job_id, employer_response))
            conn.commit()
        
        return {"message": "Message sent", "employer_response": employer_response}
