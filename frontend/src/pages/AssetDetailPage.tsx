import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  Server,
  Monitor,
  Cloud,
  Wifi,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Clock,
} from 'lucide-react';
import { assetsApi } from '@/api/assets';
import type { Asset, AssetType, AssetRelationship, License, AssetChange } from '@/types';

/* ── Mock Data ──────────────────────────────────────────────────────── */
const MOCK_ASSET: Asset = {
  id: 1,
  name: 'Prod-DB-01',
  asset_type: 'hardware',
  sub_type: 'Server',
  status: 'active',
  classification: 'CUI',
  description: 'Primary production database server running PostgreSQL 16. Handles all transactional data for the CUI boundary.',
  owner_id: 1,
  managed_by_id: 2,
  owner_name: 'Jane Smith',
  managed_by_name: 'Bob Johnson',
  vendor: 'Dell',
  location_id: 1,
  location_name: 'DC-East',
  acquired_date: '2024-03-15',
  warranty_expiry: '2027-03-15',
  attributes: { cpu: '32 cores (AMD EPYC 7543)', ram: '256GB DDR4', storage: '4TB NVMe SSD', os: 'RHEL 9.3', ip_address: '10.1.2.50' },
  security_boundary_id: 1,
  security_boundary_name: 'CUI Boundary',
  created_at: '2024-03-15T10:00:00Z',
  updated_at: '2025-11-20T14:30:00Z',
};

const MOCK_RELATIONSHIPS: AssetRelationship[] = [
  { id: 1, source_asset_id: 1, target_asset_id: 3, relationship_type: 'protected_by', description: 'Firewall protection', source_asset_name: 'Prod-DB-01', target_asset_name: 'Firewall-Edge-01', source_asset_type: 'hardware', target_asset_type: 'network', created_at: '2024-03-15T10:00:00Z' },
  { id: 2, source_asset_id: 1, target_asset_id: 7, relationship_type: 'monitored_by', description: 'Log collection', source_asset_name: 'Prod-DB-01', target_asset_name: 'Splunk Enterprise', source_asset_type: 'hardware', target_asset_type: 'software', created_at: '2024-03-15T10:00:00Z' },
  { id: 3, source_asset_id: 2, target_asset_id: 1, relationship_type: 'connects_to', description: 'Auth service database connection', source_asset_name: 'AWS-Lambda-AuthService', target_asset_name: 'Prod-DB-01', source_asset_type: 'cloud', target_asset_type: 'hardware', created_at: '2024-06-01T08:00:00Z' },
];

const MOCK_LICENSES: License[] = [];

const MOCK_CHANGES: AssetChange[] = [
  { id: 1, asset_id: 1, asset_name: 'Prod-DB-01', change_type: 'status_change', field_changed: 'status', old_value: 'maintenance', new_value: 'active', changed_by: 'admin', changed_at: new Date(Date.now() - 3600000).toISOString() },
  { id: 2, asset_id: 1, asset_name: 'Prod-DB-01', change_type: 'updated', field_changed: 'attributes.os', old_value: 'RHEL 9.2', new_value: 'RHEL 9.3', changed_by: 'admin', changed_at: new Date(Date.now() - 86400000 * 3).toISOString() },
  { id: 3, asset_id: 1, asset_name: 'Prod-DB-01', change_type: 'relationship_added', field_changed: 'relationship', old_value: '', new_value: 'monitored_by Splunk Enterprise', changed_by: 'admin', changed_at: new Date(Date.now() - 86400000 * 10).toISOString() },
  { id: 4, asset_id: 1, asset_name: 'Prod-DB-01', change_type: 'created', field_changed: '', old_value: '', new_value: '', changed_by: 'admin', changed_at: '2024-03-15T10:00:00Z' },
];

const TYPE_ICONS: Record<AssetType, React.ReactNode> = {
  hardware: <Server size={16} />,
  software: <Monitor size={16} />,
  cloud: <Cloud size={16} />,
  network: <Wifi size={16} />,
};

const TYPE_BADGE: Record<AssetType, string> = {
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
  planned: 'badge-info',
};

const CLASSIFICATION_BADGE: Record<string, string> = {
  CUI: 'badge-danger',
  FCI: 'badge-warning',
  Internal: 'badge-info',
  Public: 'badge-success',
};

