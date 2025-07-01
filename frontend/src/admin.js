import React, { useEffect, useState } from 'react';
import { CloudUpload, Calendar, Edit3, Trash2, Save, X } from 'lucide-react';
import { BASE_URL } from './config';

const AdminPage = () => {
  const [schedules, setSchedules] = useState([]);
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editStatus, setEditStatus] = useState('');

  const statusOptions = [
    { value: 'pending', label: 'Pending', color: '#f59e0b' },
    { value: 'confirmed', label: 'Confirmed', color: '#10b981' },
    { value: 'completed', label: 'Completed', color: '#6366f1' },
    { value: 'cancelled', label: 'Cancelled', color: '#ef4444' },
    { value: 'no-show', label: 'No Show', color: '#6b7280' },
  ];

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = () => {
    fetch(`${BASE_URL}/admin/schedules`)
      .then(res => res.json())
      .then(data => setSchedules(data.users || []))
      .catch(err => console.error('Error fetching schedules:', err));
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage('');
  };

  const handleUpload = async () => {
    if (!file) {
      setMessage('Please select a file to upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    try {
      const response = await fetch(`${BASE_URL}/admin/upload`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setMessage(data.message || 'File uploaded successfully');
      
      // Refresh schedules after successful upload
      if (response.ok) {
        fetchSchedules();
      }
    } catch (error) {
      console.error('Upload error:', error);
      setMessage('Upload failed. Please try again.');
    }
    setIsUploading(false);
  };

  const handleEditClick = (index, currentStatus) => {
    setEditingId(index);
    setEditStatus(currentStatus || 'pending');
  };

  const handleSaveStatus = async (index) => {
    try {
      const appointment = schedules[index];
      const response = await fetch(`${BASE_URL}/admin/schedules/${appointment.id || index}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...appointment,
          status: editStatus
        })
      });

      if (response.ok) {
        // Update local state
        const updatedSchedules = [...schedules];
        updatedSchedules[index] = { ...updatedSchedules[index], status: editStatus };
        setSchedules(updatedSchedules);
        setEditingId(null);
        setMessage('Status updated successfully');
      } else {
        setMessage('Failed to update status');
      }
    } catch (error) {
      console.error('Update error:', error);
      setMessage('Failed to update status');
    }
  };

  const handleDelete = async (index) => {
    if (!window.confirm('Are you sure you want to delete this appointment?')) {
      return;
    }

    try {
      const appointment = schedules[index];
      const response = await fetch(`${BASE_URL}/admin/schedules/${appointment.id || index}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        // Remove from local state
        const updatedSchedules = schedules.filter((_, i) => i !== index);
        setSchedules(updatedSchedules);
        setMessage('Appointment deleted successfully');
      } else {
        setMessage('Failed to delete appointment');
      }
    } catch (error) {
      console.error('Delete error:', error);
      setMessage('Failed to delete appointment');
    }
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditStatus('');
  };

  const getStatusColor = (status) => {
    const statusOption = statusOptions.find(option => option.value === status);
    return statusOption ? statusOption.color : '#6b7280';
  };

  const getStatusLabel = (status) => {
    const statusOption = statusOptions.find(option => option.value === status);
    return statusOption ? statusOption.label : status || 'Pending';
  };

  return (
    <div style={{ padding: '40px', background: '#f9f9f9', minHeight: '100vh' }}>
      <h1 style={{ fontSize: '28px', marginBottom: '20px', color: '#333' }}>🔧 Admin Dashboard</h1>

      {/* Scheduled Appointments */}
      <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 8px 16px rgba(0,0,0,0.05)', marginBottom: '30px' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Calendar size={20} /> Scheduled Appointments
        </h2>
        {schedules.length === 0 ? (
          <p>No appointments scheduled yet.</p>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '800px' }}>
              <thead>
                <tr style={{ backgroundColor: '#f1f1f1', textAlign: 'left' }}>
                  <th style={{ padding: '12px', fontWeight: 'bold' }}>Name</th>
                  <th style={{ padding: '12px', fontWeight: 'bold' }}>Phone</th>
                  <th style={{ padding: '12px', fontWeight: 'bold' }}>Date</th>
                  <th style={{ padding: '12px', fontWeight: 'bold' }}>Time</th>
                  <th style={{ padding: '12px', fontWeight: 'bold' }}>Status</th>
                  <th style={{ padding: '12px', fontWeight: 'bold' }}>Message</th>
                  <th style={{ padding: '12px', fontWeight: 'bold' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {schedules.map((appointment, index) => (
                  <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '12px' }}>{appointment.name || 'N/A'}</td>
                    <td style={{ padding: '12px' }}>{appointment.phone || 'N/A'}</td>
                    <td style={{ padding: '12px' }}>{appointment.date || 'N/A'}</td>
                    <td style={{ padding: '12px' }}>{appointment.time || 'N/A'}</td>
                    <td style={{ padding: '12px' }}>
                      {editingId === index ? (
                        <select
                          value={editStatus}
                          onChange={(e) => setEditStatus(e.target.value)}
                          style={{
                            padding: '4px 8px',
                            borderRadius: '4px',
                            border: '1px solid #ddd',
                            fontSize: '12px'
                          }}
                        >
                          {statusOptions.map(option => (
                            <option key={option.value} value={option.value}>
                              {option.label}
                            </option>
                          ))}
                        </select>
                      ) : (
                        <span style={{
                          padding: '4px 8px',
                          borderRadius: '12px',
                          fontSize: '12px',
                          fontWeight: 'bold',
                          color: 'white',
                          backgroundColor: getStatusColor(appointment.status)
                        }}>
                          {getStatusLabel(appointment.status)}
                        </span>
                      )}
                    </td>
                    <td style={{ padding: '12px', maxWidth: '200px', wordWrap: 'break-word' }}>
                      {appointment.message || 'No message'}
                    </td>
                    <td style={{ padding: '12px' }}>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        {editingId === index ? (
                          <>
                            <button
                              onClick={() => handleSaveStatus(index)}
                              style={{
                                padding: '4px 8px',
                                backgroundColor: '#10b981',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                              }}
                            >
                              <Save size={12} /> Save
                            </button>
                            <button
                              onClick={handleCancelEdit}
                              style={{
                                padding: '4px 8px',
                                backgroundColor: '#6b7280',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                              }}
                            >
                              <X size={12} /> Cancel
                            </button>
                          </>
                        ) : (
                          <>
                            <button
                              onClick={() => handleEditClick(index, appointment.status)}
                              style={{
                                padding: '4px 8px',
                                backgroundColor: '#3b82f6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                              }}
                            >
                              <Edit3 size={12} /> Edit
                            </button>
                            <button
                              onClick={() => handleDelete(index)}
                              style={{
                                padding: '4px 8px',
                                backgroundColor: '#ef4444',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                              }}
                            >
                              <Trash2 size={12} /> Delete
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* File Upload */}
      <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 8px 16px rgba(0,0,0,0.05)' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CloudUpload size={20} /> Upload Excel
        </h2>
        <input type="file" accept=".xlsx,.xls" onChange={handleFileChange} style={{ marginBottom: '10px' }} />
        <br />
        <button
          onClick={handleUpload}
          disabled={isUploading}
          style={{
            padding: '10px 20px',
            backgroundColor: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: isUploading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}>
          {isUploading ? 'Uploading...' : 'Upload File'}
        </button>

        {message && (
          <p style={{
            marginTop: '12px',
            color: message.includes('success') || message.includes('successfully') ? 'green' : 'red',
            fontSize: '14px'
          }}>{message}</p>
        )}
      </div>
    </div>
  );
};

export default AdminPage;