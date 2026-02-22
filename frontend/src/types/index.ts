export type UserRole = 'admin' | 'hr' | 'department_head' | 'employee';
export type EmployeeStatus = 'probation' | 'permanent' | 'contract' | 'resigned' | 'terminated';
export type AttendanceStatus = 'present' | 'absent' | 'late' | 'half_day' | 'leave' | 'wo' | 'holiday';
export type LeaveType = 'casual' | 'sick' | 'paid' | 'unpaid' | 'maternity' | 'paternity' | 'compulsory';
export type LeaveRequestStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type PayrollStatus = 'draft' | 'processed' | 'approved' | 'paid';
export type ComponentType = 'earning' | 'deduction';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  employee_id?: number;
  created_at: string;
}

export interface Department {
  id: number;
  name: string;
  code?: string;
  description?: string;
  manager_id?: number;
  is_active: boolean;
  created_at: string;
}

export interface Designation {
  id: number;
  name: string;
  code?: string;
  description?: string;
  department_id?: number;
  is_active: boolean;
  created_at: string;
}

export interface Employee {
  id: number;
  employee_code?: string;
  first_name: string;
  last_name?: string;
  email?: string;
  phone?: string;
  date_of_birth?: string;
  gender?: string;
  marital_status?: string;
  department_id?: number;
  designation_id?: number;
  date_of_joining?: string;
  status: EmployeeStatus;
  address?: string;
  city?: string;
  state?: string;
  pincode?: string;
  aadhar_number?: string;
  pan_number?: string;
  uan_number?: string;
  esic_number?: string;
  bank_account_number?: string;
  bank_name?: string;
  ifsc_code?: string;
  is_active: boolean;
  created_at: string;
  department?: Department;
  designation?: Designation;
}

export interface Shift {
  id: number;
  name: string;
  code?: string;
  start_time: string;
  end_time: string;
  late_threshold_minutes: number;
  full_day_hours: number;
  is_active: boolean;
  created_at: string;
}

export interface Attendance {
  id: number;
  employee_id: number;
  date: string;
  check_in?: string;
  check_out?: string;
  status: AttendanceStatus;
  late_minutes: number;
  overtime_hours: number;
  shift_id?: number;
  remarks?: string;
  is_approved: boolean;
  approved_by?: number;
  approved_at?: string;
  created_at: string;
}

export interface LeaveRequest {
  id: number;
  employee_id: number;
  leave_type: LeaveType;
  start_date: string;
  end_date: string;
  total_days: number;
  reason?: string;
  status: LeaveRequestStatus;
  approved_by?: number;
  approved_at?: string;
  remarks?: string;
  created_at: string;
}

export interface LeaveBalance {
  id: number;
  employee_id: number;
  leave_type: LeaveType;
  year: number;
  total_days: number;
  used_days: number;
  available_days: number;
}

export interface SalaryComponent {
  id: number;
  employee_id: number;
  component_name: string;
  component_type: ComponentType;
  amount: number;
  effective_from: string;
  effective_to?: string;
  is_taxable: boolean;
  is_active: boolean;
  created_at: string;
}

export interface PayrollRecord {
  id: number;
  employee_id: number;
  month: number;
  year: number;
  basic_salary: number;
  hra: number;
  conveyance: number;
  special_allowance: number;
  overtime_amount: number;
  bonus: number;
  arrears: number;
  other_earnings: number;
  pf_employee: number;
  pf_employer: number;
  esic_employee: number;
  esic_employer: number;
  professional_tax: number;
  tds: number;
  other_deductions: number;
  gross_earnings: number;
  total_deductions: number;
  net_salary: number;
  working_days: number;
  days_present: number;
  days_absent: number;
  overtime_hours: number;
  status: PayrollStatus;
  processed_by?: number;
  processed_at?: string;
  approved_by?: number;
  approved_at?: string;
  payment_date?: string;
  payment_mode?: string;
  remarks?: string;
  created_at: string;
}

export interface PayrollSummary {
  total_employees: number;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  total_pf_employee: number;
  total_pf_employer: number;
  total_esic_employee: number;
  total_esic_employer: number;
  total_professional_tax: number;
  total_tds: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}
