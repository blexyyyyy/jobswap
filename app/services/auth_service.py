from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserRegister, UserLogin
from database.connection import get_db_connection
from fastapi import HTTPException
from app.core.logging import logger

class AuthService:
    @staticmethod
    def register_user(user: UserRegister):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # Check if email already exists
                cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
                if cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Email already registered")
                
                # Create user
                password_hash = hash_password(user.password)
                cursor.execute(
                    "INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
                    (user.email, password_hash, user.name)
                )
                conn.commit()
                user_id = cursor.lastrowid
            
            # Generate token
            token = create_access_token(user_id, user.email)
            
            return {
                "access_token": token,
                "user": {"id": user_id, "email": user.email, "name": user.name}
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            logger.error(f"Registration Error: {e}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

    @staticmethod
    def login_user(user: UserLogin):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = ?", (user.email,))
                db_user = cursor.fetchone()
            
            if not db_user:
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            if not verify_password(user.password, db_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid email or password")
            
            # Generate token
            token = create_access_token(db_user["id"], db_user["email"])
            
            return {
                "access_token": token,
                "user": {
                    "id": db_user["id"],
                    "email": db_user["email"],
                    "name": db_user["name"]
                }
            }
        except HTTPException as he:
            raise he
        except Exception as e:
            # Log error details
            logger.error(f"Login Error: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal Server Error during login")
