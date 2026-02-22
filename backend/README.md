# PayrollEdge Platform - Backend

## Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. (Optional) Copy `.env.example` to `.env` and customize settings

## Running the Application

Start the development server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Configuration, database, security
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/     # Pydantic schemas
│   └── services/    # Business logic services
├── main.py           # Application entry point
├── requirements.txt  # Python dependencies
└── .env.example      # Environment variables template
```

## Features Implemented

- Employee Management
- Department & Designation Management
- User Authentication & Authorization
- Attendance Tracking
- Leave Management
- Payroll Processing
- Salary Components
- Document Management
- Onboarding Checklists
- Holiday Management
- Audit Logs

## User Roles

- `admin` - Full system access
- `hr` - HR operations
- `department_head` - Team management
- `employee` - Self-service portal
