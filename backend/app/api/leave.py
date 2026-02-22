from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.leave import (
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse,
    LeaveBalanceCreate, LeaveBalanceUpdate, LeaveBalanceResponse,
    LeaveApproval
)
from app.schemas.common import PaginatedResponse
from app.services.attendance_service import LeaveService
from app.schemas.leave import LeaveRequestStatus
from typing import Optional

router = APIRouter(prefix="/leave", tags=["Leave"])


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.post("/requests", response_model=LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def create_leave_request(
    leave_data: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = LeaveService(db)
    leave = service.create_leave_request(leave_data.model_dump())
    return leave


@router.get("/requests", response_model=PaginatedResponse[LeaveRequestResponse])
def list_leave_requests(
    employee_id: Optional[int] = None,
    status: Optional[LeaveRequestStatus] = None,
    leave_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = LeaveService(db)
    skip = (page - 1) * page_size
    leaves, total = service.get_leave_requests(
        employee_id=employee_id,
        status=status,
        leave_type=leave_type,
        skip=skip,
        limit=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": leaves,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/requests/{leave_id}", response_model=LeaveRequestResponse)
def get_leave_request(
    leave_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = LeaveService(db)
    leave = service.get_leave_request(leave_id)
    
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    return leave


@router.put("/requests/{leave_id}", response_model=LeaveRequestResponse)
def update_leave_request(
    leave_id: int,
    leave_data: LeaveRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = LeaveService(db)
    leave = service.update_leave_request(leave_id, leave_data.model_dump(exclude_unset=True))
    
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    return leave


@router.post("/requests/{leave_id}/approve", response_model=LeaveRequestResponse)
def approve_leave_request(
    leave_id: int,
    approval_data: LeaveApproval,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR, UserRole.DEPARTMENT_HEAD))
):
    service = LeaveService(db)
    leave = service.approve_leave_request(
        leave_id,
        current_user.id,
        approval_data.status,
        approval_data.remarks
    )
    
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    
    return leave


@router.get("/balances/{employee_id}", response_model=list[LeaveBalanceResponse])
def get_employee_leave_balances(
    employee_id: int,
    year: int = Query(..., ge=2020),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = LeaveService(db)
    balances = service.get_leave_balances(employee_id, year)
    return balances


@router.post("/balances", response_model=LeaveBalanceResponse, status_code=status.HTTP_201_CREATED)
def create_leave_balance(
    balance_data: LeaveBalanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = LeaveService(db)
    balance = service.create_leave_balance(balance_data.model_dump())
    return balance


@router.put("/balances/{balance_id}", response_model=LeaveBalanceResponse)
def update_leave_balance(
    balance_id: int,
    balance_data: LeaveBalanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = LeaveService(db)
    balance = service.update_leave_balance(balance_id, balance_data.model_dump(exclude_unset=True))
    
    if not balance:
        raise HTTPException(status_code=404, detail="Leave balance not found")
    
    return balance
