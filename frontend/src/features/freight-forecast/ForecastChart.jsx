import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";

const trendConfig = {
  decreasing: { icon: TrendingDown, color: "text-teal-dark", bg: "bg-teal/10" },
  increasing: { icon: TrendingUp, color: "text-amber", bg: "bg-amber/10" },
  flat: { icon: Minus, color: "text-slate-500", bg: "bg-slate-100" },
};

export default function ForecastChart({ result }) {
  if (!result) return null;

  const trend = trendConfig[result.trend] || trendConfig.flat;
  const TrendIcon = trend.icon;

  const chartData = (result.horizons || []).map((h) => ({
    day: `Day ${h.days}`,
    expected: h.expected_rate,
    range: [h.lower_bound, h.upper_bound],
  }));

  return (
    <div className="mt-8 bg-white border border-slate-200 rounded-2xl p-7">
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <p className="text-xs font-semibold tracking-wide uppercase text-teal-dark mb-1">
            {result.vessel_type} · {result.model_used}
          </p>
          <div className="flex items-baseline gap-3">
            <h3 className="text-2xl font-bold text-navy">
              ${result.current_rate?.toFixed(2)}
              <span className="text-sm font-normal text-slate-400"> current</span>
            </h3>
            <span className="text-slate-300">→</span>
            <h3 className="text-2xl font-bold text-navy">
              ${result.forecast_rate?.toFixed(2)}
              <span className="text-sm font-normal text-slate-400"> forecast</span>
            </h3>
          </div>
        </div>

        <div className={`flex items-center gap-2 px-4 py-2 rounded-full ${trend.bg}`}>
          <TrendIcon size={16} className={trend.color} />
          <span className={`text-sm font-semibold capitalize ${trend.color}`}>
            {result.trend}
          </span>
        </div>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
            <XAxis dataKey="day" tick={{ fontSize: 12, fill: "#64748b" }} />
            <YAxis tick={{ fontSize: 12, fill: "#64748b" }} />
            <Tooltip
              contentStyle={{ borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 13 }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area
              type="monotone"
              dataKey="range"
              stroke="none"
              fill="#0d948820"
              name="Confidence range"
            />
            <Line
              type="monotone"
              dataKey="expected"
              stroke="#0d9488"
              strokeWidth={2.5}
              dot={{ r: 3, fill: "#0d9488" }}
              name="Expected rate"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4 pt-6 border-t border-slate-100">
        <Stat label="Confidence" value={`${(result.confidence * 100).toFixed(0)}%`} />
        <Stat label="Volatility" value={result.volatility} />
        <Stat label="Market Entry" value={result.market_entry?.signal || "—"} />
        <Stat label="Model" value={result.model_used?.split(":")[0] || "—"} small />
      </div>
    </div>
  );
}

function Stat({ label, value, small }) {
  return (
    <div>
      <p className="text-xs text-slate-400 mb-1">{label}</p>
      <p className={`font-semibold text-navy ${small ? "text-xs" : "text-sm"}`}>{value}</p>
    </div>
  );
}