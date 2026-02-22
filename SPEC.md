# PayrollEdge Platform - Specification Document

## 1. Project Overview

**Project Name:** PayrollEdge Platform  
**Project Type:** HR Management & Payroll Processing Web Application  
**Target Users:** Factory owners, HR managers, department heads, and employees in industrial areas (Jeedimetla, Shapoor Nagar)  
**Tech Stack:**  
- Frontend: React.js + TypeScript + Tailwind CSS + Vite
- Backend: Python FastAPI
- Database: SQLite (self-hosted)

---

## 2. Core Features

### 2.1 Employee Management
- Employee profiles with personal details, role, department, contact info
- Document management: ID proofs, contracts, certificates
- Job history and role changes tracking
- Employee code generation (EMPYYYYNNNN format)

### 2.2 Payroll Processing
- Salary calculation: Basic + allowances + deductions
- Statutory compliance: PF, ESI, Professional Tax, TDS
- Automated payslip generation (PDF)
- Salary revisions, bonuses, and arrears handling
- Journal entries export for Tally/QuickBooks integration
- Payment entries export

### 2.3 Attendance & Leave Management
- Manual attendance tracking
- Leave tracking: Casual, sick, earned, unpaid leaves
- Leave balance management
- Leave request workflow (apply → approve/reject)
- Leave request notifications
- Holiday calendar management

### 2.4 Employee Onboarding
- Digital onboarding forms
- Document upload and verification
- Employee self-registration

---

## 3. Advanced Features

### 3.1 Reports & Analytics
- Monthly payroll summaries
- Compliance reports for PF, ESI, PT
- Attendance reports
- Payroll register
- PF/ESI reports
- Journal entries export (CSV)
- Audit logs

### 3.2 Tax Management
- Automated TDS calculation
- Form 16 generation

### 3.3 Employee Self-Service Portal (NEW)
- Employee login with employee code + password
- View profile information
- View and download payslips (PDF)
- Apply for leave requests
- Track leave request status

### 3.4 Role-Based Access Control
- Admin, HR, Department Head, Employee roles
- Permission-based route protection

### 3.5 Integration API (NEW)
- Public endpoint to lookup employee by code
- Attendance sync endpoint for biometric devices
- Health check endpoint

### 3.6 Audit Logging (NEW)
- Track create/update/delete actions
- Record old and new values
- User attribution for all changes

---

## 4. Technical Features

### 4.1 Security
- JWT-based authentication
- Password hashing with bcrypt
- Role-based access control
- Audit logs for compliance

### 4.2 Database
- SQLite for self-hosted deployment
- SQLAlchemy ORM
- Pydantic for data validation

### 4.3 API
- RESTful API design
- OpenAPI/Swagger documentation
- CORS enabled

---

## 5. User Roles

| Role | Description |
|------|-------------|
| Admin | Full system access, settings, user management |
| HR | Employee management, payroll processing, reports |
| Department Head | Team attendance, leave approvals |
| Employee | Self-service portal, view payslips, apply leave |

---

## 6. Database Entities

- **Users** - System users with roles
- **Employees** - Employee profiles with personal details
- **Departments** - Organizational departments
- **Designations** - Job titles/positions
- **Attendance** - Daily attendance records
- **Leave Requests** - Leave applications
- **Leave Balances** - Employee leave entitlements
- **Payroll Records** - Monthly payroll entries
- **Payroll Settings** - Salary components and deductions
- **Documents** - Employee documents
- **Holidays** - Company holiday calendar
- **Audit Logs** - System activity tracking

---

## 7. API Modules (Backend)

| Endpoint | Description |
|----------|-------------|
| `/api/auth` | Authentication, login, register, employee login |
| `/api/employees` | Employee CRUD operations |
| `/api/departments` | Department management |
| `/api/designations` | Designation management |
| `/api/attendance` | Attendance tracking |
| `/api/leave` | Leave requests and balances |
| `/api/payroll` | Payroll processing and records |
| `/api/reports` | Payslips, journal entries, compliance reports |
| `/api/documents` | Document management |
| `/api/holidays` | Holiday calendar |
| `/api/audit-logs` | System audit trail |
| `/api/integration` | External system integration endpoints |

---

## 8. Frontend Pages

| Page | Description |
|------|-------------|
| `/login` | Admin/HR login |
| `/employee-portal` | Employee self-service portal |
| `/` | Dashboard |
| `/employees` | Employee list with search |
| `/employees/:id` | Employee detail/profile |
| `/attendance` | Attendance management |
| `/leave` | Leave request management |
| `/payroll` | Payroll records list |
| `/payroll/process` | Payroll processing wizard |
| `/departments` | Department management |
| `/holidays` | Holiday calendar |
| `/documents` | Document management |
| `/reports` | Reports and exports |
| `/audit-logs` | System audit trail |
| `/settings` | System settings |

---

## 9. Employee Portal Features

- **Login:** Employee code + password
- **Profile:** View personal details, department, designation
- **Payslips:** View monthly salary details, download PDF
- **Leave:** Apply for leave, track status

---

## 10. Payroll Features

- **Salary Components:**
  - Basic salary
  - HRA (House Rent Allowance)
  - Conveyance allowance
  - Special allowance
  - Overtime

- **Deductions:**
  - PF (Provident Fund)
  - ESI (Employee State Insurance)
  - Professional Tax
  - TDS (Tax Deducted at Source)

- **Exports:**
  - Journal entries (CSV)
  - Payment entries (CSV)
  - Payslips (PDF)

---

## 11. Deployment

- **Backend:** Python FastAPI on port 8000
- **Frontend:** React + Vite on port 5173 (development)
- **Database:** SQLite (payrolledge.db)
- **Architecture:** Monolithic (single port for backend)
