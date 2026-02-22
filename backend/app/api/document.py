from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentVerification,
    OnboardingChecklistCreate, OnboardingChecklistUpdate, OnboardingChecklistResponse,
    HolidayCreate, HolidayUpdate, HolidayResponse
)
from app.schemas.common import PaginatedResponse
from app.services.document_service import DocumentService, OnboardingService, HolidayService, AuditService
from typing import Optional

router = APIRouter(prefix="/documents", tags=["Documents"])


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document_data: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = DocumentService(db)
    document = service.create_document(document_data)
    return document


@router.get("/employee/{employee_id}", response_model=list[DocumentResponse])
def get_employee_documents(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = DocumentService(db)
    documents = service.get_employee_documents(employee_id)
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = DocumentService(db)
    document = service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = DocumentService(db)
    document = service.update_document(document_id, document_data)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.post("/{document_id}/verify", response_model=DocumentResponse)
def verify_document(
    document_id: int,
    verification_data: DocumentVerification,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = DocumentService(db)
    document = service.verify_document(
        document_id,
        current_user.id,
        verification_data.status,
        verification_data.remarks
    )
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = DocumentService(db)
    success = service.delete_document(document_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}


onboarding_router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


@onboarding_router.post("/checklist", response_model=OnboardingChecklistResponse, status_code=status.HTTP_201_CREATED)
def create_checklist_item(
    checklist_data: OnboardingChecklistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = OnboardingService(db)
    checklist = service.create_checklist(checklist_data.model_dump())
    return checklist


@onboarding_router.get("/checklist/employee/{employee_id}", response_model=list[OnboardingChecklistResponse])
def get_employee_checklists(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = OnboardingService(db)
    checklists = service.get_employee_checklists(employee_id)
    return checklists


@onboarding_router.put("/checklist/{checklist_id}", response_model=OnboardingChecklistResponse)
def update_checklist_item(
    checklist_id: int,
    checklist_data: OnboardingChecklistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = OnboardingService(db)
    checklist = service.update_checklist(checklist_id, checklist_data.model_dump(exclude_unset=True))
    
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    return checklist


@onboarding_router.post("/checklist/{checklist_id}/complete", response_model=OnboardingChecklistResponse)
def complete_checklist_item(
    checklist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = OnboardingService(db)
    checklist = service.complete_checklist_item(checklist_id, current_user.id)
    
    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    
    return checklist


holidays_router = APIRouter(prefix="/holidays", tags=["Holidays"])


@holidays_router.post("/", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
def create_holiday(
    holiday_data: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = HolidayService(db)
    holiday = service.create_holiday(holiday_data.model_dump(), current_user.id)
    return holiday


@holidays_router.get("/", response_model=list[HolidayResponse])
def list_holidays(
    year: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = HolidayService(db)
    holidays, _ = service.get_holidays(year=year, skip=skip, limit=limit)
    return holidays


@holidays_router.get("/{holiday_id}", response_model=HolidayResponse)
def get_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    service = HolidayService(db)
    holiday = service.get_holiday(holiday_id)
    
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    return holiday


@holidays_router.put("/{holiday_id}", response_model=HolidayResponse)
def update_holiday(
    holiday_id: int,
    holiday_data: HolidayUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = HolidayService(db)
    holiday = service.update_holiday(holiday_id, holiday_data.model_dump(exclude_unset=True), current_user.id)
    
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    return holiday


@holidays_router.delete("/{holiday_id}")
def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    service = HolidayService(db)
    success = service.delete_holiday(holiday_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Holiday not found")
    
    return {"message": "Holiday deleted successfully"}


audit_router = APIRouter(prefix="/audit", tags=["Audit Logs"])


@audit_router.get("/", response_model=PaginatedResponse[dict])
def list_audit_logs(
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    service = AuditService(db)
    skip = (page - 1) * page_size
    logs, total = service.get_audit_logs(
        user_id=user_id,
        entity_type=entity_type,
        skip=skip,
        limit=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": logs,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }
