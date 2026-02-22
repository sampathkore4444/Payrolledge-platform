import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { payrollApi } from '../services/api';
import toast from 'react-hot-toast';

export default function PayrollProcess() {
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());

  const handleProcess = async () => {
    setProcessing(true);
    try {
      await payrollApi.process({ month, year });
      toast.success('Payroll processed successfully');
      navigate('/payroll');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to process payroll');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Process Payroll</h1>

      <div className="bg-white rounded-lg shadow p-6 max-w-lg">
        <p className="text-gray-600 mb-6">
          This will process payroll for all active employees for the selected month.
          Make sure attendance is marked before processing payroll.
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Month</label>
            <select
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            >
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i + 1} value={i + 1}>
                  {new Date(0, i).toLocaleString('default', { month: 'long' })}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Year</label>
            <select
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="w-full border border-gray-300 rounded-lg px-3 py-2"
            >
              {[2024, 2025, 2026].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> This will calculate:
            </p>
            <ul className="text-sm text-yellow-800 list-disc list-inside mt-2">
              <li>Basic salary (pro-rated based on attendance)</li>
              <li>HRA, Conveyance, Special Allowance</li>
              <li>Overtime payments</li>
              <li>PF, ESIC, Professional Tax, TDS deductions</li>
            </ul>
          </div>

          <div className="flex space-x-4 pt-4">
            <button
              onClick={() => navigate('/payroll')}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleProcess}
              disabled={processing}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              {processing ? 'Processing...' : 'Process Payroll'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
