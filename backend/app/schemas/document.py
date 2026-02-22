from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    AADHAR = "aadhar"
    PAN = "pan"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    VOTER_ID = "voter_id"
    EMPLOYMENT_CONTRACT = "employment_contract"
    EDUCATION_CERTIFICATE = "education_certificate"
    EXPERIENCE_LETTER = "experience_letter"
    PHOTO = "photo"
    SIGNATURE = "signature"
    OTHER = "other"


class DocumentStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class DocumentBase(BaseModel):
    document_type: DocumentType
    document_name: str
    document_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None


class DocumentCreate(DocumentBase):
    employee_id: int
    file_path: Optional[str] = None
    file_url: Optional[str] = None


class DocumentUpdate(DocumentBase):
    document_name: Optional[str] = None
    document_number: Optional[str] = None
    issue_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    status: Optional[DocumentStatus] = None
    remarks: Optional[str] = None


class DocumentResponse(DocumentBase):
    id: int
    employee_id: int
    file_path: Optional[str]
    file_url: Optional[str]
    status: DocumentStatus
    verified_by: Optional[int] = None
    verified_at: Optional[datetime] = None
    remarks: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DocumentVerification(BaseModel):
    status: DocumentStatus
    remarks: Optional[str] = None


class OnboardingChecklistBase(BaseModel):
    task_name: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class OnboardingChecklistCreate(OnboardingChecklistBase):
    employee_id: int


class OnboardingChecklistUpdate(BaseModel):
    task_name: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class OnboardingChecklistResponse(OnboardingChecklistBase):
    id: int
    employee_id: int
    is_completed: bool
    completed_by: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HolidayBase(BaseModel):
    date: datetime
    name: str
    description: Optional[str] = None
    isOptional: bool = False
    year: int


class HolidayCreate(HolidayBase):
    pass


class HolidayUpdate(HolidayBase):
    name: Optional[str] = None
    description: Optional[str] = None
    isOptional: Optional[bool] = None
    is_active: Optional[bool] = None


class HolidayResponse(HolidayBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    old_value: Optional[str]
    new_value: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
