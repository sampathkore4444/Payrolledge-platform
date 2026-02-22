from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    LEAVE = "leave"
    WO = "wo"  # Weekly Off
    HOLIDAY = "holiday"


class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    
    status = Column(SQLEnum(AttendanceStatus), default=AttendanceStatus.ABSENT)
    late_minutes = Column(Integer, default=0)
    overtime_hours = Column(Float, default=0)
    
    shift_id = Column(Integer, ForeignKey("shifts.id"), nullable=True)
    
    remarks = Column(Text)
    is_approved = Column(Boolean, default=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="attendances")
    shift = relationship("Shift")
    approver = relationship("User")


class Shift(Base):
    __tablename__ = "shifts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50))
    start_time = Column(String(10), nullable=False)
    end_time = Column(String(10), nullable=False)
    late_threshold_minutes = Column(Integer, default=30)
    full_day_hours = Column(Float, default=8.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class LeaveType(str, enum.Enum):
    CASUAL = "casual"
    SICK = "sick"
    PAID = "paid"
    UNPAID = "unpaid"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    COMPENSATORY = "compulsory"


class LeaveRequestStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(SQLEnum(LeaveType), nullable=False)
    
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_days = Column(Float, nullable=False)
    
    reason = Column(Text)
    status = Column(SQLEnum(LeaveRequestStatus), default=LeaveRequestStatus.PENDING)
    
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    remarks = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="leave_requests")
    approver = relationship("User")


class LeaveBalance(Base):
    __tablename__ = "leave_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(SQLEnum(LeaveType), nullable=False)
    
    year = Column(Integer, nullable=False)
    total_days = Column(Float, default=0)
    used_days = Column(Float, default=0)
    available_days = Column(Float, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee")
