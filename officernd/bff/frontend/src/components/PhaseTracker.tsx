import { useState, useEffect } from 'react';
import { fetchPhases, PhasesResponse, PhaseInfo, PhaseEndpoint } from '../api/officernd';

interface PhaseTrackerProps {
  isPolling: boolean;
}

export function PhaseTracker({ isPolling }: PhaseTrackerProps) {
  const [data, setData] = useState<PhasesResponse | null>(null);
  const [expandedPhase, setExpandedPhase] = useState<number | null>(null);

  const refresh = async () => {
    try {
      const result = await fetchPhases();
      setData(result);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    refresh();
    if (isPolling) {
      const interval = setInterval(refresh, 3000);
      return () => clearInterval(interval);
    }
  }, [isPolling]);

  if (!data || data.phases.length === 0) return null;

  const statusIcon = (s: string) => {
    switch (s) {
      case 'completed': return '\u2713';
      case 'running': return '\u25CF';
      default: return '\u25CB';
    }
  };

  const statusColor = (s: string) => {
    switch (s) {
      case 'completed': return '#22c55e';
      case 'running': return '#3b82f6';
      default: return '#4b5563';
    }
  };

  const progressPct = (p: PhaseInfo) => {
    if (p.total === 0) return 0;
    return Math.round((p.completed / p.total) * 100);
  };

  const togglePhase = (phaseNum: number) => {
    setExpandedPhase(expandedPhase === phaseNum ? null : phaseNum);
  };

  const phaseLabel = (p: PhaseInfo) => {
    if (p.status === 'pending') return 'pending';
    // For Phase 1, show sub_status if available (e.g. "Global endpoints (5/17)")
    if (p.sub_status) return p.sub_status;
    return `${p.completed}/${p.total}`;
  };

  const endpointStatusColor = (s: string) => {
    switch (s) {
      case 'completed': return '#22c55e';
      case 'in_progress': return '#3b82f6';
      case 'failed': return '#ef4444';
      default: return '#4b5563';
    }
  };

  return (
    <div style={{ marginBottom: '16px' }}>
      {/* Phase bars */}
      <div className="phase-bars" style={{
        display: 'flex',
        gap: '8px',
        fontFamily: 'Courier New, Courier, monospace',
      }}>
        {data.phases.map((p) => {
          const hasEndpoints = p.endpoints && p.endpoints.length > 0;
          const isExpanded = expandedPhase === p.phase;
          return (
            <div
              key={p.phase}
              className="phase-card"
              style={{
                flex: p.phase === 1 ? 2 : 1,
                cursor: hasEndpoints ? 'pointer' : 'default',
                borderRadius: '6px',
                border: `1px solid ${p.status === 'running' ? '#3b82f6' : '#1f2937'}`,
                backgroundColor: '#111827',
                padding: '10px 14px',
                transition: 'border-color 0.2s',
              }}
              onClick={() => hasEndpoints && togglePhase(p.phase)}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '6px',
              }}>
                <span style={{
                  fontSize: '12px',
                  fontWeight: 'bold',
                  color: statusColor(p.status),
                }}>
                  <span style={{ marginRight: '6px' }}>
                    {p.status === 'running' ? (
                      <span className="phase-spinner">{statusIcon(p.status)}</span>
                    ) : statusIcon(p.status)}
                  </span>
                  Phase {p.phase}: {p.name}
                </span>
                <span style={{
                  fontSize: '11px',
                  color: statusColor(p.status),
                  fontWeight: 'bold',
                }}>
                  {phaseLabel(p)}
                </span>
              </div>
              {/* Progress bar */}
              <div style={{
                height: '4px',
                backgroundColor: '#1f2937',
                borderRadius: '2px',
                overflow: 'hidden',
              }}>
                <div style={{
                  height: '100%',
                  width: `${progressPct(p)}%`,
                  backgroundColor: statusColor(p.status),
                  borderRadius: '2px',
                  transition: 'width 0.5s ease',
                }} />
              </div>
              {/* Phase 1: show globals progress underneath when running */}
              {p.phase === 1 && p.globals_completed !== undefined && p.globals_total !== undefined && (
                <div style={{
                  fontSize: '10px',
                  color: p.globals_completed === p.globals_total ? '#22c55e' : '#9ca3af',
                  marginTop: '4px',
                }}>
                  Global endpoints: {p.globals_completed}/{p.globals_total}
                  {p.globals_completed === p.globals_total ? ' \u2713' : ''}
                </div>
              )}
              {hasEndpoints && (
                <div style={{
                  fontSize: '10px',
                  color: '#4b5563',
                  marginTop: p.phase === 1 ? '2px' : '4px',
                  textAlign: 'right',
                }}>
                  {isExpanded ? '\u25B2 collapse' : '\u25BC details'}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Expanded endpoint details */}
      {expandedPhase !== null && (() => {
        const phase = data.phases.find(p => p.phase === expandedPhase);
        if (!phase?.endpoints) return null;
        return (
          <div style={{
            marginTop: '8px',
            borderRadius: '6px',
            border: '1px solid #1f2937',
            backgroundColor: '#111827',
            overflow: 'hidden',
          }}>
            <table className="phase-endpoint-table" style={{
              width: '100%',
              borderCollapse: 'collapse',
              fontFamily: 'Courier New, Courier, monospace',
              fontSize: '11px',
            }}>
              <thead>
                <tr>
                  <th style={thStyle}>ENDPOINT</th>
                  <th style={thStyle}>STATUS</th>
                  <th style={thStyle}>FETCHED</th>
                  <th style={thStyle}>UPSERTED</th>
                </tr>
              </thead>
              <tbody>
                {phase.endpoints.map((ep: PhaseEndpoint, i: number) => (
                  <tr key={ep.endpoint} style={{
                    backgroundColor: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                  }}>
                    <td style={tdStyle}>{ep.endpoint}</td>
                    <td style={{ ...tdStyle, color: endpointStatusColor(ep.status), fontWeight: 'bold' }}>
                      {ep.status.toUpperCase()}
                    </td>
                    <td style={{ ...tdStyle, color: '#9ca3af' }}>{ep.records_fetched}</td>
                    <td style={{ ...tdStyle, color: '#9ca3af' }}>{ep.records_upserted}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      })()}

      <style>{`
        @keyframes phase-pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        .phase-spinner {
          display: inline-block;
          animation: phase-pulse 1.2s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}

const thStyle: React.CSSProperties = {
  padding: '6px 12px',
  textAlign: 'left',
  color: '#f97316',
  fontWeight: 'bold',
  fontSize: '10px',
  letterSpacing: '1px',
  borderBottom: '1px solid #374151',
  whiteSpace: 'nowrap',
};

const tdStyle: React.CSSProperties = {
  padding: '4px 12px',
  fontSize: '11px',
  borderBottom: '1px solid #1f2937',
  whiteSpace: 'nowrap',
  color: '#e5e7eb',
};
