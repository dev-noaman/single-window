export interface SyncStatusResponse {
  success: boolean;
  api_status: 'online' | 'offline';
  companies: number;
  companies_active: number;
  companies_inactive: number;
  companies_synced: number;
  last_sync: string;
  health?: {
    status: string;
    service: string;
  };
  message?: string;
}

export interface SyncProgressResponse {
  status: 'idle' | 'running' | 'completed' | 'error';
  phase: string;
  current: number;
  total: number;
  endpoint: string | null;
  company: string | null;
  message: string | null;
  error: string | null;
  timestamp: number | null;
}

export interface SyncRunResponse {
  success: boolean;
  message: string;
  data?: any;
}

const BASE = '/officernd';

export async function fetchStatus(): Promise<SyncStatusResponse> {
  const response = await fetch(`${BASE}/api/officernd/status`);
  return response.json();
}

export async function fetchProgress(): Promise<SyncProgressResponse> {
  const response = await fetch(`${BASE}/api/officernd/progress`);
  return response.json();
}

export interface CompanyResult {
  company_id: string;
  company_name: string | null;
  status: string;
  endpoints_completed: number;
  endpoints_failed: number;
  records_fetched: number;
  records_upserted: number;
  started_at: string | null;
  completed_at: string | null;
}

export async function fetchCompanyResults(): Promise<CompanyResult[]> {
  const response = await fetch(`${BASE}/api/officernd/companies`);
  return response.json();
}

export interface PhaseEndpoint {
  endpoint: string;
  status: string;
  records_fetched: number;
  records_upserted: number;
  last_run?: string | null;
  error?: string | null;
}

export interface PhaseInfo {
  phase: number;
  name: string;
  status: 'pending' | 'running' | 'completed';
  completed: number;
  total: number;
  sub_status?: string | null;
  globals_completed?: number;
  globals_total?: number;
  endpoints?: PhaseEndpoint[];
}

export interface PhasesResponse {
  current_phase: string;
  phases: PhaseInfo[];
}

export async function fetchPhases(): Promise<PhasesResponse> {
  const response = await fetch(`${BASE}/api/officernd/phases`);
  return response.json();
}

export async function triggerSync(mode: 'full' | 'incremental' | 'smart' = 'smart', resume: boolean = false): Promise<SyncRunResponse> {
  const response = await fetch(`${BASE}/api/officernd/sync/run`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ mode, resume }),
  });
  return response.json();
}

export function getExportUrl(): string {
  return `${BASE}/api/officernd/export`;
}
