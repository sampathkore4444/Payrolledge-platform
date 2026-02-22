from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.schemas.common import SuccessResponse
from app.services.payroll_service import PayrollService
from app.models.payroll import PayrollRecord
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["Reports"])


def require_roles(*roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


@router.get("/payslip/{record_id}")
def generate_payslip(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.models.user import Employee
    
    record = db.query(PayrollRecord).filter(PayrollRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    employee = db.query(Employee).filter(Employee.id == record.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, spaceAfter=10)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, spaceBefore=10, spaceAfter=5)
    
    elements = []
    
    elements.append(Paragraph("PayrollEdge Platform", title_style))
    elements.append(Paragraph(f"Payslip for {datetime(record.year, record.month, 1).strftime('%B %Y')}", styles['Normal']))
    elements.append(Spacer(1, 10))
    
    emp_data = [
        ['Employee Code:', employee.employee_code or '-', 'Name:', f"{employee.first_name} {employee.last_name or ''}"],
        ['Department:', employee.department.name if employee.department else '-', 'Designation:', employee.designation.name if employee.designation else '-'],
        ['UAN Number:', employee.uan_number or '-', 'ESI Number:', employee.esic_number or '-'],
    ]
    
    emp_table = Table(emp_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
    emp_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 15))
    
    earnings_data = [
        ['Earnings', 'Amount (₹)', 'Deductions', 'Amount (₹)'],
        ['Basic Salary', f"{record.basic_salary:,.2f}", 'PF (Employee)', f"{record.pf_employee:,.2f}"],
        ['HRA', f"{record.hra:,.2f}", 'ESIC (Employee)', f"{record.esic_employee:,.2f}"],
        ['Conveyance', f"{record.conveyance:,.2f}", 'Professional Tax', f"{record.professional_tax:,.2f}"],
        ['Special Allowance', f"{record.special_allowance:,.2f}", 'TDS', f"{record.tds:,.2f}"],
        ['Overtime', f"{record.overtime_amount:,.2f}", 'Other Deductions', f"{record.other_deductions:,.2f}"],
        ['Bonus', f"{record.bonus:,.2f}", '', ''],
        ['Arrears', f"{record.arrears:,.2f}", '', ''],
    ]
    
    earnings_table = Table(earnings_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch, 1.5*inch])
    earnings_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]))
    elements.append(earnings_table)
    elements.append(Spacer(1, 15))
    
    totals_data = [
        ['Gross Earnings', f"₹{record.gross_earnings:,.2f}"],
        ['Total Deductions', f"₹{record.total_deductions:,.2f}"],
        ['Net Salary', f"₹{record.net_salary:,.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=[3*inch, 2*inch])
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("<b>Attendance Details</b>", heading_style))
    attendance_data = [
        ['Working Days', str(int(record.working_days))],
        ['Days Present', str(int(record.days_present))],
        ['Days Absent', str(int(record.days_absent))],
        ['Overtime Hours', f"{record.overtime_hours}"],
    ]
    
    att_table = Table(attendance_data, colWidths=[2*inch, 1.5*inch])
    att_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(att_table)
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("<b>Statutory Contributions</b>", heading_style))
    statutory_data = [
        ['PF (Employer)', f"₹{record.pf_employer:,.2f}", 'ESIC (Employer)', f"₹{record.esic_employer:,.2f}"],
    ]
    
    stat_table = Table(statutory_data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch, 1.5*inch])
    stat_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ]))
    elements.append(stat_table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    
    doc.build(elements)
    
    buffer.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=payslip_{employee.employee_code}_{record.month}_{record.year}.pdf"}
    )


