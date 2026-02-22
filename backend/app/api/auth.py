from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.schemas.auth import Token, LoginRequest, RegisterRequest, EmployeeLoginRequest
from app.schemas.user import UserResponse, ChangePassword
from app.services.auth_service import AuthService
from app.services.employee_service import EmployeeService
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.register(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Register error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for username: {login_data.username}")
    service = AuthService(db)
    try:
        result = service.login(login_data)
        logger.info(f"Login result: {result}")
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    if not result:
        logger.warning(f"Login failed for username: {login_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"Login successful for username: {login_data.username}")
    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"]
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/change-password")
def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    service = AuthService(db)
    try:
        service.change_password(current_user.id, password_data.old_password, password_data.new_password)
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/employee-login")
def employee_login(login_data: EmployeeLoginRequest, db: Session = Depends(get_db)):
    """Login using employee code and password"""
    service = EmployeeService(db)
    try:
        result = service.employee_login(login_data.employee_code, login_data.password)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid employee code or password"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Employee login error: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
