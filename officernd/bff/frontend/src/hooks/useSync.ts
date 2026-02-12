import { useState, useCallback, useEffect, useRef } from 'react';
import { triggerSync, fetchProgress, SyncProgressResponse } from '../api/officernd';

export interface LogEntry {
  id: string;
  timestamp: string;
  type: 'ERROR' | 'SUCCESS' | 'PHASE' | 'INFO';
  message: string;
}

export function useSync() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isPolling, setIsPolling] = useState(false);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const autoRunDone = useRef(false);

  const addLog = useCallback((type: 'ERROR' | 'SUCCESS' | 'PHASE' | 'INFO', message: string) => {
    const now = new Date();
    const timestamp = now.toLocaleTimeString('en-US', { hour12: false });
    setLogs((prev) => [
      ...prev,
      { id: `${now.getTime()}-${Math.random()}`, timestamp, type, message },
    ]);
  }, []);

  const startPolling = useCallback(() => {
    if (pollRef.current) return; // already polling
    setIsPolling(true);

    pollRef.current = setInterval(async () => {
      try {
        const progress: SyncProgressResponse = await fetchProgress();

        // Deduplicate by message
        setLogs((prev) => {
          const lastLog = prev[prev.length - 1];
          const newMessage = progress.message || `${progress.phase} (${progress.current}/${progress.total})`;
          if (lastLog && lastLog.message === newMessage) {
            return prev;
          }

          const now = new Date();
          const timestamp = now.toLocaleTimeString('en-US', { hour12: false });
          const type = progress.status === 'error' ? 'ERROR' : 'INFO';

          return [
            ...prev,
            { id: `${now.getTime()}-${Math.random()}`, timestamp, type, message: newMessage },
          ];
        });

        // Stop polling on completion or error
        if (progress.status === 'completed' || progress.status === 'error') {
          if (pollRef.current) clearInterval(pollRef.current);
          pollRef.current = null;
          setIsPolling(false);
          if (progress.status === 'completed') {
            addLog('SUCCESS', progress.message || 'Sync completed successfully');
          } else {
            addLog('ERROR', progress.error || 'Sync failed');
          }
        }
      } catch {
        if (pollRef.current) clearInterval(pollRef.current);
        pollRef.current = null;
        setIsPolling(false);
        addLog('ERROR', 'Failed to fetch progress');
      }
    }, 1500);
  }, [addLog]);

  // On mount: check if sync is running, interrupted, or idle (auto-run smart check)
  useEffect(() => {
    fetchProgress().then(async (progress) => {
      if (progress.status === 'running') {
        addLog('INFO', 'Reconnected to running sync...');
        startPolling();
      } else if (
        progress.status === 'error' &&
        progress.error &&
        progress.error.includes('interrupted')
      ) {
        // Sync was interrupted (server restart/crash) - run smart check instead of full resume
        addLog('INFO', 'Previous sync was interrupted - running smart check...');
        try {
          const response = await triggerSync('smart');
          if (response.success) {
            addLog('INFO', response.message);
            startPolling();
          } else {
            addLog('ERROR', response.message);
          }
        } catch {
          addLog('ERROR', 'Failed to run smart check');
        }
      } else if (progress.status === 'idle' && !autoRunDone.current) {
        // Auto-run smart check on page load
        autoRunDone.current = true;
        addLog('INFO', 'Auto-checking for new companies...');
        try {
          const response = await triggerSync('smart');
          if (response.success) {
            addLog('INFO', response.message);
            startPolling();
          } else {
            addLog('ERROR', response.message);
          }
        } catch {
          addLog('ERROR', 'Failed to auto-check');
        }
      }
    }).catch(() => {});
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [addLog, startPolling]);

  const startSync = useCallback(async () => {
    try {
      const response = await triggerSync('smart');
      if (response.success) {
        addLog('INFO', response.message);
        startPolling();
      } else {
        addLog('ERROR', response.message);
      }
    } catch {
      addLog('ERROR', 'Failed to trigger sync');
    }
  }, [addLog, startPolling]);

  return { logs, isPolling, startSync };
}
