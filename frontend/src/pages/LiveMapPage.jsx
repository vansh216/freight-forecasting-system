import { useState, useEffect, useCallback } from "react";
import { RefreshCw } from "lucide-react";
import VesselMap from "../features/live-map/VesselMap";
import { getLiveVessels } from "../features/live-map/api";

const PORTS = ["All Ports", "Paradip", "Visakhapatnam", "Gangavaram","Gopalpur","Dhamra","Haldia"];
const REFRESH_INTERVAL_MS = 15000;

export default function LiveMapPage() {
  const [selectedPort, setSelectedPort] = useState("All Ports");
  const [vessels, setVessels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchVessels = useCallback(async () => {
    setError(null);
    try {
      const data = await getLiveVessels(selectedPort);
      setVessels(data);
    } catch (err) {
      setError("Could not load live vessel data. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [selectedPort]);

  useEffect(() => {
    setLoading(true);
    fetchVessels();
    const interval = setInterval(fetchVessels, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchVessels]);

  return (
    <div className="max-w-5xl mx-auto px-6 py-16">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <span className="text-xs font-semibold tracking-widest uppercase text-teal-dark">
            Live AIS Tracking
          </span>
          <h1 className="text-3xl font-bold text-navy mt-2 mb-2">Live Vessel Map</h1>
          <p className="text-slate-600">
            Real-time vessel positions near India East Coast ports.
          </p>
        </div>
        <button
          onClick={() => { setLoading(true); fetchVessels(); }}
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

      {!loading && vessels.length === 0 && !error && (
        <p className="mb-4 text-sm text-slate-500">No vessels detected right now.</p>
      )}

      <VesselMap vessels={vessels} />
    </div>
  );
}