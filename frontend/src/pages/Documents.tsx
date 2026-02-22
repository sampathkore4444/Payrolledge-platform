import { useEffect, useState } from 'react';
import { Plus, Check, X, Eye, Pencil, Trash2 } from 'lucide-react';
import api, { employeeApi, getErrorMessage } from '../services/api';
import { Employee } from '../types';
import toast from 'react-hot-toast';

interface Document {
  id: number;
  employee_id: number;
  document_type: string;
  document_name: string;
  file_url?: string;
  document_number?: string;
  issue_date?: string;
  expiry_date?: string;
  status: string;
  verified_by?: number;
  verified_at?: string;
  remarks?: string;
  created_at: string;
}

const documentTypes = [
  { value: 'aadhar', label: 'Aadhar Card' },
  { value: 'pan', label: 'PAN Card' },
  { value: 'passport', label: 'Passport' },
  { value: 'driving_license', label: 'Driving License' },
  { value: 'voter_id', label: 'Voter ID' },
  { value: 'employment_contract', label: 'Employment Contract' },
  { value: 'education_certificate', label: 'Education Certificate' },
  { value: 'experience_letter', label: 'Experience Letter' },
  { value: 'photo', label: 'Photo' },
  { value: 'signature', label: 'Signature' },
  { value: 'other', label: 'Other' },
];

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [filterEmployee, setFilterEmployee] = useState<number | null>(null);
  const [formData, setFormData] = useState({
    employee_id: undefined as number | undefined,
    document_type: 'aadhar',
    document_name: '',
    document_number: '',
    issue_date: '',
    expiry_date: '',
  });

  useEffect(() => {
    fetchDocuments();
    fetchEmployees();
  }, [filterEmployee]);

  const fetchDocuments = async () => {
    setLoading(true);
    try {
      if (filterEmployee) {
        const response = await api.get(`/documents/employee/${filterEmployee}`);
        setDocuments(response.data);
      } else {
        setDocuments([]);
      }
    } catch (error) {
      toast.error('Failed to fetch documents');
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/documents/', {
        ...formData,
        issue_date: formData.issue_date ? formData.issue_date + 'T00:00:00' : null,
        expiry_date: formData.expiry_date ? formData.expiry_date + 'T00:00:00' : null,
      });
      toast.success('Document added successfully');
      setShowModal(false);
      setFormData({
        employee_id: undefined,
        document_type: 'aadhar',
        document_name: '',
        document_number: '',
        issue_date: '',
        expiry_date: '',
      });
      fetchDocuments();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleEditClick = (doc: Document) => {
    setEditId(doc.id);
    setFormData({
      employee_id: doc.employee_id,
      document_type: doc.document_type,
      document_name: doc.document_name || '',
      document_number: doc.document_number || '',
      issue_date: doc.issue_date ? doc.issue_date.split('T')[0] : '',
      expiry_date: doc.expiry_date ? doc.expiry_date.split('T')[0] : '',
    });
    setShowEditModal(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editId) return;
    try {
      await api.put(`/documents/${editId}`, {
        ...formData,
        issue_date: formData.issue_date ? formData.issue_date + 'T00:00:00' : null,
        expiry_date: formData.expiry_date ? formData.expiry_date + 'T00:00:00' : null,
      });
      toast.success('Document updated successfully');
      setShowEditModal(false);
      setEditId(null);
      setFormData({
        employee_id: undefined,
        document_type: 'aadhar',
        document_name: '',
        document_number: '',
        issue_date: '',
        expiry_date: '',
      });
      fetchDocuments();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    }
  };

  const handleDeleteClick = (id: number) => {
    setDeleteId(id);
    setShowDeleteModal(true);
  };

  const confirmDelete = async () => {
    if (!deleteId) return;
    try {
      await api.delete(`/documents/${deleteId}`);
      toast.success('Document deleted');
      fetchDocuments();
    } catch (error: any) {
      toast.error(getErrorMessage(error));
    } finally {
      setShowDeleteModal(false);
      setDeleteId(null);
    }
  };

  const handleVerify = async (docId: number, status: 'verified' | 'rejected') => {
    try {
      await api.post(`/documents/${docId}/verify`, { status, remarks: '' });
      toast.success(`Document ${status}`);
      fetchDocuments();
    } catch (error) {
      toast.error('Failed to verify document');
    }
  };

  const getEmployeeName = (employeeId: number) => {
    const emp = employees.find(e => e.id === employeeId);
    return emp ? `${emp.first_name} ${emp.last_name}` : `Employee #${employeeId}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'verified': return 'bg-green-100 text-green-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-yellow-100 text-yellow-800';
    }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Document Management</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
        >
          <Plus className="h-5 w-5 mr-2" />
          Add Document
        </button>
      </div>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Employee</label>
        <select
          value={filterEmployee || ''}
          onChange={(e) => setFilterEmployee(e.target.value ? Number(e.target.value) : null)}
          className="w-full md:w-64 border border-gray-300 rounded-lg px-3 py-2"
        >
          <option value="">All Employees</option>
          {employees.map((emp) => (
            <option key={emp.id} value={emp.id}>
              {emp.first_name} {emp.last_name} ({emp.employee_code})
            </option>
          ))}
        </select>
      </div>

      <div className="bg-white shadow rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Employee</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document Type</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Document No.</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Expiry</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center">Loading...</td>
              </tr>
            ) : documents.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-4 text-center">
                  {filterEmployee ? 'No documents found for this employee' : 'Select an employee to view documents'}
                </td>
              </tr>
            ) : (
              documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium">
                    {getEmployeeName(doc.employee_id)}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {documentTypes.find(t => t.value === doc.document_type)?.label || doc.document_type}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {doc.document_number || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {doc.expiry_date ? new Date(doc.expiry_date).toLocaleDateString() : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(doc.status)}`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEditClick(doc)}
                        className="p-1 text-primary-600 hover:bg-primary-50 rounded"
                        title="Edit"
                      >
                        <Pencil className="h-5 w-5" />
                      </button>
                      <button
                        onClick={() => handleDeleteClick(doc.id)}
                        className="p-1 text-red-600 hover:bg-red-50 rounded"
                        title="Delete"
                      >
                        <Trash2 className="h-5 w-5" />
                      </button>
                      {doc.status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleVerify(doc.id, 'verified')}
                            className="p-1 text-green-600 hover:bg-green-50 rounded"
                            title="Verify"
                          >
                            <Check className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleVerify(doc.id, 'rejected')}
                            className="p-1 text-red-600 hover:bg-red-50 rounded"
                            title="Reject"
                          >
                            <X className="h-5 w-5" />
                          </button>
                        </>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add Document</h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Employee *</label>
                <select
                  required
                  value={formData.employee_id || ''}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value ? Number(e.target.value) : undefined })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Select Employee</option>
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>
                      {emp.first_name} {emp.last_name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Document Type *</label>
                <select
                  value={formData.document_type}
                  onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  {documentTypes.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Document Name</label>
                <input
                  type="text"
                  value={formData.document_name}
                  onChange={(e) => setFormData({ ...formData, document_name: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Document Number</label>
                <input
                  type="text"
                  value={formData.document_number}
                  onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Issue Date</label>
                  <input
                    type="date"
                    value={formData.issue_date}
                    onChange={(e) => setFormData({ ...formData, issue_date: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
                  <input
                    type="date"
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  Add Document
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Edit Document</h2>
            <form onSubmit={handleEditSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Employee *</label>
                <select
                  required
                  value={formData.employee_id || ''}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value ? Number(e.target.value) : undefined })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="">Select Employee</option>
                  {employees.map((emp) => (
                    <option key={emp.id} value={emp.id}>{emp.first_name} {emp.last_name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Document Type *</label>
                <select
                  required
                  value={formData.document_type}
                  onChange={(e) => setFormData({ ...formData, document_type: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  {documentTypes.map((type) => (
                    <option key={type.value} value={type.value}>{type.label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Document Name</label>
                <input
                  type="text"
                  value={formData.document_name}
                  onChange={(e) => setFormData({ ...formData, document_name: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Document Number</label>
                <input
                  type="text"
                  value={formData.document_number}
                  onChange={(e) => setFormData({ ...formData, document_number: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Issue Date</label>
                  <input
                    type="date"
                    value={formData.issue_date}
                    onChange={(e) => setFormData({ ...formData, issue_date: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Expiry Date</label>
                  <input
                    type="date"
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                    className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
                >
                  Update
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-sm">
            <h2 className="text-xl font-bold mb-4">Confirm Delete</h2>
            <p className="text-gray-600 mb-6">Are you sure you want to delete this document? This action cannot be undone.</p>
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
