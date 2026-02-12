export class SyncProgressDto {
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
