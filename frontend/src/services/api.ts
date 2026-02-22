import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getErrorMessage = (error: any): string => {
  if (!error.response?.data) return 'An error occurred';
  
  const data = error.response.data;
  
  if (typeof data.detail === 'string') {
    return data.detail;
  }
  
  if (Array.isArray(data.detail)) {
    return data.detail.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
  }
  
  if (data.detail?.msg) {
    return data.detail.msg;
  }
  
  return JSON.stringify(data);
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  login: (data: { username: string; password: string }) =>
    api.post('/auth/login', data),
  register: (data: { email: string; username: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  me: () => api.get('/auth/me'),
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
};

export const employeeApi = {
  list: (params?: { page?: number; page_size?: number; search?: string; department_id?: number }) =>
    api.get('/employees/', { params }),
  get: (id: number) => api.get(`/employees/${id}`),
  create: (data: any) => api.post('/employees/', data),
  update: (id: number, data: any) => api.put(`/employees/${id}`, data),
  delete: (id: number) => api.delete(`/employees/${id}`),
};

export const departmentApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/departments/', { params }),
  get: (id: number) => api.get(`/departments/${id}`),
  create: (data: any) => api.post('/departments/', data),
  update: (id: number, data: any) => api.put(`/departments/${id}`, data),
  delete: (id: number) => api.delete(`/departments/${id}`),
};

export const designationApi = {
  list: (params?: { department_id?: number; skip?: number; limit?: number }) =>
    api.get('/designations/', { params }),
  get: (id: number) => api.get(`/designations/${id}`),
  create: (data: any) => api.post('/designations/', data),
  update: (id: number, data: any) => api.put(`/designations/${id}`, data),
  delete: (id: number) => api.delete(`/designations/${id}`),
};

export const attendanceApi = {
  list: (params?: { employee_id?: number; start_date?: string; end_date?: string; page?: number; page_size?: number }) =>
    api.get('/attendance/', { params }),
  get: (id: number) => api.get(`/attendance/${id}`),
  create: (data: any) => api.post('/attendance/', data),
  bulk: (data: any) => api.post('/attendance/bulk', data),
  update: (id: number, data: any) => api.put(`/attendance/${id}`, data),
  summary: (employeeId: number, month: number, year: number) =>
    api.get(`/attendance/summary/${employeeId}`, { params: { month, year } }),
};

export const shiftApi = {
  list: (params?: { skip?: number; limit?: number }) =>
    api.get('/attendance/shifts', { params }),
  get: (id: number) => api.get(`/attendance/shifts/${id}`),
  create: (data: any) => api.post('/attendance/shifts', data),
  update: (id: number, data: any) => api.put(`/attendance/shifts/${id}`, data),
};

export const leaveApi = {
  listRequests: (params?: { employee_id?: number; status?: string; page?: number; page_size?: number }) =>
    api.get('/leave/requests', { params }),
  getRequest: (id: number) => api.get(`/leave/requests/${id}`),
  createRequest: (data: any) => api.post('/leave/requests', data),
  updateRequest: (id: number, data: any) => api.put(`/leave/requests/${id}`, data),
  approveRequest: (id: number, data: { status: string; remarks?: string }) =>
    api.post(`/leave/requests/${id}/approve`, data),
  getBalances: (employeeId: number, year: number) =>
    api.get(`/leave/balances/${employeeId}`, { params: { year } }),
  createBalance: (data: any) => api.post('/leave/balances', data),
  updateBalance: (id: number, data: any) => api.put(`/leave/balances/${id}`, data),
};

export const payrollApi = {
  listRecords: (params?: { employee_id?: number; month?: number; year?: number; status?: string; page?: number; page_size?: number }) =>
    api.get('/payroll/records', { params }),
  getRecord: (id: number) => api.get(`/payroll/records/${id}`),
  process: (data: { month: number; year: number; employee_ids?: number[] }) =>
    api.post('/payroll/process', data),
  updateRecord: (id: number, data: any) => api.put(`/payroll/records/${id}`, data),
  approveRecord: (id: number) => api.post(`/payroll/records/${id}/approve`),
  getSummary: (month: number, year: number) =>
    api.get('/payroll/summary', { params: { month, year } }),
  calculate: (employeeId: number, month: number, year: number) =>
    api.get(`/payroll/calculate/${employeeId}`, { params: { month, year } }),
  getComponents: (employeeId: number) =>
    api.get(`/payroll/components/employee/${employeeId}`),
  createComponent: (data: any) => api.post('/payroll/components', data),
  updateComponent: (id: number, data: any) => api.put(`/payroll/components/${id}`, data),
  getSettings: () => api.get('/payroll/settings'),
  updateSettings: (data: any) => api.put('/payroll/settings', data),
};

export const reportsApi = {
  generatePayslip: (recordId: number) => 
    api.get(`/reports/payslip/${recordId}`, { responseType: 'blob' }),
  attendanceReport: (params: { month: number; year: number; department_id?: number }) =>
    api.get('/reports/attendance-report', { params }),
  payrollRegister: (month: number, year: number) =>
    api.get('/reports/payroll-register', { params: { month, year } }),
  pfEsiReport: (month: number, year: number) =>
    api.get('/reports/pf-esi-report', { params: { month, year } }),
  journalEntries: (month: number, year: number) =>
    api.get('/reports/journal-entries', { params: { month, year } }),
  journalEntriesCsv: (month: number, year: number) =>
    api.get('/reports/journal-entries-csv', { params: { month, year } }, { responseType: 'blob' }),
  markPayrollPaid: (month: number, year: number, paymentDate?: string) =>
    api.post('/reports/mark-paid', null, { params: { month, year, payment_date: paymentDate } }),
  paymentEntries: (month: number, year: number) =>
    api.get('/reports/payment-entries', { params: { month, year } }),
  paymentEntriesCsv: (month: number, year: number) =>
    api.get('/reports/payment-entries-csv', { params: { month, year } }, { responseType: 'blob' }),
};

export default api;
