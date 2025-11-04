/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../lib/auth-context';
import Layout from '../components/Layout';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import SystemHealth from '../pages/SystemHealth';
import VisualCheckPage from '../pages/VisualCheckPage';
import GovernanceDashboard from '../pages/GovernanceDashboard';
import ReviewQueuePage from '../pages/ReviewQueuePage';

function App() {
  return (
    <div data-theme="dark">
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/dashboard" element={<Layout><DashboardPage /></Layout>} />
          <Route path="/health" element={<Layout><SystemHealth /></Layout>} />
          <Route path="/visual-check" element={<Layout><VisualCheckPage /></Layout>} />

          {/* Governance Routes */}
          <Route path="/governance" element={<Layout><GovernanceDashboard /></Layout>} />
          <Route path="/governance/review-queue" element={<Layout><ReviewQueuePage /></Layout>} />

          <Route path="/" element={<Navigate to="/governance" replace />} />
        </Routes>
      </AuthProvider>
    </div>
  );
}

export default App;
