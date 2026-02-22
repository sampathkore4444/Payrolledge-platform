# PayrollEdge Platform - Getting Started Guide

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Project Structure](#project-structure)
4. [Starting the Backend](#starting-the-backend)
5. [Starting the Frontend](#starting-the-frontend)
6. [Accessing the Application](#accessing-the-application)
7. [Default Users & Credentials](#default-users--credentials)
8. [Platform Features](#platform-features)
9. [How Services Connect](#how-services-connect)
10. [Common Issues & Solutions](#common-issues--solutions)

---

## Architecture Overview

PayrollEdge is a **full-stack HR & Payroll application** with:

```
┌─────────────────┐      ┌─────────────────┐
│   React.js     │      │  Python         │
│   Frontend     │◄────►│  FastAPI        │
│   (Port 5173)  │      │  Backend        │
│                │      │  (Port 8000)    │
└─────────────────┘      └─────────────────┘
                                 │
                                 ▼
                          ┌─────────────────┐
                          │    SQLite      │
                          │   Database     │
                          │ (payrolledge.db)│
                          └─────────────────┘
```

- **Frontend:** React + TypeScript + Tailwind CSS + Vite
- **Backend:** Python FastAPI
- **Database:** SQLite (self-hosted, no setup required)
- **Communication:** REST API over HTTP

---

## Prerequisites

Before starting, ensure you have:

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.9+ | For backend |
| Node.js | 16+ | For frontend |
| npm | 8+ | Comes with Node.js |

### Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Install Frontend Dependencies

```bash
cd frontend
npm install
```

---

## Project Structure

```
PayrollEdge Platform/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── auth.py       # Login, register
│   │   │   ├── employee.py   # Employee CRUD
│   │   │   ├── attendance.py # Attendance tracking
│   │   │   ├── leave.py     # Leave management
│   │   │   ├── payroll.py   # Payroll processing
│   │   │   └── reports.py   # Reports & exports
│   │   ├── core/             # Configuration
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── main.py               # Application entry point
│   └── requirements.txt      # Python dependencies
│
├── frontend/                  # React Frontend
│   ├── src/
│   │   ├── pages/           # React pages
│   │   │   ├── Login.tsx    # Admin login
│   │   │   ├── EmployeePortal.tsx  # Self-service portal
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Employees.tsx
│   │   │   └── ...
│   │   ├── services/        # API calls
│   │   └── store/           # State management
│   └── package.json
│
├── SPEC.md                   # Feature specifications
└── README.md                # Project readme
```

---

## Starting the Backend

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Run the Backend Server

**Option A: Using Python directly**
```bash
python main.py
```

**Option B: Using Uvicorn**
```bash
python -m uvicorn main:app --reload --port 8000
```

### Step 3: Verify Backend is Running

Open a new terminal and test:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy","version":"1.0.0","timestamp":"2026-02-22T..."}
```

### Backend Logs Explained

When backend starts, you'll see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

## Starting the Frontend

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Run the Frontend Dev Server

```bash
npm run dev
```

### Step 3: Verify Frontend is Running

Open your browser to:
```
http://localhost:5173
```

---

## Accessing the Application

### Admin Panel (For HR/Management)

| URL | Purpose |
|-----|---------|
| http://localhost:5173/login | Admin login |
| http://localhost:5173 | Dashboard (after login) |

### Employee Self-Service Portal

| URL | Purpose |
|-----|---------|
| http://localhost:5173/employee-portal | Employee login |

---

## Default Users & Credentials

### Admin User (HR/Management)

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |
| Role | Admin |
| Email | admin@payrolledge.com |

### Employee Users

| Employee | Employee Code | Password |
|----------|--------------|----------|
| Ramana Kumar | EMP20260921 | emp1123 |
| Rambabu Kumar | EMP20267751 | emp2123 |
| Rakesh Kumar | EMP20262573 | emp3123 |

> **Note:** Employee password can be reset by admin from the employees page.

---

## Platform Features

### 1. Authentication System

**Backend:** `backend/app/api/auth.py`
- Admin login (username + password)
- Employee login (employee code + password)
- JWT token-based authentication
- Token stored in localStorage

**Flow:**
```
User enters credentials
       │
       ▼
Frontend sends POST /api/auth/login
       │
       ▼
Backend validates & returns JWT token
       │
       ▼
Frontend stores token & redirects to dashboard
```

### 2. Employee Management

**Backend:** `backend/app/api/employee.py`
- Create/Read/Update/Delete employees
- Generate unique employee codes (EMPYYYYNNNN)
- Link employees to departments and designations

**Frontend Pages:**
- `/employees` - Employee list with search
- `/employees/:id` - Employee detail/profile

### 3. Department Management

**Backend:** `backend/app/api/employee.py`
- Create/Update/Delete departments
- View all departments
- Assign employees to departments

**Frontend:** `/departments`

### 4. Attendance Tracking

**Backend:** `backend/app/api/attendance.py`
- Mark daily attendance
- View attendance history
- Attendance summaries

**Frontend:** `/attendance`

### 5. Leave Management

**Backend:** `backend/app/api/leave.py`
- Apply for leave (employees)
- Approve/Reject leave (HR/Admin)
- Track leave balances

**Frontend:**
- Admin: `/leave` - Manage all requests
- Employee Portal: Apply & track leave

### 6. Payroll Processing

**Backend:** `backend/app/api/payroll.py`
- Process monthly payroll
- Calculate:
  - Basic salary
  - Allowances (HRA, Conveyance, Special)
  - Deductions (PF, ESI, PT, TDS)
- Approve payroll records

**Frontend:**
- `/payroll` - View payroll records
- `/payroll/process` - Process new payroll

### 7. Reports & Exports

**Backend:** `backend/app/api/reports.py`

| Report | Endpoint | Format |
|--------|----------|--------|
| Payslip | `/api/reports/payslip/{id}` | PDF |
| Payroll Register | `/api/reports/payroll-register` | JSON |
| PF/ESI Report | `/api/reports/pf-esi-report` | JSON |
| Journal Entries | `/api/reports/journal-entries-csv` | CSV |

**Frontend:** `/reports`

### 8. Employee Self-Service Portal

**Backend:** `backend/app/api/auth.py` + `backend/app/api/employee.py`

Features:
- Login with employee code
- View profile
- View payslips
- Download payslip PDF
- Apply for leave

**Frontend:** `/employee-portal`

### 9. Integration API

**Backend:** `backend/app/api/integration.py`

For connecting with external systems:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/integration/employees/{code}` | GET | Lookup employee |
| `/api/integration/attendance/sync` | POST | Sync biometric attendance |
| `/api/integration/health` | GET | Health check |

### 10. Audit Logs

**Backend:** `backend/app/api/document.py`

Tracks:
- Employee create/update/delete
- Department changes
- Payroll processing
- Leave approvals

**Frontend:** `/audit-logs`

---

## How Services Connect

### Frontend ↔ Backend Communication

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                     │
│                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────┐ │
│  │  Pages      │───►│  API Layer  │───►│  Axios    │ │
│  │  (UI)       │    │  (services) │    │  Client   │ │
│  └─────────────┘    └─────────────┘    └─────┬─────┘ │
│                                               │        │
└───────────────────────────────────────────────┼────────┘
                                                │ HTTP
                                                │ Request
┌───────────────────────────────────────────────┼────────┐
│                    Backend (FastAPI)           │        │
│                                               ▼        │
│  ┌─────────────┐    ┌─────────────┐    ┌────────────┐ │
│  │  API        │◄───│  Services   │◄───│  Models    │ │
│  │  Routes     │    │  (Logic)    │    │  (SQLAlch) │ │
│  └──────┬──────┘    └──────┬──────┘    └─────┬──────┘ │
│         │                   │                  │        │
└─────────┼───────────────────┼──────────────────┼────────┘
          │                   │                  │
          ▼                   ▼                  ▼
    ┌─────────────────────────────────────────────────┐
    │              SQLite Database                    │
    │  (users, employees, departments, attendance,   │
    │   leave_requests, payroll_records, etc.)      │
    └─────────────────────────────────────────────────┘
```

### API Request Flow (Example: Get Employees)

```typescript
// 1. Frontend calls API
const response = await employeeApi.list({ page: 1 });

// 2. Axios adds auth token
// GET /api/employees?page=1
// Headers: Authorization: Bearer <token>

// 3. Backend receives request
// @router.get("/employees/")

// 4. Service processes request
// service.get_employees(skip=0, limit=20)

// 5. Database returns data
// SELECT * FROM employees LIMIT 20

// 6. Response flows back to frontend
```

### Authentication Flow

```
┌──────────────────────────────────────────────────────┐
│                  Login Flow                           │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. User enters credentials on Login page            │
│           │                                          │
│           ▼                                          │
│  2. authStore.login(username, password)             │
│           │                                          │
│           ▼                                          │
│  3. POST /api/auth/login                            │
│           │                                          │
│           ▼                                          │
│  4. Backend validates credentials                   │
│     - Check user exists                             │
│     - Verify password (bcrypt)                       │
│     - Generate JWT token                            │
│           │                                          │
│           ▼                                          │
│  5. Return { access_token, token_type }             │
│           │                                          │
│           ▼                                          │
│  6. Store token in localStorage                     │
│  7. Redirect to Dashboard                           │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

## Common Issues & Solutions

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find and kill the process using port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Issue: "Frontend can't connect to backend"

**Solution:**
1. Ensure backend is running on port 8000
2. Check vite.config.ts has correct proxy:

```typescript
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  },
},
```

### Issue: "Login not working"

**Solution:**
1. Check backend is running: `curl http://localhost:8000/health`
2. Verify credentials are correct
3. Check browser console for errors

### Issue: "Employee portal shows 401 error"

**Solution:**
1. Ensure employee has a linked user account
2. Check employee code and password are correct
3. Verify token is being sent (check browser Network tab)

---

## Development Commands

### Backend

```bash
# Start backend
cd backend
python main.py

# Or with auto-reload
python -m uvicorn main:app --reload

# Run tests (if available)
pytest
```

### Frontend

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## Next Steps

After getting started, you can:

1. **Add more employees** via the admin panel
2. **Configure payroll settings** (salary components, deduction rates)
3. **Process your first payroll** via `/payroll/process`
4. **Set up departments** for your organization
5. **Configure holidays** for the year
6. **Test the employee portal** with employee credentials

---

## Support

For issues or questions:
- Check the browser console (F12)
- Check backend terminal for error logs
- Review API responses in Network tab
