import { useMemo } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

export const ProtectedRoute = () => {
  const token = useAuthStore((state) => state.token);
  const clearToken = useAuthStore((state) => state.clearToken);

  const isTokenValid = useMemo(() => {
    if (!token) return false;
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(atob(base64));
      
      const isExpired = payload.exp && payload.exp * 1000 < new Date().getTime();
      return !isExpired;
    } catch {
      return false;
    }
  }, [token]);

  if (!isTokenValid) {
    if (token) {
      clearToken();
    }
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
};
