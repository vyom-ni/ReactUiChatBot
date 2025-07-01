import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BASE_URL } from './config';

const AuthSystem = () => {
  const [authType, setAuthType] = useState('user'); // 'user' or 'admin'
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    phone: ''
  });
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // For phone input, only allow digits and limit to 10 characters
    if (name === 'phone') {
      const digitsOnly = value.replace(/\D/g, '');
      if (digitsOnly.length <= 10) {
        setFormData({
          ...formData,
          [name]: digitsOnly
        });
      }
    } else {
      setFormData({
        ...formData,
        [name]: value
      });
    }
  };

  const validateEmail = (email) => {
    // More comprehensive email validation
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

  const validatePhone = (phone) => {
    // Check if phone number has exactly 10 digits
    return /^\d{10}$/.test(phone);
  };

  const validateAdminForm = () => {
    if (!formData.email || !formData.password) {
      setMessage('Email and password are required');
      return false;
    }

    // Enhanced email validation
    if (!validateEmail(formData.email)) {
      setMessage('Please enter a valid email address (e.g., user@example.com)');
      return false;
    }

    // Password validation (minimum 6 characters)
    if (formData.password.length < 6) {
      setMessage('Password must be at least 6 characters long');
      return false;
    }

    return true;
  };

  const validateUserForm = () => {
    if (!formData.phone) {
      setMessage('Phone number is required');
      return false;
    }

    // Validate phone number has exactly 10 digits
    if (!validatePhone(formData.phone)) {
      setMessage('Phone number must be exactly 10 digits');
      return false;
    }

    return true;
  };

  const handleUserLogin = async () => {
    if (!validateUserForm()) return;

    setIsLoading(true);

    try {
      const response = await fetch(`${BASE_URL}/auth/user_login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          phone: formData.phone,
        })
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(data.message || 'Login successful!');

        localStorage.setItem('phone',formData.phone);
        navigate('/home');
       
        setTimeout(() => {
          
        }, 1000);
      } else {
        setMessage(data.detail || 'Invalid credentials');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Something went wrong!.');
    }

    setIsLoading(false);
  };

  const handleAdminLogin = async () => {
    setMessage('');
    
    if (!validateAdminForm()) return;

    setIsLoading(true);

    try {
      const response = await fetch(`${BASE_URL}/auth/admin_login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();
      console.log(data);

      if (response.ok) {
        setMessage(data.message || 'Login successful!');
        
        // Redirect to admin page
        setTimeout(() => {
          navigate('/admin');
        }, 1000);
      } else {
        setMessage(data.detail || 'Invalid credentials');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Something went wrong!.');
    }

    setIsLoading(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');

    if (authType === 'user') {
      await handleUserLogin();
    } else {
      await handleAdminLogin();
    }
  };

  const switchAuthType = (type) => {
    setAuthType(type);
    setMessage('');
    setFormData({
      email: '',
      password: '',
      phone: ''
    });
  };

  // Real-time validation feedback
  const getInputStyle = (fieldName) => {
    const baseStyle = {
      width: '100%',
      padding: '12px',
      border: '2px solid #e1e5e9',
      borderRadius: '8px',
      fontSize: '14px',
      outline: 'none',
      transition: 'border-color 0.3s ease',
      boxSizing: 'border-box'
    };

    // Add validation styling
    if (fieldName === 'email' && formData.email) {
      if (validateEmail(formData.email)) {
        baseStyle.borderColor = '#28a745';
      } else {
        baseStyle.borderColor = '#dc3545';
      }
    }

    if (fieldName === 'phone' && formData.phone) {
      if (validatePhone(formData.phone)) {
        baseStyle.borderColor = '#28a745';
      } else {
        baseStyle.borderColor = '#dc3545';
      }
    }

    return baseStyle;
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '20px',
        padding: '40px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        {/* Auth Type Selector */}
        <div style={{
          display: 'flex',
          marginBottom: '30px',
          borderRadius: '10px',
          backgroundColor: '#f8f9fa',
          padding: '4px'
        }}>
          <button
            onClick={() => switchAuthType('user')}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              backgroundColor: authType === 'user' ? '#667eea' : 'transparent',
              color: authType === 'user' ? 'white' : '#666'
            }}
          >
            👤 User Login
          </button>
          <button
            onClick={() => switchAuthType('admin')}
            style={{
              flex: 1,
              padding: '12px',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 'bold',
              cursor: 'pointer',
              transition: 'all 0.3s ease',
              backgroundColor: authType === 'admin' ? '#667eea' : 'transparent',
              color: authType === 'admin' ? 'white' : '#666'
            }}
          >
            👨‍💼 Admin Login
          </button>
        </div>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{
            margin: 0,
            fontSize: '28px',
            color: '#333',
            marginBottom: '8px'
          }}>
            {authType === 'user' ? '👤 User Access' : '🔐 Admin Login'}
          </h1>
          <p style={{
            margin: 0,
            color: '#666',
            fontSize: '14px'
          }}>
            {authType === 'user' 
              ? 'Enter your 10-digit phone number' 
              : 'Sign in to admin panel'
            }
          </p>
        </div>

        {/* Message Display */}
        {message && (
          <div style={{
            padding: '12px',
            borderRadius: '8px',
            marginBottom: '20px',
            backgroundColor: message.includes('successful') ? '#d4edda' : '#f8d7da',
            border: `1px solid ${message.includes('successful') ? '#c3e6cb' : '#f5c6cb'}`,
            color: message.includes('successful') ? '#155724' : '#721c24',
            fontSize: '14px'
          }}>
            {message}
          </div>
        )}

        {/* Form */}
        <div>
          {authType === 'user' ? (
            // User Login Form (Phone Only)
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#333'
              }}>
                Phone Number (10 digits)
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="Enter 10-digit phone number"
                maxLength="10"
                style={getInputStyle('phone')}
                onFocus={(e) => {
                  if (!formData.phone || validatePhone(formData.phone)) {
                    e.target.style.borderColor = '#667eea';
                  }
                }}
                onBlur={(e) => {
                  if (!formData.phone) {
                    e.target.style.borderColor = '#e1e5e9';
                  }
                }}
              />
              {formData.phone && (
                <div style={{
                  fontSize: '12px',
                  marginTop: '4px',
                  color: validatePhone(formData.phone) ? '#28a745' : '#dc3545'
                }}>
                  {validatePhone(formData.phone) 
                    ? '✓ Valid phone number' 
                    : `${formData.phone.length}/10 digits`
                  }
                </div>
              )}
            </div>
          ) : (
            // Admin Login Form
            <>
              {/* Email Field */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '6px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: '#333'
                }}>
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="Enter your email"
                  style={getInputStyle('email')}
                  onFocus={(e) => {
                    if (!formData.email || validateEmail(formData.email)) {
                      e.target.style.borderColor = '#667eea';
                    }
                  }}
                  onBlur={(e) => {
                    if (!formData.email) {
                      e.target.style.borderColor = '#e1e5e9';
                    }
                  }}
                />
                {formData.email && (
                  <div style={{
                    fontSize: '12px',
                    marginTop: '4px',
                    color: validateEmail(formData.email) ? '#28a745' : '#dc3545'
                  }}>
                    {validateEmail(formData.email) 
                      ? '✓ Valid email format' 
                      : '✗ Invalid email format'
                    }
                  </div>
                )}
              </div>

              {/* Password Field */}
              <div style={{ marginBottom: '20px' }}>
                <label style={{
                  display: 'block',
                  marginBottom: '6px',
                  fontSize: '14px',
                  fontWeight: 'bold',
                  color: '#333'
                }}>
                  Password (min 6 characters)
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  placeholder="Enter your password"
                  style={{
                    width: '100%',
                    padding: '12px',
                    border: `2px solid ${formData.password.length >= 6 ? '#28a745' : '#e1e5e9'}`,
                    borderRadius: '8px',
                    fontSize: '14px',
                    outline: 'none',
                    transition: 'border-color 0.3s ease',
                    boxSizing: 'border-box'
                  }}
                  onFocus={(e) => {
                    if (formData.password.length >= 6) {
                      e.target.style.borderColor = '#667eea';
                    }
                  }}
                  onBlur={(e) => {
                    if (formData.password.length < 6) {
                      e.target.style.borderColor = '#e1e5e9';
                    }
                  }}
                />
                {formData.password && (
                  <div style={{
                    fontSize: '12px',
                    marginTop: '4px',
                    color: formData.password.length >= 6 ? '#28a745' : '#dc3545'
                  }}>
                    {formData.password.length >= 6 
                      ? '✓ Password meets requirements' 
                      : `${formData.password.length}/6 characters minimum`
                    }
                  </div>
                )}
              </div>
            </>
          )}

          {/* Submit Button */}
          <button
            onClick={handleSubmit}
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '14px',
              backgroundColor: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.7 : 1,
              transition: 'all 0.3s ease',
              marginBottom: '20px'
            }}
            onMouseEnter={(e) => {
              if (!isLoading) {
                e.target.style.backgroundColor = '#5a6fd8';
                e.target.style.transform = 'translateY(-2px)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isLoading) {
                e.target.style.backgroundColor = '#667eea';
                e.target.style.transform = 'translateY(0)';
              }
            }}
          >
            {isLoading ? '⏳ Processing...' : (
              authType === 'user' ? '💬 Go to Chat' : '🔐 Admin Sign In'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthSystem;