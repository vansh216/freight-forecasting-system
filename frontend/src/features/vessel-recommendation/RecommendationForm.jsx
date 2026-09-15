import { useState } from "react";
import { Loader2 } from "lucide-react";
import { getVesselRecommendation } from "./api";

const ORIGIN_PORTS = ["Australia", "Indonesia"];
const DESTINATION_PORTS = ["Paradip", "Vizag", "Gangavaram"];
const VESSEL_TYPES = ["automatic", "Handysize", "Supramax", "Panamax", "Capesize"];

export default function RecommendationForm({ onResult }) {
  const [origin, setOrigin] = useState(ORIGIN_PORTS[0]);
  const [destination, setDestination] = useState(DESTINATION_PORTS[0]);
  const [cargoQty, setCargoQty] = useState(55000);
  const [vesselType, setVesselType] = useState("automatic");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  function getErrorMessage(err) {
    // Axios-style error with a response from the server
    if (err.response) {
      const status = err.response.status;
      const serverMessage =
        err.response.data?.message ||
        err.response.data?.error ||
        (typeof err.response.data === "string" ? err.response.data : null);

      if (status === 400) {
        return serverMessage || "Invalid input. Please check the form and try again.";
      }
      if (status === 401 || status === 403) {
        return "You're not authorized to perform this action.";
      }
      if (status === 404) {
        return "Recommendation service not found. Please contact support.";
      }
      if (status === 429) {
        return "Too many requests. Please wait a moment and try again.";
      }
      if (status >= 500) {
        return serverMessage || "Server error. Please try again in a moment.";
      }
      return serverMessage || `Request failed (${status})`;
    }

    // Axios-style error where the request was made but no response was received
    if (err.request) {
      return "No response from server. Is the backend running?";
    }

    // Fetch API abort / timeout
    if (err.name === "AbortError") {
      return "The request timed out. Please try again.";
    }

    // Fetch API network failure
    if (err instanceof TypeError) {
      return "Network error. Please check your connection and try again.";
    }

    // Fallback
    return err.message || "Something went wrong. Please try again.";
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await getVesselRecommendation({
        cargo_quantity: Number(cargoQty),
        origin,
        destination,
        type: vesselType,
      });

      onResult(data);
    } catch (err) {
      console.error("Vessel recommendation request failed:", err);
      setError(getErrorMessage(err));
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
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Origin Port
          </label>
          <select
            value={origin}
            onChange={(e) => setOrigin(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal focus:border-teal"
          >
            {ORIGIN_PORTS.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Destination Port
          </label>
          <select
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal focus:border-teal"
          >
            {DESTINATION_PORTS.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Vessel Type Preference
          </label>
          <select
            value={vesselType}
            onChange={(e) => setVesselType(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal focus:border-teal"
          >
            {VESSEL_TYPES.map((v) => (
              <option key={v} value={v}>{v === "automatic" ? "Automatic recommendation" : v}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1.5">
            Cargo Quantity (tonnes)
          </label>
          <input
            type="number"
            min="1000"
            step="1000"
            value={cargoQty}
            onChange={(e) => setCargoQty(e.target.value)}
            className="w-full border border-slate-300 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-teal focus:border-teal"
            required
          />
        </div>
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
        {loading ? "Analyzing…" : "Get Vessel Recommendation"}
      </button>
    </form>
  );
}