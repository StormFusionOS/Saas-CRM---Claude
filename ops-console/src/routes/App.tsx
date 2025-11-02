/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../lib/auth-context';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import SystemHealth from '../pages/SystemHealth';
import VisualCheckPage from '../pages/VisualCheckPage';

function App() {
  return (
    <div data-theme="dark">
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/health" element={<SystemHealth />} />
          <Route path="/visual-check" element={<VisualCheckPage />} />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </div>
  );
}

export default App;
