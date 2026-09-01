import { create } from 'zustand';
import { User } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: {
    user_id: 'usr_demo_1',
    name: 'Senior Analyst',
    email: 'analyst@enterprise.com',
    role: 'admin',
    subscription: 'enterprise',
    created_at: Date.now(),
    last_login: Date.now(),
  },
  token: 'mock_token_admin',
  isAuthenticated: true,

  setAuth: (user, token) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
    set({ user, token, isAuthenticated: true });
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
