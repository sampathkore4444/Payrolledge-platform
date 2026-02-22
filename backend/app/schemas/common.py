from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List
from datetime import datetime


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: datetime
