import { useEffect, useState } from 'react';
import {
  Shield,
  ChevronDown,
  ChevronRight,
  Server,
  Monitor,
  Cloud,
  Wifi,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';
import { securityApi } from '@/api/security';
import type { SecurityBoundary, Asset, AssetType } from '@/types';

/* ── Mock Data ──────────────────────────────────────────────────────── */
const MOCK_BOUNDARIES: SecurityBoundary[] = [
  {
    id: 1,
    name: 'CUI Boundary',
    description: 'Controlled Unclassified Information boundary covering all CUI-handling systems. Includes database servers, firewalls, VPN concentrators, and SIEM systems.',
    cmmc_level: 3,
    last_assessment_date: '2025-09-15',
    next_assessment_date: '2026-09-15',
    asset_count: 6,
    stats: { hardware: 2, software: 1, cloud: 0, network: 3, cui_count: 6, fci_count: 0 },
    assets: [
      { id: 1, name: 'Prod-DB-01', asset_type: 'hardware', sub_type: 'Server', status: 'active', classification: 'CUI', description: '', owner_id: null, managed_by_id: null, vendor: 'Dell', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 1, created_at: '', updated_at: '' },
      { id: 3, name: 'Firewall-Edge-01', asset_type: 'network', sub_type: 'Firewall', status: 'active', classification: 'CUI', description: '', owner_id: null, managed_by_id: null, vendor: 'Palo Alto', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 1, created_at: '', updated_at: '' },
      { id: 6, name: 'VPN-Concentrator', asset_type: 'network', sub_type: 'VPN', status: 'maintenance', classification: 'CUI', description: '', owner_id: null, managed_by_id: null, vendor: 'Cisco', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 1, created_at: '', updated_at: '' },
      { id: 7, name: 'Splunk Enterprise', asset_type: 'software', sub_type: 'On-Premise', status: 'active', classification: 'CUI', description: '', owner_id: null, managed_by_id: null, vendor: 'Splunk', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 1, created_at: '', updated_at: '' },
    ] as Asset[],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2025-09-15T10:00:00Z',
  },
  {
    id: 2,
    name: 'FCI Boundary',
    description: 'Federal Contract Information boundary. Covers development workstations, cloud authentication services, and virtual network infrastructure.',
    cmmc_level: 1,
    last_assessment_date: '2025-06-20',
    next_assessment_date: '2026-06-20',
    asset_count: 4,
    stats: { hardware: 1, software: 0, cloud: 2, network: 0, cui_count: 0, fci_count: 4 },
    assets: [
      { id: 2, name: 'AWS-Lambda-AuthService', asset_type: 'cloud', sub_type: 'Lambda', status: 'active', classification: 'FCI', description: '', owner_id: null, managed_by_id: null, vendor: 'AWS', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 2, created_at: '', updated_at: '' },
      { id: 5, name: 'Dev-Workstation-22', asset_type: 'hardware', sub_type: 'Workstation', status: 'active', classification: 'FCI', description: '', owner_id: null, managed_by_id: null, vendor: 'Lenovo', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 2, created_at: '', updated_at: '' },
      { id: 8, name: 'Azure-VNET-Prod', asset_type: 'cloud', sub_type: 'Virtual Network', status: 'active', classification: 'FCI', description: '', owner_id: null, managed_by_id: null, vendor: 'Microsoft Azure', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 2, created_at: '', updated_at: '' },
    ] as Asset[],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2025-06-20T10:00:00Z',
  },
  {
    id: 3,
    name: 'Public Systems',
    description: 'Systems and services that are publicly accessible and do not handle sensitive data. Includes public-facing websites and general network infrastructure.',
    cmmc_level: 0,
    last_assessment_date: null,
    next_assessment_date: null,
    asset_count: 2,
    stats: { hardware: 0, software: 1, cloud: 0, network: 1, cui_count: 0, fci_count: 0 },
    assets: [
      { id: 10, name: 'Switch-Core-01', asset_type: 'network', sub_type: 'Switch', status: 'active', classification: 'Public', description: '', owner_id: null, managed_by_id: null, vendor: 'Cisco', location_id: null, acquired_date: null, warranty_expiry: null, attributes: {}, security_boundary_id: 3, created_at: '', updated_at: '' },
    ] as Asset[],
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2025-01-01T10:00:00Z',
  },
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

const STATUS_BADGE: Record<string, string> = {
  active: 'badge-success',
  retired: 'badge-muted',
  maintenance: 'badge-warning',
  disposed: 'badge-danger',
};

function cmmcBadge(level: number): string {
  if (level >= 3) return 'badge-danger';
  if (level >= 2) return 'badge-warning';
  if (level === 1) return 'badge-info';
  return 'badge-muted';
}

function formatDate(d: string | null): string {
  if (!d) return 'N/A';
  return new Date(d).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

export default function SecurityBoundaryPage() {
  const [boundaries, setBoundaries] = useState<SecurityBoundary[]>(MOCK_BOUNDARIES);
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    securityApi
      .getBoundaries()
      .then((res) => {
        setBoundaries(res.boundaries);
      })
      .catch(() => {
        /* keep mock */
      })
      .finally(() => setLoading(false));
  }, []);

  const toggleExpanded = (id: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const totalCUI = boundaries.reduce((sum, b) => sum + (b.stats?.cui_count || 0), 0);
  const totalFCI = boundaries.reduce((sum, b) => sum + (b.stats?.fci_count || 0), 0);

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-eaw-font">Security Boundaries</h1>
        <p className="text-sm text-eaw-muted mt-1">
          View and manage CMMC security boundaries and their associated assets.
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="kpi-card">
          <div className="kpi-icon bg-blue-50 text-eaw-primary">
            <Shield size={22} />
          </div>
          <div>
            <div className="kpi-value">{boundaries.length}</div>
            <div className="kpi-label">Total Boundaries</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon bg-red-50 text-eaw-danger">
            <AlertTriangle size={22} />
          </div>
          <div>
            <div className="kpi-value">{totalCUI}</div>
            <div className="kpi-label">CUI Assets</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon bg-orange-50 text-eaw-warning">
            <CheckCircle size={22} />
          </div>
          <div>
            <div className="kpi-value">{totalFCI}</div>
            <div className="kpi-label">FCI Assets</div>
          </div>
        </div>
      </div>

      {/* Boundary Cards */}
      <div className="space-y-4">
        {boundaries.map((boundary) => {
          const isExpanded = expandedIds.has(boundary.id);
          return (
            <div key={boundary.id} className="eaw-section">
              {/* Card Header */}
              <div
                className="eaw-section-header"
                onClick={() => toggleExpanded(boundary.id)}
              >
                <span className="flex items-center gap-2">
                  {isExpanded ? (
                    <ChevronDown size={14} />
                  ) : (
                    <ChevronRight size={14} />
                  )}
                  <Shield size={14} />
                  {boundary.name}
                  <span className={cmmcBadge(boundary.cmmc_level)}>
                    CMMC L{boundary.cmmc_level}
                  </span>
                </span>
                <span className="badge-muted">{boundary.asset_count} assets</span>
              </div>

              {/* Card Body (always visible summary) */}
              <div className="px-4 py-3 border-b border-eaw-border-light">
                <p className="text-sm text-eaw-muted mb-3">{boundary.description}</p>
                <div className="flex flex-wrap gap-4 text-xs">
                  {boundary.stats && (
                    <>
                      <span className="flex items-center gap-1">
                        <Server size={12} className="text-eaw-primary" />
                        Hardware: {boundary.stats.hardware}
                      </span>
                      <span className="flex items-center gap-1">
                        <Monitor size={12} className="text-eaw-success" />
                        Software: {boundary.stats.software}
                      </span>
                      <span className="flex items-center gap-1">
                        <Cloud size={12} className="text-purple-600" />
                        Cloud: {boundary.stats.cloud}
                      </span>
                      <span className="flex items-center gap-1">
                        <Wifi size={12} className="text-eaw-warning" />
                        Network: {boundary.stats.network}
                      </span>
                    </>
                  )}
                  <span className="text-eaw-muted">|</span>
                  <span>
                    Last assessment:{' '}
                    <span className="font-medium text-eaw-font">
                      {formatDate(boundary.last_assessment_date)}
                    </span>
                  </span>
                  {boundary.next_assessment_date && (
                    <span>
                      Next:{' '}
                      <span className="font-medium text-eaw-font">
                        {formatDate(boundary.next_assessment_date)}
                      </span>
                    </span>
                  )}
                </div>
              </div>

              {/* Expanded asset list */}
              {isExpanded && boundary.assets && (
                <div className="eaw-section-content p-0">
                  <table className="eaw-table">
                    <thead>
                      <tr>
                        <th>Asset Name</th>
                        <th>Type</th>
                        <th>Sub-Type</th>
                        <th>Status</th>
                        <th>Classification</th>
                        <th>Vendor</th>
                      </tr>
                    </thead>
                    <tbody>
                      {boundary.assets.map((asset) => (
                        <tr key={asset.id}>
                          <td className="font-medium text-eaw-link">
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
                            <span className={STATUS_BADGE[asset.status] || 'badge-muted'}>
                              {asset.status}
                            </span>
                          </td>
                          <td>
                            <span
                              className={
                                asset.classification === 'CUI'
                                  ? 'badge-danger'
                                  : asset.classification === 'FCI'
                                  ? 'badge-warning'
                                  : 'badge-info'
                              }
                            >
                              {asset.classification}
                            </span>
                          </td>
                          <td className="text-eaw-muted">{asset.vendor}</td>
                        </tr>
                      ))}
                      {boundary.assets.length === 0 && (
                        <tr>
                          <td colSpan={6} className="text-center text-eaw-muted py-8">
                            No assets in this boundary.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          );
        })}

        {boundaries.length === 0 && !loading && (
          <div className="eaw-card text-center py-12 text-eaw-muted">
            No security boundaries defined. Use the Data Wizard to import boundaries.
          </div>
        )}
      </div>
    </div>
  );
}
