from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.payroll import SalaryComponent, PayrollRecord, PayrollSettings, PayrollStatus
from app.models.attendance import Attendance, AttendanceStatus
from app.models.user import Employee
from app.models.document import AuditLog
from app.schemas.payroll import PayrollRecordCreate, PayrollSettingsBase
from typing import Optional, List
from datetime import datetime
import json


class PayrollService:
    def __init__(self, db: Session):
        self.db = db
        self._settings = None

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

    def _get_settings(self) -> PayrollSettings:
        if self._settings is None:
            self._settings = self.db.query(PayrollSettings).filter(PayrollSettings.is_active == True).first()
            if not self._settings:
                self._settings = PayrollSettings()
                self.db.add(self._settings)
                self.db.commit()
                self.db.refresh(self._settings)
        return self._settings

    def create_salary_component(self, component_data: dict) -> SalaryComponent:
        db_component = SalaryComponent(**component_data)
        self.db.add(db_component)
        self.db.commit()
        self.db.refresh(db_component)
        return db_component

    def get_salary_component(self, component_id: int) -> Optional[SalaryComponent]:
        return self.db.query(SalaryComponent).filter(SalaryComponent.id == component_id).first()

    def get_employee_salary_components(self, employee_id: int) -> List[SalaryComponent]:
        return self.db.query(SalaryComponent).filter(
            and_(
                SalaryComponent.employee_id == employee_id,
                SalaryComponent.is_active == True
            )
        ).all()

    def update_salary_component(self, component_id: int, component_data: dict) -> Optional[SalaryComponent]:
        component = self.get_salary_component(component_id)
        
        if not component:
            return None
        
        for key, value in component_data.items():
            if value is not None:
                setattr(component, key, value)
        
        self.db.commit()
        self.db.refresh(component)
        
        return component

    def calculate_payroll(self, employee_id: int, month: int, year: int) -> dict:
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        
        if not employee:
            raise ValueError("Employee not found")
        
        settings = self._get_settings()
        
        basic_salary = 0.0
        earnings = []
        deductions = []
        
        components = self.get_employee_salary_components(employee_id)
        for comp in components:
            if comp.component_type.value == "earning":
                basic_salary += comp.amount
                earnings.append({"name": comp.component_name, "amount": comp.amount})
            else:
                deductions.append({"name": comp.component_name, "amount": comp.amount})
        
        hra = basic_salary * 0.1
        conveyance = 1600
        special_allowance = basic_salary * 0.3
        
        attendance_summary = self._get_attendance_summary(employee_id, month, year)
        days_present = attendance_summary.get("present", 0)
        total_working_days = attendance_summary.get("total", 0)
        
        pro_rated_basic = (basic_salary / total_working_days) * days_present if total_working_days > 0 else basic_salary
        pro_rated_hra = (hra / total_working_days) * days_present if total_working_days > 0 else hra
        pro_rated_conveyance = (conveyance / total_working_days) * days_present if total_working_days > 0 else conveyance
        pro_rated_special = (special_allowance / total_working_days) * days_present if total_working_days > 0 else special_allowance
        
        overtime_amount = attendance_summary.get("overtime_hours", 0) * (basic_salary / (total_working_days * 8))
        
        gross_earnings = pro_rated_basic + pro_rated_hra + pro_rated_conveyance + pro_rated_special + overtime_amount
        
        pf_wage = min(pro_rated_basic, settings.epf_wage_limit)
        pf_employee = pf_wage * (settings.epf_rate_employee / 100)
        pf_employer = pf_wage * (settings.epf_rate_employer / 100)
        
        esic_wage = gross_earnings
        if esic_wage <= settings.esic_wage_limit:
            esic_employee = esic_wage * (settings.esic_rate_employee / 100)
            esic_employer = esic_wage * (settings.esic_rate_employer / 100)
        else:
            esic_employee = 0
            esic_employer = 0
        
        professional_tax = settings.professional_tax if gross_earnings >= settings.professional_tax_limit else 0
        
        annual_gross = gross_earnings * 12
        tds = self._calculate_tds(annual_gross) / 12
        
        total_deductions = pf_employee + esic_employee + professional_tax + tds
        for ded in deductions:
            total_deductions += ded["amount"]
        
        net_salary = gross_earnings - total_deductions
        
        return {
            "employee_id": employee_id,
            "month": month,
            "year": year,
            "basic_salary": pro_rated_basic,
            "hra": pro_rated_hra,
            "conveyance": pro_rated_conveyance,
            "special_allowance": pro_rated_special,
            "overtime_amount": overtime_amount,
            "bonus": 0,
            "arrears": 0,
            "other_earnings": 0,
            "gross_earnings": gross_earnings,
            "pf_employee": pf_employee,
            "pf_employer": pf_employer,
            "esic_employee": esic_employee,
            "esic_employer": esic_employer,
            "professional_tax": professional_tax,
            "tds": tds,
            "other_deductions": 0,
            "total_deductions": total_deductions,
            "net_salary": net_salary,
            "working_days": total_working_days,
            "days_present": days_present,
            "days_absent": attendance_summary.get("absent", 0),
            "overtime_hours": attendance_summary.get("overtime_hours", 0)
        }

    def _get_attendance_summary(self, employee_id: int, month: int, year: int) -> dict:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        attendances = self.db.query(Attendance).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date < end_date
            )
        ).all()
        
        summary = {"total": 0, "present": 0, "absent": 0, "overtime_hours": 0.0}
        
        for att in attendances:
            summary["total"] += 1
            if att.status == AttendanceStatus.PRESENT:
                summary["present"] += 1
            elif att.status == AttendanceStatus.ABSENT:
                summary["absent"] += 1
            summary["overtime_hours"] += att.overtime_hours or 0
        
        return summary

    def _calculate_tds(self, annual_gross: float) -> float:
        standard_deduction = 50000
        
        taxable_income = annual_gross - standard_deduction
        
        if taxable_income <= 250000:
            return 0
        elif taxable_income <= 500000:
            return (taxable_income - 250000) * 0.05
        elif taxable_income <= 1000000:
            return 12500 + (taxable_income - 500000) * 0.10
        elif taxable_income <= 2000000:
            return 62500 + (taxable_income - 1000000) * 0.15
        else:
            return 162500 + (taxable_income - 2000000) * 0.20

    def process_payroll(self, month: int, year: int, employee_ids: Optional[List[int]] = None) -> List[PayrollRecord]:
        if employee_ids is None:
            employees = self.db.query(Employee).filter(Employee.is_active == True).all()
        else:
            employees = self.db.query(Employee).filter(Employee.id.in_(employee_ids)).all()
        
        payroll_records = []
        
        for employee in employees:
            existing = self.db.query(PayrollRecord).filter(
                and_(
                    PayrollRecord.employee_id == employee.id,
                    PayrollRecord.month == month,
                    PayrollRecord.year == year
                )
            ).first()
            
            if existing:
                continue
            
            payroll_data = self.calculate_payroll(employee.id, month, year)
            payroll_data["status"] = PayrollStatus.PROCESSED
            payroll_data["processed_at"] = datetime.now()
            
            db_record = PayrollRecord(**payroll_data)
            self.db.add(db_record)
            payroll_records.append(db_record)
        
        self.db.commit()
        
        for record in payroll_records:
            self.db.refresh(record)
        
        return payroll_records

    def get_payroll_record(self, record_id: int) -> Optional[PayrollRecord]:
        return self.db.query(PayrollRecord).filter(PayrollRecord.id == record_id).first()

    def get_employee_payroll_records(
        self,
        employee_id: Optional[int] = None,
        month: Optional[int] = None,
        year: Optional[int] = None,
        status: Optional[PayrollStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[PayrollRecord], int]:
        query = self.db.query(PayrollRecord)
        
        if employee_id:
            query = query.filter(PayrollRecord.employee_id == employee_id)
        
        if month:
            query = query.filter(PayrollRecord.month == month)
        
        if year:
            query = query.filter(PayrollRecord.year == year)
        
        if status:
            query = query.filter(PayrollRecord.status == status)
        
        total = query.count()
        records = query.order_by(PayrollRecord.year.desc(), PayrollRecord.month.desc()).offset(skip).limit(limit).all()
        
        return records, total

    def update_payroll_record(self, record_id: int, record_data: dict) -> Optional[PayrollRecord]:
        record = self.get_payroll_record(record_id)
        
        if not record:
            return None
        
        for key, value in record_data.items():
            if value is not None:
                setattr(record, key, value)
        
        self.db.commit()
        self.db.refresh(record)
        
        return record

    def approve_payroll_record(self, record_id: int, approved_by: int) -> Optional[PayrollRecord]:
        record = self.get_payroll_record(record_id)
        
        if not record:
            return None
        
        old_status = record.status.value if record.status else None
        record.status = PayrollStatus.APPROVED
        record.approved_by = approved_by
        record.approved_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(record)
        
        self._log_audit(approved_by, "approve", "payroll", record_id, {"status": old_status}, {"status": "approved"})
        
        return record

    def get_payroll_summary(self, month: int, year: int) -> dict:
        records = self.db.query(PayrollRecord).filter(
            and_(
                PayrollRecord.month == month,
                PayrollRecord.year == year
            )
        ).all()
        
        return {
            "total_employees": len(records),
            "total_gross": sum(r.gross_earnings for r in records),
            "total_deductions": sum(r.total_deductions for r in records),
            "total_net": sum(r.net_salary for r in records),
            "total_pf_employee": sum(r.pf_employee for r in records),
            "total_pf_employer": sum(r.pf_employer for r in records),
            "total_esic_employee": sum(r.esic_employee for r in records),
            "total_esic_employer": sum(r.esic_employer for r in records),
            "total_professional_tax": sum(r.professional_tax for r in records),
            "total_tds": sum(r.tds for r in records)
        }

    def get_payroll_settings(self) -> PayrollSettings:
        return self._get_settings()

    def update_payroll_settings(self, settings_data: PayrollSettingsBase) -> PayrollSettings:
        settings = self._get_settings()
        
        settings.epf_rate_employee = settings_data.epf_rate_employee
        settings.epf_rate_employer = settings_data.epf_rate_employer
        settings.esic_rate_employee = settings_data.esic_rate_employee
        settings.esic_rate_employer = settings_data.esic_rate_employer
        settings.professional_tax = settings_data.professional_tax
        settings.professional_tax_limit = settings_data.professional_tax_limit
        settings.epf_wage_limit = settings_data.epf_wage_limit
        settings.esic_wage_limit = settings_data.esic_wage_limit
        settings.standard_deduction = settings_data.standard_deduction
        
        self.db.commit()
        self.db.refresh(settings)
        
        return settings
