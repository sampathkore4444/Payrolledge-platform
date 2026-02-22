from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.user import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    DesignationCreate, DesignationUpdate, DesignationResponse,
    UserCreate, UserResponse
)
from app.schemas.common import PaginatedResponse, SuccessResponse
from app.services.employee_service import EmployeeService, UserService
from typing import Optional

router = APIRouter(prefix="/employees", tags=["Employees"])


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    employee = service.create_employee(employee_data, current_user.id)
    return employee


@router.get("/", response_model=PaginatedResponse[EmployeeListResponse])
def list_employees(
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = EmployeeService(db)
    skip = (page - 1) * page_size
    employees, total = service.get_employees(
        skip=skip,
        limit=page_size,
        search=search,
        department_id=department_id,
        status=status,
        is_active=is_active
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": employees,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = EmployeeService(db)
    employee = service.get_employee(employee_id)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee


@router.put("/{employee_id}", response_model=EmployeeResponse)
def update_employee(
    employee_id: int,
    employee_data: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    employee = service.update_employee(employee_id, employee_data, current_user.id)
    
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return employee


@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    success = service.delete_employee(employee_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return {"message": "Employee deleted successfully"}


department_router = APIRouter(prefix="/departments", tags=["Departments"])


@department_router.post("/", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(
    department_data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    department = service.create_department(department_data, current_user.id)
    return department


@department_router.get("/", response_model=list[DepartmentResponse])
def list_departments(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = EmployeeService(db)
    departments, _ = service.get_departments(skip=skip, limit=limit)
    return departments


@department_router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = EmployeeService(db)
    department = service.get_department(department_id)
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return department


@department_router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: int,
    department_data: DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    department = service.update_department(department_id, department_data, current_user.id)
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return department


@department_router.delete("/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    success = service.delete_department(department_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Department not found")
    
    return {"message": "Department deleted successfully"}


designation_router = APIRouter(prefix="/designations", tags=["Designations"])


@designation_router.post("/", response_model=DesignationResponse, status_code=status.HTTP_201_CREATED)
def create_designation(
    designation_data: DesignationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    designation = service.create_designation(designation_data)
    return designation


@designation_router.get("/", response_model=list[DesignationResponse])
def list_designations(
    department_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = EmployeeService(db)
    designations, _ = service.get_designations(department_id=department_id, skip=skip, limit=limit)
    return designations


@designation_router.get("/{designation_id}", response_model=DesignationResponse)
def get_designation(
    designation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = EmployeeService(db)
    designation = service.get_designation(designation_id)
    
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    
    return designation


@designation_router.put("/{designation_id}", response_model=DesignationResponse)
def update_designation(
    designation_id: int,
    designation_data: DesignationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    designation = service.update_designation(designation_id, designation_data)
    
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    
    return designation


@designation_router.delete("/{designation_id}")
def delete_designation(
    designation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = EmployeeService(db)
    success = service.delete_designation(designation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Designation not found")
    
    return {"message": "Designation deleted successfully"}


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    service = UserService(db)
    try:
        user = service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@users_router.get("/", response_model=PaginatedResponse[UserResponse])
def list_users(
    role: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    service = UserService(db)
    skip = (page - 1) * page_size
    users, total = service.get_users(skip=skip, limit=page_size, role=role)
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }


@users_router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    service = UserService(db)
    user = service.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
