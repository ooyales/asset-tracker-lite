import { create } from 'zustand';
import type { AuthState, User } from '@/types';
import { authApi } from '@/api/auth';

const TOKEN_KEY = 'eaw_token';
const USER_KEY = 'eaw_user';

function loadPersistedState(): { token: string | null; user: User | null } {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const userJson = localStorage.getItem(USER_KEY);
    const user = userJson ? JSON.parse(userJson) : null;
    return { token, user };
  } catch {
    return { token: null, user: null };
  }
}

const persisted = loadPersistedState();

export const useAuthStore = create<AuthState>((set) => ({
  token: persisted.token,
  user: persisted.user,
  isAuthenticated: !!persisted.token,

  login: async (username: string, password: string) => {
    const { token, user } = await authApi.login(username, password);
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    set({ token: null, user: null, isAuthenticated: false });
  },

  setAuth: (token: string, user: User) => {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_KEY, JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },
}));
