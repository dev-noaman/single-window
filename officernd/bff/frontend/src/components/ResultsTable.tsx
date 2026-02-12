import { useState, useEffect } from 'react';
import { fetchCompanyResults, CompanyResult } from '../api/officernd';
import { PhaseTracker } from './PhaseTracker';

interface ResultsTableProps {
  isPolling: boolean;
}

export function ResultsTable({ isPolling }: ResultsTableProps) {
  const [companies, setCompanies] = useState<CompanyResult[]>([]);
  const [loading, setLoading] = useState(true);

  const refresh = async () => {
    try {
      const data = await fetchCompanyResults();
      setCompanies(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refresh();
    // Auto-refresh every 5s while syncing
    if (isPolling) {
      const interval = setInterval(refresh, 5000);
      return () => clearInterval(interval);
    }
  }, [isPolling]);

  if (loading) {
    return (
      <div>
        <PhaseTracker isPolling={isPolling} />
        <div style={{ padding: '20px', color: '#6b7280', fontSize: '13px' }}>
          Loading company results...
        </div>
      </div>
    );
  }

  if (companies.length === 0) {
    return (
      <div>
        <PhaseTracker isPolling={isPolling} />
        <div style={{ padding: '20px', color: '#6b7280', fontSize: '13px', fontStyle: 'italic' }}>
          No sync results yet. Run a sync to see company data.
        </div>
      </div>
    );
  }

  const statusColor = (s: string) => {
    switch (s) {
      case 'completed': return '#22c55e';
      case 'partial': return '#eab308';
      case 'in_progress': return '#3b82f6';
      case 'failed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const thStyle: React.CSSProperties = {
    padding: '8px 12px',
    textAlign: 'left',
    color: '#f97316',
    fontWeight: 'bold',
    fontSize: '11px',
    letterSpacing: '1px',
    borderBottom: '2px solid #374151',
    whiteSpace: 'nowrap',
  };

  const tdStyle: React.CSSProperties = {
    padding: '6px 12px',
    fontSize: '12px',
    borderBottom: '1px solid #1f2937',
    whiteSpace: 'nowrap',
  };

  return (
    <div>
      <PhaseTracker isPolling={isPolling} />
      <div style={{
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.3)',
        overflow: 'hidden',
      }}>
      <div className="terminal-container results-scroll" style={{
        maxHeight: '450px',
        overflowY: 'auto',
        overflowX: 'auto',
      }}>
        <table className="results-table" style={{
          width: '100%',
          borderCollapse: 'collapse',
          fontFamily: 'Courier New, Courier, monospace',
          minWidth: '500px',
        }}>
          <thead>
            <tr style={{ position: 'sticky', top: 0, backgroundColor: '#111827', zIndex: 1 }}>
              <th style={thStyle}>#</th>
              <th style={thStyle}>COMPANY</th>
              <th style={thStyle}>STATUS</th>
              <th style={thStyle}>ENDPOINTS</th>
              <th style={thStyle} className="col-hide-mobile">FETCHED</th>
              <th style={thStyle} className="col-hide-mobile">UPSERTED</th>
              <th style={thStyle}>MATCH</th>
            </tr>
          </thead>
          <tbody>
            {companies.map((c, i) => {
              const match = c.records_fetched === c.records_upserted;
              return (
                <tr key={c.company_id} style={{
                  backgroundColor: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,0.02)',
                }}>
                  <td style={{ ...tdStyle, color: '#4b5563' }}>{i + 1}</td>
                  <td className="company-name-cell" style={{ ...tdStyle, color: '#e5e7eb', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {c.company_name || c.company_id}
                  </td>
                  <td style={{ ...tdStyle, color: statusColor(c.status), fontWeight: 'bold' }}>
                    {c.status.toUpperCase()}
                  </td>
                  <td style={tdStyle}>
                    <span style={{ color: '#22c55e' }}>{c.endpoints_completed}</span>
                    {c.endpoints_failed > 0 && (
                      <span style={{ color: '#ef4444' }}>/{c.endpoints_failed}F</span>
                    )}
                  </td>
                  <td className="col-hide-mobile" style={{ ...tdStyle, color: '#9ca3af' }}>{c.records_fetched}</td>
                  <td className="col-hide-mobile" style={{ ...tdStyle, color: '#9ca3af' }}>{c.records_upserted}</td>
                  <td style={tdStyle}>
                    <span style={{
                      color: match ? '#22c55e' : '#ef4444',
                      fontWeight: 'bold',
                    }}>
                      {match ? 'OK' : 'MISMATCH'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="results-footer" style={{
        padding: '8px 12px',
        fontSize: '11px',
        color: '#6b7280',
        borderTop: '1px solid #1f2937',
        display: 'flex',
        justifyContent: 'space-between',
        backgroundColor: '#0d1117',
      }}>
        <span>Total: {companies.length} companies</span>
        <span>
          Fetched: {companies.reduce((s, c) => s + c.records_fetched, 0)} |
          Upserted: {companies.reduce((s, c) => s + c.records_upserted, 0)}
        </span>
      </div>
      </div>
    </div>
  );
}
