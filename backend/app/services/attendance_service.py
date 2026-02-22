from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.attendance import Attendance, Shift, LeaveRequest, LeaveBalance
from app.models.document import AuditLog
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate, AttendanceStatus
from app.schemas.leave import LeaveType, LeaveRequestStatus
from typing import Optional, List
from datetime import datetime, date
import json


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def create_shift(self, shift_data: dict) -> Shift:
        db_shift = Shift(**shift_data)
        self.db.add(db_shift)
        self.db.commit()
        self.db.refresh(db_shift)
        return db_shift

    def get_shift(self, shift_id: int) -> Optional[Shift]:
        return self.db.query(Shift).filter(Shift.id == shift_id).first()

    def get_shifts(self, skip: int = 0, limit: int = 20) -> tuple[List[Shift], int]:
        query = self.db.query(Shift).filter(Shift.is_active == True)
        total = query.count()
        shifts = query.offset(skip).limit(limit).all()
        return shifts, total

    def create_attendance(self, attendance_data: AttendanceCreate) -> Attendance:
        existing = self.db.query(Attendance).filter(
            and_(
                Attendance.employee_id == attendance_data.employee_id,
                Attendance.date == attendance_data.date
            )
        ).first()
        
        if existing:
            raise ValueError("Attendance already exists for this date")
        
        db_attendance = Attendance(**attendance_data.model_dump())
        self.db.add(db_attendance)
        self.db.commit()
        self.db.refresh(db_attendance)
        
        return db_attendance

    def get_attendance(self, attendance_id: int) -> Optional[Attendance]:
        return self.db.query(Attendance).filter(Attendance.id == attendance_id).first()

    def get_attendances(
        self,
        employee_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[AttendanceStatus] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Attendance], int]:
        query = self.db.query(Attendance)
        
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        
        if start_date:
            query = query.filter(Attendance.date >= start_date)
        
        if end_date:
            query = query.filter(Attendance.date <= end_date)
        
        if status:
            query = query.filter(Attendance.status == status)
        
        total = query.count()
        attendances = query.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()
        
        return attendances, total

    def get_employee_attendance_for_month(self, employee_id: int, month: int, year: int) -> List[Attendance]:
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        return self.db.query(Attendance).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= start_date,
                Attendance.date < end_date
            )
        ).all()

    def update_attendance(self, attendance_id: int, attendance_data: AttendanceUpdate) -> Optional[Attendance]:
        attendance = self.get_attendance(attendance_id)
        
        if not attendance:
            return None
        
        update_data = attendance_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(attendance, key, value)
        
        self.db.commit()
        self.db.refresh(attendance)
        
        return attendance

    def bulk_create_attendance(self, attendances_data: List[AttendanceCreate]) -> List[Attendance]:
        created_attendances = []
        
        for attendance_data in attendances_data:
            existing = self.db.query(Attendance).filter(
                and_(
                    Attendance.employee_id == attendance_data.employee_id,
                    Attendance.date == attendance_data.date
                )
            ).first()
            
            if not existing:
                db_attendance = Attendance(**attendance_data.model_dump())
                self.db.add(db_attendance)
                created_attendances.append(db_attendance)
        
        self.db.commit()
        
        for attendance in created_attendances:
            self.db.refresh(attendance)
        
        return created_attendances

    def get_attendance_summary(
        self,
        employee_id: int,
        month: int,
        year: int
    ) -> dict:
        attendances = self.get_employee_attendance_for_month(employee_id, month, year)
        
        summary = {
            "total": len(attendances),
            "present": 0,
            "absent": 0,
            "late": 0,
            "half_day": 0,
            "leave": 0,
            "weekly_off": 0,
            "holiday": 0,
            "overtime_hours": 0.0
        }
        
        for att in attendances:
            if att.status == AttendanceStatus.PRESENT:
                summary["present"] += 1
            elif att.status == AttendanceStatus.ABSENT:
                summary["absent"] += 1
            elif att.status == AttendanceStatus.LATE:
                summary["late"] += 1
            elif att.status == AttendanceStatus.HALF_DAY:
                summary["half_day"] += 1
            elif att.status == AttendanceStatus.LEAVE:
                summary["leave"] += 1
            elif att.status == AttendanceStatus.WO:
                summary["weekly_off"] += 1
            elif att.status == AttendanceStatus.HOLIDAY:
                summary["holiday"] += 1
            
            summary["overtime_hours"] += att.overtime_hours or 0
        
        return summary


class LeaveService:
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

    def create_leave_request(self, leave_data: dict) -> LeaveRequest:
        db_leave = LeaveRequest(**leave_data)
        self.db.add(db_leave)
        self.db.commit()
        self.db.refresh(db_leave)
        return db_leave

    def get_leave_request(self, leave_id: int) -> Optional[LeaveRequest]:
        return self.db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()

    def get_leave_requests(
        self,
        employee_id: Optional[int] = None,
        status: Optional[LeaveRequestStatus] = None,
        leave_type: Optional[LeaveType] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[LeaveRequest], int]:
        query = self.db.query(LeaveRequest)
        
        if employee_id:
            query = query.filter(LeaveRequest.employee_id == employee_id)
        
        if status:
            query = query.filter(LeaveRequest.status == status)
        
        if leave_type:
            query = query.filter(LeaveRequest.leave_type == leave_type)
        
        total = query.count()
        leaves = query.order_by(LeaveRequest.created_at.desc()).offset(skip).limit(limit).all()
        
        return leaves, total

    def update_leave_request(
        self,
        leave_id: int,
        leave_data: dict,
        approved_by: Optional[int] = None
    ) -> Optional[LeaveRequest]:
        leave = self.get_leave_request(leave_id)
        
        if not leave:
            return None
        
        for key, value in leave_data.items():
            if value is not None:
                setattr(leave, key, value)
        
        if approved_by:
            leave.approved_by = approved_by
            leave.approved_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(leave)
        
        return leave

    def approve_leave_request(self, leave_id: int, approved_by: int, status: LeaveRequestStatus, remarks: str = None) -> Optional[LeaveRequest]:
        leave = self.get_leave_request(leave_id)
        
        if not leave:
            return None
        
        old_status = leave.status.value if leave.status else None
        leave.status = status
        leave.approved_by = approved_by
        leave.approved_at = datetime.now()
        leave.remarks = remarks
        
        self.db.commit()
        self.db.refresh(leave)
        
        self._log_audit(approved_by, f"leave_{status.value}", "leave_request", leave_id, {"status": old_status}, {"status": status.value})
        
        return leave

    def get_leave_balance(self, employee_id: int, leave_type: LeaveType, year: int) -> Optional[LeaveBalance]:
        return self.db.query(LeaveBalance).filter(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type == leave_type,
                LeaveBalance.year == year
            )
        ).first()

    def get_leave_balances(self, employee_id: int, year: int) -> List[LeaveBalance]:
        return self.db.query(LeaveBalance).filter(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.year == year
            )
        ).all()

    def create_leave_balance(self, balance_data: dict) -> LeaveBalance:
        db_balance = LeaveBalance(**balance_data)
        self.db.add(db_balance)
        self.db.commit()
        self.db.refresh(db_balance)
        return db_balance

    def update_leave_balance(self, balance_id: int, balance_data: dict) -> Optional[LeaveBalance]:
        balance = self.db.query(LeaveBalance).filter(LeaveBalance.id == balance_id).first()
        
        if not balance:
            return None
        
        for key, value in balance_data.items():
            if value is not None:
                setattr(balance, key, value)
        
        self.db.commit()
        self.db.refresh(balance)
        
        return balance
