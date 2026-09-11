const steps = [
  { n: "01", title: "Freight Forecast", desc: "Time-series model predicts freight rate trend per vessel class." },
  { n: "02", title: "Vessel Feasibility", desc: "Draft, LOA, beam and DWT checked against destination port limits." },
  { n: "03", title: "Vessel Ranking", desc: "Feasible vessels scored on port compatibility and cargo utilization." },
  { n: "04", title: "Voyage Economics", desc: "Freight, fuel, port and waiting costs computed for the voyage." },
  { n: "05", title: "Charter Strategy", desc: "Spot vs. short-term vs. medium-term contract cost comparison." },
  { n: "06", title: "Risk Analysis", desc: "Freight, port, vessel and market risk scored LOW / MEDIUM / HIGH." },
  { n: "07", title: "Final Recommendation", desc: "Market-entry signal and recommended vessel, with clear reasoning." },
];

export default function HowItWorks() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-4xl mx-auto px-6">
        <div className="text-center mb-14">
          <span className="text-xs font-semibold tracking-widest uppercase text-teal-dark">
            Methodology
          </span>
          <h2 className="text-3xl font-bold text-navy mt-3">How it works</h2>
        </div>

        <div className="space-y-0">
          {steps.map((step, i) => (
            <div key={step.n} className="flex gap-6 group">
              <div className="flex flex-col items-center">
                <div className="w-10 h-10 rounded-full bg-navy text-white text-sm font-semibold flex items-center justify-center shrink-0">
                  {step.n}
                </div>
                {i !== steps.length - 1 && (
                  <div className="w-px flex-1 bg-slate-200 my-1" />
                )}
              </div>
              <div className="pb-10">
                <h3 className="font-semibold text-navy mb-1">{step.title}</h3>
                <p className="text-sm text-slate-600">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}