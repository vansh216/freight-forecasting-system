import { useNavigate } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export default function Hero() {
  const navigate = useNavigate();

  return (
    <section className="relative h-[85vh] min-h-[560px] flex items-center overflow-hidden">
      {/* Background video */}
      <video
        className="absolute inset-0 w-full h-full object-cover"
        autoPlay
        muted
        loop
        playsInline
        src="/video/bg.video.mp4"
      />
      {/* Dark overlay so text stays readable */}
      <div className="absolute inset-0 bg-navy/70" />

      <div className="relative z-10 max-w-4xl mx-auto px-6 text-center text-white">
        <span className="inline-block text-xs font-semibold tracking-widest uppercase text-amber-light mb-4">
          Bulk Cargo · India East Coast
        </span>
        <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6">
          Freight Intelligence &amp; Chartering
          <br /> Decision Support System
        </h1>
        <p className="text-lg text-slate-200 mb-8 max-w-2xl mx-auto">
          Move from reactive, daily market tracking to data-driven vessel
          chartering — forecasting, vessel recommendation, and risk alerts
          in one place.
        </p>
        <button
          onClick={() => navigate("/vessel-recommendation")}
          className="inline-flex items-center gap-2 bg-teal hover:bg-teal-dark text-white font-semibold px-7 py-3.5 rounded-lg transition-colors"
        >
          Get Recommendation
          <ArrowRight size={18} />
        </button>
      </div>
    </section>
  );
}