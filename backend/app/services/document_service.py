from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.document import Document, OnboardingChecklist, Holiday, AuditLog
from app.schemas.document import DocumentCreate, DocumentUpdate, DocumentStatus
from typing import Optional, List
from datetime import datetime
import json


class DocumentService:
    def __init__(self, db: Session):
        self.db = db

    def create_document(self, document_data: DocumentCreate) -> Document:
        db_document = Document(**document_data.model_dump())
        self.db.add(db_document)
        self.db.commit()
        self.db.refresh(db_document)
        return db_document

    def get_document(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def get_employee_documents(self, employee_id: int) -> List[Document]:
        return self.db.query(Document).filter(Document.employee_id == employee_id).all()

    def update_document(self, document_id: int, document_data: DocumentUpdate) -> Optional[Document]:
        document = self.get_document(document_id)
        
        if not document:
            return None
        
        update_data = document_data.model_dump(exclude_unset=True)
        
        for key, value in update_data.items():
            setattr(document, key, value)
        
        self.db.commit()
        self.db.refresh(document)
        
        return document

    def verify_document(self, document_id: int, verified_by: int, status: DocumentStatus, remarks: str = None) -> Optional[Document]:
        document = self.get_document(document_id)
        
        if not document:
            return None
        
        document.status = status
        document.verified_by = verified_by
        document.verified_at = datetime.now()
        document.remarks = remarks
        
        self.db.commit()
        self.db.refresh(document)
        
        return document

    def delete_document(self, document_id: int) -> bool:
        document = self.get_document(document_id)
        
        if not document:
            return False
        
        self.db.delete(document)
        self.db.commit()
        
        return True


class OnboardingService:
    def __init__(self, db: Session):
        self.db = db

    def create_checklist(self, checklist_data: dict) -> OnboardingChecklist:
        db_checklist = OnboardingChecklist(**checklist_data)
        self.db.add(db_checklist)
        self.db.commit()
        self.db.refresh(db_checklist)
        return db_checklist

    def get_checklist(self, checklist_id: int) -> Optional[OnboardingChecklist]:
        return self.db.query(OnboardingChecklist).filter(OnboardingChecklist.id == checklist_id).first()

    def get_employee_checklists(self, employee_id: int) -> List[OnboardingChecklist]:
        return self.db.query(OnboardingChecklist).filter(
            OnboardingChecklist.employee_id == employee_id
        ).all()

    def update_checklist(self, checklist_id: int, checklist_data: dict) -> Optional[OnboardingChecklist]:
        checklist = self.get_checklist(checklist_id)
        
        if not checklist:
            return None
        
        for key, value in checklist_data.items():
            if value is not None:
                setattr(checklist, key, value)
        
        self.db.commit()
        self.db.refresh(checklist)
        
        return checklist

    def complete_checklist_item(self, checklist_id: int, completed_by: int) -> Optional[OnboardingChecklist]:
        checklist = self.get_checklist(checklist_id)
        
        if not checklist:
            return None
        
        checklist.is_completed = True
        checklist.completed_by = completed_by
        checklist.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(checklist)
        
        return checklist


class HolidayService:
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

    def create_holiday(self, holiday_data: dict, user_id: int = None) -> Holiday:
        db_holiday = Holiday(**holiday_data)
        self.db.add(db_holiday)
        self.db.commit()
        self.db.refresh(db_holiday)
        
        if user_id:
            self._log_audit(user_id, "create", "holiday", db_holiday.id, None, holiday_data)
        
        return db_holiday

    def get_holiday(self, holiday_id: int) -> Optional[Holiday]:
        return self.db.query(Holiday).filter(Holiday.id == holiday_id).first()

    def get_holidays(self, year: Optional[int] = None, skip: int = 0, limit: int = 50) -> tuple[List[Holiday], int]:
        query = self.db.query(Holiday).filter(Holiday.is_active == True)
        
        if year:
            query = query.filter(Holiday.year == year)
        
        total = query.count()
        holidays = query.order_by(Holiday.date).offset(skip).limit(limit).all()
        
        return holidays, total

    def update_holiday(self, holiday_id: int, holiday_data: dict, user_id: int = None) -> Optional[Holiday]:
        holiday = self.get_holiday(holiday_id)
        
        if not holiday:
            return None
        
        old_values = {"name": holiday.name, "date": str(holiday.date), "isOptional": holiday.isOptional}
        for key, value in holiday_data.items():
            if value is not None:
                setattr(holiday, key, value)
        
        self.db.commit()
        self.db.refresh(holiday)
        
        if user_id:
            self._log_audit(user_id, "update", "holiday", holiday_id, old_values, holiday_data)
        
        return holiday

    def delete_holiday(self, holiday_id: int, user_id: int = None) -> bool:
        holiday = self.get_holiday(holiday_id)
        
        if not holiday:
            return False
        
        old_values = {"name": holiday.name, "date": str(holiday.date)}
        holiday.is_active = False
        self.db.commit()
        
        if user_id:
            self._log_audit(user_id, "delete", "holiday", holiday_id, old_values, None)
        
        return True


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    def create_audit_log(self, audit_data: dict) -> AuditLog:
        db_log = AuditLog(**audit_data)
        self.db.add(db_log)
        self.db.commit()
        self.db.refresh(db_log)
        return db_log

    def get_audit_logs(
        self,
        user_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> tuple[List[AuditLog], int]:
        query = self.db.query(AuditLog)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        total = query.count()
        logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
        
        return logs, total
