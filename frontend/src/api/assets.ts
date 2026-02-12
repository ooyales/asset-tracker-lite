import client from './client';
import type { Asset, AssetFilters, AssetChange } from '@/types';

interface AssetListResponse {
  assets: Asset[];
  total: number;
  page: number;
  per_page: number;
}

export const assetsApi = {
  getAssets: async (filters?: AssetFilters, page = 1, perPage = 50): Promise<AssetListResponse> => {
    const params: Record<string, string | number> = { page, per_page: perPage };
    if (filters?.asset_type) params.asset_type = filters.asset_type;
    if (filters?.status) params.status = filters.status;
    if (filters?.classification) params.classification = filters.classification;
    if (filters?.search) params.search = filters.search;
    const { data } = await client.get<AssetListResponse>('/assets', { params });
    return data;
  },

  getAsset: async (id: number): Promise<Asset> => {
    const { data } = await client.get<Asset>(`/assets/${id}`);
    return data;
  },

  createAsset: async (asset: Partial<Asset>): Promise<Asset> => {
    const { data } = await client.post<Asset>('/assets', asset);
    return data;
  },

  updateAsset: async (id: number, asset: Partial<Asset>): Promise<Asset> => {
    const { data } = await client.put<Asset>(`/assets/${id}`, asset);
    return data;
  },

  deleteAsset: async (id: number): Promise<void> => {
    await client.delete(`/assets/${id}`);
  },

  getAssetRelationships: async (id: number) => {
    const { data } = await client.get(`/assets/${id}/relationships`);
    return data;
  },

  getAssetLicenses: async (id: number) => {
    const { data } = await client.get(`/assets/${id}/licenses`);
    return data;
  },

  getAssetChanges: async (id: number): Promise<AssetChange[]> => {
    const { data } = await client.get<AssetChange[]>(`/assets/${id}/changes`);
    return data;
  },
};
