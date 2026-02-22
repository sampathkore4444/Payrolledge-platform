from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.payroll import (
    SalaryComponentCreate, SalaryComponentUpdate, SalaryComponentResponse,
    PayrollRecordCreate, PayrollRecordUpdate, PayrollRecordResponse,
    PayrollProcessRequest, PayrollApprovalRequest, PayrollSummary,
    PayrollSettingsBase, PayrollSettingsResponse
)
from app.schemas.common import PaginatedResponse
from app.services.payroll_service import PayrollService
from app.schemas.payroll import PayrollStatus
from typing import Optional, List

router = APIRouter(prefix="/payroll", tags=["Payroll"])


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.post("/components", response_model=SalaryComponentResponse, status_code=status.HTTP_201_CREATED)
def create_salary_component(
    component_data: SalaryComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = PayrollService(db)
    component = service.create_salary_component(component_data.model_dump())
    return component


@router.get("/components/employee/{employee_id}", response_model=list[SalaryComponentResponse])
def get_employee_components(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = PayrollService(db)
    components = service.get_employee_salary_components(employee_id)
    return components


@router.put("/components/{component_id}", response_model=SalaryComponentResponse)
def update_salary_component(
    component_id: int,
    component_data: SalaryComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = PayrollService(db)
    component = service.update_salary_component(component_id, component_data.model_dump(exclude_unset=True))
    
    if not component:
        raise HTTPException(status_code=404, detail="Salary component not found")
    
    return component


@router.post("/process", response_model=list[PayrollRecordResponse])
def process_payroll(
    process_request: PayrollProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = PayrollService(db)
    records = service.process_payroll(
        process_request.month,
        process_request.year,
        process_request.employee_ids
    )
    return records


@router.get("/records", response_model=PaginatedResponse[PayrollRecordResponse])
def list_payroll_records(
    employee_id: Optional[int] = None,
    month: Optional[int] = None,
    year: Optional[int] = None,
    status: Optional[PayrollStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = PayrollService(db)
    skip = (page - 1) * page_size
    records, total = service.get_employee_payroll_records(
        employee_id=employee_id,
        month=month,
        year=year,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": records,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/records/{record_id}", response_model=PayrollRecordResponse)
def get_payroll_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = PayrollService(db)
    record = service.get_payroll_record(record_id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    return record


@router.put("/records/{record_id}", response_model=PayrollRecordResponse)
def update_payroll_record(
    record_id: int,
    record_data: PayrollRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = PayrollService(db)
    record = service.update_payroll_record(record_id, record_data.model_dump(exclude_unset=True))
    
    if not record:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    return record


@router.post("/records/{record_id}/approve", response_model=PayrollRecordResponse)
def approve_payroll_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = PayrollService(db)
    record = service.approve_payroll_record(record_id, current_user.id)
    
    if not record:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    return record


@router.get("/summary", response_model=PayrollSummary)
def get_payroll_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = PayrollService(db)
    summary = service.get_payroll_summary(month, year)
    return summary


@router.get("/calculate/{employee_id}")
def calculate_employee_payroll(
    employee_id: int,
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = PayrollService(db)
    calculation = service.calculate_payroll(employee_id, month, year)
    return calculation


@router.get("/settings", response_model=PayrollSettingsResponse)
def get_payroll_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = PayrollService(db)
    settings = service.get_payroll_settings()
    return settings


@router.put("/settings", response_model=PayrollSettingsResponse)
def update_payroll_settings(
    settings_data: PayrollSettingsBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    service = PayrollService(db)
    settings = service.update_payroll_settings(settings_data)
    return settings
