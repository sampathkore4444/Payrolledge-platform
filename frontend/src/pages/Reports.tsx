import { useState } from 'react';
import { FileText, Download, Users, DollarSign, Calendar, BookOpen, CreditCard } from 'lucide-react';
import { reportsApi } from '../services/api';
import toast from 'react-hot-toast';

export default function Reports() {
  const [loading, setLoading] = useState(false);
  const [month, setMonth] = useState(new Date().getMonth() + 1);
  const [year, setYear] = useState(new Date().getFullYear());
  const [reportType, setReportType] = useState('payroll');

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
    } catch (error) {
      toast.error('Failed to download payslip');
    }
  };

  const handleDownloadReport = async () => {
    setLoading(true);
    try {
      let response;
      let filename;
      
      if (reportType === 'attendance') {
        response = await reportsApi.attendanceReport({ month, year });
        filename = `attendance_report_${month}_${year}.json`;
      } else if (reportType === 'payroll') {
        response = await reportsApi.payrollRegister(month, year);
        filename = `payroll_register_${month}_${year}.json`;
      } else if (reportType === 'pfesi') {
        response = await reportsApi.pfEsiReport(month, year);
        filename = `pf_esi_report_${month}_${year}.json`;
      } else if (reportType === 'journal') {
        response = await reportsApi.journalEntries(month, year);
        filename = `journal_entries_${month}_${year}.json`;
      } else if (reportType === 'payment') {
        response = await reportsApi.paymentEntries(month, year);
        filename = `payment_entries_${month}_${year}.json`;
      }
      
      if (reportType !== 'journal' && reportType !== 'payment') {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        toast.success('Report downloaded successfully');
      } else if (reportType === 'journal') {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        toast.success('Journal entries downloaded');
      } else if (reportType === 'payment') {
        const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        toast.success('Payment entries downloaded');
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to download report');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadJournalCsv = async () => {
    setLoading(true);
    try {
      const response = await reportsApi.journalEntriesCsv(month, year);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `journal_entries_${month}_${year}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Journal entries CSV downloaded');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to download');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPaymentEntries = async () => {
    setLoading(true);
    try {
      const response = await reportsApi.paymentEntries(month, year);
      const blob = new Blob([JSON.stringify(response.data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payment_entries_${month}_${year}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Payment entries downloaded');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'No paid payroll records found. Mark payroll as paid first.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPaymentEntriesCsv = async () => {
    setLoading(true);
    try {
      const response = await reportsApi.paymentEntriesCsv(month, year);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `payment_entries_${month}_${year}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success('Payment entries CSV downloaded');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'No paid payroll records found. Mark payroll as paid first.');
    } finally {
      setLoading(false);
    }
  };

  const reportTypes = [
    { id: 'payroll', name: 'Payroll Register', icon: DollarSign, description: 'Complete payroll summary for the month' },
    { id: 'attendance', name: 'Attendance Report', icon: Calendar, description: 'Employee attendance details' },
    { id: 'pfesi', name: 'PF/ESI Report', icon: Users, description: 'Statutory contributions report' },
    { id: 'journal', name: 'Journal Entries (Accrual)', icon: BookOpen, description: 'Before payment - for Tally/QuickBooks' },
    { id: 'payment', name: 'Payment Entries', icon: CreditCard, description: 'After payment - bank & liability settlements' },
  ];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Reports</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        {reportTypes.map((report) => (
          <button
            key={report.id}
            onClick={() => setReportType(report.id)}
            className={`p-6 rounded-lg border-2 text-left transition-all ${
              reportType === report.id
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
          >
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${reportType === report.id ? 'bg-primary-100' : 'bg-gray-100'}`}>
                <report.icon className={`h-6 w-6 ${reportType === report.id ? 'text-primary-600' : 'text-gray-600'}`} />
              </div>
              <div className="ml-4">
                <p className="font-semibold text-gray-900">{report.name}</p>
                <p className="text-sm text-gray-500">{report.description}</p>
              </div>
            </div>
          </button>
        ))}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Generate Report</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
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
        </div>

        <button
          onClick={handleDownloadReport}
          disabled={loading}
          className="flex items-center px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {loading ? (
            'Generating...'
          ) : (
            <>
              <Download className="h-5 w-5 mr-2" />
              Download {reportTypes.find(r => r.id === reportType)?.name} (JSON)
            </>
          )}
        </button>

        {(reportType === 'journal' || reportType === 'payment') && (
          <div className="mt-4 flex gap-3">
            <button
              onClick={reportType === 'journal' ? handleDownloadJournalCsv : handleDownloadPaymentEntriesCsv}
              disabled={loading}
              className="flex items-center px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
            >
              <Download className="h-4 w-4 mr-2" />
              Download CSV
            </button>
          </div>
        )}
      </div>

      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">Individual Payslip</h3>
        <p className="text-sm text-blue-700">
          To download individual employee payslips, go to the Payroll page and click on the download icon next to each employee record.
        </p>
      </div>

      <div className="mt-4 bg-amber-50 border border-amber-200 rounded-lg p-4">
        <h3 className="font-semibold text-amber-900 mb-2">Journal Entries Flow</h3>
        <p className="text-sm text-amber-700">
          1. <b>Journal Entries (Accrual)</b> - Download after processing payroll (before actual payment)<br/>
          2. Go to Payroll page and click <b>"Mark as Paid"</b><br/>
          3. <b>Payment Entries</b> - Download after marking as paid (actual bank payments)
        </p>
      </div>
    </div>
  );
}
