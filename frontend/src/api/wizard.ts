import client from './client';
import type { WizardSession, ImportResult, WizardPreview } from '@/types';

export const wizardApi = {
  createSession: async (): Promise<WizardSession> => {
    const { data } = await client.post<WizardSession>('/wizard/session');
    return data;
  },

  importEntity: async (
    sessionId: string,
    entityType: string,
    payload: string
  ): Promise<ImportResult> => {
    const { data } = await client.post<ImportResult>(`/wizard/${sessionId}/import`, {
      entity_type: entityType,
      data: payload,
    });
    return data;
  },

  getPreview: async (sessionId: string): Promise<WizardPreview> => {
    const { data } = await client.get<WizardPreview>(`/wizard/${sessionId}/preview`);
    return data;
  },

  getStatus: async (sessionId: string): Promise<WizardSession> => {
    const { data } = await client.get<WizardSession>(`/wizard/${sessionId}/status`);
    return data;
  },

  getSample: async (entityType: string): Promise<string> => {
    const { data } = await client.get<{ sample: string }>(`/wizard/sample/${entityType}`);
    return data.sample;
  },

  clearSession: async (sessionId: string): Promise<void> => {
    await client.delete(`/wizard/${sessionId}`);
  },

  commit: async (sessionId: string): Promise<{ message: string }> => {
    const { data } = await client.post<{ message: string }>(`/wizard/${sessionId}/commit`);
    return data;
  },
};
