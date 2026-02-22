import { useEffect, useState } from 'react';
import { payrollApi, authApi } from '../services/api';
import { useAuthStore } from '../store/authStore';
import toast from 'react-hot-toast';

export default function Settings() {
  const { user } = useAuthStore();
  const [payrollSettings, setPayrollSettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
  });

  useEffect(() => {
    fetchPayrollSettings();
  }, []);

  const fetchPayrollSettings = async () => {
    try {
      const response = await payrollApi.getSettings();
      setPayrollSettings(response.data);
    } catch (error) {
      console.error('Failed to fetch settings');
    } finally {
      setLoading(false);
    }
  };

  const handlePayrollSettingsUpdate = async () => {
    try {
      await payrollApi.updateSettings(payrollSettings);
      toast.success('Settings updated successfully');
    } catch (error) {
      toast.error('Failed to update settings');
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await authApi.changePassword(passwordData);
      toast.success('Password changed successfully');
      setPasswordData({ old_password: '', new_password: '' });
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading...</div>;
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Payroll Settings</h2>
          {payrollSettings && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">EPF Rate (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={payrollSettings.epf_rate_employee}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, epf_rate_employee: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">EPF Employer (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={payrollSettings.epf_rate_employer}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, epf_rate_employer: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ESIC Employee (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={payrollSettings.esic_rate_employee}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, esic_rate_employee: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ESIC Employer (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={payrollSettings.esic_rate_employer}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, esic_rate_employer: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Professional Tax (₹)</label>
                  <input
                    type="number"
                    value={payrollSettings.professional_tax}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, professional_tax: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">PT Limit (₹)</label>
                  <input
                    type="number"
                    value={payrollSettings.professional_tax_limit}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, professional_tax_limit: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">EPF Wage Limit (₹)</label>
                  <input
                    type="number"
                    value={payrollSettings.epf_wage_limit}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, epf_wage_limit: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">ESIC Wage Limit (₹)</label>
                  <input
                    type="number"
                    value={payrollSettings.esic_wage_limit}
                    onChange={(e) => setPayrollSettings({ ...payrollSettings, esic_wage_limit: Number(e.target.value) })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
              <button
                onClick={handlePayrollSettingsUpdate}
                className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Save Payroll Settings
              </button>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Change Password</h2>
          <form onSubmit={handlePasswordChange} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Current Password</label>
              <input
                type="password"
                required
                value={passwordData.old_password}
                onChange={(e) => setPasswordData({ ...passwordData, old_password: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">New Password</label>
              <input
                type="password"
                required
                minLength={6}
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
              />
            </div>
            <button
              type="submit"
              className="w-full px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
            >
              Change Password
            </button>
          </form>

          <div className="mt-8 pt-6 border-t">
            <h2 className="text-lg font-semibold mb-4">Profile Information</h2>
            <div className="space-y-2">
              <p><span className="text-gray-500">Username:</span> {user?.username}</p>
              <p><span className="text-gray-500">Email:</span> {user?.email}</p>
              <p><span className="text-gray-500">Role:</span> <span className="capitalize">{user?.role}</span></p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mt-6">
          <h2 className="text-lg font-semibold mb-4">Compliance Alerts</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
              <div>
                <p className="font-medium text-blue-900">PF Remittance Due</p>
                <p className="text-sm text-blue-700">PF contribution must be deposited by 15th of each month</p>
              </div>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">Monthly</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
              <div>
                <p className="font-medium text-green-900">ESIC Remittance Due</p>
                <p className="text-sm text-green-700">ESIC contribution must be deposited by 15th of each month</p>
              </div>
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">Monthly</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-orange-50 rounded-lg">
              <div>
                <p className="font-medium text-orange-900">Professional Tax</p>
                <p className="text-sm text-orange-700">PT must be deposited as per state government schedule</p>
              </div>
              <span className="px-3 py-1 bg-orange-100 text-orange-800 text-sm rounded-full">Quarterly</span>
            </div>
            <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
              <div>
                <p className="font-medium text-purple-900">TDS Quarterly Return</p>
                <p className="text-sm text-purple-700">TDS return filing due dates: Q1 (Jul 15), Q2 (Oct 15), Q3 (Jan 15), Q4 (May 15)</p>
              </div>
              <span className="px-3 py-1 bg-purple-100 text-purple-800 text-sm rounded-full">Quarterly</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
