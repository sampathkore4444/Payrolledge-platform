from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class DocumentType(str, enum.Enum):
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


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    document_type = Column(SQLEnum(DocumentType), nullable=False)
    document_name = Column(String(200), nullable=False)
    file_path = Column(String(500))
    file_url = Column(String(500))
    
    document_number = Column(String(100))
    issue_date = Column(DateTime, nullable=True)
    expiry_date = Column(DateTime, nullable=True)
    
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    remarks = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee", back_populates="documents")
    verifier = relationship("User")


class OnboardingChecklist(Base):
    __tablename__ = "onboarding_checklists"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    
    task_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_completed = Column(Boolean, default=False)
    completed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    employee = relationship("Employee")
    completer = relationship("User")


class Holiday(Base):
    __tablename__ = "holidays"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    isOptional = Column(Boolean, default=False)
    
    year = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100))
    entity_id = Column(Integer, nullable=True)
    
    old_value = Column(Text)
    new_value = Column(Text)
    
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User")
