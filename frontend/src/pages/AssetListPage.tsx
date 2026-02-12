import { useEffect, useState, useMemo } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Plus, Search, Server, Monitor, Cloud, Wifi, Filter } from 'lucide-react';
import { assetsApi } from '@/api/assets';
import type { Asset, AssetType, AssetStatus, DataClassification, AssetFilters } from '@/types';

/* ── Mock data for initial dev ──────────────────────────────────────── */
const MOCK_ASSETS: Asset[] = [
  { id: 1, name: 'Prod-DB-01', asset_type: 'hardware', sub_type: 'Server', status: 'active', classification: 'CUI', description: 'Primary production database server', owner_id: 1, managed_by_id: 2, owner_name: 'Jane Smith', managed_by_name: 'Bob Johnson', vendor: 'Dell', location_id: 1, location_name: 'DC-East', acquired_date: '2024-03-15', warranty_expiry: '2027-03-15', attributes: { cpu: '32 cores', ram: '256GB', storage: '4TB SSD' }, security_boundary_id: 1, security_boundary_name: 'CUI Boundary', created_at: '2024-03-15T10:00:00Z', updated_at: '2025-11-20T14:30:00Z' },
  { id: 2, name: 'AWS-Lambda-AuthService', asset_type: 'cloud', sub_type: 'Lambda', status: 'active', classification: 'FCI', description: 'Authentication microservice', owner_id: 1, managed_by_id: 1, owner_name: 'Jane Smith', managed_by_name: 'Jane Smith', vendor: 'AWS', location_id: null, location_name: 'AWS us-east-1', acquired_date: '2024-06-01', warranty_expiry: null, attributes: { runtime: 'Python 3.12', memory: '512MB' }, security_boundary_id: 2, security_boundary_name: 'FCI Boundary', created_at: '2024-06-01T08:00:00Z', updated_at: '2025-12-10T09:00:00Z' },
  { id: 3, name: 'Firewall-Edge-01', asset_type: 'network', sub_type: 'Firewall', status: 'active', classification: 'CUI', description: 'Primary edge firewall', owner_id: 2, managed_by_id: 2, owner_name: 'Bob Johnson', managed_by_name: 'Bob Johnson', vendor: 'Palo Alto', location_id: 1, location_name: 'DC-East', acquired_date: '2023-09-20', warranty_expiry: '2026-09-20', attributes: { model: 'PA-5260', firmware: '11.0.3' }, security_boundary_id: 1, security_boundary_name: 'CUI Boundary', created_at: '2023-09-20T12:00:00Z', updated_at: '2025-08-15T16:00:00Z' },
  { id: 4, name: 'Microsoft 365 E5', asset_type: 'software', sub_type: 'SaaS', status: 'active', classification: 'Internal', description: 'Enterprise productivity suite', owner_id: 3, managed_by_id: 1, owner_name: 'Alice Davis', managed_by_name: 'Jane Smith', vendor: 'Microsoft', location_id: null, location_name: null, acquired_date: '2024-01-01', warranty_expiry: null, attributes: { license_type: 'Subscription', seats: 100 }, security_boundary_id: null, security_boundary_name: null, created_at: '2024-01-01T00:00:00Z', updated_at: '2025-12-01T10:00:00Z' },
  { id: 5, name: 'Dev-Workstation-22', asset_type: 'hardware', sub_type: 'Workstation', status: 'active', classification: 'FCI', description: 'Developer workstation', owner_id: 4, managed_by_id: 2, owner_name: 'Charlie Brown', managed_by_name: 'Bob Johnson', vendor: 'Lenovo', location_id: 2, location_name: 'HQ-Floor2', acquired_date: '2025-01-10', warranty_expiry: '2028-01-10', attributes: { model: 'ThinkStation P360', os: 'Windows 11' }, security_boundary_id: 2, security_boundary_name: 'FCI Boundary', created_at: '2025-01-10T09:00:00Z', updated_at: '2025-01-10T09:00:00Z' },
  { id: 6, name: 'VPN-Concentrator', asset_type: 'network', sub_type: 'VPN', status: 'maintenance', classification: 'CUI', description: 'Site-to-site VPN concentrator', owner_id: 2, managed_by_id: 2, owner_name: 'Bob Johnson', managed_by_name: 'Bob Johnson', vendor: 'Cisco', location_id: 1, location_name: 'DC-East', acquired_date: '2022-05-01', warranty_expiry: '2025-05-01', attributes: { model: 'ASA 5555-X' }, security_boundary_id: 1, security_boundary_name: 'CUI Boundary', created_at: '2022-05-01T10:00:00Z', updated_at: '2025-11-01T08:00:00Z' },
  { id: 7, name: 'Splunk Enterprise', asset_type: 'software', sub_type: 'On-Premise', status: 'active', classification: 'Internal', description: 'SIEM and log management', owner_id: 2, managed_by_id: 2, owner_name: 'Bob Johnson', managed_by_name: 'Bob Johnson', vendor: 'Splunk', location_id: 1, location_name: 'DC-East', acquired_date: '2023-07-01', warranty_expiry: null, attributes: { version: '9.2', daily_ingest: '50GB' }, security_boundary_id: 1, security_boundary_name: 'CUI Boundary', created_at: '2023-07-01T10:00:00Z', updated_at: '2025-10-15T11:00:00Z' },
  { id: 8, name: 'Azure-VNET-Prod', asset_type: 'cloud', sub_type: 'Virtual Network', status: 'active', classification: 'FCI', description: 'Production virtual network', owner_id: 1, managed_by_id: 1, owner_name: 'Jane Smith', managed_by_name: 'Jane Smith', vendor: 'Microsoft Azure', location_id: null, location_name: 'Azure East US', acquired_date: '2024-02-01', warranty_expiry: null, attributes: { cidr: '10.0.0.0/16', subnets: 4 }, security_boundary_id: 2, security_boundary_name: 'FCI Boundary', created_at: '2024-02-01T10:00:00Z', updated_at: '2025-09-20T14:00:00Z' },
  { id: 9, name: 'Legacy-ERP-Server', asset_type: 'hardware', sub_type: 'Server', status: 'retired', classification: 'Internal', description: 'Decommissioned ERP server', owner_id: 3, managed_by_id: 2, owner_name: 'Alice Davis', managed_by_name: 'Bob Johnson', vendor: 'HP', location_id: 1, location_name: 'DC-East', acquired_date: '2018-04-01', warranty_expiry: '2021-04-01', attributes: { decommissioned: '2025-06-01' }, security_boundary_id: null, security_boundary_name: null, created_at: '2018-04-01T10:00:00Z', updated_at: '2025-06-01T16:00:00Z' },
  { id: 10, name: 'Switch-Core-01', asset_type: 'network', sub_type: 'Switch', status: 'active', classification: 'Public', description: 'Core network switch', owner_id: 2, managed_by_id: 2, owner_name: 'Bob Johnson', managed_by_name: 'Bob Johnson', vendor: 'Cisco', location_id: 1, location_name: 'DC-East', acquired_date: '2023-01-15', warranty_expiry: '2028-01-15', attributes: { model: 'Catalyst 9300', ports: 48 }, security_boundary_id: null, security_boundary_name: null, created_at: '2023-01-15T10:00:00Z', updated_at: '2025-03-10T12:00:00Z' },
];

