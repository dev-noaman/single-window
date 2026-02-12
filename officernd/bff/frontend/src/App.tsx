import { useState } from 'react';
import { StatusBar } from './components/StatusBar';
import { Terminal } from './components/Terminal';
import { ResultsTable } from './components/ResultsTable';
import { ActionButtons } from './components/ActionButtons';
import { useSync } from './hooks/useSync';

function App() {
  const { logs, isPolling, startSync } = useSync();
  const [showResults, setShowResults] = useState(false);

  return (
    <div className="app-container" style={{
      padding: '24px',
      fontFamily: 'Courier New, Courier, monospace',
      backgroundColor: '#0a0a0a',
      color: '#e5e7eb',
      minHeight: '100vh',
      backgroundImage: 'linear-gradient(180deg, #0a0a0a 0%, #111827 100%)',
    }}>
      <header className="app-header" style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
        paddingBottom: '24px',
        borderBottom: '2px solid #1f2937',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        <h1 className="app-title" style={{
          margin: 0,
          fontSize: '28px',
          color: '#f97316',
          fontWeight: 'bold',
          letterSpacing: '2px',
          textShadow: '0 0 10px rgba(249, 115, 22, 0.3)',
        }}>
          &gt; OFFICERND_SYNC
        </h1>
        <div className="app-header-right" style={{ display: 'flex', gap: '24px', alignItems: 'center', flexWrap: 'wrap' }}>
          <StatusBar isPolling={isPolling} />
          <div className="app-header-buttons">
            <button
              onClick={() => setShowResults(!showResults)}
              style={{
                padding: '10px 20px',
                backgroundColor: showResults ? '#1d4ed8' : '#3b82f6',
                color: '#fff',
                border: '2px solid #3b82f6',
                borderRadius: '6px',
                cursor: 'pointer',
                fontFamily: 'Courier New, Courier, monospace',
                fontSize: '14px',
                fontWeight: 'bold',
                letterSpacing: '1px',
                boxShadow: '0 2px 4px rgba(59, 130, 246, 0.3)',
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#1d4ed8'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = showResults ? '#1d4ed8' : '#3b82f6'}
            >
              {showResults ? 'TERMINAL' : 'SHOW'}
            </button>
            <ActionButtons
              isPolling={isPolling}
              onFetch={() => startSync()}
            />
          </div>
        </div>
      </header>
      <main>
        {showResults ? (
          <ResultsTable isPolling={isPolling} />
        ) : (
          <Terminal logs={logs} />
        )}
      </main>
    </div>
  );
}

export default App;
