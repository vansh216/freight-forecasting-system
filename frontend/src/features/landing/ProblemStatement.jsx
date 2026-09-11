export default function ProblemStatement() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-5xl mx-auto px-6">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <span className="text-xs font-semibold tracking-widest uppercase text-teal-dark">
              The Problem
            </span>
            <h2 className="text-3xl font-bold text-navy mt-3 mb-4">
              Reactive chartering costs money and time
            </h2>
            <p className="text-slate-600 leading-relaxed">
              Bulk cargo procurement for India's East Coast ports currently
              relies on daily, manual engagement with the freight market.
              Without forecasting, teams miss favorable rate windows. Without
              systematic vessel matching, cargo gets loaded onto the wrong
              vessel class — leading to idle time, demurrage, and inflated
              logistics costs.
            </p>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
              <p className="text-3xl font-bold text-navy">5</p>
              <p className="text-sm text-slate-500 mt-1">Origin countries tracked</p>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
              <p className="text-3xl font-bold text-navy">7</p>
              <p className="text-sm text-slate-500 mt-1">East Coast discharge ports</p>
            </div>
            <div className="bg-slate-50 border border-slate-200 rounded-xl p-6">
              <p className="text-3xl font-bold text-navy">4</p>
              <p className="text-sm text-slate-500 mt-1">Vessel classes optimized</p>
            </div>
            <div className="bg-teal/10 border border-teal/20 rounded-xl p-6">
              <p className="text-3xl font-bold text-teal-dark">1</p>
              <p className="text-sm text-slate-600 mt-1">Unified decision dashboard</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}