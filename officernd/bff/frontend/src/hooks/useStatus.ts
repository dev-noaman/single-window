import { useState, useEffect, useRef } from 'react';
import { fetchStatus, SyncStatusResponse } from '../api/officernd';

export function useStatus(autoRefresh: boolean = false) {
  const [status, setStatus] = useState<SyncStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const refresh = async () => {
    setLoading(true);
    try {
      const data = await fetchStatus();
      setStatus(data);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    } finally {
      setLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    refresh();
  }, []);

  // Auto-refresh every 5s when sync is running
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(refresh, 5000);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      // Refresh once when sync stops to get final state
      refresh();
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [autoRefresh]);

  return { status, loading, refresh };
}
