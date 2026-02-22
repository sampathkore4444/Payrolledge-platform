from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole, Employee
from app.models.employment import EmploymentHistory
from app.schemas.employment import EmploymentHistoryCreate, EmploymentHistoryResponse
from app.schemas.common import PaginatedResponse
from datetime import datetime

router = APIRouter(prefix="/employees", tags=["Employee History"])


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.get("/{employee_id}/history", response_model=list[EmploymentHistoryResponse])
def get_employee_history(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    history = db.query(EmploymentHistory).filter(
        EmploymentHistory.employee_id == employee_id
    ).order_by(EmploymentHistory.created_at.desc()).all()
    return history


@router.post("/{employee_id}/history", response_model=EmploymentHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_employment_record(
    employee_id: int,
    history_data: EmploymentHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db_history = EmploymentHistory(
        employee_id=employee_id,
        action_type=history_data.action_type,
        field_name=history_data.field_name,
        old_value=history_data.old_value,
        new_value=history_data.new_value,
        effective_date=history_data.effective_date,
        remarks=history_data.remarks,
        created_by=current_user.id
    )
    
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return db_history


@router.post("/{employee_id}/promote", response_model=EmploymentHistoryResponse)
def promote_employee(
    employee_id: int,
    new_designation_id: int,
    new_salary: float = None,
    remarks: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    from app.models.user import Designation
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    old_designation = db.query(Designation).filter(Designation.id == employee.designation_id).first() if employee.designation_id else None
    new_designation = db.query(Designation).filter(Designation.id == new_designation_id).first()
    
    history = EmploymentHistory(
        employee_id=employee_id,
        action_type="promotion",
        field_name="designation",
        old_value=old_designation.name if old_designation else "None",
        new_value=new_designation.name if new_designation else "None",
        effective_date=datetime.now(),
        remarks=remarks,
        created_by=current_user.id
    )
    
    employee.designation_id = new_designation_id
    
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return history


@router.post("/{employee_id}/transfer", response_model=EmploymentHistoryResponse)
def transfer_employee(
    employee_id: int,
    new_department_id: int,
    remarks: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    from app.models.user import Department
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    old_department = db.query(Department).filter(Department.id == employee.department_id).first() if employee.department_id else None
    new_department = db.query(Department).filter(Department.id == new_department_id).first()
    
    history = EmploymentHistory(
        employee_id=employee_id,
        action_type="transfer",
        field_name="department",
        old_value=old_department.name if old_department else "None",
        new_value=new_department.name if new_department else "None",
        effective_date=datetime.now(),
        remarks=remarks,
        created_by=current_user.id
    )
    
    employee.department_id = new_department_id
    
    db.add(history)
    db.commit()
    db.refresh(history)
    
    return history
