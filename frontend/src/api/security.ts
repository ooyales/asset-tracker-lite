import client from './client';
import type { SecurityBoundary } from '@/types';

interface SecurityBoundaryListResponse {
  boundaries: SecurityBoundary[];
  total_boundaries: number;
  total_cui: number;
  total_fci: number;
}

export const securityApi = {
  getBoundaries: async (): Promise<SecurityBoundaryListResponse> => {
    const { data } = await client.get<SecurityBoundaryListResponse>('/security-boundaries');
    return data;
  },

  getBoundary: async (id: number): Promise<SecurityBoundary> => {
    const { data } = await client.get<SecurityBoundary>(`/security-boundaries/${id}`);
    return data;
  },

  createBoundary: async (boundary: Partial<SecurityBoundary>): Promise<SecurityBoundary> => {
    const { data } = await client.post<SecurityBoundary>('/security-boundaries', boundary);
    return data;
  },

  updateBoundary: async (id: number, boundary: Partial<SecurityBoundary>): Promise<SecurityBoundary> => {
    const { data } = await client.put<SecurityBoundary>(`/security-boundaries/${id}`, boundary);
    return data;
  },
};
