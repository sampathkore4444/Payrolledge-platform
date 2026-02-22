from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserCreate
from typing import Optional
from datetime import timedelta
from app.core.config import settings


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: RegisterRequest) -> User:
        try:
            existing_user = self.db.query(User).filter(
                (User.email == user_data.email) | (User.username == user_data.username)
            ).first()
            
            if existing_user:
                raise ValueError("User with this email or username already exists")
            
            hashed_password = get_password_hash(user_data.password)
            
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=hashed_password,
                full_name=user_data.full_name,
                is_active=True
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            return db_user
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Registration failed: {str(e)}")

    def login(self, login_data: LoginRequest) -> Optional[dict]:
        user = self.db.query(User).filter(User.username == login_data.username).first()
        
        if not user:
            return None
        
        if not verify_password(login_data.password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ValueError("User not found")
        
        if not verify_password(old_password, user.hashed_password):
            raise ValueError("Invalid old password")
        
        user.hashed_password = get_password_hash(new_password)
        self.db.commit()
        
        return True
