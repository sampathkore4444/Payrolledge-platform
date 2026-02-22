from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.attendance import (
    ShiftCreate, ShiftUpdate, ShiftResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, BulkAttendanceCreate
)
from app.schemas.common import PaginatedResponse
from app.services.attendance_service import AttendanceService
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/attendance", tags=["Attendance"])


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
def create_shift(
    shift_data: ShiftCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = AttendanceService(db)
    shift = service.create_shift(shift_data.model_dump())
    return shift


@router.get("/shifts", response_model=list[ShiftResponse])
def list_shifts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = AttendanceService(db)
    shifts, _ = service.get_shifts(skip=skip, limit=limit)
    return shifts


@router.get("/shifts/{shift_id}", response_model=ShiftResponse)
def get_shift(
    shift_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = AttendanceService(db)
    shift = service.get_shift(shift_id)
    
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    return shift


@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = AttendanceService(db)
    try:
        attendance = service.create_attendance(attendance_data)
        return attendance
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/bulk", response_model=list[AttendanceResponse])
def bulk_create_attendance(
    bulk_data: BulkAttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = AttendanceService(db)
    attendances = service.bulk_create_attendance(bulk_data.attendances)
    return attendances


@router.get("/", response_model=PaginatedResponse[AttendanceResponse])
def list_attendances(
    employee_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = AttendanceService(db)
    skip = (page - 1) * page_size
    attendances, total = service.get_attendances(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": attendances,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = AttendanceService(db)
    attendance = service.get_attendance(attendance_id)
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    
    return attendance


@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR, UserRole.DEPARTMENT_HEAD))
):
    service = AttendanceService(db)
    attendance = service.update_attendance(attendance_id, attendance_data)
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance not found")
    
    return attendance


@router.get("/summary/{employee_id}")
def get_attendance_summary(
    employee_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = AttendanceService(db)
    summary = service.get_attendance_summary(employee_id, month, year)
    return summary
