import { useState, useEffect, useCallback } from "react";
import { RefreshCw } from "lucide-react";
import ArrivalTable from "../features/arrival-board/ArrivalTable";
import { getArrivals } from "../features/arrival-board/api";

const PORTS = ["All Ports", "Paradip", "Vizag", "Gangavaram"];
const REFRESH_INTERVAL_MS = 5000*60; // auto-refresh every 15s, since this is "live" data

export default function ArrivalBoardPage() {
  const [selectedPort, setSelectedPort] = useState("All Ports");
  const [arrivals, setArrivals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchArrivals = useCallback(async () => {
    setError(null);
    try {
      const data = await getArrivals(selectedPort);
      setArrivals(data);
    } catch (err) {
      setError(
        err.response
          ? `Request failed (${err.response.status})`
          : "Could not load arrivals. Is the backend running?"
      );
    } finally {
      setLoading(false);
    }
  }, [selectedPort]);

  useEffect(() => {
    setLoading(true);
    fetchArrivals();
    const interval = setInterval(fetchArrivals, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchArrivals]);

  return (
    <div className="max-w-5xl mx-auto px-6 py-16">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-10">
        <div>
          <span className="text-xs font-semibold tracking-widest uppercase text-teal-dark">
            Live AIS Tracking
          </span>
          <h1 className="text-3xl font-bold text-navy mt-2 mb-2">Arrival Board</h1>
          <p className="text-slate-600">
            Vessel arrivals and departures across India East Coast ports, updated every 15 seconds.
          </p>
        </div>

        <button
          onClick={() => { setLoading(true); fetchArrivals(); }}
          className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-teal-dark border border-slate-300 hover:border-teal/40 px-4 py-2.5 rounded-lg transition-colors"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      <div className="flex gap-2 mb-6">
        {PORTS.map((port) => (
          <button
            key={port}
            onClick={() => setSelectedPort(port)}
            className={`text-sm font-medium px-4 py-2 rounded-lg transition-colors ${
              selectedPort === port
                ? "bg-navy text-white"
                : "bg-white border border-slate-200 text-slate-600 hover:border-teal/40"
            }`}
          >
            {port}
          </button>
        ))}
      </div>

      {error && (
        <p className="mb-6 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3.5 py-2.5">
          {error}
        </p>
      )}

      <ArrivalTable arrivals={arrivals} loading={loading} />
    </div>
  );
}