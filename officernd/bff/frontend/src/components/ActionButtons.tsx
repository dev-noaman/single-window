import { getExportUrl } from '../api/officernd';

interface ActionButtonsProps {
  isPolling: boolean;
  onFetch: () => void;
}

export function ActionButtons({ isPolling, onFetch }: ActionButtonsProps) {
  const buttonText = isPolling ? 'SYNCING...' : 'FETCH';

  const handleExport = () => {
    window.location.href = getExportUrl();
  };

  return (
    <div style={{ display: 'flex', gap: '12px' }}>
      <button
        onClick={onFetch}
        disabled={isPolling}
        style={{
          padding: '10px 20px',
          backgroundColor: isPolling ? '#4b5563' : '#f97316',
          color: '#fff',
          border: '2px solid #f97316',
          borderRadius: '6px',
          cursor: isPolling ? 'not-allowed' : 'pointer',
          fontFamily: 'Courier New, Courier, monospace',
          fontSize: '14px',
          fontWeight: 'bold',
          letterSpacing: '1px',
          opacity: isPolling ? 0.6 : 1,
          boxShadow: isPolling ? 'none' : '0 2px 4px rgba(249, 115, 22, 0.3)',
        }}
        onMouseOver={(e) => !isPolling && (e.currentTarget.style.backgroundColor = '#ea580c')}
        onMouseOut={(e) => !isPolling && (e.currentTarget.style.backgroundColor = '#f97316')}
      >
        {buttonText}
      </button>
      <button
        onClick={handleExport}
        disabled={isPolling}
        style={{
          padding: '10px 20px',
          backgroundColor: isPolling ? '#4b5563' : '#22c55e',
          color: '#fff',
          border: '2px solid #22c55e',
          borderRadius: '6px',
          cursor: isPolling ? 'not-allowed' : 'pointer',
          fontFamily: 'Courier New, Courier, monospace',
          fontSize: '14px',
          fontWeight: 'bold',
          letterSpacing: '1px',
          opacity: isPolling ? 0.6 : 1,
          boxShadow: isPolling ? 'none' : '0 2px 4px rgba(34, 197, 94, 0.3)',
        }}
        onMouseOver={(e) => !isPolling && (e.currentTarget.style.backgroundColor = '#16a34a')}
        onMouseOut={(e) => !isPolling && (e.currentTarget.style.backgroundColor = '#22c55e')}
      >
        EXPORT
      </button>
    </div>
  );
}
