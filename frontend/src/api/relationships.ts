import client from './client';
import type { GraphData, AssetRelationship } from '@/types';

export const relationshipsApi = {
  getGraph: async (filters?: { asset_type?: string }): Promise<GraphData> => {
    const params: Record<string, string> = {};
    if (filters?.asset_type) params.asset_type = filters.asset_type;
    const { data } = await client.get<GraphData>('/relationships/graph', { params });
    return data;
  },

  getImpact: async (assetId: number): Promise<GraphData> => {
    const { data } = await client.get<GraphData>(`/relationships/impact/${assetId}`);
    return data;
  },

  createRelationship: async (relationship: Partial<AssetRelationship>): Promise<AssetRelationship> => {
    const { data } = await client.post<AssetRelationship>('/relationships', relationship);
    return data;
  },

  deleteRelationship: async (id: number): Promise<void> => {
    await client.delete(`/relationships/${id}`);
  },
};
