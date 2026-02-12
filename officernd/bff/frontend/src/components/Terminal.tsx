import { useEffect, useRef } from 'react';
import { ProgressLine } from './ProgressLine';

interface LogEntry {
  id: string;
  timestamp: string;
  type: 'ERROR' | 'SUCCESS' | 'PHASE' | 'INFO';
  message: string;
}

interface TerminalProps {
  logs: LogEntry[];
}

export function Terminal({ logs }: TerminalProps) {
  const terminalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div
      ref={terminalRef}
      className="terminal-container terminal-box"
      style={{
        padding: '20px',
        height: '450px',
        overflowY: 'auto',
        fontFamily: 'Courier New, Courier, monospace',
        fontSize: '13px',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
      }}
    >
      {logs.length === 0 && (
        <div style={{ 
          color: '#6b7280', 
          fontStyle: 'italic',
          padding: '10px 0',
        }}>
          <span style={{ color: '#f97316' }}>●</span> OfficeRnD Sync Terminal ready...
        </div>
      )}
      {logs.map((log) => (
        <ProgressLine
          key={log.id}
          timestamp={log.timestamp}
          type={log.type}
          message={log.message}
        />
      ))}
    </div>
  );
}