@router.get("/attendance-report")
def attendance_report(
    month: int,
    year: int,
    department_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.models.user import Employee
    from app.models.attendance import Attendance, AttendanceStatus
    from datetime import datetime
    
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)
    
    query = db.query(Employee).filter(Employee.is_active == True)
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    employees = query.all()
    
    report = []
    for emp in employees:
        attendances = db.query(Attendance).filter(
            Attendance.employee_id == emp.id,
            Attendance.date >= start_date,
            Attendance.date < end_date
        ).all()
        
        present = sum(1 for a in attendances if a.status == AttendanceStatus.PRESENT)
        absent = sum(1 for a in attendances if a.status == AttendanceStatus.ABSENT)
        late = sum(1 for a in attendances if a.status == AttendanceStatus.LATE)
        half_day = sum(1 for a in attendances if a.status == AttendanceStatus.HALF_DAY)
        leaves = sum(1 for a in attendances if a.status == AttendanceStatus.LEAVE)
        overtime = sum((a.overtime_hours or 0) for a in attendances)
        
        report.append({
            "employee_code": emp.employee_code,
            "employee_name": f"{emp.first_name} {emp.last_name or ''}",
            "department": emp.department.name if emp.department else '-',
            "present": present,
            "absent": absent,
            "late": late,
            "half_day": half_day,
            "leaves": leaves,
            "total_days": len(attendances),
            "overtime_hours": overtime
        })
    
    return {"month": month, "year": year, "report": report}


@router.get("/payroll-register")
def payroll_register(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year
    ).all()
    
    from app.models.user import Employee
    
    register = []
    for record in records:
        employee = db.query(Employee).filter(Employee.id == record.employee_id).first()
        if employee:
            register.append({
                "employee_code": employee.employee_code,
                "employee_name": f"{employee.first_name} {employee.last_name or ''}",
                "department": employee.department.name if employee.department else '-',
                "basic_salary": record.basic_salary,
                "gross_earnings": record.gross_earnings,
                "pf_employee": record.pf_employee,
                "pf_employer": record.pf_employer,
                "esic_employee": record.esic_employee,
                "esic_employer": record.esic_employer,
                "professional_tax": record.professional_tax,
                "tds": record.tds,
                "total_deductions": record.total_deductions,
                "net_salary": record.net_salary,
                "status": record.status
            })
    
    return {"month": month, "year": year, "register": register}


@router.get("/pf-esi-report")
def pf_esi_report(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year
    ).all()
    
    from app.models.user import Employee
    
    pf_data = []
    esic_data = []
    
    for record in records:
        employee = db.query(Employee).filter(Employee.id == record.employee_id).first()
        if not employee:
            continue
        
        if employee.uan_number:
            pf_data.append({
                "uan": employee.uan_number,
                "name": f"{employee.first_name} {employee.last_name or ''}",
                "wages": record.basic_salary,
                "epf": record.pf_employee,
                "eps": record.pf_employer,
                "refund": 0
            })
        
        if employee.esic_number:
            esic_data.append({
                "ip_number": employee.esic_number,
                "name": f"{employee.first_name} {employee.last_name or ''}",
                "wages": record.gross_earnings,
                "employee_contribution": record.esic_employee,
                "employer_contribution": record.esic_employer
            })
    
    return {
        "month": month,
        "year": year,
        "pf_total": sum(r['epf'] + r['eps'] for r in pf_data),
        "esic_total": sum(r['employee_contribution'] + r['employer_contribution'] for r in esic_data),
        "pf_data": pf_data,
        "esic_data": esic_data
    }


@router.get("/form16/{employee_id}")
def generate_form16(
    employee_id: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.models.user import Employee
    
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    records = db.query(PayrollRecord).filter(
        PayrollRecord.employee_id == employee_id,
        PayrollRecord.year == year,
        PayrollRecord.status.in_(['approved', 'paid'])
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No payroll records found for this year")
    
    total_gross = sum(r.gross_earnings for r in records)
    total_tds = sum(r.tds for r in records)
    total_pf = sum(r.pf_employee for r in records)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("FORM 16", styles['Heading1']))
    elements.append(Paragraph(f"Certificate under Section 203 of the Income-tax Act, 1961 for tax deducted at source", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    employer_details = [
        ['Employer Name:', 'PayrollEdge Platform'],
        ['Employer Address:', 'Jeedimetla, Hyderabad - 500055'],
        ['Employee Name:', f"{employee.first_name} {employee.last_name or ''}"],
        ['Employee PAN:', employee.pan_number or 'N/A'],
        ['Employee Designation:', employee.designation.name if employee.designation else 'N/A'],
        ['Financial Year:', f"{year}-{year + 1}"],
    ]
    
    emp_table = Table(employer_details, colWidths=[2*inch, 4*inch])
    emp_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 20))
    
    salary_data = [
        ['Month', 'Gross Salary (₹)', 'TDS (₹)', 'PF (₹)'],
    ]
    month_names = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    
    for i, record in enumerate(records[:12]):
        salary_data.append([
            month_names[record.month - 1],
            f"{record.gross_earnings:,.2f}",
            f"{record.tds:,.2f}",
            f"{record.pf_employee:,.2f}"
        ])
    
    salary_data.append(['Total', f"{total_gross:,.2f}", f"{total_tds:,.2f}", f"{total_pf:,.2f}"])
    
    salary_table = Table(salary_data, colWidths=[2*inch, 2*inch, 2*inch, 2*inch])
    salary_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    elements.append(salary_table)
    elements.append(Spacer(1, 30))
    
    elements.append(Paragraph("This is a computer-generated certificate.", styles['Normal']))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    
    doc.build(elements)
    buffer.seek(0)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Form16_{employee.employee_code}_{year}.pdf"}
    )


