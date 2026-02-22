from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.user import User, Department, Designation, Employee
from app.models.document import AuditLog
from app.schemas.user import (
    EmployeeCreate, EmployeeUpdate,
    DepartmentCreate, DepartmentUpdate,
    DesignationCreate, DesignationUpdate,
    UserCreate, UserUpdate
)
from app.core.security import get_password_hash, verify_password, create_access_token
from typing import Optional, List
from datetime import datetime, timedelta
import random
import string
import json
from app.core.config import settings


class EmployeeService:
    def __init__(self, db: Session):
        self.db = db

    def _log_audit(self, user_id: int, action: str, entity_type: str, entity_id: int, old_value: dict = None, new_value: dict = None):
        try:
            audit_log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_value=json.dumps(old_value) if old_value else None,
                new_value=json.dumps(new_value) if new_value else None,
            )
            self.db.add(audit_log)
            self.db.commit()
        except Exception:
            pass

    def _generate_employee_code(self) -> str:
        year = datetime.now().year
        while True:
            random_suffix = ''.join(random.choices(string.digits, k=4))
            code = f"EMP{year}{random_suffix}"
            existing = self.db.query(Employee).filter(Employee.employee_code == code).first()
            if not existing:
                return code

    def employee_login(self, employee_code: str, password: str) -> Optional[dict]:
        """Login using employee code and password (creates user if doesn't exist)"""
        employee = self.db.query(Employee).filter(Employee.employee_code == employee_code).first()
        
        if not employee:
            return None
        
        user = self.db.query(User).filter(User.employee_id == employee.id).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
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
            "employee": {
                "id": employee.id,
                "employee_code": employee.employee_code,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "email": employee.email,
                "phone": employee.phone,
                "department": employee.department.name if employee.department else None,
                "designation": employee.designation.name if employee.designation else None,
                "date_of_joining": employee.date_of_joining
            }
        }

    def create_employee(self, employee_data: EmployeeCreate, user_id: int = None) -> Employee:
        employee_code = self._generate_employee_code()
        
        db_employee = Employee(
            employee_code=employee_code,
            **employee_data.model_dump()
        )
        
        self.db.add(db_employee)
        self.db.commit()
        self.db.refresh(db_employee)
        
        if user_id:
            self._log_audit(user_id, "create", "employee", db_employee.id, None, employee_data.model_dump())
        
        return db_employee

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_employee_by_code(self, employee_code: str) -> Optional[Employee]:
        return self.db.query(Employee).filter(Employee.employee_code == employee_code).first()

    def get_employees(
        self,
        skip: int = 0,
        limit: int = 20,
        search: Optional[str] = None,
        department_id: Optional[int] = None,
        status: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> tuple[List[dict], int]:
        query = self.db.query(Employee)
        
        if search:
            query = query.filter(
                or_(
                    Employee.first_name.ilike(f"%{search}%"),
                    Employee.last_name.ilike(f"%{search}%"),
                    Employee.email.ilike(f"%{search}%"),
                    Employee.employee_code.ilike(f"%{search}%")
                )
            )
        
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if status:
            query = query.filter(Employee.status == status)
        
        if is_active is not None:
            query = query.filter(Employee.is_active == is_active)
        
        total = query.count()
        employees = query.order_by(Employee.id.desc()).offset(skip).limit(limit).all()
        
        result = []
        for emp in employees:
            result.append({
                "id": emp.id,
                "employee_code": emp.employee_code,
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "email": emp.email,
                "phone": emp.phone,
                "department": emp.department.name if emp.department else None,
                "designation": emp.designation.name if emp.designation else None,
                "status": emp.status.value if emp.status else None,
                "is_active": emp.is_active,
                "date_of_joining": emp.date_of_joining
            })
        
        return result, total

    def update_employee(self, employee_id: int, employee_data: EmployeeUpdate, user_id: int = None) -> Optional[Employee]:
        employee = self.get_employee(employee_id)
        
        if not employee:
            return None
        
        old_values = {}
        update_data = employee_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            old_values[key] = getattr(employee, key)
            setattr(employee, key, value)
        
        self.db.commit()
        self.db.refresh(employee)
        
        if user_id:
            self._log_audit(user_id, "update", "employee", employee_id, old_values, update_data)
        
        return employee

    def delete_employee(self, employee_id: int, user_id: int = None) -> bool:
        employee = self.get_employee(employee_id)
        
        if not employee:
            return False
        
        old_values = {"first_name": employee.first_name, "last_name": employee.last_name, "is_active": employee.is_active}
        employee.is_active = False
        self.db.commit()
        
        if user_id:
            self._log_audit(user_id, "delete", "employee", employee_id, old_values, None)
        
        return True

    def create_department(self, department_data: DepartmentCreate, user_id: int = None) -> Department:
        db_department = Department(**department_data.model_dump())
        self.db.add(db_department)
        self.db.commit()
        self.db.refresh(db_department)
        
        if user_id:
            self._log_audit(user_id, "create", "department", db_department.id, None, department_data.model_dump())
        
        return db_department

    def get_department(self, department_id: int) -> Optional[Department]:
        return self.db.query(Department).filter(Department.id == department_id).first()

    def get_departments(self, skip: int = 0, limit: int = 20) -> tuple[List[Department], int]:
        query = self.db.query(Department).filter(Department.is_active == True)
        total = query.count()
        departments = query.offset(skip).limit(limit).all()
        return departments, total

    def update_department(self, department_id: int, department_data: DepartmentUpdate, user_id: int = None) -> Optional[Department]:
        department = self.get_department(department_id)
        if not department:
            return None
        
        old_values = {}
        update_data = department_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            old_values[key] = getattr(department, key)
            setattr(department, key, value)
        
        self.db.commit()
        self.db.refresh(department)
        
        if user_id:
            self._log_audit(user_id, "update", "department", department_id, old_values, update_data)
        
        return department

    def delete_department(self, department_id: int, user_id: int = None) -> bool:
        department = self.get_department(department_id)
        if not department:
            return False
        
        old_values = {"name": department.name, "code": department.code}
        department.is_active = False
        self.db.commit()
        
        if user_id:
            self._log_audit(user_id, "delete", "department", department_id, old_values, None)
        
        return True

    def create_designation(self, designation_data: DesignationCreate) -> Designation:
        db_designation = Designation(**designation_data.model_dump())
        self.db.add(db_designation)
        self.db.commit()
        self.db.refresh(db_designation)
        return db_designation

    def get_designation(self, designation_id: int) -> Optional[Designation]:
        return self.db.query(Designation).filter(Designation.id == designation_id).first()

    def get_designations(self, department_id: Optional[int] = None, skip: int = 0, limit: int = 20) -> tuple[List[Designation], int]:
        query = self.db.query(Designation).filter(Designation.is_active == True)
        
        if department_id:
            query = query.filter(Designation.department_id == department_id)
        
        total = query.count()
        designations = query.offset(skip).limit(limit).all()
        return designations, total

    def update_designation(self, designation_id: int, designation_data: DesignationUpdate) -> Optional[Designation]:
        designation = self.get_designation(designation_id)
        if not designation:
            return None
        
        update_data = designation_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(designation, key, value)
        
        self.db.commit()
        self.db.refresh(designation)
        return designation

    def delete_designation(self, designation_id: int) -> bool:
        designation = self.get_designation(designation_id)
        if not designation:
            return False
        
        designation.is_active = False
        self.db.commit()
        return True


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        existing_user = self.db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            raise ValueError("User already exists")
        
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            employee_id=user_data.employee_id,
            is_active=True
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 20, role: Optional[str] = None) -> tuple[List[User], int]:
        query = self.db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        
        total = query.count()
        users = query.order_by(User.id.desc()).offset(skip).limit(limit).all()
        return users, total

    def update_user(self, user_id: int, user_data: dict) -> Optional[User]:
        user = self.get_user(user_id)
        if not user:
            return None
        
        for key, value in user_data.items():
            if value is not None and key != "id":
                setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
