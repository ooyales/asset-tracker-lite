import client from './client';
import type { DashboardData } from '@/types';

export const dashboardApi = {
  getDashboard: async (): Promise<DashboardData> => {
    const { data } = await client.get<DashboardData>('/dashboard');
    return data;
  },
};
