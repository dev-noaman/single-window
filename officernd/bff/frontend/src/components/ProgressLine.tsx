interface ProgressLineProps {
  timestamp: string;
  type: 'ERROR' | 'SUCCESS' | 'PHASE' | 'INFO';
  message: string;
}

export function ProgressLine({ timestamp, type, message }: ProgressLineProps) {
  const getTypeColor = () => {
    switch (type) {
      case 'ERROR':
        return '#ef4444';
      case 'SUCCESS':
        return '#22c55e';
      case 'PHASE':
        return '#f97316';
      case 'INFO':
      default:
        return '#9ca3af';
    }
  };

  const color = getTypeColor();

  return (
    <div
      className="terminal-line progress-line"
      style={{
        display: 'flex',
        gap: '12px',
        padding: '6px 0',
        fontFamily: 'Courier New, Courier, monospace',
        fontSize: '13px',
        lineHeight: '1.5',
      }}
    >
      <span className="progress-timestamp" style={{ color: '#4b5563', minWidth: '100px', fontWeight: '500' }}>{timestamp}</span>
      <span className="progress-type" style={{ color, fontWeight: 'bold', minWidth: '90px', letterSpacing: '0.5px' }}>[{type}]</span>
      <span style={{ color: '#e5e7eb', wordBreak: 'break-word' }}>{message}</span>
    </div>
  );
}
