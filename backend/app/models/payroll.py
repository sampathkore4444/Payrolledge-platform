from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ComponentType(str, enum.Enum):
    EARNING = "earning"
    DEDUCTION = "deduction"


class SalaryComponent(Base):
    __tablename__ = "salary_components"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    component_name = Column(String(100), nullable=False)
    component_type = Column(SQLEnum(ComponentType), nullable=False)
    amount = Column(Float, nullable=False, default=0)
    
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    
    is_taxable = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="salary_components")


class PayrollStatus(str, enum.Enum):
    DRAFT = "draft"
    PROCESSED = "processed"
    APPROVED = "approved"
    PAID = "paid"


class PayrollRecord(Base):
    __tablename__ = "payroll_records"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    
    basic_salary = Column(Float, nullable=False, default=0)
    hra = Column(Float, default=0)
    conveyance = Column(Float, default=0)
    special_allowance = Column(Float, default=0)
    overtime_amount = Column(Float, default=0)
    bonus = Column(Float, default=0)
    arrears = Column(Float, default=0)
    other_earnings = Column(Float, default=0)
    
    pf_employee = Column(Float, default=0)
    pf_employer = Column(Float, default=0)
    esic_employee = Column(Float, default=0)
    esic_employer = Column(Float, default=0)
    professional_tax = Column(Float, default=0)
    tds = Column(Float, default=0)
    other_deductions = Column(Float, default=0)
    
    gross_earnings = Column(Float, default=0)
    total_deductions = Column(Float, default=0)
    net_salary = Column(Float, default=0)
    
    working_days = Column(Float, default=0)
    days_present = Column(Float, default=0)
    days_absent = Column(Float, default=0)
    overtime_hours = Column(Float, default=0)
    
    status = Column(SQLEnum(PayrollStatus), default=PayrollStatus.DRAFT)
    
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    payment_date = Column(DateTime, nullable=True)
    payment_mode = Column(String(50))
    
    remarks = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="payroll_records")
    processor = relationship("User", foreign_keys=[processed_by])
    approver = relationship("User", foreign_keys=[approved_by])


class PayrollSettings(Base):
    __tablename__ = "payroll_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    epf_rate_employee = Column(Float, default=12.0)
    epf_rate_employer = Column(Float, default=12.0)
    esic_rate_employee = Column(Float, default=0.75)
    esic_rate_employer = Column(Float, default=3.25)
    
    professional_tax = Column(Float, default=200.0)
    professional_tax_limit = Column(Float, default=15000.0)
    
    epf_wage_limit = Column(Float, default=15000.0)
    esic_wage_limit = Column(Float, default=21000.0)
    
    standard_deduction = Column(Float, default=50000.0)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
