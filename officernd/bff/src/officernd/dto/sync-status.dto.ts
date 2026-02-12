export class SyncStatusDto {
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
