/**
 * Copyright (c) 2025 RiverCityClean
 * SPDX-License-Identifier: MIT
 *
 * This file is part of the RiverCityClean SaaS CRM system.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../lib/auth-context';
import Shell from '../components/layout/Shell';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import LeadsPage from '../pages/LeadsPage';
import InboxPage from '../pages/InboxPage';
import VisualCheckPage from '../pages/VisualCheckPage';
import QuotesInvoicesPage from '../pages/QuotesInvoicesPage';
import CalendarPage from '../pages/CalendarPage';
import ReportsPage from '../pages/ReportsPage';
import SEOPage from '../pages/SEOPage';
import HealthPage from '../pages/HealthPage';
import SettingsPage from '../pages/SettingsPage';
import PWAView from '../pages/PWAView';
import ClientPortalPreview from '../pages/ClientPortalPreview';
import EstimatorPage from '../pages/EstimatorPage';
import NavDemoPage from '../pages/NavDemoPage';
// Suite Dashboards
import AIDashboardPage from '../pages/AIDashboardPage';
import SEODashboardPage from '../pages/SEODashboardPage';
import ScrapeDashboardPage from '../pages/ScrapeDashboardPage';
import SalesDashboardPage from '../pages/SalesDashboardPage';
import AdminDashboardPage from '../pages/AdminDashboardPage';
import ServiceCatalogPage from '../pages/ServiceCatalogPage';
import FormulaTestingPage from '../pages/FormulaTestingPage';
import CompliancePage from '../pages/CompliancePage';
// AI Suite Pages
import AIGovernancePage from '../pages/AIGovernancePage';
import AIJobsPage from '../pages/AIJobsPage';
import AIPromptsPage from '../pages/AIPromptsPage';
import AIContextPage from '../pages/AIContextPage';

function App() {
  return (
    <div data-theme="dark">
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Suite Dashboards */}
          <Route path="/ai/dashboard" element={<Shell><AIDashboardPage /></Shell>} />
          <Route path="/ai" element={<Shell><AIDashboardPage /></Shell>} />
          <Route path="/ai/governance" element={<Shell><AIGovernancePage /></Shell>} />
          <Route path="/ai/jobs" element={<Shell><AIJobsPage /></Shell>} />
          <Route path="/ai/prompts" element={<Shell><AIPromptsPage /></Shell>} />
          <Route path="/ai/context" element={<Shell><AIContextPage /></Shell>} />
          <Route path="/seo/dashboard" element={<Shell><SEODashboardPage /></Shell>} />
          <Route path="/scrape/dashboard" element={<Shell><ScrapeDashboardPage /></Shell>} />
          <Route path="/sales/dashboard" element={<Shell><SalesDashboardPage /></Shell>} />
          <Route path="/sales/services" element={<Shell><ServiceCatalogPage /></Shell>} />
          <Route path="/sales/formulas" element={<Shell><FormulaTestingPage /></Shell>} />
          <Route path="/admin/dashboard" element={<Shell><AdminDashboardPage /></Shell>} />
          <Route path="/admin/compliance" element={<Shell><CompliancePage /></Shell>} />

          {/* Legacy/General Routes */}
          <Route path="/dashboard" element={<Shell><DashboardPage /></Shell>} />
          <Route path="/leads" element={<Shell><LeadsPage /></Shell>} />
          <Route path="/estimator" element={<Shell><EstimatorPage /></Shell>} />
          <Route path="/inbox" element={<Shell><InboxPage /></Shell>} />
          <Route path="/quotes" element={<Shell><QuotesInvoicesPage /></Shell>} />
          <Route path="/calendar" element={<Shell><CalendarPage /></Shell>} />
          <Route path="/reports" element={<Shell><ReportsPage /></Shell>} />
          <Route path="/seo" element={<Shell><SEOPage /></Shell>} />
          <Route path="/health" element={<Shell><HealthPage /></Shell>} />
          <Route path="/settings" element={<Shell><SettingsPage /></Shell>} />
          <Route path="/pwa" element={<Shell><PWAView /></Shell>} />
          <Route path="/client-portal" element={<Shell><ClientPortalPreview /></Shell>} />
          <Route path="/visual-check" element={<Shell><VisualCheckPage /></Shell>} />
          <Route path="/nav-demo" element={<NavDemoPage />} />
          <Route path="/" element={<Navigate to="/sales/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </div>
  );
}

export default App;
