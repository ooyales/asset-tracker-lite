import { useEffect, useState, useMemo } from 'react';
import {
  Key,
  DollarSign,
  Users,
  BarChart3,
  AlertTriangle,
} from 'lucide-react';
import { licensesApi } from '@/api/licenses';
import type { License } from '@/types';

/* ── Mock Data ──────────────────────────────────────────────────────── */
const MOCK_LICENSES: License[] = [
  { id: 1, software_name: 'Microsoft 365 E5', vendor: 'Microsoft', license_type: 'Subscription', total_seats: 100, used_seats: 87, annual_cost: 38400, billing_period: 'Annual', expiry_date: new Date(Date.now() + 15 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 2, software_name: 'Adobe Creative Suite', vendor: 'Adobe', license_type: 'Subscription', total_seats: 25, used_seats: 22, annual_cost: 18000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 45 * 86400000).toISOString().split('T')[0], auto_renew: true, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 3, software_name: 'Splunk Enterprise', vendor: 'Splunk', license_type: 'Perpetual', total_seats: 5, used_seats: 5, annual_cost: 52000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 120 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 4, software_name: 'Jira Software', vendor: 'Atlassian', license_type: 'Subscription', total_seats: 50, used_seats: 41, annual_cost: 7500, billing_period: 'Annual', expiry_date: new Date(Date.now() + 10 * 86400000).toISOString().split('T')[0], auto_renew: true, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 5, software_name: 'Tenable.io', vendor: 'Tenable', license_type: 'Subscription', total_seats: 200, used_seats: 142, annual_cost: 28000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 70 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 6, software_name: 'GitHub Enterprise', vendor: 'GitHub', license_type: 'Subscription', total_seats: 30, used_seats: 28, annual_cost: 6300, billing_period: 'Annual', expiry_date: new Date(Date.now() + 200 * 86400000).toISOString().split('T')[0], auto_renew: true, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 7, software_name: 'Slack Business+', vendor: 'Salesforce', license_type: 'Subscription', total_seats: 75, used_seats: 62, annual_cost: 11250, billing_period: 'Annual', expiry_date: new Date(Date.now() + 150 * 86400000).toISOString().split('T')[0], auto_renew: true, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 8, software_name: 'Palo Alto Panorama', vendor: 'Palo Alto', license_type: 'Subscription', total_seats: 10, used_seats: 3, annual_cost: 15000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 280 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 9, software_name: 'CrowdStrike Falcon', vendor: 'CrowdStrike', license_type: 'Subscription', total_seats: 150, used_seats: 130, annual_cost: 45000, billing_period: 'Annual', expiry_date: new Date(Date.now() + 25 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'active', asset_id: null, notes: '', created_at: '', updated_at: '' },
  { id: 10, software_name: 'AutoCAD LT', vendor: 'Autodesk', license_type: 'Perpetual', total_seats: 5, used_seats: 2, annual_cost: 2100, billing_period: 'Annual', expiry_date: new Date(Date.now() - 30 * 86400000).toISOString().split('T')[0], auto_renew: false, status: 'expired', asset_id: null, notes: 'Expired, needs renewal', created_at: '', updated_at: '' },
];

function daysUntil(dateStr: string): number {
  const d = new Date(dateStr);
  const now = new Date();
  return Math.ceil((d.getTime() - now.getTime()) / 86400000);
}

function formatDate(d: string): string {
  return new Date(d).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatCurrency(n: number): string {
  return '$' + n.toLocaleString();
}

export default function LicenseTrackerPage() {
  const [licenses, setLicenses] = useState<License[]>(MOCK_LICENSES);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    licensesApi
      .getLicenses()
      .then((res) => setLicenses(res.licenses))
      .catch(() => {
        /* keep mock */
      })
      .finally(() => setLoading(false));
  }, []);

  const stats = useMemo(() => {
    const totalCost = licenses.reduce((sum, l) => sum + l.annual_cost, 0);
    const totalSeats = licenses.reduce((sum, l) => sum + l.total_seats, 0);
    const usedSeats = licenses.reduce((sum, l) => sum + l.used_seats, 0);
    const avgUtil = totalSeats > 0 ? Math.round((usedSeats / totalSeats) * 100) : 0;
    const expiringSoon = licenses.filter(
      (l) => l.status === 'active' && daysUntil(l.expiry_date) <= 90 && daysUntil(l.expiry_date) > 0
    ).length;
    return { totalCost, totalSeats, avgUtil, expiringSoon };
  }, [licenses]);

  // Sort: expired first, then by expiry date ascending
  const sortedLicenses = useMemo(() => {
    return [...licenses].sort((a, b) => {
      if (a.status === 'expired' && b.status !== 'expired') return -1;
      if (b.status === 'expired' && a.status !== 'expired') return 1;
      return new Date(a.expiry_date).getTime() - new Date(b.expiry_date).getTime();
    });
  }, [licenses]);

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-eaw-font">License Tracker</h1>
        <p className="text-sm text-eaw-muted mt-1">
          Monitor software licenses, utilization, and upcoming renewals.
        </p>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="kpi-card">
          <div className="kpi-icon bg-green-50 text-eaw-success">
            <DollarSign size={22} />
          </div>
          <div>
            <div className="kpi-value">{formatCurrency(stats.totalCost)}</div>
            <div className="kpi-label">Total Annual Cost</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon bg-blue-50 text-eaw-primary">
            <Users size={22} />
          </div>
          <div>
            <div className="kpi-value">{stats.totalSeats.toLocaleString()}</div>
            <div className="kpi-label">Total Seats</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className="kpi-icon bg-purple-50 text-purple-600">
            <BarChart3 size={22} />
          </div>
          <div>
            <div className="kpi-value">{stats.avgUtil}%</div>
            <div className="kpi-label">Avg Utilization</div>
          </div>
        </div>
        <div className="kpi-card">
          <div className={`kpi-icon ${stats.expiringSoon > 0 ? 'bg-red-50 text-eaw-danger' : 'bg-gray-50 text-eaw-muted'}`}>
            <AlertTriangle size={22} />
          </div>
          <div>
            <div className="kpi-value">{stats.expiringSoon}</div>
            <div className="kpi-label">Expiring Soon</div>
          </div>
        </div>
      </div>

      {/* License Table */}
      <div className="eaw-section">
        <div className="eaw-section-header">
          <span className="flex items-center gap-2">
            <Key size={14} />
            All Licenses
          </span>
          <span className="badge-muted">{licenses.length}</span>
        </div>
        {/* Desktop table */}
        <div className="eaw-section-content p-0 overflow-x-auto hidden md:block">
          <table className="eaw-table">
            <thead>
              <tr>
                <th>Software</th>
                <th>Vendor</th>
                <th>Type</th>
                <th>Seats</th>
                <th>Utilization</th>
                <th>Cost / Period</th>
                <th>Expiry Date</th>
                <th>Auto-Renew</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {sortedLicenses.map((lic) => {
                const days = daysUntil(lic.expiry_date);
                const utilPct =
                  lic.total_seats > 0
                    ? Math.round((lic.used_seats / lic.total_seats) * 100)
                    : 0;

                let rowClass = '';
                if (lic.status === 'expired' || days < 0) rowClass = 'bg-red-50';
                else if (days < 30) rowClass = 'bg-red-50';
                else if (days < 90) rowClass = 'bg-yellow-50';

                let utilColor = 'bg-eaw-success';
                if (utilPct > 90) utilColor = 'bg-eaw-danger';
                else if (utilPct > 75) utilColor = 'bg-eaw-warning';

                return (
                  <tr key={lic.id} className={rowClass}>
                    <td className="font-medium text-eaw-font">{lic.software_name}</td>
                    <td className="text-eaw-muted">{lic.vendor}</td>
                    <td>
                      <span className="badge-info">{lic.license_type}</span>
                    </td>
                    <td>
                      <span className="text-eaw-font">
                        {lic.used_seats}
                        <span className="text-eaw-muted">/{lic.total_seats}</span>
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${utilColor}`}
                            style={{ width: `${Math.min(utilPct, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-eaw-muted">{utilPct}%</span>
                      </div>
                    </td>
                    <td className="font-medium text-eaw-font">
                      {formatCurrency(lic.annual_cost)}
                      <span className="text-xs text-eaw-muted ml-1">
                        / {lic.billing_period}
                      </span>
                    </td>
                    <td>
                      <div className="flex items-center gap-1">
                        <span className="whitespace-nowrap">{formatDate(lic.expiry_date)}</span>
                        {days < 0 && <span className="badge-danger">Expired</span>}
                        {days >= 0 && days < 30 && (
                          <span className="badge-danger">{days}d</span>
                        )}
                        {days >= 30 && days < 90 && (
                          <span className="badge-warning">{days}d</span>
                        )}
                      </div>
                    </td>
                    <td>
                      {lic.auto_renew ? (
                        <span className="badge-success">Yes</span>
                      ) : (
                        <span className="badge-muted">No</span>
                      )}
                    </td>
                    <td>
                      <span
                        className={
                          lic.status === 'active'
                            ? 'badge-success'
                            : lic.status === 'expired'
                            ? 'badge-danger'
                            : 'badge-muted'
                        }
                      >
                        {lic.status}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {licenses.length === 0 && (
                <tr>
                  <td colSpan={9} className="text-center text-eaw-muted py-12">
                    {loading ? 'Loading licenses...' : 'No licenses found.'}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Mobile cards */}
        <div className="md:hidden mobile-card-table p-3">
          {sortedLicenses.map((lic) => {
            const days = daysUntil(lic.expiry_date);
            const utilPct = lic.total_seats > 0 ? Math.round((lic.used_seats / lic.total_seats) * 100) : 0;
            let utilColor = 'bg-eaw-success';
            if (utilPct > 90) utilColor = 'bg-eaw-danger';
            else if (utilPct > 75) utilColor = 'bg-eaw-warning';

            return (
              <div
                key={lic.id}
                className={`mobile-card-row ${(lic.status === 'expired' || days < 0) ? 'border-l-4 border-l-red-400' : days < 30 ? 'border-l-4 border-l-red-400' : days < 90 ? 'border-l-4 border-l-yellow-400' : ''}`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-eaw-font">{lic.software_name}</span>
                  <span className={lic.status === 'active' ? 'badge-success' : lic.status === 'expired' ? 'badge-danger' : 'badge-muted'}>
                    {lic.status}
                  </span>
                </div>
                <div className="text-xs text-eaw-muted mb-2">{lic.vendor} &middot; <span className="badge-info">{lic.license_type}</span></div>
                <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-sm">
                  <span className="text-eaw-muted">Seats</span>
                  <span className="text-right font-medium">{lic.used_seats}/{lic.total_seats}</span>
                  <span className="text-eaw-muted">Utilization</span>
                  <span className="text-right flex items-center justify-end gap-1.5">
                    <span className="w-12 h-1.5 bg-gray-200 rounded-full overflow-hidden inline-block">
                      <span className={`block h-full rounded-full ${utilColor}`} style={{ width: `${Math.min(utilPct, 100)}%` }} />
                    </span>
                    <span className="text-xs">{utilPct}%</span>
                  </span>
                  <span className="text-eaw-muted">Cost</span>
                  <span className="text-right font-medium">{formatCurrency(lic.annual_cost)}<span className="text-xs text-eaw-muted ml-0.5">/{lic.billing_period}</span></span>
                  <span className="text-eaw-muted">Expires</span>
                  <span className="text-right">
                    {formatDate(lic.expiry_date)}
                    {days < 0 && <span className="badge-danger ml-1">Expired</span>}
                    {days >= 0 && days < 30 && <span className="badge-danger ml-1">{days}d</span>}
                    {days >= 30 && days < 90 && <span className="badge-warning ml-1">{days}d</span>}
                  </span>
                  <span className="text-eaw-muted">Auto-Renew</span>
                  <span className="text-right">{lic.auto_renew ? 'Yes' : 'No'}</span>
                </div>
              </div>
            );
          })}
          {licenses.length === 0 && (
            <div className="text-center text-eaw-muted py-12 text-sm">
              {loading ? 'Loading licenses...' : 'No licenses found.'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
