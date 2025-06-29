import React, { useEffect, useState } from 'react';
import { CloudUpload, Users } from 'lucide-react';

const AdminPage = () => {
  const [users, setUsers] = useState([]);
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    fetch('http://54.147.150.238:8501/admin/list-users')
      .then(res => res.json())
      .then(data => setUsers(data.users || []))
      .catch(err => console.error('Error fetching users:', err));
  }, []);

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
      const response = await fetch('http://54.147.150.238:8501/admin/upload', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setMessage(data.message || 'File uploaded successfully');
    } catch (error) {
      console.error('Upload error:', error);
      setMessage('Upload failed. Please try again.');
    }
    setIsUploading(false);
  };

  return (
    <div style={{ padding: '40px', background: '#f9f9f9', minHeight: '100vh' }}>
      <h1 style={{ fontSize: '28px', marginBottom: '20px', color: '#333' }}>🔧 Admin Dashboard</h1>

      {/* Users List */}
      <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 8px 16px rgba(0,0,0,0.05)', marginBottom: '30px' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}><Users size={20} /> Logged In Users</h2>
        {users.length === 0 ? (
          <p>No users logged in yet.</p>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f1f1f1', textAlign: 'left' }}>
                <th style={{ padding: '10px' }}>Name</th>
                <th style={{ padding: '10px' }}>Email</th>
                <th style={{ padding: '10px' }}>Phone</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user, index) => (
                <tr key={index} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '10px' }}>{user.name}</td>
                  <td style={{ padding: '10px' }}>{user.email}</td>
                  <td style={{ padding: '10px' }}>{user.phone}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* File Upload */}
      <div style={{ background: 'white', padding: '20px', borderRadius: '12px', boxShadow: '0 8px 16px rgba(0,0,0,0.05)' }}>
        <h2 style={{ fontSize: '20px', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}><CloudUpload size={20} /> Upload Excel</h2>
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
            color: message.includes('success') ? 'green' : 'red',
            fontSize: '14px'
          }}>{message}</p>
        )}
      </div>
    </div>
  );
};

export default AdminPage;