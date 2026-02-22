import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { payrollApi, employeeApi, reportsApi } from '../services/api';
import { PayrollRecord, Employee, PayrollSummary } from '../types';
import { Download } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Payroll() {
  const [records, setRecords] = useState<PayrollRecord[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [summary, setSummary] = useState<PayrollSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());

  useEffect(() => {
    fetchRecords();
    fetchEmployees();
    fetchSummary();
  }, [month, year]);

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const response = await payrollApi.listRecords({ month, year, page_size: 50 });
      setRecords(response.data.items);
    } catch (error) {
      toast.error('Failed to fetch payroll records');
    } finally {
      setLoading(false);
    }
  };

  const fetchEmployees = async () => {
    try {
      const response = await employeeApi.list({ page_size: 100 });
      setEmployees(response.data.items);
    } catch (error) {
      console.error('Failed to fetch employees');
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await payrollApi.getSummary(month, year);
      setSummary(response.data);
    } catch (error) {
      setSummary(null);
    }
  };

  const handleApprove = async (id: number) => {
    try {
      await payrollApi.approveRecord(id);
      toast.success('Payroll approved');
      fetchRecords();
    } catch (error) {
      toast.error('Failed to approve payroll');
    }
  };

  const handleMarkAsPaid = async () => {
    try {
      await reportsApi.markPayrollPaid(month, year);
      toast.success('Payroll marked as paid');
      fetchRecords();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to mark as paid');
    }
  };

  const hasApprovedRecords = records.some(r => r.status === 'approved');
  const hasPaidRecords = records.some(r => r.status === 'paid');

  const handleDownloadPayslip = async (recordId: number) => {
    try {
      const response = await reportsApi.generatePayslip(recordId);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payslip_${recordId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Payslip downloaded');
    } catch (error) {
      toast.error('Failed to download payslip');
    }
  };

  const getEmployeeName = (employeeId: number) => {
    const emp = employees.find(e => e.id === employeeId);
    return emp ? `${emp.first_name} ${emp.last_name}` : `Employee #${employeeId}`;
  };

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-100 text-gray-800',
    processed: 'bg-blue-100 text-blue-800',
    approved: 'bg-green-100 text-green-800',
    paid: 'bg-purple-100 text-purple-800',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Payroll</h1>
        <div className="flex items-center space-x-4">
          <select
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            className="border border-gray-300 rounded-lg px-3 py-2"
          >
            {Array.from({ length: 12 }, (_, i) => (
              <option key={i + 1} value={i + 1}>
                {new Date(0, i).toLocaleString('default', { month: 'long' })}
              </option>
            ))}
          </select>
          <select
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="border border-gray-300 rounded-lg px-3 py-2"
          >
            {[2024, 2025, 2026].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
          <Link
            to="/payroll/process"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            Process Payroll
          </Link>
          {hasApprovedRecords && !hasPaidRecords && (
            <button
              onClick={handleMarkAsPaid}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
            >
              Mark as Paid
            </button>
          )}
        </div>
      </div>

      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Employees</p>
            <p className="text-2xl font-bold">{summary.total_employees}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Gross</p>
            <p className="text-2xl font-bold">₹{(summary.total_gross / 100000).toFixed(1)}L</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Deductions</p>
            <p className="text-2xl font-bold">₹{(summary.total_deductions / 100000).toFixed(1)}L</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-500">Total Net Salary</p>
            <p className="text-2xl font-bold text-green-600">₹{(summary.total_net / 100000).toFixed(1)}L</p>
          </div>
        </div>
      )}

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Basic</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gross</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Deductions</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Net Salary</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-4 text-center">Loading...</td>
              </tr>
            ) : records.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-4 text-center">No payroll records for this month</td>
              </tr>
            ) : (
              records.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">
                    {getEmployeeName(record.employee_id)}
                  </td>
                  <td className="px-6 py-4 text-sm">₹{record.basic_salary.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm">₹{record.gross_earnings.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm text-red-600">₹{record.total_deductions.toLocaleString()}</td>
                  <td className="px-6 py-4 text-sm font-medium text-green-600">₹{record.net_salary.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusColors[record.status]}`}>
                      {record.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {record.status !== 'draft' && (
                      <button
                        onClick={() => handleDownloadPayslip(record.id)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                        title="Download Payslip"
                      >
                        <Download className="h-5 w-5" />
                      </button>
                    )}
                    {record.status === 'processed' && (
                      <button
                        onClick={() => handleApprove(record.id)}
                        className="text-primary-600 hover:text-primary-900 text-sm"
                      >
                        Approve
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
