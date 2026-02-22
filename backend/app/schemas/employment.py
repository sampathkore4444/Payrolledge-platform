from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class EmploymentHistoryBase(BaseModel):
    employee_id: int
    action_type: str
    field_name: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    effective_date: datetime
    remarks: Optional[str] = None


class EmploymentHistoryCreate(EmploymentHistoryBase):
    pass


class EmploymentHistoryResponse(EmploymentHistoryBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
