import { Ship, CheckCircle2, XCircle, Trophy } from "lucide-react";

function formatUsd(value) {
  if (value === null || value === undefined) return "—";
  return `$${value.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
}

export default function RecommendationResult({ result }) {
  if (!result) return null;

  if (result.error || !result.recommended_vessel) {
    return (
      <div className="mt-8 bg-white border border-slate-200 rounded-2xl p-7">
        <div className="flex items-center gap-3 text-slate-600">
          <XCircle size={22} className="text-amber shrink-0" />
          <p className="text-sm">
            {result.error || "No suitable vessel found for these constraints."}
          </p>
        </div>
      </div>
    );
  }

  const topVessel = result.ranked_vessels?.find(
    (v) => v.vessel_type === result.recommended_vessel
  );

  return (
    <div className="mt-8 space-y-6">
      {/* Top recommendation banner */}
      <div className="bg-white border border-teal/30 rounded-2xl p-7">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 rounded-xl bg-teal/10 flex items-center justify-center shrink-0">
            <Trophy size={22} className="text-teal-dark" />
          </div>
          <div className="flex-1">
            <p className="text-xs font-semibold tracking-wide uppercase text-teal-dark mb-1">
              Recommended Vessel
            </p>
            <h3 className="text-2xl font-bold text-navy mb-3">
              {result.recommended_vessel}
              {topVessel && (
                <span className="ml-3 text-sm font-medium text-slate-400">
                  Score {topVessel.score}/100
                </span>
              )}
            </h3>
            <ul className="space-y-1.5">
              {result.reasons?.map((r, i) => (
                <li key={i} className="text-sm text-slate-600 flex items-start gap-2">
                  <CheckCircle2 size={14} className="text-teal-dark mt-0.5 shrink-0" />
                  {r}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* Ranked comparison table */}
      {result.ranked_vessels?.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h4 className="text-sm font-semibold text-navy">Vessel Comparison</h4>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <th className="text-left font-semibold px-5 py-3">Vessel</th>
                  <th className="text-left font-semibold px-5 py-3">Score</th>
                  <th className="text-left font-semibold px-5 py-3">Cost / Tonne</th>
                  <th className="text-left font-semibold px-5 py-3">Total Voyage Cost</th>
                  <th className="text-left font-semibold px-5 py-3">Voyage Duration</th>
                  <th className="text-left font-semibold px-5 py-3">Port Fit</th>
                </tr>
              </thead>
              <tbody>
                {result.ranked_vessels.map((v) => {
                  const isTop = v.vessel_type === result.recommended_vessel;
                  return (
                    <tr
                      key={v.vessel_type}
                      className={`border-t border-slate-100 ${isTop ? "bg-teal/5" : ""}`}
                    >
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <Ship size={14} className={isTop ? "text-teal-dark" : "text-slate-400"} />
                          <span className={`font-medium ${isTop ? "text-teal-dark" : "text-navy"}`}>
                            {v.vessel_type}
                          </span>
                          {!v.feasible && (
                            <span className="text-xs text-red-500 ml-1">infeasible</span>
                          )}
                        </div>
                      </td>
                      <td className="px-5 py-3.5 text-slate-600">{v.score}</td>
                      <td className="px-5 py-3.5 text-slate-600">
                        ${v.estimated_voyage_cost?.toFixed(2)}
                      </td>
                      <td className="px-5 py-3.5 text-slate-600">
                        {formatUsd(v.economics?.total_voyage_cost_usd)}
                      </td>
                      <td className="px-5 py-3.5 text-slate-600">
                        {v.economics?.voyage_duration_days?.toFixed(1)} days
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="flex items-center gap-2">
                          <div className="w-16 h-1.5 bg-slate-100 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-teal"
                              style={{ width: `${v.port_compatibility_score}%` }}
                            />
                          </div>
                          <span className="text-xs text-slate-500">
                            {v.port_compatibility_score?.toFixed(0)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}