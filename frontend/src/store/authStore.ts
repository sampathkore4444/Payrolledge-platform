import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '../types';
import { authApi } from '../services/api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        console.log('AuthStore: Attempting login for', username);
        try {
          const response = await authApi.login({ username, password });
          console.log('AuthStore: Login response', response.data);
          const { access_token } = response.data;
          localStorage.setItem('token', access_token);
          
          const userResponse = await authApi.me();
          set({ token: access_token, user: userResponse.data, isAuthenticated: true });
        } catch (error) {
          console.error('AuthStore: Login error', error);
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('token');
        set({ token: null, user: null, isAuthenticated: false });
      },

      checkAuth: async () => {
        const token = localStorage.getItem('token');
        if (!token) {
          set({ isAuthenticated: false, user: null, token: null });
          return;
        }
        
        try {
          const response = await authApi.me();
          set({ user: response.data, token, isAuthenticated: true });
        } catch {
          localStorage.removeItem('token');
          set({ token: null, user: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token }),
    }
  )
);
