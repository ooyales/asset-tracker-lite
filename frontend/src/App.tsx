import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import AppShell from '@/components/layout/AppShell';
import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import AssetListPage from '@/pages/AssetListPage';
import AssetDetailPage from '@/pages/AssetDetailPage';
import RelationshipMapPage from '@/pages/RelationshipMapPage';
import SecurityBoundaryPage from '@/pages/SecurityBoundaryPage';
import LicenseTrackerPage from '@/pages/LicenseTrackerPage';
import DataWizardPage from '@/pages/DataWizardPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="assets" element={<AssetListPage />} />
        <Route path="assets/:id" element={<AssetDetailPage />} />
        <Route path="relationships" element={<RelationshipMapPage />} />
        <Route path="security" element={<SecurityBoundaryPage />} />
        <Route path="licenses" element={<LicenseTrackerPage />} />
        <Route path="data-wizard" element={<DataWizardPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
