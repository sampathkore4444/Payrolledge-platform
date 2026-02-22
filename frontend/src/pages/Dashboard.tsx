import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, Calendar, DollarSign, Clock } from 'lucide-react';
import { employeeApi, payrollApi } from '../services/api';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalEmployees: 0,
    totalPayroll: 0,
    pendingLeaves: 0,
    presentToday: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [empRes] = await Promise.all([
          employeeApi.list({ page_size: 1 })
        ]);
        
        const currentMonth = new Date().getMonth() + 1;
        const currentYear = new Date().getFullYear();
        const payrollRes = await payrollApi.getSummary(currentMonth, currentYear).catch(() => ({ data: {} }));

        setStats({
          totalEmployees: empRes.data.total || 0,
          totalPayroll: payrollRes.data.total_net || 0,
          pendingLeaves: 0,
          presentToday: 0
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const statCards = [
    { name: 'Total Employees', value: stats.totalEmployees, icon: Users, color: 'bg-blue-500' },
    { name: 'Monthly Payroll', value: `₹${(stats.totalPayroll / 100000).toFixed(1)}L`, icon: DollarSign, color: 'bg-green-500' },
    { name: 'Present Today', value: stats.presentToday || '-', icon: Clock, color: 'bg-purple-500' },
    { name: 'Pending Leaves', value: stats.pendingLeaves || '-', icon: Calendar, color: 'bg-orange-500' },
  ];

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((stat) => (
          <div key={stat.name} className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className={`${stat.color} rounded-lg p-3`}>
                <stat.icon className="h-6 w-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.name}</p>
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link
              to="/employees"
              className="block p-4 border border-gray-200 rounded-lg hover:border-primary-500 transition-colors"
            >
              <p className="font-medium text-gray-900">Add New Employee</p>
              <p className="text-sm text-gray-500">Register a new employee in the system</p>
            </Link>
            <Link
              to="/payroll/process"
              className="block p-4 border border-gray-200 rounded-lg hover:border-primary-500 transition-colors"
            >
              <p className="font-medium text-gray-900">Process Payroll</p>
              <p className="text-sm text-gray-500">Run monthly payroll calculations</p>
            </Link>
            <Link
              to="/attendance"
              className="block p-4 border border-gray-200 rounded-lg hover:border-primary-500 transition-colors"
            >
              <p className="font-medium text-gray-900">Mark Attendance</p>
              <p className="text-sm text-gray-500">Record employee attendance</p>
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <p className="text-gray-500 text-sm">No recent activity to display</p>
        </div>
      </div>
    </div>
  );
}
