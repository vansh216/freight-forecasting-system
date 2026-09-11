import { Ship } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-navy text-slate-300">
      <div className="max-w-6xl mx-auto px-6 py-14 grid md:grid-cols-3 gap-10">
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Ship size={18} className="text-teal" />
            <span className="font-bold text-white text-lg">
              Freight<span className="text-teal">DSS</span>
            </span>
          </div>
          <p className="text-sm text-slate-400 leading-relaxed max-w-xs">
            A freight intelligence and chartering decision support system for
            bulk cargo procurement to India's East Coast ports.
          </p>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3 text-sm">Platform</h4>
          <ul className="space-y-2 text-sm text-slate-400">
            <li><a href="/vessel-recommendation" className="hover:text-teal transition-colors">Vessel Recommendation</a></li>
            <li><a href="/forecast" className="hover:text-teal transition-colors">Freight Forecast</a></li>
            <li><a href="/arrivals" className="hover:text-teal transition-colors">Arrival Board</a></li>
            <li><a href="/live-map" className="hover:text-teal transition-colors">Live Map</a></li>
          </ul>
        </div>

        <div>
          <h4 className="text-white font-semibold mb-3 text-sm">Scope</h4>
          <ul className="space-y-2 text-sm text-slate-400">
            <li>Origins: Australia, Indonesia</li>
            <li>Discharge: Paradip, Vizag, Gangavaram</li>
            <li>Vessels: Handysize – Capesize</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-white/10 py-5">
        <p className="text-center text-xs text-slate-500">
          Demo build — port, vessel and freight-rate data is simulated where live feeds are not yet connected.
        </p>
      </div>
    </footer>
  );
}