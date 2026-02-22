from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ComponentType(str, Enum):
    EARNING = "earning"
    DEDUCTION = "deduction"


class PayrollStatus(str, Enum):
    DRAFT = "draft"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"


class SalaryComponentBase(BaseModel):
    component_name: str
    component_type: ComponentType
    amount: float
    effective_from: datetime
    effective_to: Optional[datetime] = None
    is_taxable: bool = True


class SalaryComponentCreate(SalaryComponentBase):
    employee_id: int


class SalaryComponentUpdate(SalaryComponentBase):
    component_name: Optional[str] = None
    component_type: Optional[ComponentType] = None
    amount: Optional[float] = None
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_taxable: Optional[bool] = None
    is_active: Optional[bool] = None


class SalaryComponentResponse(SalaryComponentBase):
    id: int
    employee_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PayrollRecordBase(BaseModel):
    employee_id: int
    month: int
    year: int
    basic_salary: float = 0
    hra: float = 0
    conveyance: float = 0
    special_allowance: float = 0
    overtime_amount: float = 0
    bonus: float = 0
    arrears: float = 0
    other_earnings: float = 0
    pf_employee: float = 0
    pf_employer: float = 0
    esic_employee: float = 0
    esic_employer: float = 0
    professional_tax: float = 0
    tds: float = 0
    other_deductions: float = 0
    working_days: float = 0
    days_present: float = 0
    days_absent: float = 0
    overtime_hours: float = 0


class PayrollRecordCreate(PayrollRecordBase):
    pass


class PayrollRecordUpdate(PayrollRecordBase):
    status: Optional[PayrollStatus] = None
    payment_date: Optional[datetime] = None
    payment_mode: Optional[str] = None
    remarks: Optional[str] = None


class PayrollRecordResponse(PayrollRecordBase):
    id: int
    gross_earnings: float
    total_deductions: float
    net_salary: float
    status: PayrollStatus
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    payment_mode: Optional[str] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PayrollProcessRequest(BaseModel):
    month: int
    year: int
    employee_ids: Optional[List[int]] = None


class PayrollApprovalRequest(BaseModel):
    status: PayrollStatus
    remarks: Optional[str] = None


class PayrollSummary(BaseModel):
    total_employees: int
    total_gross: float
    total_deductions: float
    total_net: float
    total_pf_employee: float
    total_pf_employer: float
    total_esic_employee: float
    total_esic_employer: float
    total_professional_tax: float
    total_tds: float
    
    class Config:
        from_attributes = True


class PayrollSettingsBase(BaseModel):
    epf_rate_employee: float = 12.0
    epf_rate_employer: float = 12.0
    esic_rate_employee: float = 0.75
    esic_rate_employer: float = 3.25
    professional_tax: float = 200.0
    professional_tax_limit: float = 15000.0
    epf_wage_limit: float = 15000.0
    esic_wage_limit: float = 21000.0
    standard_deduction: float = 50000.0


class PayrollSettingsCreate(PayrollSettingsBase):
    pass


class PayrollSettingsUpdate(PayrollSettingsBase):
    is_active: Optional[bool] = None


class PayrollSettingsResponse(PayrollSettingsBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
