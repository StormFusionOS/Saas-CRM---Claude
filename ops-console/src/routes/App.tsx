import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '../lib/auth-context';
import LoginPage from '../pages/LoginPage';
import DashboardPage from '../pages/DashboardPage';
import SystemHealth from '../pages/SystemHealth';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/health" element={<SystemHealth />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
