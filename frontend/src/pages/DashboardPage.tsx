import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Server,
  CheckCircle,
  AlertTriangle,
  Unlink,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { dashboardApi } from '@/api/dashboard';
import type { DashboardData, License, AssetChange } from '@/types';

/* ── Mock data for initial dev (replaced once API is live) ────────── */
const MOCK_DASHBOARD: DashboardData = {
  total_assets: 142,
  active_assets: 118,
  expiring_licenses: 5,
  orphan_assets: 8,
  assets_by_type: [
    { name: 'Hardware', value: 48, color: '#337ab7' },
    { name: 'Software', value: 52, color: '#5cb85c' },
    { name: 'Cloud', value: 28, color: '#7c3aed' },
    { name: 'Network', value: 14, color: '#f0ad4e' },
  ],
  assets_by_status: [
    { name: 'Active', value: 118 },
    { name: 'Maintenance', value: 12 },
    { name: 'Retired', value: 8 },
    { name: 'Disposed', value: 4 },
  ],
  classification_breakdown: [
    { name: 'CUI', value: 24, color: '#d9534f' },
    { name: 'FCI', value: 36, color: '#f0ad4e' },
    { name: 'Internal', value: 55, color: '#337ab7' },
    { name: 'Public', value: 27, color: '#5cb85c' },
  ],
  expiring_license_list: [
    { id: 1, software_name: 'Microsoft 365 E5', vendor: 'Microsoft', license_type: 'Subscription', total_seats: 100, used_seats: 87, annual_cost: 38400, billing_period: 'Annual', expiry_date: new Date(Date.now() + 15 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
    { id: 2, software_name: 'Adobe Creative Suite', vendor: 'Adobe', license_type: 'Subscription', total_seats: 25, used_seats: 22, annual_cost: 18000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 45 * 86400000).toISOString().split('T')[0], auto_renew: true, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
    { id: 3, software_name: 'Splunk Enterprise', vendor: 'Splunk', license_type: 'Perpetual', total_seats: 5, used_seats: 5, annual_cost: 52000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 120 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
    { id: 4, software_name: 'Jira Software', vendor: 'Atlassian', license_type: 'Subscription', total_seats: 50, used_seats: 41, annual_cost: 7500, billing_period: 'Annual', expiry_date: new Date(Date.now() + 10 * 86400000).toISOString().split('T')[0], auto_renew: true, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
    { id: 5, software_name: 'Tenable.io', vendor: 'Tenable', license_type: 'Subscription', total_seats: 200, used_seats: 142, annual_cost: 28000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 70 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  ],
  recent_changes: [
    { id: 1, asset_id: 12, asset_name: 'Prod-DB-01', change_type: 'status_change', field_changed: 'status', old_value: 'maintenance', new_value: 'active', changed_by: 'admin', changed_at: new Date(Date.now() - 3600000).toISOString() },
    { id: 2, asset_id: 34, asset_name: 'AWS-Lambda-AuthService', change_type: 'updated', field_changed: 'vendor', old_value: '', new_value: 'AWS', changed_by: 'admin', changed_at: new Date(Date.now() - 7200000).toISOString() },
    { id: 3, asset_id: 8, asset_name: 'Firewall-Edge-01', change_type: 'relationship_added', field_changed: 'relationship', old_value: '', new_value: 'protects Prod-DB-01', changed_by: 'admin', changed_at: new Date(Date.now() - 14400000).toISOString() },
    { id: 4, asset_id: 56, asset_name: 'Dev-Workstation-22', change_type: 'created', field_changed: '', old_value: '', new_value: '', changed_by: 'admin', changed_at: new Date(Date.now() - 28800000).toISOString() },
    { id: 5, asset_id: 19, asset_name: 'VPN-Concentrator', change_type: 'updated', field_changed: 'classification', old_value: 'Internal', new_value: 'CUI', changed_by: 'admin', changed_at: new Date(Date.now() - 43200000).toISOString() },
  ],
};

const STATUS_COLORS: Record<string, string> = {
  Active: '#5cb85c',
  Maintenance: '#f0ad4e',
  Retired: '#777',
  Disposed: '#d9534f',
  Planned: '#5bc0de',
};

function daysUntil(dateStr: string): number {
  const d = new Date(dateStr);
  const now = new Date();
  return Math.ceil((d.getTime() - now.getTime()) / 86400000);
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatTime(dateStr: string): string {
  return new Date(dateStr).toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
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
    case 'relationship_added': return 'Relationship';
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

export default function DashboardPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<DashboardData>(MOCK_DASHBOARD);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    dashboardApi
      .getDashboard()
      .then((d) => {
        if (!cancelled) setData(d);
      })
      .catch(() => {
        /* keep mock data */
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, []);

  const kpis = [
    {
      label: 'Total Assets',
      value: data.total_assets,
      icon: <Server size={22} />,
      bg: 'bg-blue-50',
      color: 'text-eaw-primary',
    },
    {
      label: 'Active',
      value: data.active_assets,
      icon: <CheckCircle size={22} />,
      bg: 'bg-green-50',
      color: 'text-eaw-success',
    },
    {
      label: 'Expiring Licenses',
      value: data.expiring_licenses,
      icon: <AlertTriangle size={22} />,
      bg: data.expiring_licenses > 0 ? 'bg-red-50' : 'bg-gray-50',
      color: data.expiring_licenses > 0 ? 'text-eaw-danger' : 'text-eaw-muted',
    },
    {
      label: 'Orphan Assets',
      value: data.orphan_assets,
      icon: <Unlink size={22} />,
      bg: 'bg-orange-50',
      color: 'text-eaw-warning',
    },
  ];

  return (
    <div>
      {/* Page Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-eaw-font">Dashboard</h1>
        <p className="text-sm text-eaw-muted mt-1">
          Overview of your IT asset inventory, compliance, and licensing.
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="kpi-card">
            <div className={`kpi-icon ${kpi.bg} ${kpi.color}`}>{kpi.icon}</div>
            <div>
              <div className="kpi-value">{kpi.value.toLocaleString()}</div>
              <div className="kpi-label">{kpi.label}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
        {/* Assets by Type - Pie */}
        <div className="eaw-card">
          <h3 className="text-sm font-semibold text-eaw-font mb-3">Assets by Type</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={data.assets_by_type}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                dataKey="value"
                nameKey="name"
                paddingAngle={2}
              >
                {data.assets_by_type.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value: string) => (
                  <span className="text-xs text-eaw-font">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Assets by Status - Bar */}
        <div className="eaw-card">
          <h3 className="text-sm font-semibold text-eaw-font mb-3">Assets by Status</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data.assets_by_status} barSize={36}>
              <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
              <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#777' }} />
              <YAxis tick={{ fontSize: 11, fill: '#777' }} />
              <Tooltip />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {data.assets_by_status.map((entry, idx) => (
                  <Cell key={idx} fill={STATUS_COLORS[entry.name] || '#337ab7'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Classification - Pie */}
        <div className="eaw-card">
          <h3 className="text-sm font-semibold text-eaw-font mb-3">Data Classification</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={data.classification_breakdown}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                dataKey="value"
                nameKey="name"
                paddingAngle={2}
              >
                {data.classification_breakdown.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend
                verticalAlign="bottom"
                height={36}
                formatter={(value: string) => (
                  <span className="text-xs text-eaw-font">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Expiring Licenses */}
      <div className="eaw-section mb-6">
        <div className="eaw-section-header">
          <span className="flex items-center gap-2">
            <AlertTriangle size={14} />
            Expiring Licenses
          </span>
          <span className="badge-danger">{data.expiring_license_list.length}</span>
        </div>
        <div className="eaw-section-content p-0">
          <table className="eaw-table">
            <thead>
              <tr>
                <th>Software</th>
                <th>Vendor</th>
                <th>Type</th>
                <th>Seats</th>
                <th>Annual Cost</th>
                <th>Expiry Date</th>
                <th>Auto-Renew</th>
              </tr>
            </thead>
            <tbody>
              {data.expiring_license_list.map((lic) => {
                const days = daysUntil(lic.expiry_date);
                let rowClass = '';
                if (days < 30) rowClass = 'bg-red-50';
                else if (days < 90) rowClass = 'bg-yellow-50';
                return (
                  <tr key={lic.id} className={rowClass}>
                    <td className="font-medium text-eaw-font">{lic.software_name}</td>
                    <td>{lic.vendor}</td>
                    <td>{lic.license_type}</td>
                    <td>
                      {lic.used_seats}/{lic.total_seats}
                    </td>
                    <td>${lic.annual_cost.toLocaleString()}</td>
                    <td>
                      <span className="flex items-center gap-1">
                        {formatDate(lic.expiry_date)}
                        {days < 30 && (
                          <span className="badge-danger ml-1">{days}d</span>
                        )}
                        {days >= 30 && days < 90 && (
                          <span className="badge-warning ml-1">{days}d</span>
                        )}
                      </span>
                    </td>
                    <td>{lic.auto_renew ? 'Yes' : 'No'}</td>
                  </tr>
                );
              })}
              {data.expiring_license_list.length === 0 && (
                <tr>
                  <td colSpan={7} className="text-center text-eaw-muted py-8">
                    No expiring licenses.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Changes */}
      <div className="eaw-section">
        <div className="eaw-section-header">
          <span>Recent Changes</span>
        </div>
        <div className="eaw-section-content p-0">
          <table className="eaw-table">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Change</th>
                <th>Details</th>
                <th>By</th>
                <th>When</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_changes.map((ch) => (
                <tr
                  key={ch.id}
                  className="cursor-pointer"
                  onClick={() => navigate(`/assets/${ch.asset_id}`)}
                >
                  <td className="font-medium text-eaw-link hover:text-eaw-link-hover">
                    {ch.asset_name}
                  </td>
                  <td>
                    <span className={changeTypeBadge(ch.change_type)}>
                      {changeTypeLabel(ch.change_type)}
                    </span>
                  </td>
                  <td className="text-eaw-muted">
                    {ch.field_changed && (
                      <span>
                        {ch.field_changed}
                        {ch.old_value && (
                          <>
                            : <span className="line-through">{ch.old_value}</span>
                          </>
                        )}
                        {ch.new_value && <> &rarr; {ch.new_value}</>}
                      </span>
                    )}
                  </td>
                  <td>{ch.changed_by}</td>
                  <td className="text-eaw-muted whitespace-nowrap">
                    {formatTime(ch.changed_at)}
                  </td>
                </tr>
              ))}
              {data.recent_changes.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center text-eaw-muted py-8">
                    No recent changes.
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
