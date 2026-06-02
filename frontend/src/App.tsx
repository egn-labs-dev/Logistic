
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Login } from '@/pages/Login';
import { Register } from '@/pages/Register';
import { Dashboard } from '@/pages/Dashboard';
import { NotFound } from '@/pages/NotFound';
import { ProtectedRoute } from '@/components/ProtectedRoute';
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
        
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
        </Route>
        
        {/* Fallback route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
}

export default App;
