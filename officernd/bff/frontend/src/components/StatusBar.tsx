import { useStatus } from '../hooks/useStatus';

interface StatusBarProps {
  isPolling?: boolean;
}

export function StatusBar({ isPolling = false }: StatusBarProps) {
  const { status, loading } = useStatus(isPolling);

  if (loading || !status) {
    return (
      <div style={{ padding: '10px', color: '#666', fontSize: '13px' }}>
        <span className="spinner">●</span> Loading...
      </div>
    );
  }

  const statusClass = status.api_status === 'online' ? 'status-online' : 'status-offline';

  return (
    <div className="status-bar" style={{ display: 'flex', gap: '20px', alignItems: 'center', fontSize: '13px', flexWrap: 'wrap' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: '#6b7280', fontWeight: '500' }}>API:</span>
        <span className={statusClass} style={{ fontWeight: 'bold', letterSpacing: '1px' }}>
          {status.api_status.toUpperCase()}
        </span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: '#6b7280', fontWeight: '500' }}>Active:</span>
        <span style={{ color: '#22c55e', fontWeight: '600' }}>{status.companies_active}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: '#6b7280', fontWeight: '500' }}>Inactive:</span>
        <span style={{ color: '#ef4444', fontWeight: '600' }}>{status.companies_inactive}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: '#6b7280', fontWeight: '500' }}>Fetched:</span>
        <span style={{ color: '#e5e7eb', fontWeight: '600' }}>{status.companies}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: '#6b7280', fontWeight: '500' }}>Synced:</span>
        <span style={{ color: '#3b82f6', fontWeight: '600' }}>{status.companies_synced}</span>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ color: '#6b7280', fontWeight: '500' }}>Last Sync:</span>
        <span style={{ color: '#e5e7eb', fontWeight: '600' }}>
          {status.last_sync === 'Never' ? 'Never' : new Date(status.last_sync).toLocaleString()}
        </span>
      </div>
    </div>
  );
}
