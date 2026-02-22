from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LeaveType(str, Enum):
    CASUAL = "casual"
    SICK = "sick"
    PAID = "paid"
    UNPAID = "unpaid"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    COMPENSATORY = "compulsory"


class LeaveRequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveRequestBase(BaseModel):
    leave_type: LeaveType
    start_date: datetime
    end_date: datetime
    total_days: float
    reason: Optional[str] = None


class LeaveRequestCreate(LeaveRequestBase):
    employee_id: int


class LeaveRequestUpdate(BaseModel):
    leave_type: Optional[LeaveType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_days: Optional[float] = None
    reason: Optional[str] = None
    status: Optional[LeaveRequestStatus] = None
    remarks: Optional[str] = None


class LeaveRequestResponse(LeaveRequestBase):
    id: int
    employee_id: int
    status: LeaveRequestStatus
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaveBalanceBase(BaseModel):
    employee_id: int
    leave_type: LeaveType
    year: int
    total_days: float = 0
    used_days: float = 0
    available_days: float = 0


class LeaveBalanceCreate(LeaveBalanceBase):
    pass


class LeaveBalanceUpdate(BaseModel):
    total_days: Optional[float] = None
    used_days: Optional[float] = None
    available_days: Optional[float] = None


class LeaveBalanceResponse(LeaveBalanceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaveApproval(BaseModel):
    status: LeaveRequestStatus
    remarks: Optional[str] = None
