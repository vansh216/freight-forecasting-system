import { Anchor, Navigation, CheckCircle2 } from "lucide-react";

const statusConfig = {
  en_route: { label: "En Route", icon: Navigation, className: "bg-amber/10 text-amber" },
  arrived: { label: "Arrived", icon: Anchor, className: "bg-teal/10 text-teal-dark" },
  departed: { label: "Departed", icon: CheckCircle2, className: "bg-slate-100 text-slate-500" },
};

function formatTime(isoString) {
  if (!isoString) return "—";
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function ArrivalTable({ arrivals, loading }) {
  if (loading) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center text-slate-400 text-sm">
        Loading arrivals…
      </div>
    );
  }

  if (!arrivals || arrivals.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-2xl p-10 text-center">
        <Anchor size={28} className="mx-auto mb-3 text-slate-300" />
        <p className="text-sm text-slate-500">
          No vessel activity detected for this port right now.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-navy text-white text-xs uppercase tracking-wide">
            <th className="text-left font-semibold px-5 py-3.5">Vessel</th>
            <th className="text-left font-semibold px-5 py-3.5">MMSI</th>
            <th className="text-left font-semibold px-5 py-3.5">Port</th>
            <th className="text-left font-semibold px-5 py-3.5">Status</th>
            <th className="text-left font-semibold px-5 py-3.5">Last Updated</th>
          </tr>
        </thead>
        <tbody>
          {arrivals.map((v, i) => {
            const status = statusConfig[v.status] || statusConfig.en_route;
            const StatusIcon = status.icon;
            return (
              <tr
                key={v.mmsi || i}
                className={`border-t border-slate-100 ${i % 2 === 1 ? "bg-slate-50/50" : ""}`}
              >
                <td className="px-5 py-3.5 font-medium text-navy">{v.vessel_name}</td>
                <td className="px-5 py-3.5 text-slate-500 font-mono text-xs">{v.mmsi}</td>
                <td className="px-5 py-3.5 text-slate-600">{v.port}</td>
                <td className="px-5 py-3.5">
                  <span
                    className={`inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-full ${status.className}`}
                  >
                    <StatusIcon size={12} />
                    {status.label}
                  </span>
                </td>
                <td className="px-5 py-3.5 text-slate-500">{formatTime(v.last_updated)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}