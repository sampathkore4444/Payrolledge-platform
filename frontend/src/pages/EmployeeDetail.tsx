import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { employeeApi, payrollApi, leaveApi } from '../services/api';
import { Employee, PayrollRecord, LeaveBalance } from '../types';
import toast from 'react-hot-toast';

export default function EmployeeDetail() {
  const { id } = useParams<{ id: string }>();
  const [employee, setEmployee] = useState<Employee | null>(null);
  const [payrollRecords, setPayrollRecords] = useState<PayrollRecord[]>([]);
  const [leaveBalances, setLeaveBalances] = useState<LeaveBalance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      fetchEmployee();
      fetchPayrollRecords();
      fetchLeaveBalances();
    }
  }, [id]);

  const fetchEmployee = async () => {
    try {
      const response = await employeeApi.get(Number(id));
      setEmployee(response.data);
    } catch (error) {
      toast.error('Failed to fetch employee');
    } finally {
      setLoading(false);
    }
  };

  const fetchPayrollRecords = async () => {
    try {
      const response = await payrollApi.listRecords({ employee_id: Number(id), page_size: 5 });
      setPayrollRecords(response.data.items);
    } catch (error) {
      console.error('Failed to fetch payroll records');
    }
  };

  const fetchLeaveBalances = async () => {
    try {
      const response = await leaveApi.getBalances(Number(id), new Date().getFullYear());
      setLeaveBalances(response.data);
    } catch (error) {
      console.error('Failed to fetch leave balances');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  if (!employee) {
    return <div>Employee not found</div>;
  }

  return (
    <div>
      <Link to="/employees" className="flex items-center text-gray-600 hover:text-gray-900 mb-4">
        <ArrowLeft className="h-5 w-5 mr-2" />
        Back to Employees
      </Link>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Employee Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Employee Code</p>
                <p className="font-medium">{employee.employee_code || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Name</p>
                <p className="font-medium">{employee.first_name} {employee.last_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Email</p>
                <p className="font-medium">{employee.email || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Phone</p>
                <p className="font-medium">{employee.phone || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Department</p>
                <p className="font-medium">{employee.department?.name || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Designation</p>
                <p className="font-medium">{employee.designation?.name || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Date of Joining</p>
                <p className="font-medium">
                  {employee.date_of_joining ? new Date(employee.date_of_joining).toLocaleDateString() : '-'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Status</p>
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                  employee.status === 'permanent' ? 'bg-green-100 text-green-800' :
                  employee.status === 'probation' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {employee.status}
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Bank & Statutory Details</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-gray-500">Bank Name</p>
                <p className="font-medium">{employee.bank_name || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Account Number</p>
                <p className="font-medium">{employee.bank_account_number || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">IFSC Code</p>
                <p className="font-medium">{employee.ifsc_code || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Aadhar Number</p>
                <p className="font-medium">{employee.aadhar_number || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">PAN Number</p>
                <p className="font-medium">{employee.pan_number || '-'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">UAN Number</p>
                <p className="font-medium">{employee.uan_number || '-'}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Leave Balances</h2>
            {leaveBalances.length === 0 ? (
              <p className="text-gray-500 text-sm">No leave balances</p>
            ) : (
              <div className="space-y-3">
                {leaveBalances.map((balance) => (
                  <div key={balance.id} className="flex justify-between items-center">
                    <span className="text-sm capitalize">{balance.leave_type}</span>
                    <span className="font-medium">{balance.available_days} / {balance.total_days}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold mb-4">Recent Payroll</h2>
            {payrollRecords.length === 0 ? (
              <p className="text-gray-500 text-sm">No payroll records</p>
            ) : (
              <div className="space-y-3">
                {payrollRecords.map((record) => (
                  <div key={record.id} className="border-b pb-2">
                    <div className="flex justify-between">
                      <span className="text-sm">{record.month}/{record.year}</span>
                      <span className="font-medium">₹{record.net_salary.toLocaleString()}</span>
                    </div>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      record.status === 'paid' ? 'bg-green-100 text-green-800' :
                      record.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {record.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
