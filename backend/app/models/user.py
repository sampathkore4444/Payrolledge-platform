from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    HR = "hr"
    DEPARTMENT_HEAD = "department_head"
    EMPLOYEE = "employee"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(SQLEnum(UserRole), default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="user", foreign_keys=[employee_id])


class Department(Base):
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    code = Column(String(50), unique=True)
    description = Column(Text)
    manager_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employees = relationship("Employee", back_populates="department", foreign_keys="[Employee.department_id]")
    manager = relationship("Employee", foreign_keys=[manager_id])
    designations = relationship("Designation", back_populates="department")


class Designation(Base):
    __tablename__ = "designations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    code = Column(String(50))
    description = Column(Text)
    department_id = Column(Integer, ForeignKey("departments.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    department = relationship("Department", back_populates="designations")


class EmployeeStatus(str, enum.Enum):
    PROBATION = "probation"
    PERMANENT = "permanent"
    CONTRACT = "contract"
    RESIGNED = "resigned"
    TERMINATED = "terminated"


class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(20))
    date_of_birth = Column(DateTime)
    gender = Column(String(20))
    marital_status = Column(String(20))
    
    department_id = Column(Integer, ForeignKey("departments.id"))
    designation_id = Column(Integer, ForeignKey("designations.id"))
    
    date_of_joining = Column(DateTime)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.PROBATION)
    
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(20))
    
    aadhar_number = Column(String(20))
    pan_number = Column(String(20))
    uan_number = Column(String(20))
    esic_number = Column(String(20))
    bank_account_number = Column(String(30))
    bank_name = Column(String(200))
    ifsc_code = Column(String(20))
    
    photo = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    department = relationship("Department", back_populates="employees", foreign_keys="[Employee.department_id]")
    designation = relationship("Designation")
    user = relationship("User", back_populates="employee", foreign_keys="[User.employee_id]")
    attendances = relationship("Attendance", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee")
    payroll_records = relationship("PayrollRecord", back_populates="employee")
    documents = relationship("Document", back_populates="employee")
    salary_components = relationship("SalaryComponent", back_populates="employee")
