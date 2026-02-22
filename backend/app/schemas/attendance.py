from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    LEAVE = "leave"
    WO = "wo"
    HOLIDAY = "holiday"


class ShiftBase(BaseModel):
    name: str
    code: Optional[str] = None
    start_time: str
    end_time: str
    late_threshold_minutes: int = 30
    full_day_hours: float = 8.0


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(ShiftBase):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ShiftResponse(ShiftBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceBase(BaseModel):
    employee_id: int
    date: datetime
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: AttendanceStatus = AttendanceStatus.ABSENT
    late_minutes: int = 0
    overtime_hours: float = 0.0
    shift_id: Optional[int] = None
    remarks: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: Optional[AttendanceStatus] = None
    late_minutes: Optional[int] = None
    overtime_hours: Optional[float] = None
    shift_id: Optional[int] = None
    remarks: Optional[str] = None
    is_approved: Optional[bool] = None


class AttendanceResponse(AttendanceBase):
    id: int
    is_approved: bool
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BulkAttendanceCreate(BaseModel):
    attendances: List[AttendanceCreate]


class AttendanceReport(BaseModel):
    employee_id: int
    month: int
    year: int
    total_days: int
    present: int
    absent: int
    late: int
    half_day: int
    leaves: int
    weekly_off: int
    holiday: int
    overtime_hours: float
    
    class Config:
        from_attributes = True
