import { AlertTriangle, Info } from "lucide-react";

// Static/demo alerts for now — swap for a real GET /api/risk-alerts call once that endpoint exists.
const DEMO_ALERTS = [
  {
    level: "medium",
    category: "Market Volatility",
    message: "Supramax freight rates up 6% over the past 2 weeks.",
  },
  {
    level: "low",
    category: "Port Congestion",
    message: "No significant vessel backlog reported at Paradip.",
  },
];

const levelStyles = {
  high: "bg-red-50 border-red-200 text-red-700",
  medium: "bg-amber/10 border-amber/30 text-amber",
  low: "bg-teal/10 border-teal/20 text-teal-dark",
};

export default function RiskAlertSection() {
  return (
    <div className="mt-8">
      <div className="flex items-center gap-2 mb-4">
        <AlertTriangle size={18} className="text-amber" />
        <h3 className="text-sm font-semibold text-navy uppercase tracking-wide">
          Risk Alerts
        </h3>
        <span className="text-xs text-slate-400 flex items-center gap-1">
          <Info size={12} /> Demo data
        </span>
      </div>

      <div className="space-y-3">
        {DEMO_ALERTS.map((alert, i) => (
          <div
            key={i}
            className={`flex items-start gap-3 border rounded-xl px-4 py-3.5 ${levelStyles[alert.level]}`}
          >
            <AlertTriangle size={16} className="mt-0.5 shrink-0" />
            <div>
              <p className="text-sm font-semibold">{alert.category}</p>
              <p className="text-sm opacity-90">{alert.message}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}