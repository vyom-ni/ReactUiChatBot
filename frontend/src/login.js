import React, { useState } from 'react';

const AuthSystem = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    phone: '',
    confirmPassword: ''
  });
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setMessage('Email and password are required');
      return false;
    }

    if (!isLogin) {
      if (!formData.name || !formData.phone) {
        setMessage('All fields are required for signup');
        return false;
      }
      if (formData.password !== formData.confirmPassword) {
        setMessage('Passwords do not match');
        return false;
      }
      if (formData.password.length < 6) {
        setMessage('Password must be at least 6 characters');
        return false;
      }
      // Basic phone validation
      if (!/^\d{10}$/.test(formData.phone)) {
        setMessage('Phone number must be 10 digits');
        return false;
      }
    }

    // Basic email validation
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setMessage('Please enter a valid email');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    
    if (!validateForm()) return;

    setIsLoading(true);

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/signup';
      const payload = isLogin 
        ? { email: formData.email, password: formData.password }
        : { 
            email: formData.email, 
            password: formData.password, 
            name: formData.name, 
            phone: formData.phone 
          };

      const response = await fetch(`http://localhost:8001${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('userToken', data.token || 'dummy-token');
        localStorage.setItem('userData', JSON.stringify(data.user || {}));
        
        setMessage(data.message || `${isLogin ? 'Login' : 'Signup'} successful!`);
        
        // Redirect to your landing page
        setTimeout(() => {
            window.location.href = '/home';
        }, 1500);
      }else {
        setMessage(data.detail || 'Something went wrong');
      }
    } catch (error) {
      console.error('Error:', error);
      setMessage('Network error. Make sure the backend server is running on port 8000.');
    }

    setIsLoading(false);
  };

  const switchMode = () => {
    setIsLogin(!isLogin);
    setMessage('');
    setFormData({
      email: '',
      password: '',
      name: '',
      phone: '',
      confirmPassword: ''
    });
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
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '30px' }}>
          <h1 style={{
            margin: 0,
            fontSize: '28px',
            color: '#333',
            marginBottom: '8px'
          }}>
            {isLogin ? '🔐 Welcome Back' : '🎉 Join Us'}
          </h1>
          <p style={{
            margin: 0,
            color: '#666',
            fontSize: '14px'
          }}>
            {isLogin ? 'Sign in to your account' : 'Create your new account'}
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

        {/* Form Container */}
        <div>
          {/* Name Field (Signup only) */}
          {!isLogin && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#333'
              }}>
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Enter your full name"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e1e5e9',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
              />
            </div>
          )}

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
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.3s ease',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
            />
          </div>

          {/* Phone Field (Signup only) */}
          {!isLogin && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#333'
              }}>
                Phone Number
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="Enter 10-digit phone number"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e1e5e9',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
              />
            </div>
          )}

          {/* Password Field */}
          <div style={{ marginBottom: '20px' }}>
            <label style={{
              display: 'block',
              marginBottom: '6px',
              fontSize: '14px',
              fontWeight: 'bold',
              color: '#333'
            }}>
              Password
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
                border: '2px solid #e1e5e9',
                borderRadius: '8px',
                fontSize: '14px',
                outline: 'none',
                transition: 'border-color 0.3s ease',
                boxSizing: 'border-box'
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
            />
          </div>

          {/* Confirm Password Field (Signup only) */}
          {!isLogin && (
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '6px',
                fontSize: '14px',
                fontWeight: 'bold',
                color: '#333'
              }}>
                Confirm Password
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Re-enter your password"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e1e5e9',
                  borderRadius: '8px',
                  fontSize: '14px',
                  outline: 'none',
                  transition: 'border-color 0.3s ease',
                  boxSizing: 'border-box'
                }}
                onFocus={(e) => e.target.style.borderColor = '#667eea'}
                onBlur={(e) => e.target.style.borderColor = '#e1e5e9'}
              />
            </div>
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
            {isLoading ? '⏳ Processing...' : (isLogin ? '🔐 Sign In' : '🎉 Create Account')}
          </button>
        </div>

        {/* Switch Mode */}
        <div style={{ textAlign: 'center' }}>
          <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={switchMode}
              style={{
                background: 'none',
                border: 'none',
                color: '#667eea',
                textDecoration: 'underline',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 'bold'
              }}
            >
              {isLogin ? 'Sign Up' : 'Sign In'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default AuthSystem;