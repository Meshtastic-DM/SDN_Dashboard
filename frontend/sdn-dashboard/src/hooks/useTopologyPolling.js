import { useEffect, useState, useRef } from "react";
import { fetchTopology, fetchEntries } from "../api/topologyApi";

export function useTopologyPolling(pollIntervalMs = 1000) {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [entryCount, setEntryCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    let cancelled = false;

    const fetchAll = async () => {
      try {
        const [topology, entries] = await Promise.all([
          fetchTopology(),
          fetchEntries(),
        ]);

        if (cancelled) return;

        // Only update if topology actually changed
        setGraphData((prev) => {
          const prevStr = JSON.stringify(prev);
          const newStr = JSON.stringify(topology);
          if (prevStr === newStr) {
            return prev; // no change → no re-render
          }
          return topology;
        });

        setEntryCount(entries.count);
        setError(null);
        setLoading(false);
      } catch (err) {
        if (cancelled) return;
        console.error(err);
        setError(err);
        setLoading(false);
      }
    };

    fetchAll();
    intervalRef.current = setInterval(fetchAll, pollIntervalMs);

    return () => {
      cancelled = true;
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [pollIntervalMs]);

  return { graphData, entryCount, loading, error };
}
