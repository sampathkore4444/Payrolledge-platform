from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    HR = "hr"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"


class EmployeeStatus(str, Enum):
    PROBATION = "probation"
    PERMANENT = "permanent"
    CONTRACT = "contract"
    RESIGNED = "resigned"
    TERMINATED = "terminated"


class DepartmentBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(DepartmentBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class DepartmentResponse(DepartmentBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class DesignationBase(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    department_id: Optional[int] = None


class DesignationCreate(DesignationBase):
    pass


class DesignationUpdate(DesignationBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class DesignationResponse(DesignationBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    marital_status: Optional[str] = None
    department_id: Optional[int] = None
    designation_id: Optional[int] = None
    date_of_joining: Optional[datetime] = None
    status: EmployeeStatus = EmployeeStatus.PROBATION
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    aadhar_number: Optional[str] = None
    pan_number: Optional[str] = None
    uan_number: Optional[str] = None
    esic_number: Optional[str] = None
    bank_account_number: Optional[str] = None
    bank_name: Optional[str] = None
    ifsc_code: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(EmployeeBase):
    first_name: Optional[str] = None
    is_active: Optional[bool] = None


class EmployeeResponse(EmployeeBase):
    id: int
    employee_code: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentResponse] = None
    designation: Optional[DesignationResponse] = None
    
    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    id: int
    employee_code: Optional[str]
    first_name: str
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    department: Optional[str] = None
    designation: Optional[str] = None
    status: EmployeeStatus
    is_active: bool
    date_of_joining: Optional[datetime]
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    role: UserRole = UserRole.EMPLOYEE
    employee_id: Optional[int] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChangePassword(BaseModel):
    old_password: str
    new_password: str