function formatDate(d: string | null): string {
  if (!d) return '-';
  return new Date(d).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatDateTime(d: string): string {
  return new Date(d).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function changeTypeLabel(ct: string): string {
  switch (ct) {
    case 'created': return 'Created';
    case 'updated': return 'Updated';
    case 'deleted': return 'Deleted';
    case 'status_change': return 'Status Change';
    case 'relationship_added': return 'Relationship Added';
    default: return ct;
  }
}

function changeTypeBadge(ct: string): string {
  switch (ct) {
    case 'created': return 'badge-success';
    case 'updated': return 'badge-info';
    case 'deleted': return 'badge-danger';
    case 'status_change': return 'badge-warning';
    case 'relationship_added': return 'badge-info';
    default: return 'badge-muted';
  }
}

interface CollapsibleSectionProps {
  title: string;
  icon?: React.ReactNode;
  defaultOpen?: boolean;
  count?: number;
  children: React.ReactNode;
}

function CollapsibleSection({ title, icon, defaultOpen = true, count, children }: CollapsibleSectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="eaw-section">
      <div className="eaw-section-header" onClick={() => setOpen(!open)}>
        <span className="flex items-center gap-2">
          {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
          {icon}
          {title}
          {count !== undefined && (
            <span className="badge-muted ml-1">{count}</span>
          )}
        </span>
      </div>
      {open && <div className="eaw-section-content">{children}</div>}
    </div>
  );
}

export default function AssetDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [asset, setAsset] = useState<Asset>(MOCK_ASSET);
  const [relationships, setRelationships] = useState<AssetRelationship[]>(MOCK_RELATIONSHIPS);
  const [licenses, setLicenses] = useState<License[]>(MOCK_LICENSES);
  const [changes, setChanges] = useState<AssetChange[]>(MOCK_CHANGES);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!id) return;
    const numId = parseInt(id, 10);
    if (isNaN(numId)) return;

    let cancelled = false;
    setLoading(true);

    Promise.allSettled([
      assetsApi.getAsset(numId),
      assetsApi.getAssetRelationships(numId),
      assetsApi.getAssetLicenses(numId),
      assetsApi.getAssetChanges(numId),
    ]).then(([assetRes, relRes, licRes, chgRes]) => {
      if (cancelled) return;
      if (assetRes.status === 'fulfilled') setAsset(assetRes.value);
      if (relRes.status === 'fulfilled') setRelationships(relRes.value.relationships || relRes.value);
      if (licRes.status === 'fulfilled') setLicenses(licRes.value.licenses || licRes.value);
      if (chgRes.status === 'fulfilled') setChanges(chgRes.value);
    }).finally(() => {
      if (!cancelled) setLoading(false);
    });

    return () => { cancelled = true; };
  }, [id]);

  if (loading && !asset) {
    return (
      <div className="flex items-center justify-center py-20 text-eaw-muted">
        Loading asset...
      </div>
    );
  }

  const overviewFields = [
    { label: 'Type', value: asset.asset_type, badge: TYPE_BADGE[asset.asset_type] },
    { label: 'Sub-Type', value: asset.sub_type },
    { label: 'Status', value: asset.status, badge: STATUS_BADGE[asset.status] },
    { label: 'Classification', value: asset.classification, badge: CLASSIFICATION_BADGE[asset.classification] },
    { label: 'Owner', value: asset.owner_name || '-' },
    { label: 'Managed By', value: asset.managed_by_name || '-' },
    { label: 'Vendor', value: asset.vendor || '-' },
    { label: 'Location', value: asset.location_name || '-' },
    { label: 'Acquired', value: formatDate(asset.acquired_date) },
    { label: 'Warranty Expiry', value: formatDate(asset.warranty_expiry) },
    { label: 'Security Boundary', value: asset.security_boundary_name || '-' },
    { label: 'Last Updated', value: formatDateTime(asset.updated_at) },
  ];

  return (
    <div>
      {/* Back + Header */}
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-1 text-sm text-eaw-link hover:text-eaw-link-hover mb-4"
      >
        <ArrowLeft size={14} />
        Back
      </button>

      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-gray-100 rounded text-eaw-primary">
          {TYPE_ICONS[asset.asset_type]}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-eaw-font">{asset.name}</h1>
            <span className={TYPE_BADGE[asset.asset_type]}>{asset.asset_type}</span>
            <span className={STATUS_BADGE[asset.status]}>{asset.status}</span>
          </div>
          <p className="text-sm text-eaw-muted mt-0.5">{asset.description}</p>
        </div>
      </div>

      {/* Overview */}
      <CollapsibleSection title="Overview">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3">
          {overviewFields.map((f) => (
            <div key={f.label} className="flex items-baseline gap-2">
              <span className="text-sm text-eaw-muted w-36 flex-shrink-0">{f.label}:</span>
              {f.badge ? (
                <span className={f.badge}>{f.value}</span>
              ) : (
                <span className="text-sm font-medium text-eaw-font">{f.value}</span>
              )}
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {/* Attributes */}
      <CollapsibleSection
        title="Attributes"
        count={Object.keys(asset.attributes || {}).length}
      >
        {Object.keys(asset.attributes || {}).length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-2">
            {Object.entries(asset.attributes).map(([key, val]) => (
              <div key={key} className="flex items-baseline gap-2">
                <span className="text-sm text-eaw-muted w-36 flex-shrink-0 font-mono">
                  {key}:
                </span>
                <span className="text-sm font-medium text-eaw-font">{String(val)}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-eaw-muted">No attributes defined.</p>
        )}
      </CollapsibleSection>

      {/* Relationships */}
      <CollapsibleSection title="Relationships" count={relationships.length}>
        {relationships.length > 0 ? (
          <table className="eaw-table">
            <thead>
              <tr>
                <th>Direction</th>
                <th>Relationship</th>
                <th>Related Asset</th>
                <th>Type</th>
                <th>Description</th>
              </tr>
            </thead>
            <tbody>
              {relationships.map((rel) => {
                const isSource = rel.source_asset_id === asset.id;
                const relatedName = isSource ? rel.target_asset_name : rel.source_asset_name;
                const relatedId = isSource ? rel.target_asset_id : rel.source_asset_id;
                const relatedType = isSource ? rel.target_asset_type : rel.source_asset_type;
                return (
                  <tr key={rel.id}>
                    <td>
                      <span className="badge-muted">
                        {isSource ? 'Outgoing' : 'Incoming'}
                      </span>
                    </td>
                    <td className="font-medium text-eaw-font">{rel.relationship_type}</td>
                    <td>
                      <Link
                        to={`/assets/${relatedId}`}
                        className="flex items-center gap-1 text-eaw-link hover:text-eaw-link-hover"
                      >
                        {relatedType && TYPE_ICONS[relatedType]}
                        {relatedName}
                        <ExternalLink size={12} />
                      </Link>
                    </td>
                    <td>
                      {relatedType && (
                        <span className={TYPE_BADGE[relatedType]}>{relatedType}</span>
                      )}
                    </td>
                    <td className="text-eaw-muted">{rel.description}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <p className="text-sm text-eaw-muted">No relationships defined.</p>
        )}
      </CollapsibleSection>

      {/* Licenses (for software-type assets) */}
      {(asset.asset_type === 'software' || licenses.length > 0) && (
        <CollapsibleSection title="Licenses" count={licenses.length}>
          {licenses.length > 0 ? (
            <table className="eaw-table">
              <thead>
                <tr>
                  <th>Software</th>
                  <th>Vendor</th>
                  <th>Type</th>
                  <th>Seats</th>
                  <th>Cost</th>
                  <th>Expiry</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {licenses.map((lic) => (
                  <tr key={lic.id}>
                    <td className="font-medium text-eaw-font">{lic.software_name}</td>
                    <td>{lic.vendor}</td>
                    <td>{lic.license_type}</td>
                    <td>{lic.used_seats}/{lic.total_seats}</td>
                    <td>${lic.annual_cost.toLocaleString()}</td>
                    <td>{formatDate(lic.expiry_date)}</td>
                    <td>
                      <span className={lic.status === 'active' ? 'badge-success' : 'badge-danger'}>
                        {lic.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-sm text-eaw-muted">No licenses associated with this asset.</p>
          )}
        </CollapsibleSection>
      )}

      {/* Change History */}
      <CollapsibleSection title="Change History" icon={<Clock size={14} />} count={changes.length}>
        {changes.length > 0 ? (
          <div className="space-y-3">
            {changes.map((ch, idx) => (
              <div
                key={ch.id}
                className="flex items-start gap-3 relative"
              >
                {/* Timeline line */}
                {idx < changes.length - 1 && (
                  <div className="absolute left-[11px] top-6 bottom-0 w-px bg-eaw-border" />
                )}
                <div className="w-6 h-6 rounded-full bg-gray-100 border-2 border-eaw-border flex items-center justify-center flex-shrink-0 relative z-10">
                  <div className="w-2 h-2 rounded-full bg-eaw-primary" />
                </div>
                <div className="flex-1 pb-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={changeTypeBadge(ch.change_type)}>
                      {changeTypeLabel(ch.change_type)}
                    </span>
                    {ch.field_changed && (
                      <span className="text-sm text-eaw-font">
                        {ch.field_changed}
                        {ch.old_value && (
                          <>: <span className="line-through text-eaw-muted">{ch.old_value}</span></>
                        )}
                        {ch.new_value && <> &rarr; <span className="font-medium">{ch.new_value}</span></>}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-eaw-muted mt-1">
                    {ch.changed_by} &middot; {formatDateTime(ch.changed_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-eaw-muted">No change history available.</p>
        )}
      </CollapsibleSection>
    </div>
  );
}