const TYPE_ICONS: Record<AssetType, React.ReactNode> = {
  hardware: <Server size={14} />,
  software: <Monitor size={14} />,
  cloud: <Cloud size={14} />,
  network: <Wifi size={14} />,
};

const TYPE_COLORS: Record<AssetType, string> = {
  hardware: 'badge-info',
  software: 'badge-success',
  cloud: 'badge-muted',
  network: 'badge-warning',
};

const STATUS_BADGE: Record<AssetStatus, string> = {
  active: 'badge-success',
  retired: 'badge-muted',
  maintenance: 'badge-warning',
  disposed: 'badge-danger',
  planned: 'badge-info',
};

const CLASSIFICATION_BADGE: Record<DataClassification, string> = {
  CUI: 'badge-danger',
  FCI: 'badge-warning',
  Internal: 'badge-info',
  Public: 'badge-success',
};

export default function AssetListPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [assets, setAssets] = useState<Asset[]>(MOCK_ASSETS);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<AssetFilters>({
    asset_type: '' as AssetType | '',
    status: '' as AssetStatus | '',
    classification: '' as DataClassification | '',
    search: searchParams.get('search') || '',
  });

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    assetsApi
      .getAssets(filters)
      .then((res) => {
        if (!cancelled) setAssets(res.assets);
      })
      .catch(() => {
        /* keep mock */
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [filters]);

  const filteredAssets = useMemo(() => {
    let result = assets;
    if (filters.asset_type) {
      result = result.filter((a) => a.asset_type === filters.asset_type);
    }
    if (filters.status) {
      result = result.filter((a) => a.status === filters.status);
    }
    if (filters.classification) {
      result = result.filter((a) => a.classification === filters.classification);
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(
        (a) =>
          a.name.toLowerCase().includes(q) ||
          a.vendor.toLowerCase().includes(q) ||
          a.description.toLowerCase().includes(q) ||
          (a.owner_name && a.owner_name.toLowerCase().includes(q))
      );
    }
    return result;
  }, [assets, filters]);

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-eaw-font">Asset Inventory</h1>
          <p className="text-sm text-eaw-muted mt-1">
            {filteredAssets.length} asset{filteredAssets.length !== 1 ? 's' : ''} found
          </p>
        </div>
        <button className="btn-primary">
          <Plus size={16} />
          Add Asset
        </button>
      </div>

      {/* Filter Bar */}
      <div className="eaw-card mb-4">
        <div className="flex flex-wrap items-center gap-3">
          <Filter size={16} className="text-eaw-muted" />

          <select
            value={filters.asset_type}
            onChange={(e) =>
              setFilters((f) => ({ ...f, asset_type: e.target.value as AssetType | '' }))
            }
            className="select-field"
          >
            <option value="">All Types</option>
            <option value="hardware">Hardware</option>
            <option value="software">Software</option>
            <option value="cloud">Cloud</option>
            <option value="network">Network</option>
          </select>

          <select
            value={filters.status}
            onChange={(e) =>
              setFilters((f) => ({ ...f, status: e.target.value as AssetStatus | '' }))
            }
            className="select-field"
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="maintenance">Maintenance</option>
            <option value="retired">Retired</option>
            <option value="disposed">Disposed</option>
            <option value="planned">Planned</option>
          </select>

          <select
            value={filters.classification}
            onChange={(e) =>
              setFilters((f) => ({
                ...f,
                classification: e.target.value as DataClassification | '',
              }))
            }
            className="select-field"
          >
            <option value="">All Classifications</option>
            <option value="CUI">CUI</option>
            <option value="FCI">FCI</option>
            <option value="Internal">Internal</option>
            <option value="Public">Public</option>
          </select>

          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search
                size={14}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-eaw-muted"
              />
              <input
                type="text"
                value={filters.search}
                onChange={(e) =>
                  setFilters((f) => ({ ...f, search: e.target.value }))
                }
                placeholder="Search by name, vendor, owner..."
                className="input-field pl-8"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="eaw-section">
        <div className="overflow-x-auto">
          <table className="eaw-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Sub-Type</th>
                <th>Status</th>
                <th>Classification</th>
                <th>Owner</th>
                <th>Location</th>
              </tr>
            </thead>
            <tbody>
              {filteredAssets.map((asset) => (
                <tr
                  key={asset.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/assets/${asset.id}`)}
                >
                  <td className="font-medium text-eaw-link hover:text-eaw-link-hover">
                    <span className="flex items-center gap-2">
                      {TYPE_ICONS[asset.asset_type]}
                      {asset.name}
                    </span>
                  </td>
                  <td>
                    <span className={TYPE_COLORS[asset.asset_type]}>
                      {asset.asset_type}
                    </span>
                  </td>
                  <td className="text-eaw-muted">{asset.sub_type}</td>
                  <td>
                    <span className={STATUS_BADGE[asset.status]}>{asset.status}</span>
                  </td>
                  <td>
                    <span className={CLASSIFICATION_BADGE[asset.classification]}>
                      {asset.classification}
                    </span>
                  </td>
                  <td className="text-eaw-font">{asset.owner_name || '-'}</td>
                  <td className="text-eaw-muted">{asset.location_name || '-'}</td>
                </tr>
              ))}
              {filteredAssets.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center text-eaw-muted py-12">
                    {loading ? 'Loading assets...' : 'No assets match your filters.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
