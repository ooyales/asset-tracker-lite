import client from './client';
import type { License } from '@/types';

interface LicenseListResponse {
  licenses: License[];
  total: number;
}

export const licensesApi = {
  getLicenses: async (): Promise<LicenseListResponse> => {
    const { data } = await client.get<LicenseListResponse>('/licenses');
    return data;
  },

  getLicense: async (id: number): Promise<License> => {
    const { data } = await client.get<License>(`/licenses/${id}`);
    return data;
  },

  createLicense: async (license: Partial<License>): Promise<License> => {
    const { data } = await client.post<License>('/licenses', license);
    return data;
  },

  updateLicense: async (id: number, license: Partial<License>): Promise<License> => {
    const { data } = await client.put<License>(`/licenses/${id}`, license);
    return data;
  },

  deleteLicense: async (id: number): Promise<void> => {
    await client.delete(`/licenses/${id}`);
  },
};
