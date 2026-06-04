import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface UserInfo {
  userId: string;
  role: string;
  organizationId: string;
}

interface AuthState {
  token: string | null;
  user: UserInfo | null;
  setToken: (token: string | null) => void;
  clearToken: () => void;
}

function decodeJwtPayload(token: string): UserInfo | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const payload = JSON.parse(atob(base64));
    return {
      userId: payload.sub || '',
      role: payload.role || '',
      organizationId: payload.org_id || '',
    };
  } catch {
    return null;
  }
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      setToken: (token) => set({ 
        token, 
        user: token ? decodeJwtPayload(token) : null 
      }),
      clearToken: () => set({ token: null, user: null }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => sessionStorage),
    }
  )
);
