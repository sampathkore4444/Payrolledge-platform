from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, Employee
from app.services.employee_service import EmployeeService
from typing import Optional

router = APIRouter(prefix="/integration", tags=["Integration"])


@router.get("/employees/{employee_code}")
def get_employee_by_code(
    employee_code: str,
    db: Session = Depends(get_db)
):
    """Public endpoint to lookup employee by code (for biometric integration)"""
    service = EmployeeService(db)
    employee = service.get_employee_by_code(employee_code)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {
        "employee_code": employee.employee_code,
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "department": employee.department.name if employee.department else None,
        "is_active": employee.is_active
    }


@router.post("/attendance/sync")
def sync_attendance(
    records: list[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Sync attendance from biometric device"""
    from app.services.attendance_service import AttendanceService
    service = AttendanceService(db)
    
    results = []
    for record in records:
        try:
            emp = service.get_employee_by_code(record.get('employee_code'))
            if emp:
                service.mark_attendance(
                    employee_id=emp.id,
                    date=record.get('date'),
                    check_in=record.get('check_in'),
                    check_out=record.get('check_out'),
                    user_id=current_user.id
                )
                results.append({"employee_code": record.get('employee_code'), "status": "success"})
            else:
                results.append({"employee_code": record.get('employee_code'), "status": "employee_not_found"})
        except Exception as e:
            results.append({"employee_code": record.get('employee_code'), "status": "error", "message": str(e)})
    
    return {"results": results}


@router.get("/health")
def integration_health():
    """Health check for integration"""
    return {"status": "ok", "service": "payrolledge-integration-api"}
