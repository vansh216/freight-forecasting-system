import { useState } from "react";
import { Loader2 } from "lucide-react";
import { getForecast } from "./api"; 


const ORIGIN_PORTS = ["Australia", "Indonesia","USA", "Mozambique", "Russia" ];
const DESTINATION_PORTS = ["Paradip", "Visakhapatnam", "Gangavaram","Gopalpur","Dhamra","Sagar/Sandheads","Haldia"];
const VESSEL_TYPES = ["automatic", "Handysize", "Supramax", "Panamax", "Capesize"];
const HORIZON = [30,60,90];

export default function ForecastForm({ onResult }) {
   const [origin, setOrigin] = useState(ORIGIN_PORTS[0]);
  const [destination, setDestination] = useState(DESTINATION_PORTS[0]);
  const [cargoType, setCargoType] = useState("Coal");
  const [cargoQty, setCargoQty] = useState(55000);
  const [vesselType, setVesselType] = useState("automatic");
  const [horizon, setHorizon] = useState(30);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await getForecast({
        origin,
        destination,    
        cargo_type: cargoType,
        cargo_quantity: Number(cargoQty),
        vessel_type: vesselType,
        forecast_horizon: Number(horizon),
      });
      onResult(data);
    } catch (err) {
      setError(
        err.response
          ? `Request failed (${err.response.status})`
          : "Something went wrong. Is the backend running?"
      );
      onResult(null);
    } finally {
      setLoading(false);
    }
}

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white border border-slate-200 rounded-2xl p-7 shadow-sm"
    >
      <div className="grid sm:grid-cols-2 gap-5">
        <Field label="Origin">
          <select value={origin} onChange={(e) => setOrigin(e.target.value)} className={selectClass}>
            {ORIGIN_PORTS.map((o) => <option key={o} value={o}>{o}</option>)}
          </select>
        </Field>

        <Field label="Destination Port">
          <select value={destination} onChange={(e) => setDestination(e.target.value)} className={selectClass}>
            {DESTINATION_PORTS.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </Field>

        <Field label="Cargo Type">
          <select value={cargoType} onChange={(e) => setCargoType(e.target.value)} className={selectClass}>
            {["Coal", "Iron ore", "Grain", "Other dry bulk"].map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </Field>

        <Field label="Cargo Quantity (tonnes)">
          <input
            type="number"
            min="1000"
            step="1000"
            value={cargoQty}
            onChange={(e) => setCargoQty(e.target.value)}
            className={selectClass}
            required
          />
        </Field>

        <Field label="Vessel Type">
          <select value={vesselType} onChange={(e) => setVesselType(e.target.value)} className={selectClass}>
            {VESSEL_TYPES.map((v) => (
              <option key={v} value={v}>{v === "automatic" ? "Automatic" : v}</option>
            ))}
          </select>
        </Field>

        <Field label="Forecast Horizon (days)">
          <select value={horizon} onChange={(e) => setHorizon(e.target.value)} className={selectClass}>
            {HORIZON.map((h) => <option key={h} value={h}>{h}</option>)}
          </select>
        </Field>
      </div>

      {error && (
        <p className="mt-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3.5 py-2.5">
          {error}
        </p>
      )}

      <button
        type="submit"
        disabled={loading}
        className="mt-6 w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-teal hover:bg-teal-dark disabled:opacity-60 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
      >
        {loading && <Loader2 size={16} className="animate-spin" />}
        {loading ? "Forecasting…" : "Generate Forecast"}
      </button>
    </form>
  );
}

const selectClass =
  "w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal focus:border-teal";

function Field({ label, children }) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-1.5">{label}</label>
      {children}
    </div>
  );
}