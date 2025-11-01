import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../lib/auth-context';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import LeadsPage from '../pages/LeadsPage';
import InboxPage from '../pages/InboxPage';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/leads" element={<LeadsPage />} />
        <Route path="/inbox" element={<InboxPage />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
