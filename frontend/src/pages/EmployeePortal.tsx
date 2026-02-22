import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api, { getErrorMessage, authApi, employeeApi, leaveApi, payrollApi } from '../services/api';
import toast from 'react-hot-toast';
import { User, Clock, FileText, LogOut, Calendar, DollarSign, Download } from 'lucide-react';

interface EmployeeData {
  id: number;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  department: string;
  designation: string;
  date_of_joining: string;
}

interface LeaveRequest {
  id: number;
  leave_type: string;
  start_date: string;
  end_date: string;
  reason: string;
  status: string;
}

interface Payslip {
  id: number;
  month: number;
  year: number;
  basic_salary: number;
  allowances: number;
  deductions: number;
  net_salary: number;
  status: string;
}

export default function EmployeePortal() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [employeeCode, setEmployeeCode] = useState('');
  const [password, setPassword] = useState('');
  const [employee, setEmployee] = useState<EmployeeData | null>(null);
  const [leaveRequests, setLeaveRequests] = useState<LeaveRequest[]>([]);
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [activeTab, setActiveTab] = useState('profile');
  const [showLeaveForm, setShowLeaveForm] = useState(false);
  const [leaveForm, setLeaveForm] = useState({
    leave_type: 'casual',
    start_date: '',
    end_date: '',
    reason: ''
  });

  useEffect(() => {
    const storedEmployee = localStorage.getItem('employee_data');
    const token = localStorage.getItem('employee_token');
    if (storedEmployee && token) {
      setEmployee(JSON.parse(storedEmployee));
      setIsLoggedIn(true);
      fetchEmployeeData();
    }
  }, []);

  const fetchEmployeeData = async () => {
    try {
      const empResponse = await api.get('/employees/me');
      setEmployee(empResponse.data);

      const leaveResponse = await leaveApi.listRequests({});
      setLeaveRequests(leaveResponse.data.items || []);

      const payslipResponse = await payrollApi.listRecords({});
      setPayslips(payslipResponse.data.items || []);
    } catch (error) {
      console.error('Error fetching employee data:', error);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await authApi.employeeLogin({
        employee_code: employeeCode,
        password: password
      });

      const { access_token, employee: empData } = response.data;
      localStorage.setItem('employee_token', access_token);
      localStorage.setItem('employee_data', JSON.stringify(empData));
      setEmployee(empData);
      setIsLoggedIn(true);
      toast.success('Welcome!');
      fetchEmployeeData();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('employee_token');
    localStorage.removeItem('employee_data');
    setIsLoggedIn(false);
    setEmployee(null);
  };

  const handleLeaveSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const startDate = new Date(leaveForm.start_date);
      const endDate = new Date(leaveForm.end_date);
      const totalDays = Math.ceil((endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)) + 1;
      
      await leaveApi.createRequest({
        employee_id: employee?.id,
        leave_type: leaveForm.leave_type,
        start_date: leaveForm.start_date + 'T00:00:00',
        end_date: leaveForm.end_date + 'T00:00:00',
        total_days: totalDays,
        reason: leaveForm.reason,
        status: 'pending'
      });
      toast.success('Leave request submitted!');
      setShowLeaveForm(false);
      fetchEmployeeData();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  const downloadPayslip = async (recordId: number) => {
    try {
      const response = await api.get(`/reports/payslip/${recordId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payslip_${recordId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      toast.error('Failed to download payslip');
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-600 to-primary-800 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-primary-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Employee Portal</h1>
            <p className="text-gray-600 mt-2">Login to view your payslips and apply for leave</p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Employee Code
              </label>
              <input
                type="text"
                value={employeeCode}
                onChange={(e) => setEmployeeCode(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="e.g., EMP20260001"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Enter your password"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
            >
              {loading ? 'Logging in...' : 'Login'}
            </button>
          </form>

          <p className="text-center mt-6 text-sm text-gray-500">
            Contact HR if you don't have login credentials
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">Employee Portal</h1>
              <p className="text-sm text-gray-500">
                {employee?.first_name} {employee?.last_name}
              </p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center space-x-2 text-gray-600 hover:text-red-600"
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="md:col-span-1">
            <nav className="space-y-2">
              <button
                onClick={() => setActiveTab('profile')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg ${
                  activeTab === 'profile' ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <User className="w-5 h-5" />
                <span>My Profile</span>
              </button>
              <button
                onClick={() => setActiveTab('payslips')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg ${
                  activeTab === 'payslips' ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <DollarSign className="w-5 h-5" />
                <span>My Payslips</span>
              </button>
              <button
                onClick={() => setActiveTab('leave')}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg ${
                  activeTab === 'leave' ? 'bg-primary-600 text-white' : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Calendar className="w-5 h-5" />
                <span>Leave Requests</span>
              </button>
            </nav>
          </div>

          <div className="md:col-span-3">
            {activeTab === 'profile' && (
              <div className="bg-white rounded-xl shadow p-6">
                <h2 className="text-xl font-bold mb-6">My Profile</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="text-sm text-gray-500">Employee Code</label>
                    <p className="font-medium">{employee?.employee_code}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Full Name</label>
                    <p className="font-medium">{employee?.first_name} {employee?.last_name}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Email</label>
                    <p className="font-medium">{employee?.email || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Phone</label>
                    <p className="font-medium">{employee?.phone || 'Not provided'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Department</label>
                    <p className="font-medium">{employee?.department || 'Not assigned'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Designation</label>
                    <p className="font-medium">{employee?.designation || 'Not assigned'}</p>
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Date of Joining</label>
                    <p className="font-medium">
                      {employee?.date_of_joining ? new Date(employee.date_of_joining).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'payslips' && (
              <div className="bg-white rounded-xl shadow p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold">My Payslips</h2>
                </div>
                {payslips.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No payslips available</p>
                ) : (
                  <div className="space-y-4">
                    {payslips.map((payslip) => (
                      <div key={payslip.id} className="border rounded-lg p-4 flex justify-between items-center">
                        <div>
                          <p className="font-medium">
                            {new Date(payslip.year, payslip.month - 1).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                          </p>
                          <p className="text-sm text-gray-500">
                            Basic: ₹{payslip.basic_salary?.toLocaleString()} | Net: ₹{payslip.net_salary?.toLocaleString()}
                          </p>
                        </div>
                        <div className="flex items-center space-x-3">
                          <span className={`px-3 py-1 rounded-full text-sm ${
                            payslip.status === 'approved' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {payslip.status}
                          </span>
                          <button
                            onClick={() => downloadPayslip(payslip.id)}
                            className="p-2 text-primary-600 hover:bg-primary-50 rounded"
                          >
                            <Download className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {activeTab === 'leave' && (
              <div className="bg-white rounded-xl shadow p-6">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-xl font-bold">Leave Requests</h2>
                  <button
                    onClick={() => setShowLeaveForm(true)}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                  >
                    Apply for Leave
                  </button>
                </div>

                {showLeaveForm && (
                  <form onSubmit={handleLeaveSubmit} className="mb-6 p-4 border rounded-lg bg-gray-50">
                    <h3 className="font-medium mb-4">New Leave Request</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">Leave Type</label>
                        <select
                          value={leaveForm.leave_type}
                          onChange={(e) => setLeaveForm({...leaveForm, leave_type: e.target.value})}
                          className="w-full px-3 py-2 border rounded-lg"
                        >
                          <option value="casual">Casual Leave</option>
                          <option value="sick">Sick Leave</option>
                          <option value="earned">Earned Leave</option>
                          <option value="unpaid">Unpaid Leave</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">Start Date</label>
                        <input
                          type="date"
                          value={leaveForm.start_date}
                          onChange={(e) => setLeaveForm({...leaveForm, start_date: e.target.value})}
                          className="w-full px-3 py-2 border rounded-lg"
                          required
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-600 mb-1">End Date</label>
                        <input
                          type="date"
                          value={leaveForm.end_date}
                          onChange={(e) => setLeaveForm({...leaveForm, end_date: e.target.value})}
                          className="w-full px-3 py-2 border rounded-lg"
                          required
                        />
                      </div>
                      <div className="md:col-span-2">
                        <label className="block text-sm text-gray-600 mb-1">Reason</label>
                        <textarea
                          value={leaveForm.reason}
                          onChange={(e) => setLeaveForm({...leaveForm, reason: e.target.value})}
                          className="w-full px-3 py-2 border rounded-lg"
                          rows={2}
                          required
                        />
                      </div>
                    </div>
                    <div className="flex space-x-3 mt-4">
                      <button
                        type="submit"
                        disabled={loading}
                        className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                      >
                        {loading ? 'Submitting...' : 'Submit'}
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowLeaveForm(false)}
                        className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}

                {leaveRequests.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No leave requests</p>
                ) : (
                  <div className="space-y-4">
                    {leaveRequests.map((request) => (
                      <div key={request.id} className="border rounded-lg p-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <p className="font-medium capitalize">{request.leave_type} Leave</p>
                            <p className="text-sm text-gray-500">
                              {new Date(request.start_date).toLocaleDateString()} - {new Date(request.end_date).toLocaleDateString()}
                            </p>
                            <p className="text-sm mt-1">{request.reason}</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-sm ${
                            request.status === 'approved' ? 'bg-green-100 text-green-800' :
                            request.status === 'rejected' ? 'bg-red-100 text-red-800' :
                            'bg-yellow-100 text-yellow-800'
                          }`}>
                            {request.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
