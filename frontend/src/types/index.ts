/* ── Core Entity Types ──────────────────────────────────────────────── */

export interface Asset {
  id: number;
  name: string;
  asset_type: AssetType;
  sub_type: string;
  status: AssetStatus;
  classification: DataClassification;
  description: string;
  owner_id: number | null;
  managed_by_id: number | null;
  owner_name?: string | null;
  managed_by_name?: string | null;
  vendor: string;
  location_id: number | null;
  location_name?: string | null;
  acquired_date: string | null;
  warranty_expiry: string | null;
  attributes: Record<string, string | number | boolean>;
  security_boundary_id: number | null;
  security_boundary_name?: string | null;
  created_at: string;
  updated_at: string;
}

export type AssetType = 'hardware' | 'software' | 'cloud' | 'network';
export type AssetStatus = 'active' | 'retired' | 'maintenance' | 'disposed' | 'planned';
export type DataClassification = 'CUI' | 'FCI' | 'Public' | 'Internal';

export interface AssetRelationship {
  id: number;
  source_asset_id: number;
  target_asset_id: number;
  relationship_type: string;
  description: string;
  source_asset_name?: string;
  target_asset_name?: string;
  source_asset_type?: AssetType;
  target_asset_type?: AssetType;
  created_at: string;
}

export interface Person {
  id: number;
  name: string;
  email: string;
  title: string;
  department: string;
  phone: string;
  created_at: string;
}

export interface Location {
  id: number;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  location_type: string;
  created_at: string;
}

export interface SecurityBoundary {
  id: number;
  name: string;
  description: string;
  cmmc_level: number;
  last_assessment_date: string | null;
  next_assessment_date: string | null;
  asset_count: number;
  assets?: Asset[];
  stats?: {
    hardware: number;
    software: number;
    cloud: number;
    network: number;
    cui_count: number;
    fci_count: number;
  };
  created_at: string;
  updated_at: string;
}

export interface License {
  id: number;
  software_name: string;
  vendor: string;
  license_type: string;
  total_seats: number;
  used_seats: number;
  annual_cost: number;
  billing_period: string;
  expiry_date: string;
  auto_renew: boolean;
  status: 'active' | 'expired' | 'cancelled';
  asset_id: number | null;
  asset_name?: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface AssetChange {
  id: number;
  asset_id: number;
  asset_name: string;
  change_type: 'created' | 'updated' | 'deleted' | 'status_change' | 'relationship_added';
  field_changed: string;
  old_value: string;
  new_value: string;
  changed_by: string;
  changed_at: string;
}

/* ── Dashboard Types ───────────────────────────────────────────────── */

export interface DashboardData {
  total_assets: number;
  active_assets: number;
  expiring_licenses: number;
  orphan_assets: number;
  assets_by_type: { name: string; value: number; color: string }[];
  assets_by_status: { name: string; value: number }[];
  classification_breakdown: { name: string; value: number; color: string }[];
  expiring_license_list: License[];
  recent_changes: AssetChange[];
}

/* ── Graph Types ───────────────────────────────────────────────────── */

export interface GraphNode {
  id: string;
  name: string;
  asset_type: AssetType;
  status: AssetStatus;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
  vx?: number;
  vy?: number;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  relationship_type: string;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

/* ── Wizard Types ──────────────────────────────────────────────────── */

export interface WizardSession {
  session_id: string;
  status: string;
  created_at: string;
}

export interface ImportResult {
  entity_type: string;
  created: number;
  updated: number;
  errors: string[];
}

export interface WizardPreview {
  people: Person[];
  locations: Location[];
  security_boundaries: SecurityBoundary[];
  assets: Asset[];
  licenses: License[];
  relationships: AssetRelationship[];
}

/* ── Auth Types ────────────────────────────────────────────────────── */

export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

export interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  setAuth: (token: string, user: User) => void;
}

/* ── Filter Types ──────────────────────────────────────────────────── */

export interface AssetFilters {
  asset_type?: AssetType | '';
  status?: AssetStatus | '';
  classification?: DataClassification | '';
  search?: string;
}
