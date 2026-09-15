import { Link } from "react-router-dom";
import { Ship, TrendingUp, Anchor, Map, ArrowUpRight } from "lucide-react";

const features = [
  {
    to: "/vessel-recommendation",
    icon: Ship,
    title: "Vessel Recommendation",
    description:
      "Get the optimal vessel type — Handysize, Supramax, Panamax, or Capesize — based on cargo volume and real port draft/LOA/beam constraints. Includes live risk alerts.",
    status: "Live",
    video: "/video/bg.video.mp4",
  },
  {
    to: "/forecast",
    icon: TrendingUp,
    title: "Freight Forecast",
    description:
      "Time-series forecasting of freight rate trends across vessel classes, helping you identify the right window to enter the charter market.",
    status: "Live",
    video: "/video/grid.video.mp4",
  },
  {
    to: "/arrivals",
    icon: Anchor,
    title: "Arrival Board",
    description:
      "A live, train-station-style board of vessel arrivals and departures across Paradip, Vizag, and Gangavaram, powered by real-time AIS tracking.",
    status: "Live",
    video: "/video/port.mp4",
  },
  {
    to: "/live-map",
    icon: Map,
    title: "Live Vessel Map",
    description:
      "Visualize vessel positions in real time along active shipping routes between origin and discharge ports.",
    status: "Live",
    video: "video/map.video.mp4",
  },
];

export default function FeaturesGrid() {
  return (
    <section className="relative py-20 overflow-hidden">
      {/* Section-wide background video */}
      <video
        className="absolute inset-0 w-full h-full object-cover"
        autoPlay
        muted
        loop
        playsInline
        src=""
      />
      {/* Light overlay so the whole section stays readable */}
      <div className="absolute inset-0 " />

      <div className="relative z-10 max-w-6xl mx-auto px-6">
        <div className="text-center mb-14">
          <span className="text-xs font-semibold tracking-widest uppercase text-teal-dark">
            Platform
          </span>
          <h2 className="text-3xl font-bold text-navy mt-3">
            Everything in one dashboard
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {features.map(({ to, icon: Icon, title, description, status, video }) => (
            <Link
              key={to}
              to={to}
              className="group relative overflow-hidden rounded-2xl p-7 border border-slate-200 hover:border-teal/40 hover:shadow-lg transition-all"
            >
              {/* Per-card background video */}
              <video
                className="absolute inset-0 w-full h-full object-cover scale-105 group-hover:scale-110 transition-transform duration-700"
                autoPlay
                muted
                loop
                playsInline
                src={video}
              />
              {/* Card overlay — light, so card content stays readable over its own video */}
              <div className="absolute inset-0 bg-white/85 group-hover:bg-white/75 transition-colors duration-300" />

              {/* Card content, above its video */}
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-4">
                  <div className="w-11 h-11 rounded-xl bg-navy flex items-center justify-center">
                    <Icon size={20} className="text-white" />
                  </div>
                  <span
                    className={`text-xs font-semibold px-2.5 py-1 rounded-full ${
                      status === "Live"
                        ? "bg-teal/10 text-teal-dark"
                        : "bg-amber/10 text-amber"
                    }`}
                  >
                    {status}
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-navy mb-2 flex items-center gap-1.5">
                  {title}
                  <ArrowUpRight
                    size={16}
                    className="text-slate-400 group-hover:text-teal-dark transition-colors"
                  />
                </h3>
                <p className="text-sm text-slate-600 leading-relaxed">{description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}