@router.post("/send-payslip/{record_id}")
def send_payslip_email(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    from app.models.user import Employee
    from app.core.config import settings
    
    record = db.query(PayrollRecord).filter(PayrollRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    
    employee = db.query(Employee).filter(Employee.id == record.employee_id).first()
    if not employee or not employee.email:
        raise HTTPException(status_code=400, detail="Employee email not found")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        from email.mime.base import MIMEBase
        from email import encoders
        
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME if hasattr(settings, 'SMTP_USERNAME') else 'noreply@payrolledge.com'
        msg['To'] = employee.email
        msg['Subject'] = f" Payslip for {datetime(record.year, record.month, 1).strftime('%B %Y')}"
        
        body = f"""Dear {employee.first_name},

Please find attached your payslip for {datetime(record.year, record.month, 1).strftime('%B %Y')}.

Net Salary: ₹{record.net_salary:,.2f}

Login to PayrollEdge Platform to view detailed payslip.

Best regards,
HR Team
PayrollEdge Platform"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        return {"message": f"Payslip email sent to {employee.email}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/bulk-send-payslips")
def bulk_send_payslips(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year,
        PayrollRecord.status.in_(['approved', 'paid'])
    ).all()
    
    from app.models.user import Employee
    
    sent_count = 0
    failed_count = 0
    
    for record in records:
        employee = db.query(Employee).filter(Employee.id == record.employee_id).first()
        if employee and employee.email:
            sent_count += 1
    
    return {
        "message": f"Bulk payslip processing initiated",
        "total_records": len(records),
        "emails_to_send": sent_count,
        "note": "Email sending requires SMTP configuration"
    }


@router.get("/journal-entries")
def generate_journal_entries(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year,
        PayrollRecord.status.in_(['approved', 'paid'])
    ).all()
    
    from app.models.user import Employee
    
    entries = []
    total_debit = 0
    total_credit = 0
    
    total_gross = sum(r.gross_earnings for r in records)
    total_pf_emp = sum(r.pf_employee for r in records)
    total_pf_er = sum(r.pf_employer for r in records)
    total_esic_emp = sum(r.esic_employee for r in records)
    total_esic_er = sum(r.esic_employer for r in records)
    total_pt = sum(r.professional_tax for r in records)
    total_tds = sum(r.tds for r in records)
    total_net = sum(r.net_salary for r in records)
    
    entries.append({
        "date": f"{year}-{month:02d}-01",
        "voucher_type": "Payment",
        "voucher_no": f"SLR/{month:02d}/{year}",
        "account": "Salary Expense - Gross",
        "debit": round(total_gross, 2),
        "credit": 0,
        "narration": f"Salary expense for {datetime(year, month, 1).strftime('%B %Y')}"
    })
    total_debit += total_gross
    
    entries.append({
        "date": f"{year}-{month:02d}-01",
        "voucher_type": "Payment",
        "voucher_no": f"SLR/{month:02d}/{year}",
        "account": "PF Expense - Employer",
        "debit": round(total_pf_er, 2),
        "credit": 0,
        "narration": f"PF employer contribution for {datetime(year, month, 1).strftime('%B %Y')}"
    })
    total_debit += total_pf_er
    
    entries.append({
        "date": f"{year}-{month:02d}-01",
        "voucher_type": "Payment",
        "voucher_no": f"SLR/{month:02d}/{year}",
        "account": "ESI Expense - Employer",
        "debit": round(total_esic_er, 2),
        "credit": 0,
        "narration": f"ESI employer contribution for {datetime(year, month, 1).strftime('%B %Y')}"
    })
    total_debit += total_esic_er
    
    entries.append({
        "date": f"{year}-{month:02d}-01",
        "voucher_type": "Payment",
        "voucher_no": f"SLR/{month:02d}/{year}",
        "account": "Bank/Cash",
        "debit": 0,
        "credit": round(total_net, 2),
        "narration": f"Net salary payment for {datetime(year, month, 1).strftime('%B %Y')}"
    })
    total_credit += total_net
    
    if total_pf_emp > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"SLR/{month:02d}/{year}",
            "account": "PF Payable - Employee",
            "debit": 0,
            "credit": round(total_pf_emp, 2),
            "narration": f"PF deduction from employees for {datetime(year, month, 1).strftime('%B %Y')}"
        })
        total_credit += total_pf_emp
    
    if total_pf_er > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"SLR/{month:02d}/{year}",
            "account": "PF Payable - Employer",
            "debit": 0,
            "credit": round(total_pf_er, 2),
            "narration": f"PF employer contribution for {datetime(year, month, 1).strftime('%B %Y')}"
        })
        total_credit += total_pf_er
    
    if total_esic_emp > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"SLR/{month:02d}/{year}",
            "account": "ESI Payable - Employee",
            "debit": 0,
            "credit": round(total_esic_emp, 2),
            "narration": f"ESI deduction from employees for {datetime(year, month, 1).strftime('%B %Y')}"
        })
        total_credit += total_esic_emp
    
    if total_esic_er > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"SLR/{month:02d}/{year}",
            "account": "ESI Payable - Employer",
            "debit": 0,
            "credit": round(total_esic_er, 2),
            "narration": f"ESI employer contribution for {datetime(year, month, 1).strftime('%B %Y')}"
        })
        total_credit += total_esic_er
    
    if total_pt > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"SLR/{month:02d}/{year}",
            "account": "Professional Tax Payable",
            "debit": 0,
            "credit": round(total_pt, 2),
            "narration": f"Professional Tax for {datetime(year, month, 1).strftime('%B %Y')}"
        })
        total_credit += total_pt
    
    if total_tds > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"SLR/{month:02d}/{year}",
            "account": "TDS Payable",
            "debit": 0,
            "credit": round(total_tds, 2),
            "narration": f"TDS deducted for {datetime(year, month, 1).strftime('%B %Y')}"
        })
        total_credit += total_tds
    
    return {
        "month": month,
        "year": year,
        "voucher_date": f"{year}-{month:02d}-01",
        "voucher_number": f"SLR/{month:02d}/{year}",
        "entries": entries,
        "totals": {
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "balanced": abs(total_debit - total_credit) < 0.01
        }
    }


@router.get("/journal-entries-csv")
def generate_journal_entries_csv(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year,
        PayrollRecord.status.in_(['approved', 'paid'])
    ).all()
    
    total_gross = sum(r.gross_earnings for r in records)
    total_pf_emp = sum(r.pf_employee for r in records)
    total_pf_er = sum(r.pf_employer for r in records)
    total_esic_emp = sum(r.esic_employee for r in records)
    total_esic_er = sum(r.esic_employer for r in records)
    total_pt = sum(r.professional_tax for r in records)
    total_tds = sum(r.tds for r in records)
    total_net = sum(r.net_salary for r in records)
    
    csv_lines = [
        "Date,Voucher Type,Voucher No,Account,Debit,Credit,Narration"
    ]
    
    def add_entry(date, voucher_type, voucher_no, account, debit, credit, narration):
        csv_lines.append(f'{date},{voucher_type},{voucher_no},"{account}",{debit:.2f},{credit:.2f},"{narration}"')
    
    add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "Salary Expense - Gross", total_gross, 0, f"Salary expense for {datetime(year, month, 1).strftime('%B %Y')}")
    add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "PF Expense - Employer", total_pf_er, 0, f"PF employer contribution")
    add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "ESI Expense - Employer", total_esic_er, 0, f"ESI employer contribution")
    add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "Bank/Cash", 0, total_net, f"Net salary payment")
    if total_pf_emp > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "PF Payable - Employee", 0, total_pf_emp, f"PF employee deduction")
    if total_pf_er > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "PF Payable - Employer", 0, total_pf_er, f"PF employer contribution")
    if total_esic_emp > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "ESI Payable - Employee", 0, total_esic_emp, f"ESI employee deduction")
    if total_esic_er > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "ESI Payable - Employer", 0, total_esic_er, f"ESI employer contribution")
    if total_pt > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "Professional Tax Payable", 0, total_pt, f"Professional Tax")
    if total_tds > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"SLR/{month:02d}/{year}", "TDS Payable", 0, total_tds, f"TDS deduction")
    
    csv_content = "\n".join(csv_lines)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=journal_entries_{month}_{year}.csv"}
    )


@router.post("/mark-paid")
def mark_payroll_paid(
    month: int,
    year: int,
    payment_date: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.HR))
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year,
        PayrollRecord.status == 'approved'
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No approved payroll records found")
    
    payment_date = payment_date or f"{year}-{month:02d}-28"
    
    total_gross = sum(r.gross_earnings for r in records)
    total_pf_emp = sum(r.pf_employee for r in records)
    total_pf_er = sum(r.pf_employer for r in records)
    total_esic_emp = sum(r.esic_employee for r in records)
    total_esic_er = sum(r.esic_employer for r in records)
    total_pt = sum(r.professional_tax for r in records)
    total_tds = sum(r.tds for r in records)
    total_net = sum(r.net_salary for r in records)
    total_other_deductions = sum(r.other_deductions for r in records)
    
    for record in records:
        record.status = 'paid'
        record.payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date() if payment_date else None
    
    db.commit()
    
    return {
        "message": f"Payroll marked as paid for {datetime(year, month, 1).strftime('%B %Y')}",
        "payment_date": payment_date,
        "total_records": len(records),
        "total_net_paid": round(total_net, 2),
        "payment_entries": {
            "net_salary": round(total_net, 2),
            "pf_employee": round(total_pf_emp, 2),
            "pf_employer": round(total_pf_er, 2),
            "esic_employee": round(total_esic_emp, 2),
            "esic_employer": round(total_esic_er, 2),
            "professional_tax": round(total_pt, 2),
            "tds": round(total_tds, 2),
            "other_deductions": round(total_other_deductions, 2)
        }
    }


@router.get("/payment-entries")
def generate_payment_entries(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year,
        PayrollRecord.status == 'paid'
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No paid payroll records found for this period")
    
    total_gross = sum(r.gross_earnings for r in records)
    total_pf_emp = sum(r.pf_employee for r in records)
    total_pf_er = sum(r.pf_employer for r in records)
    total_esic_emp = sum(r.esic_employee for r in records)
    total_esic_er = sum(r.esic_employer for r in records)
    total_pt = sum(r.professional_tax for r in records)
    total_tds = sum(r.tds for r in records)
    total_net = sum(r.net_salary for r in records)
    total_other = sum(r.other_deductions for r in records)
    
    entries = []
    total_debit = 0
    total_credit = 0
    
    if total_net > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"PMT/{month:02d}/{year}",
            "account": "Salary Payable - Net",
            "debit": round(total_net, 2),
            "credit": 0,
            "narration": f"Net salary payment for {datetime(year, month, 1).strftime('%B %Y')}"
        })
        total_debit += total_net
    
    if total_pf_emp > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"PMT/{month:02d}/{year}",
            "account": "PF Payable - Employee",
            "debit": round(total_pf_emp, 2),
            "credit": 0,
            "narration": f"PF remittance for employees"
        })
        total_debit += total_pf_emp
    
    if total_pf_er > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"PMT/{month:02d}/{year}",
            "account": "PF Payable - Employer",
            "debit": round(total_pf_er, 2),
            "credit": 0,
            "narration": f"PF employer contribution remittance"
        })
        total_debit += total_pf_er
    
    if total_esic_emp > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"PMT/{month:02d}/{year}",
            "account": "ESI Payable - Employee",
            "debit": round(total_esic_emp, 2),
            "credit": 0,
            "narration": f"ESI remittance for employees"
        })
        total_debit += total_esic_emp
    
    if total_esic_er > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"PMT/{month:02d}/{year}",
            "account": "ESI Payable - Employer",
            "debit": round(total_esic_er, 2),
            "credit": 0,
            "narration": f"ESI employer contribution remittance"
        })
        total_debit += total_esic_er
    
    if total_pt > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"PMT/{month:02d}/{year}",
            "account": "Professional Tax Payable",
            "debit": round(total_pt, 2),
            "credit": 0,
            "narration": f"Professional Tax payment"
        })
        total_debit += total_pt
    
    if total_tds > 0:
        entries.append({
            "date": f"{year}-{month:02d}-01",
            "voucher_type": "Payment",
            "voucher_no": f"PMT/{month:02d}/{year}",
            "account": "TDS Payable",
            "debit": round(total_tds, 2),
            "credit": 0,
            "narration": f"TDS remittance"
        })
        total_debit += total_tds
    
    entries.append({
        "date": f"{year}-{month:02d}-01",
        "voucher_type": "Payment",
        "voucher_no": f"PMT/{month:02d}/{year}",
        "account": "Bank",
        "debit": 0,
        "credit": round(total_debit, 2),
        "narration": f"Total payment via bank for {datetime(year, month, 1).strftime('%B %Y')}"
    })
    total_credit += total_debit
    
    return {
        "month": month,
        "year": year,
        "voucher_date": f"{year}-{month:02d}-01",
        "voucher_number": f"PMT/{month:02d}/{year}",
        "entries": entries,
        "totals": {
            "total_debit": round(total_debit, 2),
            "total_credit": round(total_credit, 2),
            "balanced": abs(total_debit - total_credit) < 0.01
        }
    }


@router.get("/payment-entries-csv")
def generate_payment_entries_csv(
    month: int,
    year: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    records = db.query(PayrollRecord).filter(
        PayrollRecord.month == month,
        PayrollRecord.year == year,
        PayrollRecord.status == 'paid'
    ).all()
    
    if not records:
        raise HTTPException(status_code=404, detail="No paid payroll records found")
    
    total_gross = sum(r.gross_earnings for r in records)
    total_pf_emp = sum(r.pf_employee for r in records)
    total_pf_er = sum(r.pf_employer for r in records)
    total_esic_emp = sum(r.esic_employee for r in records)
    total_esic_er = sum(r.esic_employer for r in records)
    total_pt = sum(r.professional_tax for r in records)
    total_tds = sum(r.tds for r in records)
    total_net = sum(r.net_salary for r in records)
    
    csv_lines = ["Date,Voucher Type,Voucher No,Account,Debit,Credit,Narration"]
    
    def add_entry(date, voucher_type, voucher_no, account, debit, credit, narration):
        csv_lines.append(f'{date},{voucher_type},{voucher_no},"{account}",{debit:.2f},{credit:.2f},"{narration}"')
    
    if total_net > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "Salary Payable - Net", total_net, 0, "Net salary payment")
    if total_pf_emp > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "PF Payable - Employee", total_pf_emp, 0, "PF employee remittance")
    if total_pf_er > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "PF Payable - Employer", total_pf_er, 0, "PF employer remittance")
    if total_esic_emp > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "ESI Payable - Employee", total_esic_emp, 0, "ESI employee remittance")
    if total_esic_er > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "ESI Payable - Employer", total_esic_er, 0, "ESI employer remittance")
    if total_pt > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "Professional Tax Payable", total_pt, 0, "Professional Tax payment")
    if total_tds > 0:
        add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "TDS Payable", total_tds, 0, "TDS remittance")
    
    total_payment = total_net + total_pf_emp + total_pf_er + total_esic_emp + total_esic_er + total_pt + total_tds
    add_entry(f"{year}-{month:02d}-01", "Payment", f"PMT/{month:02d}/{year}", "Bank", 0, total_payment, "Total bank payment")
    
    csv_content = "\n".join(csv_lines)
    
    from fastapi.responses import StreamingResponse
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=payment_entries_{month}_{year}.csv"}
    )
