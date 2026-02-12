import client from './client';
import type { User } from '@/types';

interface LoginResponse {
  token: string;
  user: User;
}

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const { data } = await client.post<LoginResponse>('/auth/login', {
      username,
      password,
    });
    return data;
  },

  me: async (): Promise<User> => {
    const { data } = await client.get<User>('/auth/me');
    return data;
  },
};
