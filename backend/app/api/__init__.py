from app.api.auth import router as auth_router
from app.api.employee import router as employee_router, department_router, designation_router, users_router
from app.api.employment import router as employment_router
from app.api.attendance import router as attendance_router
from app.api.leave import router as leave_router
from app.api.payroll import router as payroll_router
from app.api.document import router as document_router, onboarding_router, holidays_router, audit_router
from app.api.reports import router as reports_router

__all__ = [
    "auth_router",
    "employee_router",
    "department_router",
    "designation_router",
    "users_router",
    "employment_router",
    "attendance_router",
    "leave_router",
    "payroll_router",
    "document_router",
    "onboarding_router",
    "holidays_router",
    "audit_router",
    "reports_router"
]
