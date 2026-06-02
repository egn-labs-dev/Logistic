
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import { Dashboard } from '@/pages/Dashboard';
import { NotFound } from '@/pages/NotFound';
import { PrivacyPolicy } from '@/pages/PrivacyPolicy';
import { TermsOfService } from '@/pages/TermsOfService';
import { ForgotPassword } from '@/pages/ForgotPassword';
import { ResetPassword } from '@/pages/ResetPassword';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { CookieConsent } from '@/components/CookieConsent';
import { useAuthStore } from '@/store/authStore';

function App() {
  const token = useAuthStore((state) => state.token);

  return (
    <Router>
      <Routes>
        <Route 
          path="/login" 
          element={token ? <Navigate to="/" replace /> : <Login />} 
        />
        <Route 
          path="/register" 
          element={token ? <Navigate to="/" replace /> : <Register />} 
        />
        <Route path="/forgot-password" element={token ? <Navigate to="/" replace /> : <ForgotPassword />} />
        <Route path="/reset-password" element={token ? <Navigate to="/" replace /> : <ResetPassword />} />
        
        <Route path="/privacy" element={<PrivacyPolicy />} />
        <Route path="/terms" element={<TermsOfService />} />
        
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
        </Route>
        
        {/* Fallback route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
      <CookieConsent />
    </Router>
  );
}

export default App;
