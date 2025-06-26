import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import AuthSystem from './login';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AuthSystem />} />
        <Route path="/home" element={<App />} /> {/* Landing or dashboard */}
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
